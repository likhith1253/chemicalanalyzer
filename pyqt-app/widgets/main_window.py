import sys
import os
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QMessageBox, 
                            QTableWidget, QTableWidgetItem, QListWidget, 
                            QListWidgetItem, QFileDialog, QFrame, QScrollArea,
                            QSplitter, QGridLayout, QSizePolicy, QProgressBar,
                            QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QPalette
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from api_client import api_client


class DataWorker(QThread):
    """Worker thread for API calls to avoid blocking UI"""
    datasets_loaded = pyqtSignal(list)
    dataset_detail_loaded = pyqtSignal(dict)
    upload_progress = pyqtSignal(int)
    upload_complete = pyqtSignal(dict)
    ai_insights_ready = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, action, **kwargs):
        super().__init__()
        self.action = action
        self.kwargs = kwargs
    
    def run(self):
        try:
            if self.action == "load_datasets":
                datasets = api_client.get_datasets()
                self.datasets_loaded.emit(datasets)
            elif self.action == "load_dataset_detail":
                dataset_id = self.kwargs.get("dataset_id")
                detail = api_client.get_dataset_detail(dataset_id)
                self.dataset_detail_loaded.emit(detail)
            elif self.action == "upload_csv":
                file_path = self.kwargs.get("file_path")
                # Simulate progress for demo (in real app, you'd track actual progress)
                for i in range(0, 101, 10):
                    self.upload_progress.emit(i)
                    self.msleep(100)
                result = api_client.upload_csv(file_path)
                self.upload_complete.emit(result)
            elif self.action == "generate_ai_insights":
                dataset_id = self.kwargs.get("dataset_id")
                insights = api_client.get_ai_insights(dataset_id)
                self.ai_insights_ready.emit(insights)

        except Exception as e:
            self.error.emit(str(e))


