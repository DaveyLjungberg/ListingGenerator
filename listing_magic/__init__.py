"""
Listing Magic - AI-Powered Real Estate Marketing Platform

A modular package for generating professional real estate listings,
video scripts, features sheets, and RESO-compliant data.
"""

__version__ = "1.0.0"

# Package-level imports for convenience (optional)
# Users can import directly from submodules or use these shortcuts

from . import components
from . import services
from . import utils
from . import styles

__all__ = [
    'components',
    'services',
    'utils',
    'styles'
]
