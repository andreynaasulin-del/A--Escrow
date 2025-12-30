"""
Localization module for Big Stepa Safe Escrow Bot.
Provides translation strings and middleware for multi-language support.
"""

from locales.translations import get_text, MESSAGES
from locales.middleware import L10nMiddleware

__all__ = ["get_text", "MESSAGES", "L10nMiddleware"]