class ChartCanvas(FigureCanvas):
    """Matplotlib canvas for displaying charts"""
    
    def __init__(self, parent=None, width=6, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()
    
    def clear_chart(self):
        """Clear the chart"""
        self.fig.clear()
        self.draw()
    
    def plot_type_distribution(self, data):
        """Plot equipment type distribution as bar chart"""
        if not data or 'type_distribution' not in data:
            self.clear_chart()
            return
        
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        types = list(data['type_distribution'].keys())
        counts = list(data['type_distribution'].values())
        
        colors = ['#667eea', '#48bb78', '#ed8936', '#9f7aea', '#f56565', '#38b2ac']
        colors = colors[:len(types)]  # Ensure we have enough colors
        
        bars = ax.bar(types, counts, color=colors)
        ax.set_xlabel('Equipment Type')
        ax.set_ylabel('Count')
        ax.set_title('Equipment Type Distribution')
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels if needed
        if len(types) > 5:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom')
        
        try:
            self.fig.tight_layout()
        except Exception as e:
            print(f"DEBUG: tight_layout failed: {e}")
        
        self.draw()


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.current_dataset = None
        self.datasets = []
        self.worker = None
        self.init_ui()
        self.load_initial_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("ChemViz - Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel (History)
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel (Main content)
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter sizes (30% left, 70% right)
        splitter.setSizes([360, 840])
        
        # Apply styles
        self.apply_styles()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
    
    def create_left_panel(self):
        """Create the left panel with history and controls"""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        
        # User info
        self.user_label = QLabel("User: Not logged in")
        self.user_label.setFont(QFont("Arial", 10, QFont.Bold))
        left_layout.addWidget(self.user_label)
        
        # Upload section
        upload_frame = QFrame()
        upload_frame.setObjectName("uploadFrame")
        upload_layout = QVBoxLayout(upload_frame)
        
        upload_title = QLabel("Upload Data")
        upload_title.setFont(QFont("Arial", 12, QFont.Bold))
        upload_layout.addWidget(upload_title)
        
        self.upload_button = QPushButton("📁 Upload CSV")
        self.upload_button.clicked.connect(self.handle_upload_csv)
        upload_layout.addWidget(self.upload_button)
        
        self.upload_progress = QProgressBar()
        self.upload_progress.setVisible(False)
        upload_layout.addWidget(self.upload_progress)
        
        left_layout.addWidget(upload_frame)
        
        # History section
        history_frame = QFrame()
        history_frame.setObjectName("historyFrame")
        history_layout = QVBoxLayout(history_frame)
        
        history_title = QLabel("Dataset History")
        history_title.setFont(QFont("Arial", 12, QFont.Bold))
        history_layout.addWidget(history_title)
        
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.handle_history_selection)
        history_layout.addWidget(self.history_list)
        
        left_layout.addWidget(history_frame)
        
        # Actions section
        actions_frame = QFrame()
        actions_frame.setObjectName("actionsFrame")
        actions_layout = QVBoxLayout(actions_frame)
        
        self.pdf_button = QPushButton("📄 Download PDF")
        self.pdf_button.clicked.connect(self.handle_download_pdf)
        self.pdf_button.setEnabled(False)
        actions_layout.addWidget(self.pdf_button)
        
        self.ai_button = QPushButton("✨ AI Insights")
        self.ai_button.clicked.connect(self.handle_ai_insights)
        self.ai_button.setEnabled(False)
        self.ai_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ed8936, stop:1 #f6ad55);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #dd6b20, stop:1 #ed8936);
            }
        """)
        actions_layout.addWidget(self.ai_button)
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self.load_initial_data)
        actions_layout.addWidget(self.refresh_button)
        
        left_layout.addWidget(actions_frame)
        
        left_layout.addStretch()
        
        return left_panel
    
    def create_right_panel(self):
        """Create the right panel with main content"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)
        
        # Title
        self.title_label = QLabel("Dashboard")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        right_layout.addWidget(self.title_label)
        
        # Summary cards
        self.summary_frame = QFrame()
        self.summary_frame.setObjectName("summaryFrame")
        self.summary_layout = QGridLayout(self.summary_frame)
        right_layout.addWidget(self.summary_frame)
        
        # Chart section
        chart_frame = QFrame()
        chart_frame.setObjectName("chartFrame")
        chart_layout = QVBoxLayout(chart_frame)
        
        chart_title = QLabel("Equipment Type Distribution")
        chart_title.setFont(QFont("Arial", 12, QFont.Bold))
        chart_layout.addWidget(chart_title)
        
        self.chart_canvas = ChartCanvas(self, width=8, height=4)
        chart_layout.addWidget(self.chart_canvas)
        
        right_layout.addWidget(chart_frame)
        
        # Table section
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        table_layout = QVBoxLayout(table_frame)
        
        table_title = QLabel("Equipment Data")
        table_title.setFont(QFont("Arial", 12, QFont.Bold))
        table_layout.addWidget(table_title)
        
        # Create table with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        
        scroll_area.setWidget(self.data_table)
        table_layout.addWidget(scroll_area)
        
        right_layout.addWidget(table_frame)
        
        return right_panel
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        upload_action = file_menu.addAction('Upload CSV')
        upload_action.triggered.connect(self.handle_upload_csv)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
    
    def apply_styles(self):
        """Apply modern styling to the window"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f5f7fa, stop:1 #c3cfe2);
            }
            
            QFrame#uploadFrame, QFrame#historyFrame, QFrame#actionsFrame,
            QFrame#summaryFrame, QFrame#chartFrame, QFrame#tableFrame {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4c51bf, stop:1 #553c9a);
            }
            
            QPushButton:disabled {
                background: #cbd5e0;
                color: #718096;
            }
            
            QListWidget {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 5px;
            }
            
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f7fafc;
            }
            
            QListWidget::item:selected {
                background: #667eea;
                color: white;
            }
            
            QListWidget::item:hover {
                background: #edf2f7;
            }
            
            QTableWidget {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f7fafc;
            }
            
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f7fafc;
            }
            
            QTableWidget::item:selected {
                background: #667eea;
                color: white;
            }
            
            QHeaderView::section {
                background: #f7fafc;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 8px;
                font-weight: bold;
            }
            
            QProgressBar {
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                text-align: center;
                background: white;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 3px;
            }
        """)
    
    def load_initial_data(self):
        """Load initial data from API"""
        if not api_client.is_authenticated():
            self.show_error("Not authenticated. Please login first.")
            return
        
        self.status_bar.showMessage("Loading datasets...")
        self.worker = DataWorker("load_datasets")
        self.worker.datasets_loaded.connect(self.on_datasets_loaded)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    @pyqtSlot(list)
    def on_datasets_loaded(self, datasets):
        """Handle datasets loaded from API"""
        self.datasets = datasets
        self.populate_history_list(datasets)
        self.status_bar.showMessage(f"Loaded {len(datasets)} datasets")
        
        # Load the most recent dataset if available
        if datasets:
            self.load_dataset_detail(datasets[0]['id'])
    
    @pyqtSlot(dict)
    def on_dataset_detail_loaded(self, detail):
        """Handle dataset detail loaded from API"""
        self.current_dataset = detail
        self.update_ui_with_dataset(detail)
        self.status_bar.showMessage(f"Loaded dataset: {detail.get('name', 'Unknown')}")
    
    @pyqtSlot(str)
    def on_error(self, error_message):
        """Handle error from worker thread"""
        self.show_error(error_message)
        self.status_bar.showMessage("Error occurred")
    
    def populate_history_list(self, datasets):
        """Populate the history list with datasets"""
        self.history_list.clear()
        
        for dataset in datasets[:10]:  # Show last 10 datasets
            name = dataset.get('name', 'Unknown')
            uploaded_at = dataset.get('uploaded_at', '')
            
            # Format date
            if uploaded_at:
                try:
                    date_obj = datetime.fromisoformat(uploaded_at.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_date = uploaded_at
            else:
                formatted_date = 'Unknown date'
            
            item_text = f"{name}\n{formatted_date}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, dataset['id'])
            self.history_list.addItem(item)
    
    def load_dataset_detail(self, dataset_id):
        """Load detail for a specific dataset"""
        self.status_bar.showMessage("Loading dataset details...")
        self.worker = DataWorker("load_dataset_detail", dataset_id=dataset_id)
        self.worker.dataset_detail_loaded.connect(self.on_dataset_detail_loaded)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def update_ui_with_dataset(self, dataset):
        """Update UI with dataset data"""
        # Update title
        self.title_label.setText(f"Dashboard - {dataset.get('name', 'Unknown Dataset')}")
        
        # Update summary cards
        self.update_summary_cards(dataset)
        
        # Update chart
        self.chart_canvas.plot_type_distribution(dataset)
        
        # Update table
        self.update_data_table(dataset)
        
        # Enable PDF button
        self.pdf_button.setEnabled(True)
        self.ai_button.setEnabled(True)
    
    def update_summary_cards(self, dataset):
        """Update summary cards with dataset information"""
        # Clear existing widgets
        for i in reversed(range(self.summary_layout.count())): 
            self.summary_layout.itemAt(i).widget().setParent(None)
        
        # Create summary cards
        cards_data = [
            ("Total Records", dataset.get('total_count', 0), "📊"),
            ("Avg Flowrate", f"{dataset.get('avg_flowrate', 0):.2f}", "💧"),
            ("Avg Pressure", f"{dataset.get('avg_pressure', 0):.2f}", "🔥"),
            ("Avg Temperature", f"{dataset.get('avg_temperature', 0):.2f}", "🌡️"),
        ]
        
        for i, (title, value, icon) in enumerate(cards_data):
            card = self.create_summary_card(title, value, icon)
            self.summary_layout.addWidget(card, i // 2, i % 2)
    
    def create_summary_card(self, title, value, icon):
        """Create a summary card widget"""
        card = QFrame()
        card.setObjectName("summaryCard")
        card_layout = QVBoxLayout(card)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont("Arial", 24))
        card_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 10))
        card_layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setFont(QFont("Arial", 16, QFont.Bold))
        card_layout.addWidget(value_label)
        
        # Style the card
        card.setStyleSheet("""
            QFrame#summaryCard {
                background: rgba(255, 255, 255, 0.8);
                border: 1px solid rgba(102, 126, 234, 0.3);
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
        """)
        
        return card
    
    def update_data_table(self, dataset):
        """Update data table with dataset preview rows"""
        preview_rows = dataset.get('preview_rows', [])
        
        if not preview_rows:
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            return
        
        # Get column names from first row
        columns = list(preview_rows[0].keys())
        self.data_table.setColumnCount(len(columns))
        self.data_table.setHorizontalHeaderLabels(columns)
        
        # Set row count and populate data
        self.data_table.setRowCount(len(preview_rows))
        
        for row_idx, row_data in enumerate(preview_rows):
            for col_idx, column in enumerate(columns):
                value = str(row_data.get(column, ''))
                item = QTableWidgetItem(value)
                self.data_table.setItem(row_idx, col_idx, item)
        
        # Resize columns to content
        self.data_table.resizeColumnsToContents()
    
    @pyqtSlot()
    def handle_upload_csv(self):
        """Handle CSV file upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.upload_csv_file(file_path)
    
    def upload_csv_file(self, file_path):
        """Upload CSV file to API"""
        if not api_client.is_authenticated():
            self.show_error("Not authenticated. Please login first.")
            return
        
        # Show progress bar
        self.upload_progress.setVisible(True)
        self.upload_progress.setValue(0)
        self.upload_button.setEnabled(False)
        
        self.status_bar.showMessage("Uploading CSV file...")
        self.worker = DataWorker("upload_csv", file_path=file_path)
        self.worker.upload_progress.connect(self.on_upload_progress)
        self.worker.upload_complete.connect(self.on_upload_complete)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    @pyqtSlot(int)
    def on_upload_progress(self, progress):
        """Handle upload progress"""
        self.upload_progress.setValue(progress)
    
    @pyqtSlot(dict)
    def on_upload_complete(self, result):
        """Handle upload completion"""
        self.upload_progress.setVisible(False)
        self.upload_button.setEnabled(True)
        
        QMessageBox.information(
            self,
            "Upload Successful",
            "CSV file uploaded successfully!"
        )
        
        # Refresh datasets
        self.load_initial_data()
    
    @pyqtSlot(QListWidgetItem)
    def handle_history_selection(self, item):
        """Handle history list item selection"""
        dataset_id = item.data(Qt.UserRole)
        if dataset_id:
            self.load_dataset_detail(dataset_id)
    
    @pyqtSlot()
    def handle_download_pdf(self):
        """Handle PDF download"""
        if not self.current_dataset:
            self.show_error("No dataset selected")
            return
        
        # Get save path from user
        dataset_name = self.current_dataset.get('name', 'dataset')
        default_filename = f"{dataset_name}_report.pdf"
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            default_filename,
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if save_path:
            self.download_pdf_report(save_path)
    
    def download_pdf_report(self, save_path):
        """Download PDF report for current dataset"""
        if not api_client.is_authenticated():
            self.show_error("Not authenticated. Please login first.")
            return
        
        if not self.current_dataset:
            self.show_error("No dataset selected")
            return
        
        try:
            self.status_bar.showMessage("Downloading PDF report...")
            success = api_client.download_pdf(self.current_dataset['id'], save_path)
            
            if success:
                QMessageBox.information(
                    self,
                    "Download Successful",
                    f"PDF report saved to:\n{save_path}"
                )
                self.status_bar.showMessage("PDF downloaded successfully")
            else:
                self.show_error("Failed to download PDF")
        except Exception as e:
            self.show_error(f"PDF download failed: {str(e)}")
    
    def handle_ai_insights(self):
        """Handle AI insights generation"""
        if not self.current_dataset:
            self.show_error("No dataset selected")
            return
            
        self.status_bar.showMessage("Generating AI insights... This may take a moment.")
        self.ai_button.setEnabled(False)
        self.ai_button.setText("Generating...")
        
        self.worker = DataWorker("generate_ai_insights", dataset_id=self.current_dataset['id'])
        self.worker.ai_insights_ready.connect(self.on_ai_insights_ready)
        self.worker.error.connect(self.on_ai_error)
        self.worker.start()
        
    @pyqtSlot(str)
    def on_ai_insights_ready(self, insights):
        """Handle AI insights ready"""
        self.ai_button.setEnabled(True)
        self.ai_button.setText("✨ AI Insights")
        self.status_bar.showMessage("AI Insights generated")
        
        # Show insights in a dialog
        from PyQt5.QtWidgets import QDialog, QTextEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle("AI Analysis Results")
        dialog.resize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel(f"Insights for {self.current_dataset.get('name', 'Dataset')}")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setMarkdown(insights) # Use setMarkdown for formatting
        text_area.setFont(QFont("Arial", 11))
        layout.addWidget(text_area)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()

    @pyqtSlot(str)
    def on_ai_error(self, error_message):
        """Handle AI generation error"""
        self.ai_button.setEnabled(True)
        self.ai_button.setText("✨ AI Insights")
        self.show_error(error_message)
        self.status_bar.showMessage("Error generating insights")

    def show_error(self, message):
        """Show error message"""
        QMessageBox.critical(self, "Error", message)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About ChemViz",
            "ChemViz - Chemical Equipment Parameter Visualizer\n\n"
            "A desktop application for visualizing and analyzing\n"
            "chemical equipment parameters from CSV data.\n\n"
            "Version 1.0"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Cancel any running worker
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
