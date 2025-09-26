"""
ログサービスモジュール

構造化ログ出力とログレベル管理を提供します。
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

class LoggerService:
    """
    統一ログサービス
    構造化ログ出力とレベル制御を提供
    """
    
    _instance: Optional['LoggerService'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        """ログシステム初期化"""
        if self._logger is not None:
            return
        
        # ログレベル設定
        log_level = logging.INFO
        
        # ログフォーマッター設定
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # メインロガー作成
        self._logger = logging.getLogger('office_converter')
        self._logger.setLevel(log_level)
        
        # 既存ハンドラーをクリア
        if self._logger.handlers:
            self._logger.handlers.clear()
        
        # コンソールハンドラー追加
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # ファイルハンドラー追加（オプション）
        try:
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(
                logs_dir / "converter.log",
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        except Exception:
            # ファイルログが失敗しても続行
            pass
    
    def debug(self, message: str, **kwargs):
        """デバッグメッセージログ出力"""
        if self._logger:
            self._logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """情報メッセージログ出力"""
        if self._logger:
            self._logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """警告メッセージログ出力"""
        if self._logger:
            self._logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """エラーメッセージログ出力"""
        if self._logger:
            self._logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """致命的エラーメッセージログ出力"""
        if self._logger:
            self._logger.critical(message, **kwargs)
    
    def set_level(self, level: str):
        """ログレベル変更"""
        if self._logger:
            numeric_level = getattr(logging, level.upper(), logging.INFO)
            self._logger.setLevel(numeric_level)
            for handler in self._logger.handlers:
                handler.setLevel(numeric_level)