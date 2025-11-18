import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QMessageBox, QFrame, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor
from api_client import api_client


class LoginWorker(QThread):
    """Worker thread for login to avoid blocking UI"""
    success = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
    
    def run(self):
        try:
            result = api_client.login(self.username, self.password)
            self.success.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class LoginWindow(QMainWindow):
    """Login window for the application"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("ChemViz - Login")
        self.setFixedSize(400, 500)
        
        # Set window to center of screen
        self.center_on_screen()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Create login form
        self.create_login_form(main_layout)
        
        # Apply styles
        self.apply_styles()
    
    def create_login_form(self, parent_layout):
        """Create the login form"""
        # Title
        title_label = QLabel("ChemViz")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2d3748; margin-bottom: 10px;")
        
        subtitle_label = QLabel("Chemical Equipment Parameter Visualizer")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setStyleSheet("color: #718096; margin-bottom: 30px;")
        
        # Login form container
        form_container = QFrame()
        form_container.setObjectName("formContainer")
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)
        
        # Username field
        username_label = QLabel("Username:")
        username_label.setFont(QFont("Arial", 10, QFont.Bold))
        username_label.setStyleSheet("color: #4a5568;")
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFont(QFont("Arial", 10))
        self.username_input.setObjectName("usernameInput")
        
        # Password field
        password_label = QLabel("Password:")
        password_label.setFont(QFont("Arial", 10, QFont.Bold))
        password_label.setStyleSheet("color: #4a5568;")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Arial", 10))
        self.password_input.setObjectName("passwordInput")
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.handle_login)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 9))
        self.status_label.setObjectName("statusLabel")
        
        # Add widgets to form layout
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_button)
        form_layout.addWidget(self.status_label)
        
        # Add all to main layout
        parent_layout.addWidget(title_label)
        parent_layout.addWidget(subtitle_label)
        parent_layout.addWidget(form_container)
        
        # Add spacer at bottom
        parent_layout.addStretch()
        
        # Set up keyboard shortcuts
        self.password_input.returnPressed.connect(self.handle_login)
    
    def apply_styles(self):
        """Apply modern styling to the window"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f5f7fa, stop:1 #c3cfe2);
            }
            
            QFrame#formContainer {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            }
            
            QLineEdit#usernameInput, QLineEdit#passwordInput {
                padding: 12px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background: white;
                font-size: 14px;
                color: #2d3748;
            }
            
            QLineEdit#usernameInput:focus, QLineEdit#passwordInput:focus {
                border-color: #667eea;
                outline: none;
            }
            
            QPushButton#loginButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton#loginButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
            
            QPushButton#loginButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4c51bf, stop:1 #553c9a);
            }
            
            QPushButton#loginButton:disabled {
                background: #cbd5e0;
                color: #718096;
            }
            
            QLabel#statusLabel {
                color: #e53e3e;
                padding: 5px;
            }
        """)
    
    def center_on_screen(self):
        """Center the window on the screen"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    @pyqtSlot()
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validation
        if not username:
            self.show_error("Please enter your username")
            return
        
        if not password:
            self.show_error("Please enter your password")
            return
        
        # Disable login button and show loading state
        self.login_button.setEnabled(False)
        self.login_button.setText("Logging in...")
        self.status_label.setText("")
        
        # Start login worker thread
        self.worker = LoginWorker(username, password)
        self.worker.success.connect(self.on_login_success)
        self.worker.error.connect(self.on_login_error)
        self.worker.start()
    
    @pyqtSlot(dict)
    def on_login_success(self, result):
        """Handle successful login"""
        self.login_button.setEnabled(True)
        self.login_button.setText("Login")
        
        # Show success message
        QMessageBox.information(
            self, 
            "Login Successful", 
            f"Welcome! You have been successfully logged in."
        )
        
        # Accept the dialog (close window and return success)
        self.accept()
    
    @pyqtSlot(str)
    def on_login_error(self, error_message):
        """Handle login error"""
        self.login_button.setEnabled(True)
        self.login_button.setText("Login")
        self.show_error(error_message)
    
    def show_error(self, message):
        """Show error message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("""
            QLabel#statusLabel {
                color: #e53e3e;
                padding: 5px;
                background: rgba(229, 62, 62, 0.1);
                border-radius: 5px;
            }
        """)
    
    def show_info(self, message):
        """Show info message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("""
            QLabel#statusLabel {
                color: #3182ce;
                padding: 5px;
                background: rgba(49, 130, 206, 0.1);
                border-radius: 5px;
            }
        """)
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
