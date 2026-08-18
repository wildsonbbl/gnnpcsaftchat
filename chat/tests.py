"""Module for django tests."""

import json
import os
import uuid
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from .models import ChatSession
from .plot_utils import plot_pure_density


class ViewsTestCase(TestCase):
    """Test case for views."""

    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        # Store the original API key if it exists
        self.original_api_key = os.environ.get("GOOGLE_API_KEY")

    def tearDown(self):
        """Clean up after tests."""
        # Restore the original API key if it existed
        if self.original_api_key:
            os.environ["GOOGLE_API_KEY"] = self.original_api_key
        elif "GOOGLE_API_KEY" in os.environ:
            del os.environ["GOOGLE_API_KEY"]

    def test_about(self):
        """Test about page view."""
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about.html")


class PlotUtilsContractTest(TestCase):
    """Test that plotting helper tools return structured, agent-safe payloads."""

    @patch("chat.plot_utils.predict_pcsaft_parameters", return_value={"mock": "params"})
    @patch(
        "chat.plot_utils.pure_den_feos",
        side_effect=lambda parameters, state: float(state[0]) * 2.0,
    )
    def test_plot_pure_density_returns_agent_safe_payload(
        self, _mock_pure_den_feos, _mock_predict
    ):
        """Plot helpers should expose only plot metadata and success status."""
        result = plot_pure_density("CC", 280.0, 300.0, 101325.0)

        self.assertIsInstance(result, dict)
        self.assertTrue(result["success"])
        self.assertIn("message", result)
        self.assertIn("data", result)
        self.assertNotIn("html", result)
        self.assertEqual(result["plot_type"], "density")


class APIViewsTestCase(TestCase):
    """Test case for API views."""

    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        # Create test sessions
        self.session1 = ChatSession.objects.create(name="Test Session 1")
        self.session2 = ChatSession.objects.create(name="Test Session 2")

    def test_get_sessions(self):
        """Test get_sessions API endpoint."""
        response = self.client.get(reverse("get_sessions"))
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertIn("sessions", data)
        self.assertEqual(len(data["sessions"]), 2)

        # Check that session data is correct
        session_ids = [s["session_id"] for s in data["sessions"]]
        self.assertIn(str(self.session1.session_id), session_ids)
        self.assertIn(str(self.session2.session_id), session_ids)

    def test_create_session(self):
        """Test create_session API endpoint."""
        data = {"name": "New Test Session"}
        response = self.client.post(
            reverse("create_session"), json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertIn("session_id", response_data)
        self.assertIn("name", response_data)
        self.assertEqual(response_data["name"], "New Test Session")

        # Verify session was created in database
        session = ChatSession.objects.get(session_id=response_data["session_id"])
        self.assertEqual(session.name, "New Test Session")

    def test_delete_session(self):
        """Test delete_session API endpoint."""
        # Delete existing session
        response = self.client.delete(
            reverse("delete_session", args=[self.session1.session_id])
        )
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertTrue(response_data["success"])

        # Verify session was deleted from database
        with self.assertRaises(ChatSession.DoesNotExist):
            ChatSession.objects.get(session_id=self.session1.session_id)

    def test_delete_nonexistent_session(self):
        """Test delete_session API endpoint with nonexistent session ID."""
        nonexistent_id = uuid.uuid4()
        response = self.client.delete(reverse("delete_session", args=[nonexistent_id]))
        self.assertEqual(response.status_code, 404)

        response_data = json.loads(response.content)
        self.assertFalse(response_data["success"])
        self.assertEqual(response_data["error"], "Session not found")
