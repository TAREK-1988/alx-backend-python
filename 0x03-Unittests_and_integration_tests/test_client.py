#!/usr/bin/env python3
"""Tests for GithubOrgClient (Tasks 4–8)."""
import unittest
from unittest import TestCase
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient

# ---- Try to import fixtures (used only in Task 8) ----
_HAVE_FIXTURES = True
try:
    from fixtures import (
        org_payload,
        repos_payload,
        expected_repos,
        apache2_repos,
    )
except Exception:  # pragma: no cover
    _HAVE_FIXTURES = False


class TestGithubOrgClient(TestCase):
    """Unit tests for GithubOrgClient (tasks 4–7)."""

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
        repos = [
            {"name": "alpha", "license": {"key": "mit"}},
            {"name": "beta", "license": {"key": "apache-2.0"}},
        ]
        mock_get_json.return_value = repos

        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock,
            return_value=sample_url,
        ) as mocked_url:
            client = GithubOrgClient("google")
            self.assertEqual(client.public_repos(), ["alpha", "beta"])
            mock_get_json.assert_called_once_with(sample_url)
            mocked_url.assert_called_once()

    # ---- Task 7: has_license (parameterized) ----
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """has_license returns True only when license key matches."""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected,
        )


# ---- Task 8: Integration tests with fixtures ----
if _HAVE_FIXTURES:
    @parameterized_class((
        "org_payload",
        "repos_payload",
        "expected_repos",
        "apache2_repos",
    ), [
        (org_payload, repos_payload, expected_repos, apache2_repos),
    ])
    class TestIntegrationGithubOrgClient(unittest.TestCase):
        """Integration tests for GithubOrgClient.public_repos."""

        @classmethod
        def setUpClass(cls):
            """Patch requests.get; route responses to fixtures via side_effect."""
            def mocked_get(url):
                class _Resp:
                    def __init__(self, payload):
                        self._payload = payload

                    def json(self):
                        return self._payload

                # org endpoints
                if url.endswith("/orgs/google") or url.endswith("/orgs/abc"):
                    return _Resp(cls.org_payload)
                # repos endpoints
                if url.endswith("/orgs/google/repos") or url.endswith(
                    "/orgs/abc/repos"
                ):
                    return _Resp(cls.repos_payload)
                # fallback
                if "/repos" in url:
                    return _Resp(cls.repos_payload)
                return _Resp(cls.org_payload)

            cls.get_patcher = patch("requests.get", side_effect=mocked_get)
            cls.get_patcher.start()

        @classmethod
        def tearDownClass(cls):
            """Stop the requests.get patcher."""
            cls.get_patcher.stop()

        def test_public_repos(self):
            """End-to-end: returns all repo names."""
            client = GithubOrgClient("google")
            self.assertEqual(client.public_repos(), self.expected_repos)

        def test_public_repos_with_license(self):
            """End-to-end with license filter 'apache-2.0'."""
            client = GithubOrgClient("google")
            self.assertEqual(
                client.public_repos(license="apache-2.0"),
                self.apache2_repos,
            )


if __name__ == "__main__":
    unittest.main()
