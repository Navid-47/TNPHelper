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

    def test_missing_db_name_raises_in_production(self):
        """Simulate loading settings with DEBUG=False and missing DB_NAME."""
        import os
        env_overrides = {
            'DEBUG': 'False',
            'SECRET_KEY': 'valid-secret-key-for-test-purposes-only',
            'DB_NAME': '',
            'DB_USER': 'tnp_user',
            'DB_PASSWORD': 'secret_password',
            'DB_HOST': 'db.internal',
        }
        with patch.dict(os.environ, env_overrides, clear=False):
            with self.assertRaises(ImproperlyConfigured) as cm:
                import resume_bank.settings as settings_module
                importlib.reload(settings_module)
            self.assertIn('DB_NAME', str(cm.exception))

    def test_missing_db_user_raises_in_production(self):
        """Simulate loading settings with DEBUG=False and missing DB_USER."""
        import os
        env_overrides = {
            'DEBUG': 'False',
            'SECRET_KEY': 'valid-secret-key-for-test-purposes-only',
            'DB_NAME': 'tnp_prod_db',
            'DB_USER': '',
            'DB_PASSWORD': 'secret_password',
            'DB_HOST': 'db.internal',
        }
        with patch.dict(os.environ, env_overrides, clear=False):
            with self.assertRaises(ImproperlyConfigured) as cm:
                import resume_bank.settings as settings_module
                importlib.reload(settings_module)
            self.assertIn('DB_USER', str(cm.exception))

    def test_missing_db_password_raises_in_production(self):
        """Simulate loading settings with DEBUG=False and missing/empty DB_PASSWORD."""
        import os
        env_overrides = {
            'DEBUG': 'False',
            'SECRET_KEY': 'valid-secret-key-for-test-purposes-only',
            'DB_NAME': 'tnp_prod_db',
            'DB_USER': 'tnp_user',
            'DB_PASSWORD': '',
            'DB_HOST': 'db.internal',
        }
        with patch.dict(os.environ, env_overrides, clear=False):
            with self.assertRaises(ImproperlyConfigured) as cm:
                import resume_bank.settings as settings_module
                importlib.reload(settings_module)
            self.assertIn('DB_PASSWORD', str(cm.exception))

    def test_missing_db_host_raises_in_production(self):
        """Simulate loading settings with DEBUG=False and missing DB_HOST."""
        import os
        env_overrides = {
            'DEBUG': 'False',
            'SECRET_KEY': 'valid-secret-key-for-test-purposes-only',
            'DB_NAME': 'tnp_prod_db',
            'DB_USER': 'tnp_user',
            'DB_PASSWORD': 'secret_password',
            'DB_HOST': '',
        }
        with patch.dict(os.environ, env_overrides, clear=False):
            with self.assertRaises(ImproperlyConfigured) as cm:
                import resume_bank.settings as settings_module
                importlib.reload(settings_module)
            self.assertIn('DB_HOST', str(cm.exception))

    def test_valid_production_config_succeeds(self):
        """With all required variables provided, DEBUG=False loads without error."""
        import os
        env_overrides = {
            'DEBUG': 'False',
            'SECRET_KEY': 'valid-secret-key-for-test-purposes-only',
            'DB_NAME': 'tnp_prod_db',
            'DB_USER': 'tnp_user',
            'DB_PASSWORD': 'secret_password',
            'DB_HOST': 'db.internal',
            'ALLOWED_HOSTS': 'tnp.university.edu',
        }
        with patch.dict(os.environ, env_overrides, clear=False):
            try:
                import resume_bank.settings as settings_module
                importlib.reload(settings_module)
            except ImproperlyConfigured:
                self.fail("ImproperlyConfigured raised unexpectedly with valid production settings")

