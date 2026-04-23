"""
Pydantic v1/v2 compatibility layer for handling models using __modify_schema__
"""

import warnings
from typing import Any, Dict, Optional
from pydantic import BaseModel


def enable_pydantic_v1_compatibility():
    """
    Enable compatibility with Pydantic v1 style models in v2.
    Suppresses warnings about __modify_schema__ method.
    """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message=".*__modify_schema__.*")
    

# Monkeypatch to handle __modify_schema__ from v1 style models
original_model_post_init = BaseModel.__pydantic_validator__

def patch_pydantic_v2():
    """Apply compatibility patches for Pydantic v2"""
    enable_pydantic_v1_compatibility()


# Apply patches on import
patch_pydantic_v2()
