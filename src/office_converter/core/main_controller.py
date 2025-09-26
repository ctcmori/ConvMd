"""
メインコントローラーモジュール

システム全体の制御、監視モード・一回実行モードの管理を行います。
"""
import signal
import sys
import time
from pathlib import Path
from typing import Optional, List
import threading

from office_converter.config.manager import ConfigManager
from office_converter.core.conversion_manager import ConversionManager
from office_converter.monitoring.file_watcher import FileWatcher
from office_converter.services.logger_service import LoggerService
from office_converter.utils.path_utils import PathUtils

class MainControllerError(Exception):
    """Main controller related exceptions"""
    pass

class MainController:
    """
    System orchestration and lifecycle management
    - Watch mode: continuous monitoring
    - Single mode: one-time processing
    - Graceful shutdown handling
    - Component integration
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        # Load configuration
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_folders_config()
        
        # Initialize logger
        self.logger = LoggerService()
        
        # Initialize components
        intermediate_dir = Path(self.config["intermediate"])
        self.conversion_manager = ConversionManager(self.config_manager, temp_dir=intermediate_dir)
        self.file_watcher: Optional[FileWatcher] = None
        
        # State management
        self._shutdown_requested = False
        self._shutdown_lock = threading.Lock()
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        # Clean up intermediate directory
        self._cleanup_intermediate_directory()
        
        self.logger.info("Main controller initialized")
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown")
            self.shutdown()
        
        signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
    
    def _cleanup_intermediate_directory(self):
        """Clean up intermediate directory"""
        try:
            intermediate_dir = Path(self.config["intermediate"])
            pdf_dir = intermediate_dir / "pdf"
            if pdf_dir.exists():
                import shutil
                shutil.rmtree(pdf_dir)
                self.logger.info(f"Cleaned up intermediate directory: {pdf_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup intermediate directory: {e}")
    
    def run_single_mode(self, input_file: Optional[Path] = None):
        """Run single processing mode"""
        try:
            self.logger.info("Starting single mode")
            
            if input_file and input_file.exists():
                # Process specific file
                result = self.conversion_manager.convert_single_file(input_file)
                self.logger.info(f"Single file processed: {result}")
            else:
                # Process input directory
                input_dir = Path(self.config["input"])
                files = self._get_office_files(input_dir)
                
                if not files:
                    self.logger.info(f"No Office files found in {input_dir}")
                    return
                
                self.logger.info(f"Processing {len(files)} files")
                results = self.conversion_manager.convert_batch(files)
                
                self.logger.info("Starting batch conversion: {} files".format(len(files)))
                for file_path in files:
                    if self._shutdown_requested:
                        break
                    try:
                        self.logger.info(f"Starting PDF conversion: {file_path.name}")
                        result = self.conversion_manager.convert_single_file(file_path)
                        if result:
                            self.logger.info(f"Conversion completed: {file_path.name}")
                        else:
                            self.logger.error("Conversion failed")
                    except Exception as e:
                        self.logger.error(f"Conversion failed for {file_path.name}: {e}")
                
            self.logger.info("Batch conversion completed")
            
        except Exception as e:
            self.logger.error(f"Single mode error: {e}")
            raise MainControllerError(f"Single mode failed: {e}")
        finally:
            self.logger.info("Single mode completed")
    
    def run_watch_mode(self):
        """Run continuous monitoring mode"""
        try:
            self.logger.info("Starting watch mode")
            
            input_dir = Path(self.config["input"])
            if not input_dir.exists():
                input_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created input directory: {input_dir}")
            
            # Initialize and start file watcher
            self.file_watcher = FileWatcher(
                input_dir,
                self._on_file_change,
                patterns=["*.docx", "*.xlsx", "*.pptx", "*.doc", "*.xls", "*.ppt"]
            )
            
            self.file_watcher.start()
            self.logger.info(f"File watcher started for: {input_dir}")
            
            # Keep running until shutdown
            while not self._shutdown_requested:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Watch mode interrupted by user")
        except Exception as e:
            self.logger.error(f"Watch mode error: {e}")
            raise MainControllerError(f"Watch mode failed: {e}")
        finally:
            self._stop_file_watcher()
            self.logger.info("Watch mode completed")
    
    def _on_file_change(self, file_path: Path):
        """Handle file change events"""
        try:
            if self._shutdown_requested:
                return
            
            self.logger.info(f"File change detected: {file_path}")
            
            if self._is_office_file(file_path):
                # Add delay to ensure file is fully written
                time.sleep(2)
                
                if file_path.exists():
                    result = self.conversion_manager.convert_single_file(file_path)
                    if result:
                        self.logger.info(f"Auto-conversion completed: {file_path.name}")
                    else:
                        self.logger.warning(f"Auto-conversion failed: {file_path.name}")
                        
        except Exception as e:
            self.logger.error(f"File change handling error: {e}")
    
    def _get_office_files(self, directory: Path) -> List[Path]:
        """Get all Office files from directory"""
        office_extensions = [".docx", ".xlsx", ".pptx", ".doc", ".xls", ".ppt"]
        files = []
        
        if directory.exists():
            for ext in office_extensions:
                files.extend(directory.glob(f"*{ext}"))
        
        return files
    
    def _is_office_file(self, file_path: Path) -> bool:
        """Check if file is an Office file"""
        office_extensions = [".docx", ".xlsx", ".pptx", ".doc", ".xls", ".ppt"]
        return file_path.suffix.lower() in office_extensions
    
    def _stop_file_watcher(self):
        """Stop file watcher safely"""
        if self.file_watcher:
            try:
                self.file_watcher.stop()
                self.logger.info("File watcher stopped")
            except Exception as e:
                self.logger.warning(f"Error stopping file watcher: {e}")
            finally:
                self.file_watcher = None
    
    def shutdown(self):
        """Graceful shutdown"""
        with self._shutdown_lock:
            if self._shutdown_requested:
                return
            
            self._shutdown_requested = True
            self.logger.info("Initiating system shutdown")
            
            # Stop file watcher
            self._stop_file_watcher()
            
            # Stop conversion manager
            if hasattr(self.conversion_manager, 'shutdown'):
                try:
                    self.conversion_manager.shutdown()
                except Exception as e:
                    self.logger.warning(f"Error during conversion manager shutdown: {e}")
            
            self.logger.info("System shutdown completed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()