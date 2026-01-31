"""
ComfyUI-DJZ-ZeroPrompt
Procedural Semantic Prompt Generation using Position-is-Seed Methodology

Zero files. Zero storage. Infinite prompts.
"""

from .DJZ_ZeroPrompt_V1 import (
    NODE_CLASS_MAPPINGS as V1_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as V1_DISPLAY_MAPPINGS
)
from .DJZ_ZeroPrompt_V2 import (
    NODE_CLASS_MAPPINGS as V2_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as V2_DISPLAY_MAPPINGS
)

# Merge all node mappings
NODE_CLASS_MAPPINGS = {**V1_MAPPINGS, **V2_MAPPINGS}
NODE_DISPLAY_NAME_MAPPINGS = {**V1_DISPLAY_MAPPINGS, **V2_DISPLAY_MAPPINGS}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

__version__ = "1.1.0"
__author__ = "Drift Johnson"
