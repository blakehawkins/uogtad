"""Utilities for declaring lazy module dependencies."""

import importlib.util
import sys
from types import ModuleType


def lazy_import(name: str) -> ModuleType:
    """Register *name* without executing it until an attribute is accessed."""
    spec = importlib.util.find_spec(name)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot find module {name!r}")

    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module
