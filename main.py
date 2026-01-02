#!/usr/bin/env python3
"""
Mouse Configuration Tool - Main Application
A comprehensive mouse configuration utility with advanced features
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

# Import core components
from mouse_config.utils.logger import get_logger
from mouse_config.utils.config import check_dependencies, get_system_info

# Import PC optimizer
from mouse_config.advanced import PCOptimizer


def main():
    """Main application entry point"""
    try:
        # Initialize logger
        logger = get_logger(__name__)
        logger.info("Starting Mouse Configuration Tool v2.1.0")
        
        # Check dependencies
        logger.info("Checking dependencies...")
        missing_deps = check_dependencies()
        
        if missing_deps:
            error_msg = f"Missing dependencies: {', '.join(missing_deps)}"
            logger.error(error_msg)
            
            # Show error dialog
            app = QApplication(sys.argv)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Missing Dependencies")
            msg.setText(error_msg)
            msg.setInformativeText("Please install the missing dependencies:\n\n" + 
                              "pip install " + " ".join(missing_deps))
            msg.exec()
            return
        
        # Get system info
        system_info = get_system_info()
        logger.info(f"System: {system_info['system']} {system_info['release']}")
        logger.info(f"Python: {system_info['python_version']}")
        logger.info(f"CPU: {system_info['cpu']} ({system_info['cpu_count']} cores)")
        logger.info(f"Memory: {system_info['memory']['total'] / (1024**3):.1f} GB")
        
        # Initialize PC optimizer
        pc_optimizer = PCOptimizer()
        logger.info(f"PC Specs: {pc_optimizer.pc_specs.cpu_name if pc_optimizer.pc_specs else 'Unknown'}")
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Mouse Configuration Tool")
        app.setApplicationVersion("2.1.0")
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create main window with error handling
        try:
            from mouse_config.gui.main_window import MouseConfigGUI
            main_window = MouseConfigGUI()
            main_window.show()
            
            logger.info("Application started successfully")
            sys.exit(app.exec())
            
        except ImportError as e:
            logger.error(f"Failed to import GUI components: {e}")
            
            # Show error dialog
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Import Error")
            msg.setText(f"Failed to load GUI components:\n{e}")
            msg.setInformativeText("Some GUI components may not be available.\n"
                              "The application will run with limited functionality.")
            msg.exec()
            return
            
        except Exception as e:
            logger.error(f"Error initializing GUI: {e}")
            
            # Show error dialog
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Initialization Error")
            msg.setText(f"Error initializing application:\n{e}")
            msg.setInformativeText("Please check the logs for more details.")
            msg.exec()
            return
        
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
