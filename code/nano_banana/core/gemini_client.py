"""Gemini API client for image-to-image transformations."""

from typing import Optional, Tuple
from pathlib import Path
from io import BytesIO
from PIL import Image
import google.genai as genai
import keyring


class GeminiClient:
    """Client for interacting with Gemini's image generation API."""

    MODEL_NAME = "gemini-2.5-flash-image-preview"
    KEYRING_SERVICE = "nano-banana-desktop"
    KEYRING_USERNAME = "gemini-api-key"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client.

        Args:
            api_key: Optional API key. If not provided, will try to load from keyring.
        """
        self.api_key = api_key or self._load_api_key()
        self.client = None

        if self.api_key:
            self._initialize_client()

    def _load_api_key(self) -> Optional[str]:
        """Load API key from system keyring."""
        try:
            return keyring.get_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME)
        except Exception as e:
            print(f"Failed to load API key from keyring: {e}")
            return None

    def _initialize_client(self):
        """Initialize the Gemini API client."""
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini client: {e}")

    def save_api_key(self, api_key: str):
        """
        Save API key to system keyring.

        Args:
            api_key: The Gemini API key to save
        """
        try:
            keyring.set_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME, api_key)
            self.api_key = api_key
            self._initialize_client()
        except Exception as e:
            raise ValueError(f"Failed to save API key: {e}")

    def has_api_key(self) -> bool:
        """Check if an API key is configured."""
        return self.api_key is not None and self.client is not None

    def edit_image(
        self,
        image_path: Path,
        prompt: str,
        aspect_ratio: Optional[str] = None
    ) -> Tuple[Image.Image, Optional[str]]:
        """
        Edit an image using Gemini's image-to-image capabilities.

        Args:
            image_path: Path to the input image
            prompt: Text prompt describing the desired edits
            aspect_ratio: Optional aspect ratio (e.g., "1:1", "16:9", "9:16", "21:9")
                         If None, uses "sync" (subject resolution)

        Returns:
            Tuple of (edited PIL Image, optional text response from model)

        Raises:
            ValueError: If no API key is configured
            FileNotFoundError: If image file doesn't exist
            Exception: If API call fails
        """
        if not self.has_api_key():
            raise ValueError("No API key configured. Please set your Gemini API key first.")

        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Load the input image
        input_image = Image.open(image_path)

        # Prepare the request
        contents = [prompt, input_image]

        # TODO: Add aspect ratio support once we understand the API parameter
        # The API docs don't show aspect ratio in the Python SDK examples
        # May need to add this as a parameter or in generation_config

        try:
            # Make the API request
            response = self.client.models.generate_content(
                model=self.MODEL_NAME,
                contents=contents,
            )

            # Extract the generated image and any text response
            generated_image = None
            text_response = None

            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    text_response = part.text
                elif part.inline_data is not None:
                    # Convert the inline data to a PIL Image
                    generated_image = Image.open(BytesIO(part.inline_data.data))

            if generated_image is None:
                raise Exception("No image generated in response")

            return generated_image, text_response

        except Exception as e:
            raise Exception(f"Failed to edit image: {e}")

    def generate_image(self, prompt: str) -> Tuple[Image.Image, Optional[str]]:
        """
        Generate an image from text (text-to-image).

        Args:
            prompt: Text description of the image to generate

        Returns:
            Tuple of (generated PIL Image, optional text response)
        """
        if not self.has_api_key():
            raise ValueError("No API key configured. Please set your Gemini API key first.")

        try:
            response = self.client.models.generate_content(
                model=self.MODEL_NAME,
                contents=[prompt],
            )

            generated_image = None
            text_response = None

            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    text_response = part.text
                elif part.inline_data is not None:
                    generated_image = Image.open(BytesIO(part.inline_data.data))

            if generated_image is None:
                raise Exception("No image generated in response")

            return generated_image, text_response

        except Exception as e:
            raise Exception(f"Failed to generate image: {e}")
