"""
Config flow for ksenia.

This module provides backwards compatibility for hassfest.
The actual implementation is in the config_flow_handler package.
"""

from .config_flow_handler import KseniaLaresConfigFlowHandler

__all__ = ["KseniaLaresConfigFlowHandler"]
