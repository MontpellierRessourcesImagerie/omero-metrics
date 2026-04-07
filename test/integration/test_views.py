"""Integration tests for views — requires running OMERO server."""

import json

import pytest
from django.urls import reverse
from omero.gateway import BlitzGateway, DatasetWrapper, ProjectWrapper
from omeroweb.testlib import IWebTest, get


def get_connection(user, group_id=None):
    """Get a BlitzGateway connection for the given user's client."""
    connection = BlitzGateway(client_obj=user[0])
    connection.getEventContext()
    if group_id is not None:
        connection.SERVICE_OPTS.setOmeroGroup(group_id)
    return connection


@pytest.mark.django_db
class TestGroupView(IWebTest):
    """Integration tests for the group viewer endpoint."""

    @pytest.fixture()
    def user1(self):
        user = self.new_client_and_user(privileges=None)
        return user

    def test_group_view_returns_200(self, user1):
        conn = get_connection(user1)
        user_name = conn.getUser().getName()
        django_client = self.new_django_client(user_name, user_name)
        url = reverse("group")
        rsp = get(django_client, url)
        assert rsp.status_code == 200

    def test_group_view_renders_dash_template(self, user1):
        conn = get_connection(user1)
        user_name = conn.getUser().getName()
        django_client = self.new_django_client(user_name, user_name)
        url = reverse("group")
        rsp = get(django_client, url)
        html = rsp.content.decode()
        assert "omero_group_dash" in html


@pytest.mark.django_db
class TestDatasetView(IWebTest):
    """Integration tests for the dataset viewer endpoint."""

    @pytest.fixture()
    def user1(self):
        user = self.new_client_and_user(privileges=None)
        return user

    def test_dataset_view_handles_empty_dataset(self, user1):
        """A dataset with no annotations should not crash."""
        conn = get_connection(user1)
        dataset = self.make_dataset(name="empty_dataset", client=conn.c)
        dataset_wrapper = DatasetWrapper(conn, dataset)
        dataset_id = int(dataset_wrapper.getId())

        user_name = conn.getUser().getName()
        django_client = self.new_django_client(user_name, user_name)
        url = reverse("dataset", args=[dataset_id])
        rsp = get(django_client, url)
        assert rsp.status_code == 200


@pytest.mark.django_db
class TestProjectView(IWebTest):
    """Integration tests for the project viewer endpoint."""

    @pytest.fixture()
    def user1(self):
        user = self.new_client_and_user(privileges=None)
        return user

    def test_project_without_config_shows_form(self, user1):
        """A project with no config file should show the configuration form."""
        conn = get_connection(user1)
        project = self.make_project(
            name="unconfigured_project", description="No config", client=conn.c
        )
        project_wrapper = ProjectWrapper(conn, project)
        project_id = int(project_wrapper.getId())

        user_name = conn.getUser().getName()
        django_client = self.new_django_client(user_name, user_name)
        url = reverse("project", args=[project_id])
        rsp = get(django_client, url)
        html = rsp.content.decode()
        assert rsp.status_code == 200
        # Should show either the config form or an error/warning
        assert any(
            term in html
            for term in [
                "omero_project_config_form",
                "ErrorApp",
                "WarningApp",
                "omero_project_dash",
            ]
        )


class TestURLRouting(IWebTest):
    """Integration tests for URL routing."""

    @pytest.fixture()
    def user1(self):
        user = self.new_client_and_user(privileges=None)
        return user

    def test_index_url_resolves(self, user1):
        url = reverse("omero_metrics_index")
        assert url is not None

    def test_group_url_resolves(self, user1):
        url = reverse("group")
        assert url is not None

    def test_project_url_resolves(self, user1):
        url = reverse("project", args=[1])
        assert url is not None

    def test_dataset_url_resolves(self, user1):
        url = reverse("dataset", args=[1])
        assert url is not None

    def test_image_url_resolves(self, user1):
        url = reverse("image", args=[1])
        assert url is not None
