"""Reusable logging configuration for independent applications."""

import logging
import os
import sys

LOGGER_NAME = "quick_qm"
DEFAULT_FORMAT = "%(levelname)s %(name)s: %(message)s"
_HANDLER_MARKER = "_molecular_utilities_handler"


def _validate_namespace(namespace):
    if not isinstance(namespace, str) or not namespace or namespace.strip() != namespace:
        raise ValueError("namespace must be a nonempty logger name without surrounding whitespace")
    if any(not part for part in namespace.split(".")):
        raise ValueError("namespace must not contain empty name components")


def get_logger(name, *, namespace=LOGGER_NAME):
    """Return a child logger in the specified application namespace."""
    _validate_namespace(namespace)
    if not isinstance(name, str) or not name or name.strip() != name:
        raise ValueError("name must be a nonempty logger name without surrounding whitespace")
    if any(not part for part in name.split(".")):
        raise ValueError("name must not contain empty name components")
    return logging.getLogger(f"{namespace}.{name}")


def configure_logging(level=logging.INFO, stream=None, *, namespace=LOGGER_NAME,
                      format=DEFAULT_FORMAT, datefmt=None, file=None, propagate=False):
    """Configure one managed console handler and optional file handler.

    Reconfiguration replaces only handlers managed by this utility, leaving
    application-provided handlers untouched. Files are appended, not truncated.
    """
    _validate_namespace(namespace)
    if not isinstance(format, str):
        raise ValueError("format must be a string")
    if datefmt is not None and not isinstance(datefmt, str):
        raise ValueError("datefmt must be a string or None")
    if type(propagate) is not bool:
        raise ValueError("propagate must be a boolean")
    if file is not None and (not isinstance(file, (str, os.PathLike)) or not os.fspath(file)):
        raise ValueError("file must be a nonempty path or None")
    resolved_level = logging._checkLevel(level)
    formatter = logging.Formatter(format, datefmt=datefmt)
    handlers = []
    try:
        console = logging.StreamHandler(stream if stream is not None else sys.stderr)
        handlers.append(console)
        if file is not None:
            handlers.append(logging.FileHandler(file, mode="a", encoding="utf-8"))
        for handler in handlers:
            handler.setFormatter(formatter)
            setattr(handler, _HANDLER_MARKER, True)
    except (OSError, ValueError, TypeError):
        for handler in handlers:
            handler.close()
        raise

    logger = logging.getLogger(namespace)
    previous = [handler for handler in logger.handlers
                if getattr(handler, _HANDLER_MARKER, False)
                or (namespace == LOGGER_NAME and getattr(handler, "_quick_qm_handler", False))]
    for handler in previous:
        logger.removeHandler(handler)
    for handler in handlers:
        logger.addHandler(handler)
    logger.setLevel(resolved_level)
    logger.propagate = propagate
    for handler in previous:
        handler.close()
