"""Prompt template selector widget."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QListWidget,
    QListWidgetItem, QComboBox, QLabel
)
from PySide6.QtCore import Qt

from ..utils.prompts import PromptManager


class PromptSelector(QWidget):
    """Widget for selecting prompt templates."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.prompt_manager = PromptManager()
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout()

        # Group box
        group_box = QGroupBox("Prompt Templates")
        group_layout = QVBoxLayout()

        # Category selector
        category_label = QLabel("Category:")
        group_layout.addWidget(category_label)

        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        for category in self.prompt_manager.get_categories():
            # Convert category name to title case
            display_name = category.replace('-', ' ').replace('_', ' ').title()
            self.category_combo.addItem(display_name, category)

        self.category_combo.currentIndexChanged.connect(self.on_category_changed)
        group_layout.addWidget(self.category_combo)

        # Template list
        templates_label = QLabel("Select Templates (hold Ctrl for multiple):")
        group_layout.addWidget(templates_label)

        self.template_list = QListWidget()
        self.template_list.setSelectionMode(QListWidget.MultiSelection)
        group_layout.addWidget(self.template_list)

        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

        self.setLayout(layout)

        # Load all templates initially
        self.load_all_templates()

    def on_category_changed(self, index):
        """Handle category selection change."""
        if index == 0:  # "All Categories"
            self.load_all_templates()
        else:
            category = self.category_combo.itemData(index)
            self.load_category_templates(category)

    def load_all_templates(self):
        """Load all templates across all categories."""
        self.template_list.clear()

        for template in self.prompt_manager.get_all_templates():
            display_name = f"{template.category}: {template.get_display_name()}"
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, template)
            self.template_list.addItem(item)

    def load_category_templates(self, category: str):
        """Load templates for a specific category."""
        self.template_list.clear()

        for template in self.prompt_manager.get_templates_by_category(category):
            item = QListWidgetItem(template.get_display_name())
            item.setData(Qt.UserRole, template)
            self.template_list.addItem(item)

    def get_selected_templates(self):
        """Get list of selected templates."""
        selected = []
        for item in self.template_list.selectedItems():
            template = item.data(Qt.UserRole)
            selected.append(template)
        return selected

    def get_combined_prompt(self, custom_text: str = "") -> str:
        """
        Get the combined prompt from selected templates and custom text.

        Args:
            custom_text: Optional custom text to include

        Returns:
            Combined prompt string
        """
        selected_templates = self.get_selected_templates()

        if custom_text and selected_templates:
            # Custom + templates
            return self.prompt_manager.create_custom_prompt(custom_text, selected_templates)
        elif custom_text:
            # Custom only
            return custom_text
        elif selected_templates:
            # Templates only
            return self.prompt_manager.combine_prompts(selected_templates)
        else:
            return ""
