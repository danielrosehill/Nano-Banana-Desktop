"""Main application window for Nano Banana Desktop."""

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMenuBar, QMenu, QFileDialog,
    QMessageBox, QWidget, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent
from pathlib import Path

from .api_key_dialog import ApiKeyDialog
from .image_editor_tab import ImageEditorTab
from ..core.gemini_client import GeminiClient


class MainWindow(QMainWindow):
    """Main application window with tabbed image editor interface."""

    def __init__(self):
        super().__init__()
        self.gemini_client = GeminiClient()
        self.default_aspect_ratio = "preserve"  # Default aspect ratio
        self.setup_ui()
        self.check_api_key()

        # Enable drag and drop
        self.setAcceptDrops(True)

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Nano Banana Desktop - AI Image Editor")
        self.resize(1200, 800)

        # Create central widget with tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        self.setCentralWidget(self.tab_widget)

        # Create menu bar
        self.create_menu_bar()

        # Show welcome message if no tabs
        if self.tab_widget.count() == 0:
            self.show_welcome()

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Image...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Settings menu
        settings_menu = menubar.addMenu("&Settings")

        api_key_action = QAction("&Configure API Key...", self)
        api_key_action.triggered.connect(self.configure_api_key)
        settings_menu.addAction(api_key_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_welcome(self):
        """Show a welcome widget when no tabs are open."""
        from PySide6.QtWidgets import QPushButton, QComboBox, QGroupBox, QFormLayout
        from PySide6.QtCore import Qt

        welcome_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Welcome title
        title = QLabel("<h1>Nano Banana Desktop</h1>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "<p>AI-powered image editor using Google Gemini</p>"
            "<p><b>Getting Started:</b></p>"
            "<ul>"
            "<li><b>Drag and drop</b> an image file here</li>"
            "<li>Click <b>File → Open Image</b> or the button below</li>"
            "<li>Configure your Gemini API key in <b>Settings</b></li>"
            "<li>Use <b>Ctrl+O</b> to quickly open images</li>"
            "</ul>"
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Aspect Ratio Settings
        settings_group = QGroupBox("Default Settings")
        settings_layout = QFormLayout()

        self.aspect_ratio_combo = QComboBox()
        self.aspect_ratio_combo.addItem("Preserve Original", "preserve")
        self.aspect_ratio_combo.addItem("Square (1:1)", "1:1")
        self.aspect_ratio_combo.addItem("Widescreen (16:9)", "16:9")
        self.aspect_ratio_combo.addItem("Ultrawide (21:9)", "21:9")
        self.aspect_ratio_combo.addItem("Portrait (9:16)", "9:16")
        self.aspect_ratio_combo.currentIndexChanged.connect(self.on_aspect_ratio_changed)

        settings_layout.addRow("Output Aspect Ratio:", self.aspect_ratio_combo)
        settings_group.setLayout(settings_layout)
        settings_group.setMaximumWidth(400)
        layout.addWidget(settings_group, alignment=Qt.AlignCenter)

        # Open button
        open_btn = QPushButton("Open Image")
        open_btn.clicked.connect(self.open_image)
        open_btn.setMinimumWidth(200)
        layout.addWidget(open_btn, alignment=Qt.AlignCenter)

        layout.addStretch()
        welcome_widget.setLayout(layout)

        # Add as a tab
        self.tab_widget.addTab(welcome_widget, "Welcome")

    def check_api_key(self):
        """Check if API key is configured on startup."""
        if not self.gemini_client.has_api_key():
            reply = QMessageBox.question(
                self,
                "API Key Required",
                "No Gemini API key found. Would you like to configure it now?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.configure_api_key()

    def configure_api_key(self):
        """Show dialog to configure Gemini API key."""
        dialog = ApiKeyDialog(self, self.gemini_client)
        dialog.exec()

    def open_image(self):
        """Open an image file in a new tab."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*)"
        )

        if file_path:
            self.create_image_tab(Path(file_path))

    def create_image_tab(self, image_path: Path):
        """
        Create a new tab for editing an image.

        Args:
            image_path: Path to the image file
        """
        try:
            # Create new editor tab with current aspect ratio setting
            editor_tab = ImageEditorTab(
                image_path,
                self.gemini_client,
                self,
                aspect_ratio=self.default_aspect_ratio
            )

            # Add tab with filename as title
            tab_index = self.tab_widget.addTab(editor_tab, image_path.name)
            self.tab_widget.setCurrentIndex(tab_index)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Opening Image",
                f"Failed to open image: {str(e)}"
            )

    def close_tab(self, index: int):
        """
        Close a tab.

        Args:
            index: Index of the tab to close
        """
        # TODO: Ask to save if there are unsaved changes
        widget = self.tab_widget.widget(index)
        if widget:
            widget.deleteLater()
        self.tab_widget.removeTab(index)

    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Nano Banana Desktop",
            "<h3>Nano Banana Desktop</h3>"
            "<p>AI-powered image editor using Google's Gemini Flash 2.5 Images</p>"
            "<p>Version 0.1.0</p>"
            "<p>Author: Daniel Rosehill</p>"
        )

    def on_aspect_ratio_changed(self, index):
        """Handle aspect ratio selection change."""
        if hasattr(self, 'aspect_ratio_combo'):
            self.default_aspect_ratio = self.aspect_ratio_combo.itemData(index)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            # Check if any of the URLs are image files
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = Path(url.toLocalFile())
                    if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp']:
                        event.acceptProposedAction()
                        return

    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = Path(url.toLocalFile())
                if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp']:
                    self.create_image_tab(file_path)
        event.acceptProposedAction()
