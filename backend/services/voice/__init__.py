"""
__init__ cho services.voice
"""

from .tts import synthesize, extract_voiceover_from_script

__all__ = ["synthesize", "extract_voiceover_from_script"]
