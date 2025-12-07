"""Authentication module for user verification and allowlist management."""

from .allowlist import (
    is_user_authorized,
    add_user_to_allowlist,
    update_last_active,
    load_users,
    save_users
)
from .password_manager import verify_password

__all__ = [
    'is_user_authorized',
    'add_user_to_allowlist',
    'update_last_active',
    'verify_password',
    'load_users',
    'save_users'
]
