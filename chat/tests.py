"""Module for django tests."""

import json
import os
import uuid
from unittest.mock import patch

import numpy as np
from django.test import Client, TestCase
from django.urls import reverse

from .models import ChatSession
from .utils_plot import (
    _experimental_plot_data,
    plot_mix_density,
    plot_pure_density,
    plot_pure_surface_tension,
    plot_pure_vapor_pressure,
    pop_plot_html,
)


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

    def _plot_html(self, result):
        """Return and remove the rendered HTML associated with a plot response."""
        html = pop_plot_html(result["plot_id"])
        if html is None:
            raise AssertionError("Plot HTML was not stored")
        return html

    def test_plot_pure_density_returns_agent_safe_payload(self):
        """Plot helpers should expose only plot metadata and success status."""
        result = plot_pure_density("CC", 280.0, 300.0, 101325.0)

        self.assertIsInstance(result, dict)
        self.assertTrue(result["success"])
        self.assertIn("message", result)
        self.assertIn("data", result)
        self.assertNotIn("html", result)
        self.assertEqual(result["plot_type"], "density")

    def test_experimental_plot_data_applies_axis_scaling(self):
        """Experimental values are converted independently on each axis."""
        data = np.array([[300.0, 2.5], [310.0, 3.0]])

        self.assertEqual(
            _experimental_plot_data(data, y_scale=1000.0),
            [[300.0, 310.0], [2500.0, 3000.0]],
        )

    @patch("chat.utils_plot.retrieve_rho_pure_data")
    def test_pure_density_uses_kpa_for_experimental_lookup(self, mock_retrieve):
        """The pure-density lookup receives pressure converted from Pa to kPa."""
        mock_retrieve.return_value = np.array([[280.0, 900.0]])

        result = plot_pure_density("CC", 280.0, 280.0, 101325.0)

        mock_retrieve.assert_called_once_with(smiles="CC", pressure=101.325)
        self.assertIn('"TML": [[280.0], [900.0]]', self._plot_html(result))

    @patch("chat.utils_plot.retrieve_vp_pure_data")
    def test_pure_vapor_pressure_converts_kpa_to_pa(self, mock_retrieve):
        """Experimental vapor pressure is rendered in Pa, not source kPa."""
        mock_retrieve.return_value = np.array([[300.0, 2.5]])

        result = plot_pure_vapor_pressure("CC", 300.0, 300.0)

        self.assertIn("[300.0], [2500.0]", self._plot_html(result))

    @patch("chat.utils_plot.retrieve_st_pure_data")
    def test_surface_tension_converts_n_per_m_to_mn_per_m(self, mock_retrieve):
        """Experimental surface tension is rendered in mN/m."""
        mock_retrieve.return_value = np.array([[300.0, 0.025]])

        result = plot_pure_surface_tension("CC", 300.0)

        self.assertIn("[300.0], [25.0]", self._plot_html(result))

    @patch("chat.utils_plot.retrieve_rho_binary_data")
    def test_mixture_density_keeps_experimental_density_units(self, mock_retrieve):
        """Experimental mixture density is already returned in mol/m3."""
        mock_retrieve.return_value = np.array([[280.0, 850.0]])

        result = plot_mix_density(["CC", "O"], 280.0, 280.0, 101325.0, [0.5, 0.5])

        mock_retrieve.assert_called_once_with(
            smiles_list=["CC", "O"], pressure=101.325, x1=0.5
        )
        self.assertIn("[280.0], [850.0]", self._plot_html(result))


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
