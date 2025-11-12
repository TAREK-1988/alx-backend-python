#!/usr/bin/env python3
"""Tests for GithubOrgClient (Tasks 4 & 5 only)."""
from unittest import TestCase
from unittest.mock import patch, PropertyMock
from parameterized import parameterized

from client import GithubOrgClient


class TestGithubOrgClient(TestCase):
    """Unit tests for GithubOrgClient."""

    # ---- Task 4 ----
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """org returns payload from get_json and calls it once with URL."""
        payload = {"login": org_name}
        mock_get_json.return_value = payload

        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    # ---- Task 5 ----
    def test_public_repos_url(self):
        """_public_repos_url is derived from the org payload (mocked)."""
        expected = "https://api.github.com/orgs/google/repos"
        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock,
            return_value={"repos_url": expected},
        ):
            client = GithubOrgClient("google")
            self.assertEqual(client._public_repos_url, expected)


if __name__ == "__main__":
    import unittest
    unittest.main()
