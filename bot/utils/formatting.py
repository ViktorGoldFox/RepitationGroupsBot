from html import escape


def format_user_display(username: str | None, full_name: str | None) -> str:
    if username:
        return f"@{username}"

    return full_name or "Unknown user"


def format_user_storage(username: str | None, full_name: str | None) -> str:
    if username:
        return f"@{username}"

    return full_name or "Unknown user"


def format_user_mention_html(
    user_id: int, username: str | None, full_name: str | None
) -> str:
    if username:
        return escape(f"@{username}")

    safe_full_name = escape(full_name or "Unknown user")
    return f'<a href="tg://user?id={user_id}">{safe_full_name}</a>'
