"""变换管理模块

Office→PDF→Markdown変換の全体フローを管理し、エラーハンドリングとステータス管理を行います。
"""
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from office_converter.converters import PDFConverter, MarkdownConverter
from office_converter.llm import AzureOpenAIClient, PromptBuilder
from office_converter.services.logger_service import LoggerService
from office_converter.utils.file_system_utils import FileSystemUtils
from office_converter.utils.path_utils import PathUtils

class ProcessingStatus(Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PDF_CONVERTING = "pdf_converting"
    MARKDOWN_CONVERTING = "markdown_converting"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"

@dataclass
class ConversionResult:
    """Conversion result information"""
    input_file: Path
    output_file: Optional[Path]
    status: ProcessingStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    pdf_files: Optional[List[Path]] = None
    
class ConversionManagerError(Exception):
    """Conversion manager related exceptions"""
    pass

class ConversionManager:
    """
    Office-to-Markdown conversion workflow manager
    - Office to PDF conversion
    - PDF to Markdown conversion via LLM
    - Error handling and recovery
    - Progress tracking
    """
    
    def __init__(self, config_manager, temp_dir: Optional[Path] = None):
        self.config = config_manager
        self.logger = LoggerService()
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "office_converter"
        
        # Clean up previous intermediate files at startup
        self._cleanup_intermediate_directory()
        
        # Initialize converters
        self.pdf_converter = PDFConverter()
        
        # Initialize Azure OpenAI client
        azure_config = self.config.get_azure_openai_config()
        self.azure_client = AzureOpenAIClient(
            endpoint=azure_config["endpoint"],
            api_key=azure_config["api_key"],
            deployment_name=azure_config["deployment_name"],
            verify_ssl=False  # SSL証明書検証を無効化（開発環境用）
        )
        
        # Initialize Markdown converter
        prompts_dir = self.config.get_prompts_config()["template_directory"]
        self.markdown_converter = MarkdownConverter(
            azure_client=self.azure_client,
            prompts_dir=Path(prompts_dir)
        )
        
        # Ensure temp directory exists
        FileSystemUtils.ensure_directory(self.temp_dir)
    
    def convert_office_file(self, input_file: Path, output_dir: Path) -> ConversionResult:
        """
        Convert single Office file to Markdown
        
        Args:
            input_file: Input Office file path
            output_dir: Output directory for Markdown
            
        Returns:
            ConversionResult with processing information
        """
        result = ConversionResult(
            input_file=input_file,
            output_file=None,
            status=ProcessingStatus.PENDING,
            start_time=datetime.now()
        )
        
        try:
            # Validate input file
            if not PathUtils.is_office_file(str(input_file)):
                result.status = ProcessingStatus.SKIPPED
                result.error_message = "Not an Office file"
                result.end_time = datetime.now()
                return result
            
            if not input_file.exists():
                result.status = ProcessingStatus.FAILED
                result.error_message = "Input file does not exist"
                result.end_time = datetime.now()
                return result
            
            # Step 1: Convert Office to PDF
            self.logger.info(f"Starting PDF conversion: {input_file.name}")
            result.status = ProcessingStatus.PDF_CONVERTING
            
            pdf_temp_dir = self.temp_dir / "pdf" / input_file.stem
            FileSystemUtils.ensure_directory(pdf_temp_dir)
            
            pdf_files = self.pdf_converter.convert_office_to_pdf(input_file, pdf_temp_dir)
            result.pdf_files = pdf_files
            
            if not pdf_files:
                result.status = ProcessingStatus.FAILED
                result.error_message = "PDF conversion failed - no output files"
                result.end_time = datetime.now()
                return result
            
            # Step 2: Check PDF content for protection
            self.logger.info(f"Checking PDF content: {len(pdf_files)} PDF files")
            
            # For multiple PDFs (Excel sheets), combine them
            if len(pdf_files) == 1:
                pdf_file = pdf_files[0]
                output_file = output_dir / f"{input_file.stem}.md"
            else:
                # Handle multiple PDFs (Excel sheets)
                pdf_file = pdf_files[0]  # Use first for now, TODO: combine multiple
                output_file = output_dir / f"{input_file.stem}.md"
            
            # Check if PDF is protected by Microsoft Information Protection
            if self._is_protected_pdf(pdf_file):
                result.status = ProcessingStatus.WARNING
                result.error_message = "Microsoft Information Protection detected - cannot process protected content"
                result.end_time = datetime.now()
                
                # Create a warning markdown file
                FileSystemUtils.ensure_directory(output_dir)
                self._create_warning_markdown(output_file, input_file, "Microsoft Information Protection")
                result.output_file = output_file
                
                self.logger.warning(
                    f"Protected content detected",
                    input_file=input_file.name,
                    protection_type="Microsoft Information Protection"
                )
                
                return result
            
            # Step 3: Convert PDF(s) to Markdown with Excel data enhancement
            self.logger.info(f"Starting Markdown conversion: {len(pdf_files)} PDF files")
            result.status = ProcessingStatus.MARKDOWN_CONVERTING
            
            FileSystemUtils.ensure_directory(output_dir)
            
            # Convert PDF to Markdown using LLM
            converted_file = self.markdown_converter.convert_pdf_to_markdown(
                pdf_file, output_file, preserve_structure=True
            )
            
            result.output_file = converted_file
            result.status = ProcessingStatus.COMPLETED
            result.end_time = datetime.now()
            
            self.logger.info(
                f"Conversion completed successfully",
                input_file=input_file.name,
                output_file=converted_file.name,
                duration=(result.end_time - result.start_time).total_seconds()
            )
            
            return result
            
        except Exception as e:
            result.status = ProcessingStatus.FAILED
            result.error_message = str(e)
            result.end_time = datetime.now()
            
            # Import traceback for detailed error information
            import traceback
            
            self.logger.error(
                f"Conversion failed",
                input_file=input_file.name,
                error=str(e),
                traceback=traceback.format_exc()
            )
            
            return result
        
        finally:
            # Keep temp files for inspection - cleanup at next startup instead
            pass
    
    def convert_batch(self, input_files: List[Path], output_dir: Path) -> Dict[str, Any]:
        """
        Convert multiple Office files to Markdown
        
        Args:
            input_files: List of input Office files
            output_dir: Output directory for Markdown files
            
        Returns:
            Batch conversion results
        """
        results = {
            'total': len(input_files),
            'completed': 0,
            'failed': 0,
            'skipped': 0,
            'warning': 0,
            'details': []
        }
        
        self.logger.info(f"Starting batch conversion: {len(input_files)} files")
        
        for input_file in input_files:
            try:
                result = self.convert_office_file(input_file, output_dir)
                results['details'].append(result)
                
                if result.status == ProcessingStatus.COMPLETED:
                    results['completed'] += 1
                elif result.status == ProcessingStatus.FAILED:
                    results['failed'] += 1
                elif result.status == ProcessingStatus.SKIPPED:
                    results['skipped'] += 1
                elif result.status == ProcessingStatus.WARNING:
                    results['warning'] += 1
                    
            except Exception as e:
                self.logger.error(f"Batch conversion error: {e}")
                results['failed'] += 1
        
        # Detailed batch completion report
        self.logger.info(f"=== バッチ変換完了レポート ===")
        self.logger.info(f"総処理件数: {results['total']}")
        self.logger.info(f"正常処理件数: {results['completed']}")  
        self.logger.info(f"異常処理件数: {results['failed']}")
        self.logger.info(f"Warning処理件数: {results['warning']}")
        self.logger.info(f"スキップ件数: {results['skipped']}")
        self.logger.info(f"============================")
        
        # Log details for problematic files
        for detail in results['details']:
            if detail.status == ProcessingStatus.WARNING:
                self.logger.warning(f"WARNING: {detail.input_file.name} - {detail.error_message}")
            elif detail.status == ProcessingStatus.FAILED:
                self.logger.error(f"FAILED: {detail.input_file.name} - {detail.error_message}")
        
        return results
    
    def _cleanup_temp_files(self, result: ConversionResult):
        """Clean up temporary files after conversion (DEPRECATED - now done at startup)"""
        # This method is deprecated - cleanup is now done at startup to allow inspection
        pass
    
    def _is_protected_pdf(self, pdf_file: Path) -> bool:
        """
        Check if PDF is protected by Microsoft Information Protection
        
        Args:
            pdf_file: PDF file to check
            
        Returns:
            True if protected, False otherwise
        """
        try:
            # Try to read PDF content using PyPDF2 or similar
            import PyPDF2
            
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    return True
                
                # Check first few pages for protection indicators
                pages_to_check = min(3, len(pdf_reader.pages))
                for i in range(pages_to_check):
                    try:
                        page = pdf_reader.pages[i]
                        text = page.extract_text().lower()
                        
                        # Check for Microsoft Information Protection indicators
                        protection_indicators = [
                            "microsoft information protection",
                            "azure rights management",
                            "このドキュメントでは、microsoft information protection",
                            "rights management",
                            "暗号化が使用されています"
                        ]
                        
                        for indicator in protection_indicators:
                            if indicator in text:
                                return True
                                
                    except Exception:
                        # If we can't extract text from page, might be protected
                        continue
                        
        except Exception as e:
            self.logger.warning(f"Could not check PDF protection status: {e}")
            # If we can't read the PDF at all, assume it might be protected
            return False
            
        return False
    
    def _create_warning_markdown(self, output_file: Path, input_file: Path, protection_type: str):
        """
        Create a warning markdown file for protected content
        
        Args:
            output_file: Output markdown file path
            input_file: Original input file
            protection_type: Type of protection detected
        """
        warning_content = f"""# 変換警告: {input_file.name}

## ⚠️ 処理できませんでした

**理由**: {protection_type}による保護

このファイルは{protection_type}により保護されているため、Markdown変換を実行できませんでした。

### 対処方法
1. ファイルの所有者に連絡してアクセス許可を取得してください
2. 保護されていないバージョンのファイルを取得してください  
3. {protection_type}をサポートするビューアーでファイルを開いてください

### ファイル情報
- 元ファイル名: {input_file.name}
- 変換日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 検出された保護: {protection_type}

---
*この警告ファイルは自動生成されました*
"""
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(warning_content)
        except Exception as e:
            self.logger.error(f"Could not create warning markdown: {e}")

    def _cleanup_intermediate_directory(self):
        """Clean up intermediate directory at startup"""
        try:
            if self.temp_dir.exists():
                # Remove all PDF subdirectories from previous runs
                pdf_dir = self.temp_dir / "pdf"
                if pdf_dir.exists():
                    import shutil
                    shutil.rmtree(pdf_dir, ignore_errors=True)
                    self.logger.info(f"Cleaned up intermediate directory: {pdf_dir}")
        except Exception as e:
            self.logger.warning(f"Intermediate directory cleanup error: {e}")
