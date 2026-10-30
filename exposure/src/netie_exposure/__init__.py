"""Netie Exposure - Cortex-crew marketing pack. No fake followers."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("netie-exposure")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = ["__version__"]
