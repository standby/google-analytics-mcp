# Copyright 2025 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test cases for the utils module."""

import os
import unittest
from unittest.mock import patch, MagicMock

from analytics_mcp.tools import utils


class TestUtils(unittest.TestCase):
    """Test cases for the utils module."""

    def test_construct_property_rn(self):
        """Tests construct_property_rn using valid input."""
        self.assertEqual(
            utils.construct_property_rn(12345),
            "properties/12345",
            "Numeric property ID should b considered valid",
        )
        self.assertEqual(
            utils.construct_property_rn("12345"),
            "properties/12345",
            "Numeric property ID as string should be considered valid",
        )
        self.assertEqual(
            utils.construct_property_rn(" 12345  "),
            "properties/12345",
            "Whitespace around property ID should be considered valid",
        )
        self.assertEqual(
            utils.construct_property_rn("properties/12345"),
            "properties/12345",
            "Full resource name should be considered valid",
        )

    def test_construct_property_rn_invalid_input(self):
        """Tests that construct_property_rn raises a ValueError for invalid input."""
        with self.assertRaises(ValueError, msg="None should fail"):
            utils.construct_property_rn(None)
        with self.assertRaises(ValueError, msg="Empty string should fail"):
            utils.construct_property_rn("")
        with self.assertRaises(
            ValueError, msg="Non-numeric string should fail"
        ):
            utils.construct_property_rn("abc")
        with self.assertRaises(
            ValueError, msg="Resource name without ID should fail"
        ):
            utils.construct_property_rn("properties/")
        with self.assertRaises(
            ValueError, msg="Resource name with non-numeric ID should fail"
        ):
            utils.construct_property_rn("properties/abc")
        with self.assertRaises(
            ValueError,
            msg="Resource name with more than 2 components should fail",
        ):
            utils.construct_property_rn("properties/123/abc")


class TestCredentials(unittest.TestCase):
    """Test cases for credential creation."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear any cached credentials
        utils._oauth_credentials = None
        # Store original environment
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
        # Clear cached credentials
        utils._oauth_credentials = None

    def test_create_credentials_requires_oauth_by_default(self):
        """Tests that OAuth is required by default when no env vars are set."""
        # Remove OAuth-related env vars if present
        os.environ.pop("GOOGLE_OAUTH_CLIENT_SECRETS", None)
        os.environ.pop("GOOGLE_ANALYTICS_USE_ADC", None)

        with self.assertRaises(ValueError) as context:
            utils._create_credentials()

        # Verify the error message mentions OAuth setup
        self.assertIn("Authentication Required", str(context.exception))
        self.assertIn("GOOGLE_OAUTH_CLIENT_SECRETS", str(context.exception))

    @patch("analytics_mcp.tools.utils.google.auth.default")
    def test_create_credentials_with_adc_flag(self, mock_auth_default):
        """Tests that ADC is used when explicitly enabled."""
        # Mock the credentials
        mock_creds = MagicMock()
        mock_auth_default.return_value = (mock_creds, None)

        # Enable ADC mode
        os.environ["GOOGLE_ANALYTICS_USE_ADC"] = "true"
        os.environ.pop("GOOGLE_OAUTH_CLIENT_SECRETS", None)

        creds = utils._create_credentials()

        # Verify ADC was called
        mock_auth_default.assert_called_once()
        self.assertEqual(creds, mock_creds)

    @patch("analytics_mcp.oauth_handler.OAuthHandler")
    def test_create_credentials_with_oauth(self, mock_oauth_handler_class):
        """Tests that OAuth is used when client secrets are provided."""
        # Mock the OAuth handler
        mock_handler = MagicMock()
        mock_creds = MagicMock()
        mock_handler.get_credentials.return_value = mock_creds
        mock_oauth_handler_class.return_value = mock_handler

        # Set OAuth client secrets
        os.environ["GOOGLE_OAUTH_CLIENT_SECRETS"] = "/path/to/secrets.json"
        os.environ.pop("GOOGLE_ANALYTICS_USE_ADC", None)

        creds = utils._create_credentials()

        # Verify OAuth handler was used
        mock_oauth_handler_class.assert_called_once()
        mock_handler.get_credentials.assert_called_once()
        self.assertEqual(creds, mock_creds)

    @patch("analytics_mcp.oauth_handler.OAuthHandler")
    def test_create_credentials_oauth_takes_precedence(
        self, mock_oauth_handler_class
    ):
        """Tests that OAuth is used even when ADC flag is false."""
        # Mock the OAuth handler
        mock_handler = MagicMock()
        mock_creds = MagicMock()
        mock_handler.get_credentials.return_value = mock_creds
        mock_oauth_handler_class.return_value = mock_handler

        # Set OAuth but ADC flag to false (should still use OAuth)
        os.environ["GOOGLE_OAUTH_CLIENT_SECRETS"] = "/path/to/secrets.json"
        os.environ["GOOGLE_ANALYTICS_USE_ADC"] = "false"

        creds = utils._create_credentials()

        # Verify OAuth was used (not ADC)
        mock_oauth_handler_class.assert_called_once()
        self.assertEqual(creds, mock_creds)
