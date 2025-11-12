#!/usr/bin/env python3
"""
Unit & integration tests for client.GithubOrgClient.

- Unit tests: org property, _public_repos_url, public_repos, has_license
- Integration tests: public_repos with only HTTP boundary mocked
  via fixtures.py payloads through requests.get(...).json().
"""
from typing import Any, Dict
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str, mock_get_json) -> None:
        """org returns value from get_json and calls it once with org URL."""
        mock_get_json.return_value = {"ok": True}
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, {"ok": True})
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")

    def test_public_repos_url(self) -> None:
        """_public_repos_url is derived from org payload (mocked property)."""
        expected_url = "https://api.github.com/orgs/google/repos"
        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock,
            return_value={"repos_url": expected_url},
        ):
            client = GithubOrgClient("google")
            self.assertEqual(client._public_repos_url, expected_url)

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json) -> None:
        """public_repos returns repo names list from JSON payload."""
        sample_url = "https://api.github.com/orgs/google/repos"
        with patch.object(GithubOrgClient, "_public_repos_url", new=sample_url):
            mock_get_json.return_value = [
                {"name": "alpha", "license": {"key": "mit"}},
                {"name": "beta", "license": {"key": "apache-2.0"}},
            ]
            client = GithubOrgClient("google")
            self.assertEqual(client.public_repos(), ["alpha", "beta"])
            mock_get_json.assert_called_once_with(sample_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(
        self,
        repo: Dict[str, Any],
        license_key: str,
        expected: bool
    ) -> None:
        """has_license returns True only when repo['license']['key'] matches."""
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)


# ---------------- Integration tests ---------------- #

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
    def setUpClass(cls) -> None:
        """Patch requests.get and route responses to fixtures via side_effect."""
        def mocked_get(url: str):
            class _Resp:
                def __init__(self, payload):
                    self._payload = payload

                def json(self):
                    return self._payload
            if url.endswith("/orgs/google") or url.endswith("/orgs/abc"):
                return _Resp(cls.org_payload)
            if url.endswith("/orgs/google/repos") or url.endswith("/orgs/abc/repos"):
                return _Resp(cls.repos_payload)
            if "/repos" in url:
                return _Resp(cls.repos_payload)
            return _Resp(cls.org_payload)

        cls.get_patcher = patch("requests.get", side_effect=mocked_get)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:
        """Stop the requests.get patcher."""
        cls.get_patcher.stop()

    def test_public_repos_integration_all(self) -> None:
        """End-to-end: returns all repos' names."""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_integration_apache2_only(self) -> None:
        """End-to-end with license filter 'apache-2.0'."""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos,
        )


if __name__ == "__main__":
    unittest.main()

