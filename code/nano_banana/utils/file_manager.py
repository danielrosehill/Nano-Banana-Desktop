"""File management and versioning system."""

from pathlib import Path
import shutil
from PIL import Image


class FileManager:
    """Manages file versioning for edited images."""

    def __init__(self, original_image_path: Path):
        """
        Initialize the file manager.

        Args:
            original_image_path: Path to the original image file
        """
        self.original_path = Path(original_image_path)
        self.version_dir = self._setup_version_directory()
        self.original_in_version_dir = self.version_dir / "original.png"

        # Move original to version directory if not already done
        if not self.original_in_version_dir.exists():
            self._move_original()

    def _setup_version_directory(self) -> Path:
        """
        Set up the version directory for this image.

        Following the spec:
        - If original is foo/a.png
        - Create foo/a/ directory
        - Move original to foo/a/original.png

        Returns:
            Path to the version directory
        """
        # Get the parent directory and filename without extension
        parent_dir = self.original_path.parent
        stem = self.original_path.stem

        # Create version directory
        version_dir = parent_dir / stem
        version_dir.mkdir(exist_ok=True)

        return version_dir

    def _move_original(self):
        """Move the original file into the version directory."""
        # Copy to preserve the original
        shutil.copy2(self.original_path, self.original_in_version_dir)

    def save_version(self, image: Image.Image, version_number: int) -> Path:
        """
        Save a new version of the image.

        Args:
            image: PIL Image to save
            version_number: Version number (1, 2, 3, etc.)

        Returns:
            Path to the saved version file
        """
        version_path = self.version_dir / f"v{version_number}.png"
        image.save(version_path, "PNG")
        return version_path

    def get_current_version_path(self, version_number: int) -> Path:
        """
        Get the path to a specific version.

        Args:
            version_number: 0 for original, 1+ for versions

        Returns:
            Path to the version file
        """
        if version_number == 0:
            return self.original_in_version_dir
        else:
            return self.version_dir / f"v{version_number}.png"

    def delete_version(self, version_number: int):
        """
        Delete a specific version.

        Args:
            version_number: Version number to delete (must be > 0)
        """
        if version_number <= 0:
            raise ValueError("Cannot delete original version")

        version_path = self.get_current_version_path(version_number)
        if version_path.exists():
            version_path.unlink()

    def get_all_versions(self) -> list[Path]:
        """
        Get paths to all versions in order.

        Returns:
            List of paths: [original, v1, v2, ...]
        """
        versions = [self.original_in_version_dir]

        # Find all version files
        version_files = sorted(self.version_dir.glob("v*.png"))
        versions.extend(version_files)

        return versions

    def get_version_count(self) -> int:
        """
        Get the number of versions (not including original).

        Returns:
            Number of edited versions
        """
        return len(list(self.version_dir.glob("v*.png")))
