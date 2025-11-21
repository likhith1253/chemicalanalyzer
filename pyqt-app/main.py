#!/usr/bin/env python3
"""
ChemViz - Chemical Equipment Parameter Visualizer
Main application entry point
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from widgets.login_window import LoginWindow
from widgets.main_window import MainWindow
from api_client import api_client


def setup_application():
    """Setup the Qt application"""
    # Enable high DPI scaling - MUST be done before QApplication is created
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("ChemViz")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("ChemViz")
    
    # Set default font
    font = QFont("Arial", 10)
    app.setFont(font)
    
    return app


def main():
    """Main application entry point"""
    print("DEBUG: Starting application setup...")
    app = setup_application()
    print("DEBUG: Application setup complete.")
    
    # Show login window first
    print("DEBUG: Initializing LoginWindow...")
    login_window = LoginWindow()
    print("DEBUG: LoginWindow initialized. Showing dialog...")
    
    result = login_window.exec_()
    print(f"DEBUG: LoginWindow closed with result: {result}")
    
    if result == LoginWindow.Accepted:
        # Login successful, show main window
        print("DEBUG: Login accepted. Initializing MainWindow...")
        main_window = MainWindow()
        main_window.show()
        print("DEBUG: MainWindow shown. Starting event loop...")
        
        # Run the application
        return_code = app.exec_()
        print(f"DEBUG: Application exited with code: {return_code}")
        
        # Cleanup
        api_client.logout()
        sys.exit(return_code)
    else:
        # Login failed or cancelled
        print("DEBUG: Login cancelled or failed. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Show error dialog for unhandled exceptions
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        QMessageBox.critical(
            None,
            "Application Error",
            f"An unexpected error occurred:\n\n{str(e)}\n\n"
            "Please check your configuration and try again."
        )
        sys.exit(1)
