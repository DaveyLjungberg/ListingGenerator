"""
File Manager for Temporary File Handling

Manages temporary files with unique session IDs to prevent conflicts
and enable proper cleanup.
"""

import os
import uuid
import shutil
from pathlib import Path


class FileManager:
    """Manages temporary files for a session with unique IDs"""

    def __init__(self, session_id=None):
        """
        Initialize FileManager with a session ID

        Args:
            session_id: Optional session ID. If not provided, generates a new UUID
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.base_dir = Path("temp") / self.session_id
        self._ensure_directory()

    def _ensure_directory(self):
        """Create the temp directory if it doesn't exist"""
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create temp directory: {e}")

    def get_path(self, filename):
        """
        Get the full path for a filename in this session's temp directory

        Args:
            filename: Name of the file (e.g., 'voiceover.mp3')

        Returns:
            str: Full path to the file
        """
        return str(self.base_dir / filename)

    def cleanup(self):
        """
        Remove the temp directory and all its contents

        Handles errors gracefully if directory doesn't exist or can't be removed
        """
        try:
            if self.base_dir.exists():
                shutil.rmtree(self.base_dir)
                print(f"Cleaned up temp directory: {self.base_dir}")
            else:
                print(f"Temp directory does not exist: {self.base_dir}")
        except Exception as e:
            print(f"Warning: Could not cleanup temp directory {self.base_dir}: {e}")

    def list_files(self):
        """
        List all files in the session's temp directory

        Returns:
            list: List of file paths
        """
        try:
            if self.base_dir.exists():
                return [str(f) for f in self.base_dir.iterdir() if f.is_file()]
            return []
        except Exception as e:
            print(f"Warning: Could not list files in {self.base_dir}: {e}")
            return []

    def file_exists(self, filename):
        """
        Check if a file exists in the session's temp directory

        Args:
            filename: Name of the file to check

        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            return (self.base_dir / filename).exists()
        except Exception:
            return False

    def __repr__(self):
        return f"FileManager(session_id='{self.session_id}', base_dir='{self.base_dir}')"
