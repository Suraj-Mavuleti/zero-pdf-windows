import sys
import os

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtWebEngineWidgets import *
except ImportError:
    print("FATAL: PyQt5 or PyQtWebEngine not found.")
    sys.exit(1)

class ZeroPDF(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zero PDF - Premium Document Viewer")
        self.setGeometry(100, 100, 1000, 800)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a24; }
            QToolBar { background: #1a1a24; border-bottom: 1px solid #3d3d4e; padding: 10px; spacing: 15px;}
            QPushButton { background: #00C7FF; color: #1a1a24; border-radius: 8px; padding: 8px 20px; font-weight: bold; font-size: 14px;}
            QPushButton:hover { background: #00A3CC; }
            QLabel { color: #cccccc; padding-left: 15px; font-size: 14px; font-family: 'Helvetica Neue', sans-serif;}
        """)
        
        # Chromium WebEngine with PDF Viewer Plugin explicitly enabled
        self.browser = QWebEngineView()
        self.browser.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.browser.settings().setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        self.setCentralWidget(self.browser)
        
        nav_bar = QToolBar("Toolbar")
        nav_bar.setMovable(False)
        self.addToolBar(nav_bar)
        
        open_btn = QPushButton("📂 Open PDF")
        open_btn.clicked.connect(self.open_pdf)
        nav_bar.addWidget(open_btn)
        
        self.file_label = QLabel("No PDF loaded. Click 'Open PDF' to select a file.")
        nav_bar.addWidget(self.file_label)
        
    def open_pdf(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf)", options=options)
        if file_path:
            self.browser.setUrl(QUrl.fromLocalFile(file_path))
            self.file_label.setText(f"Viewing: {os.path.basename(file_path)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    window = ZeroPDF()
    window.show()
    sys.exit(app.exec_())
