"""
Module Import Integrity Test Suite
Verifies every module in backend/ can be imported cleanly without NameError, ImportError, or SyntaxError.
"""

import os
import importlib
import pytest


def test_import_all_backend_modules():
    """
    Recursively discovers and imports every python module under backend directory.
    Fails build if any module raises NameError, ImportError, or SyntaxError.
    """
    backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
    backend_dir = os.path.abspath(backend_dir)

    imported_modules = []
    for root, _, files in os.walk(backend_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                rel_path = os.path.relpath(os.path.join(root, file), backend_dir)
                mod_name = "backend." + rel_path.replace(os.sep, ".").replace(".py", "")
                mod = importlib.import_module(mod_name)
                imported_modules.append(mod_name)
                assert mod is not None

    assert len(imported_modules) >= 10
    assert "backend.main" in imported_modules
    assert "backend.services.retrieval" in imported_modules
    assert "backend.api.routes" in imported_modules
    assert "backend.services.auth" in imported_modules
