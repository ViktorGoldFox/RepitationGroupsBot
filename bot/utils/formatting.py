def format_user_display(username: str | None, full_name: str | None) -> str:
    if username:
        return f"@{username}"

    return full_name or "Unknown user"
