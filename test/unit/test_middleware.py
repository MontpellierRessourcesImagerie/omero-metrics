"""Tests for omero_metrics.middleware module."""

from unittest.mock import MagicMock

import pytest

from omero_metrics.middleware import OmeroAuth


class TestOmeroAuth:
    def test_sets_user_on_request(self):
        get_response = MagicMock(return_value=MagicMock())
        middleware = OmeroAuth(get_response)
        request = MagicMock(spec=[])

        middleware(request)

        assert request.user == "Omero User"

    def test_calls_get_response(self):
        get_response = MagicMock(return_value="response")
        middleware = OmeroAuth(get_response)
        request = MagicMock(spec=[])

        result = middleware(request)

        get_response.assert_called_once_with(request)
        assert result == "response"

    def test_user_set_before_get_response(self):
        """Verify user is set before downstream middleware runs."""
        call_order = []

        def get_response(req):
            call_order.append(("get_response", getattr(req, "user", None)))
            return "response"

        middleware = OmeroAuth(get_response)
        request = MagicMock(spec=[])

        middleware(request)

        assert call_order[0] == ("get_response", "Omero User")
