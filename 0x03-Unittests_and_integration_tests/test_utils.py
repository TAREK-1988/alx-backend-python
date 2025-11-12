#!/usr/bin/env python3
"""
Unit tests for utils.py: access_nested_map, get_json, memoize.
Covers happy paths, error paths, HTTP mocking, and memoization behavior.
"""
from typing import Any, Dict, Tuple
import unittest
from unittest.mock import Mock, patch
from parameterized import parameterized

from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Tests for utils.access_nested_map."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(
        self,
        nested_map: Dict[str, Any],
        path: Tuple[str, ...],
        expected: Any
    ) -> None:
        """It returns the expected value for valid paths."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "'a'"),
        ({"a": 1}, ("a", "b"), "'b'"),
    ])
    def test_access_nested_map_exception(
        self,
        nested_map: Dict[str, Any],
        path: Tuple[str, ...],
        expected_msg: str
    ) -> None:
        """It raises KeyError with the missing key in the message."""
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), expected_msg)


class TestGetJson(unittest.TestCase):
    """Tests for utils.get_json with HTTP call mocked."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url: str, test_payload: Dict[str, Any]) -> None:
        """It returns the JSON payload and calls requests.get exactly once."""
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        with patch("utils.requests.get", return_value=mock_response) as mock_get:
            self.assertEqual(get_json(test_url), test_payload)
            mock_get.assert_called_once_with(test_url)


class TestMemoize(unittest.TestCase):
    """Tests for utils.memoize decorator."""

    def test_memoize(self) -> None:
        """It calls the wrapped method only once and caches the result."""
        class TestClass:
            """Simple class to exercise memoize decorator."""

            def a_method(self) -> int:
                """Return a constant to verify memoization."""
                return 42

            @memoize
            def a_property(self) -> int:
                """Memoized property-like method that forwards to a_method."""
                return self.a_method()

        obj = TestClass()
        with patch.object(TestClass, "a_method", return_value=42) as mock_m:
            # First call computes, second call hits cache
            self.assertEqual(obj.a_property, 42)
            self.assertEqual(obj.a_property, 42)
            mock_m.assert_called_once()


if __name__ == "__main__":
    unittest.main()

