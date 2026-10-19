"""
Tests for settings safety — ensuring the app refuses to start without
SECRET_KEY in production mode (DEBUG=False).
"""
from django.test import SimpleTestCase
from django.core.exceptions import ImproperlyConfigured
from unittest.mock import patch
import importlib


class ProductionSettingsSafetyTest(SimpleTestCase):
    """
    The app must raise ImproperlyConfigured when:
        - DEBUG=False
        - SECRET_KEY is not set (or empty)
    This prevents accidental deployment with a missing secret key.
    """

    def test_missing_secret_key_raises_in_production(self):
        """
        Simulate loading settings with DEBUG=False and no SECRET_KEY.
        Must raise ImproperlyConfigured.
        """
        import os

        env_overrides = {
            'DEBUG': 'False',
            'SECRET_KEY': '',
            'DB_NAME': 'test',
            'DB_USER': 'test',
            'DB_PASSWORD': 'test',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'ALLOWED_HOSTS': 'localhost',
        }

        with patch.dict(os.environ, env_overrides, clear=False):
            with self.assertRaises(ImproperlyConfigured):
                import resume_bank.settings as settings_module
                importlib.reload(settings_module)

    def test_debug_true_allows_default_key(self):
        """
        With DEBUG=True, the settings module should allow a default (insecure)
        key without raising.
        """
        import os

        env_overrides = {
            'DEBUG': 'True',
            'SECRET_KEY': '',
        }

        with patch.dict(os.environ, env_overrides, clear=False):
            try:
                import resume_bank.settings as settings_module
                importlib.reload(settings_module)
            except ImproperlyConfigured:
                self.fail("ImproperlyConfigured raised unexpectedly when DEBUG=True")
