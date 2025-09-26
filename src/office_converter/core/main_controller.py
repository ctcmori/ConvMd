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
from office_converter.core.conversion_manager import ConversionManager, ProcessingStatus
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
        
        # Initialize components with intermediate directory as temp_dir
        intermediate_dir = Path(self.config["temp_directory"])
        self.conversion_manager = ConversionManager(self.config_manager, temp_dir=intermediate_dir)
        self.file_watcher: Optional[FileWatcher] = None
        
        # State management
        self._shutdown_requested = False
        self._shutdown_lock = threading.Lock()
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        self.logger.info("Main controller initialized")
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown")
            self.shutdown()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run_watch_mode(self):
        """
        Run in continuous monitoring mode
        Watches input folder and processes files as they are added/modified
        """
        try:
            input_dir = Path(self.config["input_directory"])
            output_dir = Path(self.config["output_directory"])
            
            self.logger.info(
                f"Starting watch mode",
                input_dir=str(input_dir),
                output_dir=str(output_dir)
            )
            
            # Initialize file watcher
            self.file_watcher = FileWatcher(
                watch_directory=input_dir,
                debounce_seconds=2.0,
                cooldown_seconds=10.0,
                recursive=True
            )
            
            # Register change handler
            def handle_file_change(change):
                if change.change_type in ['created', 'modified']:
                    self.logger.info(f"Processing file change: {change.file_path.name}")
                    self.conversion_manager.convert_office_file(
                        change.file_path, output_dir
                    )
            
            self.file_watcher.register_change_handler('any', handle_file_change)
            
            # Start watching
            self.file_watcher.start_watching()
            
            # Process existing files
            self.file_watcher.scan_existing_files()
            
            self.logger.info("Watch mode active - monitoring for file changes")
            
            # Keep running until shutdown
            while not self._shutdown_requested:
                time.sleep(1)
                
                # Periodic cleanup
                if hasattr(self.file_watcher, 'cleanup_old_records'):
                    self.file_watcher.cleanup_old_records()
            
            self.logger.info("Watch mode stopped")
            
        except Exception as e:
            self.logger.error(f"Watch mode error: {e}")
            raise MainControllerError(f"Watch mode failed: {e}")
    
    def run_single_mode(self, input_path: Optional[Path] = None):
        """
        Run in single execution mode
        Processes files once and exits
        
        Args:
            input_path: Specific file or directory to process (optional)
        """
        try:
            if input_path:
                input_target = input_path
            else:
                input_target = Path(self.config["input_directory"])
            
            output_dir = Path(self.config["output_directory"])
            
            self.logger.info(
                f"Starting single mode",
                input_target=str(input_target),
                output_dir=str(output_dir)
            )
            
            # Collect files to process
            if input_target.is_file():
                if PathUtils.is_office_file(str(input_target)):
                    files_to_process = [input_target]
                else:
                    self.logger.warning(f"Not an Office file: {input_target}")
                    return
            else:
                files_to_process = list(PathUtils.find_office_files(
                    input_target, recursive=True
                ))
            
            if not files_to_process:
                self.logger.info("No Office files found to process")
                return
            
            # Process files
            self.logger.info(f"Processing {len(files_to_process)} files")
            results = self.conversion_manager.convert_batch(files_to_process, output_dir)
            
            # Report results with detailed statistics
            self.logger.info(f"=== 処理完了レポート ===")
            self.logger.info(f"総処理件数: {results['total']}")
            self.logger.info(f"正常処理件数: {results['completed']}")
            self.logger.info(f"異常処理件数: {results['failed']}")
            self.logger.info(f"Warning処理件数: {results['warning']}")
            self.logger.info(f"スキップ件数: {results['skipped']}")
            self.logger.info(f"========================")
            
            # Log individual file results for warnings/failures
            for detail in results['details']:
                if detail.status in [ProcessingStatus.WARNING, ProcessingStatus.FAILED]:
                    self.logger.warning(
                        f"{detail.input_file.name}: {detail.status.value} - {detail.error_message}"
                    )
            
        except Exception as e:
            self.logger.error(f"Single mode error: {e}")
            raise MainControllerError(f"Single mode failed: {e}")
    
    def shutdown(self):
        """Graceful shutdown of all components"""
        with self._shutdown_lock:
            if self._shutdown_requested:
                return
            
            self._shutdown_requested = True
            self.logger.info("Initiating system shutdown")
            
            # Stop file watcher
            if self.file_watcher and self.file_watcher.is_watching():
                self.file_watcher.stop_watching()
            
            self.logger.info("System shutdown completed")
    
    def get_system_status(self):
        """Get current system status information"""
        status = {
            'config_loaded': bool(self.config_manager),
            'shutdown_requested': self._shutdown_requested,
            'watch_mode_active': False
        }
        
        if self.file_watcher:
            status.update({
                'watch_mode_active': self.file_watcher.is_watching(),
                'watcher_stats': self.file_watcher.get_statistics()
            })
        
        return status