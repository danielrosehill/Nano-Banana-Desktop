"""Utilities for loading and managing prompt templates."""

from pathlib import Path
from typing import Dict, List, Optional
import re


class PromptTemplate:
    """Represents a single prompt template."""

    def __init__(self, name: str, category: str, content: str, file_path: Path):
        self.name = name
        self.category = category
        self.content = content.strip()
        self.file_path = file_path

    def get_display_name(self) -> str:
        """Get a human-readable display name from the file name."""
        # Convert 'comic-book.md' to 'Comic Book'
        name = self.file_path.stem.replace('-', ' ').replace('_', ' ')
        return name.title()

    def __repr__(self) -> str:
        return f"PromptTemplate(name='{self.name}', category='{self.category}')"


class PromptManager:
    """Manages loading and organizing prompt templates."""

    def __init__(self, prompts_dir: Optional[Path] = None):
        if prompts_dir is None:
            # Default to prompts directory relative to this file
            prompts_dir = Path(__file__).parent.parent.parent / "prompts"

        self.prompts_dir = Path(prompts_dir)
        self.templates: Dict[str, List[PromptTemplate]] = {}
        self._load_templates()

    def _load_templates(self):
        """Load all prompt templates from the prompts directory."""
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Prompts directory not found: {self.prompts_dir}")

        # Iterate through category directories
        for category_dir in self.prompts_dir.iterdir():
            if not category_dir.is_dir():
                continue

            category_name = category_dir.name
            self.templates[category_name] = []

            # Load all .md files in the category
            for prompt_file in category_dir.glob("*.md"):
                content = prompt_file.read_text(encoding='utf-8')

                # Skip the markdown header if present
                lines = content.split('\n')
                if lines and lines[0].startswith('#'):
                    # Remove the title line
                    content = '\n'.join(lines[1:]).strip()

                template = PromptTemplate(
                    name=prompt_file.stem,
                    category=category_name,
                    content=content,
                    file_path=prompt_file
                )

                self.templates[category_name].append(template)

    def get_categories(self) -> List[str]:
        """Get list of all prompt categories."""
        return sorted(self.templates.keys())

    def get_templates_by_category(self, category: str) -> List[PromptTemplate]:
        """Get all templates for a specific category."""
        return self.templates.get(category, [])

    def get_all_templates(self) -> List[PromptTemplate]:
        """Get all templates across all categories."""
        all_templates = []
        for templates in self.templates.values():
            all_templates.extend(templates)
        return all_templates

    def get_template_by_name(self, name: str) -> Optional[PromptTemplate]:
        """Find a template by its name (searches all categories)."""
        for templates in self.templates.values():
            for template in templates:
                if template.name == name:
                    return template
        return None

    def combine_prompts(self, templates: List[PromptTemplate]) -> str:
        """
        Combine multiple prompt templates into a single formatted prompt.

        Uses uppercase section headers to separate instructions as per the spec.
        """
        if not templates:
            return ""

        if len(templates) == 1:
            return templates[0].content

        combined = "Please apply the following edits to this image:\n\n"

        for template in templates:
            section_header = template.get_display_name().upper()
            combined += f"{section_header}\n\n{template.content}\n\n"

        return combined.strip()

    def create_custom_prompt(self, custom_text: str, templates: Optional[List[PromptTemplate]] = None) -> str:
        """
        Create a prompt with custom text, optionally combined with templates.

        Custom text comes before templated prompts as per the spec.
        """
        if not templates:
            return custom_text

        combined = f"{custom_text}\n\n"
        combined += "Additionally, please apply these edits:\n\n"

        for template in templates:
            section_header = template.get_display_name().upper()
            combined += f"{section_header}\n\n{template.content}\n\n"

        return combined.strip()


if __name__ == "__main__":
    # Demo/test code
    manager = PromptManager()

    print("Available categories:")
    for category in manager.get_categories():
        templates = manager.get_templates_by_category(category)
        print(f"  {category}: {len(templates)} templates")

    print("\nSample combined prompt:")
    templates = manager.get_templates_by_category("color-adjustments")[:2]
    if templates:
        combined = manager.combine_prompts(templates)
        print(combined)
