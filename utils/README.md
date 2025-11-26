# Utils Package

This directory contains utility modules for Listing Magic.

## FileManager

The `FileManager` class handles temporary file creation with unique session IDs to prevent file conflicts and enable proper cleanup.

### Features

- **Unique Session IDs**: Each FileManager instance uses a UUID to create isolated temporary directories
- **Automatic Directory Creation**: Creates `temp/[session_id]/` directories automatically
- **Path Management**: Provides `get_path(filename)` method for consistent file path handling
- **Safe Cleanup**: `cleanup()` method removes temporary directories gracefully
- **Error Handling**: All operations handle errors gracefully with informative messages

### Usage

```python
from utils.file_manager import FileManager

# Initialize (automatically creates temp directory)
fm = FileManager()

# Get path for a file
video_path = fm.get_path("property_tour.mp4")
audio_path = fm.get_path("voiceover.mp3")

# Use the paths for file operations
tts.save(audio_path)
video.write_videofile(video_path)

# Clean up when done
fm.cleanup()
```

### Session State Integration

In `main.py`, the FileManager is stored in Streamlit's session state:

```python
if 'file_manager' not in st.session_state:
    st.session_state.file_manager = FileManager()

# Use throughout the session
video_path = generate_video_with_voiceover(
    images,
    script,
    st.session_state.file_manager
)
```

### File Structure

```
Real Estate/
├── temp/
│   ├── [session-id-1]/
│   │   ├── voiceover.mp3
│   │   └── property_tour_with_voice.mp4
│   └── [session-id-2]/
│       ├── voiceover.mp3
│       └── property_tour_with_voice.mp4
└── utils/
    ├── __init__.py
    ├── file_manager.py
    └── README.md
```

### Benefits

1. **No File Conflicts**: Multiple concurrent sessions don't overwrite each other's files
2. **Clean Workspace**: Temporary files are isolated and easy to clean up
3. **Session Isolation**: Each user/session has its own temporary directory
4. **Easy Debugging**: Session IDs make it easy to trace files to specific sessions

### Methods

- `__init__(session_id=None)`: Initialize with optional session ID (generates UUID if not provided)
- `get_path(filename)`: Get full path for a filename in the session's temp directory
- `cleanup()`: Remove the temp directory and all contents
- `list_files()`: List all files in the session's temp directory
- `file_exists(filename)`: Check if a file exists in the temp directory
