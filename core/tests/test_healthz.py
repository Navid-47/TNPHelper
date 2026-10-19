"""
Tests for the /healthz/ health-check endpoint.

Covers:
    - Shallow check returns HTTP 200 with {"status": "ok"}
    - Deep check (?deep=1) returns 200 when DB is reachable
    - Deep check returns 503 when DB is unavailable (simulated)
    - HEAD request is accepted (same as GET for status)
    - POST request is rejected (405)
    - Endpoint requires NO authentication
"""
import json
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse


class HealthzShallowTest(TestCase):
    """Tests for the shallow (default) health-check."""

    def setUp(self):
        self.client = Client()

    def test_shallow_returns_200(self):
        response = self.client.get('/healthz/')
        self.assertEqual(response.status_code, 200)

    def test_shallow_returns_json_ok(self):
        response = self.client.get('/healthz/')
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content)
        self.assertEqual(data, {'status': 'ok'})

    def test_head_returns_200(self):
        response = self.client.head('/healthz/')
        self.assertEqual(response.status_code, 200)

    def test_post_returns_405(self):
        response = self.client.post('/healthz/')
        self.assertEqual(response.status_code, 405)

    def test_no_authentication_required(self):
        """Endpoint must be reachable by anonymous users."""
        # Client has no session — verify 200 is returned
        anon_client = Client()
        response = anon_client.get('/healthz/')
        self.assertEqual(response.status_code, 200)

    def test_shallow_does_not_hit_db(self):
        """Shallow check must NOT query the database."""
        with patch('core.views.connection') as mock_conn:
            self.client.get('/healthz/')
            mock_conn.cursor.assert_not_called()


class HealthzDeepTest(TestCase):
    """Tests for the deep health-check (?deep=1)."""

    def setUp(self):
        self.client = Client()

    def test_deep_returns_200_when_db_ok(self):
        response = self.client.get('/healthz/?deep=1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, {'status': 'ok'})

    def test_deep_returns_503_on_db_failure(self):
        """Simulate DB failure: OperationalError must produce 503."""
        from django.db import OperationalError

        with patch('core.views.connection') as mock_conn:
            mock_conn.cursor.side_effect = OperationalError("Connection refused")
            response = self.client.get('/healthz/?deep=1')

        self.assertEqual(response.status_code, 503)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        # Must NOT expose DB details or stack trace
        content_str = response.content.decode()
        self.assertNotIn('Connection refused', content_str)
        self.assertNotIn('traceback', content_str.lower())

    def test_deep_response_contains_no_secrets(self):
        """Deep check response must not leak settings or credentials."""
        response = self.client.get('/healthz/?deep=1')
        content_str = response.content.decode()
        self.assertNotIn('SECRET_KEY', content_str)
        self.assertNotIn('DB_PASSWORD', content_str)
        self.assertNotIn('DEBUG', content_str)
