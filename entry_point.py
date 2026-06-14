#!/usr/bin/env python3
"""
Entry point for LittleMiner application.
This file is used when packaging the application as an executable.
"""

import sys
import os
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('littleminer.log', encoding='utf-8')
        ]
    )

def main():
    """Main entry point"""
    try:
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting LittleMiner application")
        
        # Import and run the FastAPI application
        import uvicorn
        from main import app, settings
        
        logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
        uvicorn.run(
            app,
            host=settings.api_host,
            port=settings.api_port,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("LittleMiner application stopped")

if __name__ == "__main__":
    main()