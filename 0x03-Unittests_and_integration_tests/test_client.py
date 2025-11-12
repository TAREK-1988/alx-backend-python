#!/usr/bin/env python3
"""Tests for GithubOrgClient (Tasks 4, 5, 6)."""
from unittest import TestCase
from unittest.mock import patch, PropertyMock
from parameterized import parameterized

from client import GithubOrgClient


class TestGithubOrgClient(TestCase):
    """Unit tests for GithubOrgClient (tasks 4–6)."""

    # ---- Task 4: org ----
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

    # ---- Task 5: _public_repos_url ----
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

    # ---- Task 6: public_repos ----
    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """
        public_repos returns repo names list.
        - Decorator: patch get_json
        - Context manager: patch _public_repos_url as PropertyMock
        """
        sample_url = "https://api.github.com/orgs/google/repos"
        repos_payload = [
            {"name": "alpha", "license": {"key": "mit"}},
            {"name": "beta", "license": {"key": "apache-2.0"}},
        ]
        mock_get_json.return_value = repos_payload

        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock,
            return_value=sample_url,
        ) as mocked_url:
            client = GithubOrgClient("google")
            self.assertEqual(client.public_repos(), ["alpha", "beta"])
            # called once with the mocked URL
            mock_get_json.assert_called_once_with(sample_url)
            mocked_url.assert_called_once()


if __name__ == "__main__":
    import unittest
    unittest.main()
