"""Image editor tab widget."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QTextEdit, QSplitter, QGroupBox, QMessageBox,
    QProgressDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QImage
from pathlib import Path
from PIL import Image

from .prompt_selector import PromptSelector
from ..core.gemini_client import GeminiClient
from ..utils.file_manager import FileManager


class ImageEditWorker(QThread):
    """Worker thread for image editing to prevent UI freezing."""

    finished = Signal(object, str)  # (PIL Image, text_response)
    error = Signal(str)

    def __init__(self, gemini_client, image_path, prompt, aspect_ratio="preserve"):
        super().__init__()
        self.gemini_client = gemini_client
        self.image_path = image_path
        self.prompt = prompt
        self.aspect_ratio = aspect_ratio

    def run(self):
        """Run the image editing task."""
        try:
            # Convert aspect ratio to API parameter if needed
            api_aspect_ratio = None if self.aspect_ratio == "preserve" else self.aspect_ratio

            result_image, text_response = self.gemini_client.edit_image(
                self.image_path,
                self.prompt,
                aspect_ratio=api_aspect_ratio
            )
            self.finished.emit(result_image, text_response or "")
        except Exception as e:
            self.error.emit(str(e))


class ImageEditorTab(QWidget):
    """Tab widget for editing a single image."""

    def __init__(self, image_path: Path, gemini_client: GeminiClient, parent=None, aspect_ratio: str = "preserve"):
        super().__init__(parent)
        self.original_image_path = image_path
        self.gemini_client = gemini_client
        self.file_manager = FileManager(image_path)
        self.current_version = 0  # 0 = original
        self.worker = None
        self.aspect_ratio = aspect_ratio

        self.setup_ui()
        self.load_original_image()

    def setup_ui(self):
        """Set up the tab UI."""
        main_layout = QHBoxLayout()

        # Left side: Image viewer and versions
        left_splitter = QSplitter(Qt.Vertical)

        # Main image viewer
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setScaledContents(False)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        left_splitter.addWidget(scroll_area)

        # Version thumbnails
        version_group = QGroupBox("Versions")
        version_layout = QHBoxLayout()

        # TODO: Add thumbnail grid
        self.version_label = QLabel("Version: Original")
        version_layout.addWidget(self.version_label)

        version_group.setLayout(version_layout)
        left_splitter.addWidget(version_group)

        left_splitter.setStretchFactor(0, 3)
        left_splitter.setStretchFactor(1, 1)

        # Right side: Prompt selection and controls
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # Prompt selector
        self.prompt_selector = PromptSelector(self)
        right_layout.addWidget(self.prompt_selector)

        # Custom prompt input
        custom_group = QGroupBox("Custom Prompt")
        custom_layout = QVBoxLayout()

        self.custom_prompt_input = QTextEdit()
        self.custom_prompt_input.setPlaceholderText(
            "Enter custom editing instructions here..."
        )
        self.custom_prompt_input.setMaximumHeight(100)
        custom_layout.addWidget(self.custom_prompt_input)

        custom_group.setLayout(custom_layout)
        right_layout.addWidget(custom_group)

        # Action buttons
        button_layout = QVBoxLayout()

        self.apply_button = QPushButton("Apply Edits")
        self.apply_button.clicked.connect(self.apply_edits)
        button_layout.addWidget(self.apply_button)

        self.discard_button = QPushButton("Discard Last Version")
        self.discard_button.clicked.connect(self.discard_version)
        self.discard_button.setEnabled(False)
        button_layout.addWidget(self.discard_button)

        right_layout.addLayout(button_layout)
        right_layout.addStretch()

        right_widget.setLayout(right_layout)

        # Add to main layout
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(right_widget)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 1)

        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

    def load_original_image(self):
        """Load and display the original image."""
        try:
            pixmap = QPixmap(str(self.original_image_path))
            self.display_image(pixmap)
            self.version_label.setText("Version: Original")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load image: {str(e)}"
            )

    def display_image(self, pixmap: QPixmap):
        """Display an image in the viewer."""
        # Scale to fit while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def apply_edits(self):
        """Apply the selected edits to the current image."""
        if not self.gemini_client.has_api_key():
            QMessageBox.warning(
                self,
                "API Key Required",
                "Please configure your Gemini API key in Settings."
            )
            return

        # Get the combined prompt
        prompt = self.prompt_selector.get_combined_prompt(
            self.custom_prompt_input.toPlainText()
        )

        if not prompt:
            QMessageBox.warning(
                self,
                "No Prompt",
                "Please select at least one prompt template or enter custom text."
            )
            return

        # Get current image path
        current_image_path = self.file_manager.get_current_version_path(self.current_version)

        # Show progress dialog
        progress = QProgressDialog(
            "Generating edited image...",
            None,
            0,
            0,
            self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Processing")
        progress.show()

        # Disable apply button during processing
        self.apply_button.setEnabled(False)

        # Create and start worker thread
        self.worker = ImageEditWorker(
            self.gemini_client,
            current_image_path,
            prompt,
            aspect_ratio=self.aspect_ratio
        )
        self.worker.finished.connect(
            lambda img, txt: self.on_edit_complete(img, txt, progress)
        )
        self.worker.error.connect(
            lambda err: self.on_edit_error(err, progress)
        )
        self.worker.start()

    def on_edit_complete(self, result_image: Image.Image, text_response: str, progress):
        """Handle successful image edit."""
        progress.close()
        self.apply_button.setEnabled(True)

        try:
            # Save the new version
            self.current_version += 1
            version_path = self.file_manager.save_version(result_image, self.current_version)

            # Display the new version
            pixmap = self.pil_to_qpixmap(result_image)
            self.display_image(pixmap)

            # Update version label
            self.version_label.setText(f"Version: {self.current_version}")

            # Enable discard button
            self.discard_button.setEnabled(True)

            # TODO: Update thumbnail display

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save edited image: {str(e)}"
            )

    def on_edit_error(self, error_message: str, progress):
        """Handle image edit error."""
        progress.close()
        self.apply_button.setEnabled(True)

        QMessageBox.critical(
            self,
            "Edit Failed",
            f"Failed to edit image:\n{error_message}"
        )

    def discard_version(self):
        """Discard the current version and load the previous one."""
        if self.current_version == 0:
            return

        try:
            # Delete current version
            self.file_manager.delete_version(self.current_version)

            # Go back to previous version
            self.current_version -= 1

            # Load previous version
            if self.current_version == 0:
                self.load_original_image()
                self.discard_button.setEnabled(False)
            else:
                version_path = self.file_manager.get_current_version_path(self.current_version)
                pixmap = QPixmap(str(version_path))
                self.display_image(pixmap)
                self.version_label.setText(f"Version: {self.current_version}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to discard version: {str(e)}"
            )

    @staticmethod
    def pil_to_qpixmap(pil_image: Image.Image) -> QPixmap:
        """Convert PIL Image to QPixmap."""
        # Convert PIL image to bytes
        pil_image = pil_image.convert("RGBA")
        data = pil_image.tobytes("raw", "RGBA")

        # Create QImage
        qimage = QImage(
            data,
            pil_image.width,
            pil_image.height,
            QImage.Format_RGBA8888
        )

        # Convert to QPixmap
        return QPixmap.fromImage(qimage)
