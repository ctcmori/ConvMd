#!/usr/bin/env python3
"""
Office-to-Markdown Converter Main Entry Point

OfficeファイルをDify RAG用Markdownに変換するシステムのメインエントリポイント
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from office_converter.core.main_controller import MainController
from office_converter.services.logger_service import LoggerService

def main():
    """Main application entry point"""
    logger = LoggerService()
    
    try:
        # Simple argument parsing for demo
        if len(sys.argv) > 1 and sys.argv[1] == "--watch":
            # Watch mode
            controller = MainController()
            controller.run_watch_mode()
        else:
            # Single mode
            controller = MainController()
            input_file = Path(sys.argv[1]) if len(sys.argv) > 1 else None
            controller.run_single_mode(input_file)
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()