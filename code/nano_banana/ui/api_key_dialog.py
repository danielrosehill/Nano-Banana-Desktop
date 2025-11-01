"""Dialog for configuring the Gemini API key."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt

from ..core.gemini_client import GeminiClient


class ApiKeyDialog(QDialog):
    """Dialog for entering and saving the Gemini API key."""

    def __init__(self, parent=None, gemini_client: GeminiClient = None):
        super().__init__(parent)
        self.gemini_client = gemini_client
        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Configure Gemini API Key")
        self.setModal(True)
        self.resize(500, 150)

        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "Enter your Google Gemini API key.\n"
            "Get your key at: https://aistudio.google.com/app/apikey"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # API Key input
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your Gemini API key")
        self.api_key_input.setEchoMode(QLineEdit.Password)

        # Load existing key if available
        if self.gemini_client and self.gemini_client.api_key:
            self.api_key_input.setText(self.gemini_client.api_key)

        layout.addWidget(self.api_key_input)

        # Show/Hide button
        show_key_button = QPushButton("Show Key")
        show_key_button.setCheckable(True)
        show_key_button.toggled.connect(self.toggle_key_visibility)
        layout.addWidget(show_key_button)

        # Buttons
        button_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_key)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def toggle_key_visibility(self, checked: bool):
        """Toggle visibility of the API key."""
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)

    def save_key(self):
        """Save the API key."""
        api_key = self.api_key_input.text().strip()

        if not api_key:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter an API key."
            )
            return

        try:
            if self.gemini_client:
                self.gemini_client.save_api_key(api_key)

            QMessageBox.information(
                self,
                "Success",
                "API key saved successfully!"
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save API key: {str(e)}"
            )
