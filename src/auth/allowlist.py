"""User allowlist management with JSON file storage."""

import json
import os
import logging
import shutil
from datetime import datetime, timezone
from typing import Dict, Optional
import aiofiles

logger = logging.getLogger(__name__)

USERS_FILE = "data/users.json"


async def load_users() -> Dict:
    """
    Load users from JSON file. Create empty structure if file doesn't exist.

    Returns:
        dict: Users dictionary with structure {"users": {user_id: {user_data}}}

    Error Handling:
        - FileNotFoundError: Returns empty users dict
        - JSONDecodeError: Backs up corrupted file, returns empty dict
    """
    try:
        async with aiofiles.open(USERS_FILE, 'r', encoding='utf-8') as f:
            content = await f.read()
            users = json.loads(content)
            logger.debug(f"Loaded {len(users.get('users', {}))} users from allowlist")
            return users
    except FileNotFoundError:
        logger.info(f"{USERS_FILE} not found, creating new allowlist")
        return {"users": {}}
    except json.JSONDecodeError as e:
        logger.error(f"Corrupted JSON in {USERS_FILE}: {e}")
        # Backup the corrupted file
        backup_path = f"{USERS_FILE}.corrupted.{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copy2(USERS_FILE, backup_path)
            logger.info(f"Backed up corrupted file to {backup_path}")
        except Exception as backup_error:
            logger.error(f"Failed to backup corrupted file: {backup_error}")
        return {"users": {}}
    except Exception as e:
        logger.error(f"Unexpected error loading users: {e}")
        raise


async def save_users(users: Dict) -> None:
    """
    Save users to JSON file with atomic write to prevent corruption.

    Args:
        users: Users dictionary to save

    Error Handling:
        - Uses temporary file and atomic rename to prevent corruption
        - Logs errors for permission and OS errors
        - Raises exceptions for critical failures

    Raises:
        PermissionError: If unable to write to file
        OSError: For other OS-level errors
    """
    try:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

        # Write to temporary file first
        temp_file = f"{USERS_FILE}.tmp"
        async with aiofiles.open(temp_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(users, indent=2, ensure_ascii=False))
            await f.flush()

        # Atomic rename (replaces existing file)
        os.replace(temp_file, USERS_FILE)
        logger.debug(f"Saved {len(users.get('users', {}))} users to allowlist")

    except PermissionError as e:
        logger.error(f"Permission denied writing to {USERS_FILE}: {e}")
        raise
    except OSError as e:
        logger.error(f"OS error writing to {USERS_FILE}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving users: {e}")
        raise


async def is_user_authorized(user_id: int) -> bool:
    """
    Check if a user is in the allowlist.

    Args:
        user_id: Telegram user ID to check

    Returns:
        bool: True if user is authorized, False otherwise
    """
    try:
        users = await load_users()
        authorized = str(user_id) in users.get("users", {})
        logger.debug(f"Authorization check for user {user_id}: {authorized}")
        return authorized
    except Exception as e:
        logger.error(f"Error checking authorization for user {user_id}: {e}")
        return False


async def add_user_to_allowlist(
    user_id: int,
    username: Optional[str],
    first_name: str,
    last_name: Optional[str]
) -> None:
    """
    Add a new user to the allowlist with metadata.

    Args:
        user_id: Telegram user ID
        username: Telegram username (can be None)
        first_name: User's first name
        last_name: User's last name (can be None)

    Raises:
        Exception: If unable to save user data
    """
    try:
        users = await load_users()

        # Create user entry
        now = datetime.now(timezone.utc).isoformat()
        user_data = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "added_at": now,
            "last_active": now
        }

        # Add to users dict (use string key for JSON compatibility)
        users["users"][str(user_id)] = user_data

        # Save to file
        await save_users(users)

        logger.info(
            f"Added user to allowlist: {user_id} "
            f"({username or 'no_username'}, {first_name})"
        )

    except Exception as e:
        logger.error(f"Failed to add user {user_id} to allowlist: {e}")
        raise


async def update_last_active(user_id: int) -> None:
    """
    Update the last_active timestamp for a user.

    Args:
        user_id: Telegram user ID

    Note:
        Silently fails if user not found (logs warning)
    """
    try:
        users = await load_users()

        user_key = str(user_id)
        if user_key not in users.get("users", {}):
            logger.warning(f"Attempted to update last_active for unknown user: {user_id}")
            return

        # Update timestamp
        users["users"][user_key]["last_active"] = datetime.now(timezone.utc).isoformat()

        # Save to file
        await save_users(users)

        logger.debug(f"Updated last_active for user {user_id}")

    except Exception as e:
        logger.error(f"Failed to update last_active for user {user_id}: {e}")
        # Don't raise - this is not critical
