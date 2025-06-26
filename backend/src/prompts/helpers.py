"""Helper functions for prompt generation."""

from datetime import datetime


def get_current_date():
    """Get current date in a readable format."""
    return datetime.now().strftime("%B %d, %Y")