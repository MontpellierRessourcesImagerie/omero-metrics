"""Tests for omero_metrics.views module — unit tests with mocked OMERO."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

pytest.importorskip("omero", reason="omero package not available locally")

# Configure minimal Django settings for unit tests (avoids omeroweb.settings which needs OMERODIR)
from django.conf import settings as django_settings

if not django_settings.configured:
    django_settings.configure(
        STATIC_URL="/static/",
        SECRET_KEY="test-secret-key",
    )


class FakeSession(dict):
    """A dict subclass that works as a Django session mock."""

    def get(self, key, default=None):
        return super().get(key, default)


class TestCenterViewerGroupSessionSerialization:
    """Verify that DataFrames are serialized to JSON strings before session storage."""

    @patch("omero_metrics.views.load")
    @patch("omero_metrics.views.render")
    def test_dataframes_serialized_to_json(self, mock_render, mock_load):
        """The file_ann and map_ann DataFrames must be JSON strings in the session."""
        from omero_metrics.views import center_viewer_group

        file_ann_df = pd.DataFrame(
            {
                "Name": ["file1.yaml"],
                "ID": [1],
                "File_ID": [101],
                "Description": ["desc"],
                "Date": pd.to_datetime(["2024-01-15"]),
                "Owner": ["user"],
                "NS": ["microscopemetrics_schema:core"],
            }
        )
        map_ann_df = pd.DataFrame(
            {
                "Name": ["map1"],
                "ID": [10],
                "Description": ["desc"],
                "Date": pd.to_datetime(["2024-01-15"]),
                "Owner": ["user"],
                "NS": ["microscopemetrics_schema:core"],
            }
        )
        mock_load.get_annotations_tables.return_value = (file_ann_df, map_ann_df)

        mock_group = MagicMock()
        mock_group.getName.return_value = "TestGroup"
        mock_group.getDescription.return_value = "Test description"

        mock_conn = MagicMock()
        mock_conn.getEventContext.return_value = MagicMock(groupId=1)
        mock_conn.getObject.return_value = mock_group

        request = MagicMock()
        request.session = FakeSession(active_group=1)
        mock_render.return_value = "rendered"

        # Call the view (bypassing @login_required)
        result = center_viewer_group.__wrapped__(request, conn=mock_conn)

        # Verify session contains JSON strings, not DataFrames
        dash_ctx = request.session["django_plotly_dash"]["context"]
        assert isinstance(
            dash_ctx["file_ann"], str
        ), "file_ann should be a JSON string"
        assert isinstance(
            dash_ctx["map_ann"], str
        ), "map_ann should be a JSON string"

        # Verify the JSON can be parsed back to a DataFrame
        restored = pd.read_json(dash_ctx["file_ann"])
        assert "Name" in restored.columns


class TestViewErrorHandling:
    """Test that views handle errors gracefully."""

    @patch("omero_metrics.views.data_managers")
    @patch("omero_metrics.views.render")
    def test_center_viewer_image_error(self, mock_render, mock_dm):
        from omero_metrics.views import center_viewer_image

        mock_dm.ImageManager.side_effect = ValueError("Image not found")
        mock_render.return_value = "rendered"

        request = MagicMock()
        request.session = FakeSession()
        mock_conn = MagicMock()

        result = center_viewer_image.__wrapped__(request, image_id=1, conn=mock_conn)

        # Should render ErrorApp
        mock_render.assert_called_once()
        call_kwargs = mock_render.call_args
        assert call_kwargs[1]["context"]["app_name"] == "ErrorApp"

    @patch("omero_metrics.views.data_managers")
    @patch("omero_metrics.views.render")
    def test_center_viewer_dataset_error(self, mock_render, mock_dm):
        from omero_metrics.views import center_viewer_dataset

        mock_dm.DatasetManager.side_effect = RuntimeError("Load failed")
        mock_render.return_value = "rendered"

        request = MagicMock()
        request.session = FakeSession()
        mock_conn = MagicMock()

        result = center_viewer_dataset.__wrapped__(
            request, dataset_id=1, conn=mock_conn
        )

        call_kwargs = mock_render.call_args
        assert call_kwargs[1]["context"]["app_name"] == "ErrorApp"
        dash_ctx = request.session["django_plotly_dash"]["context"]
        assert "Load failed" in dash_ctx["message"]
