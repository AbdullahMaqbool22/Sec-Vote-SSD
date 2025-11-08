"""
Shared validation utilities
"""
import re


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username):
    """Validate username (alphanumeric, 3-20 characters)"""
    if len(username) < 3 or len(username) > 20:
        return False
    return username.isalnum()


def validate_password(password):
    """Validate password strength (min 8 characters, at least one number)"""
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    return True


def sanitize_input(text, max_length=500):
    """Sanitize text input"""
    if not text:
        return text
    # Remove potential XSS characters
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length]
    return text
