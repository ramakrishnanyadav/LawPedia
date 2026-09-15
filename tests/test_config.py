"""
Test Suite for Backend Configuration & Startup Settings
"""

import os
import pytest
from backend.config import _get_secret_key, Settings


def test_config_debug_defaults_consistency(monkeypatch):
    """
    Asserts that when LAWPEDIA_SECRET_KEY is missing and DEBUG is unset,
    the app is unambiguously in dev mode (Settings.DEBUG is True and dev secret is used).
    """
    monkeypatch.delenv("LAWPEDIA_SECRET_KEY", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)

    s = Settings()
    assert s.DEBUG is True
    assert s.SECRET_KEY == "lawpedia_dev_secret_key_change_in_production"


def test_config_production_without_secret_key_raises(monkeypatch):
    """
    Asserts that in production mode (DEBUG=False) without LAWPEDIA_SECRET_KEY,
    startup raises a RuntimeError.
    """
    monkeypatch.delenv("LAWPEDIA_SECRET_KEY", raising=False)
    monkeypatch.setenv("DEBUG", "False")

    with pytest.raises(RuntimeError, match="CRITICAL SECURITY CONFIGURATION ERROR"):
        _get_secret_key()
