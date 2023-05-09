import functools
import os
from typing import Any, Callable

import click


def option_log_level(f: Callable) -> Callable:
    @click.option(
        "-l",
        "--log-level",
        type=click.Choice(["info", "debug"]),
        default="info",
        show_default=True,
        required=True,
        help="log level",
    )
    @functools.wraps(f)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        return f(*args, **kwargs)

    return wrapped


def option_mongodb_url(f: Callable) -> Callable:
    @click.option(
        "--mongodb-url",
        type=str,
        default=os.environ.get("OCAZ_MONGODB_URL", None),
        show_default=True,
        required=True,
    )
    @functools.wraps(f)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        return f(*args, **kwargs)

    return wrapped
