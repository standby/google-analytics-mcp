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

"""Test cases for the OAuth handler module."""

import os
import pathlib
import tempfile
import unittest
from unittest.mock import MagicMock, patch, mock_open

from analytics_mcp.oauth_handler import OAuthHandler


class TestOAuthHandler(unittest.TestCase):
    """Test cases for the OAuthHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.client_secrets_file = os.path.join(
            self.temp_dir, "client_secrets.json"
        )
        self.token_file = os.path.join(self.temp_dir, "token.json")

        # Create a fake client secrets file
        with open(self.client_secrets_file, "w") as f:
            f.write('{"installed": {"client_id": "test_id"}}')

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_init_with_explicit_path(self):
        """Tests initialization with explicit client secrets path."""
        handler = OAuthHandler(
            client_secrets_file=self.client_secrets_file,
            token_file=self.token_file,
        )
        self.assertEqual(handler.client_secrets_file, self.client_secrets_file)
        self.assertEqual(handler.token_file, self.token_file)

    def test_init_with_env_var(self):
        """Tests initialization using environment variables."""
        os.environ["GOOGLE_OAUTH_CLIENT_SECRETS"] = self.client_secrets_file
        os.environ["GOOGLE_OAUTH_TOKEN_FILE"] = self.token_file

        try:
            handler = OAuthHandler()
            self.assertEqual(
                handler.client_secrets_file, self.client_secrets_file
            )
            self.assertEqual(handler.token_file, self.token_file)
        finally:
            del os.environ["GOOGLE_OAUTH_CLIENT_SECRETS"]
            del os.environ["GOOGLE_OAUTH_TOKEN_FILE"]

    def test_init_without_client_secrets(self):
        """Tests that initialization fails without client secrets."""
        with self.assertRaises(ValueError) as context:
            OAuthHandler()
        self.assertIn(
            "OAuth client secrets file must be provided", str(context.exception)
        )

    def test_clear_credentials(self):
        """Tests clearing stored credentials."""
        # Create a token file
        with open(self.token_file, "w") as f:
            f.write('{"token": "test"}')

        handler = OAuthHandler(
            client_secrets_file=self.client_secrets_file,
            token_file=self.token_file,
        )

        # Verify file exists
        self.assertTrue(os.path.exists(self.token_file))

        # Clear credentials
        handler.clear_credentials()

        # Verify file is removed
        self.assertFalse(os.path.exists(self.token_file))

    @patch("analytics_mcp.oauth_handler.Credentials")
    def test_get_credentials_with_valid_token(self, mock_credentials_class):
        """Tests getting credentials when valid token exists."""
        # Create a fake token file
        with open(self.token_file, "w") as f:
            f.write('{"token": "test", "refresh_token": "refresh"}')

        # Mock credentials
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials_class.from_authorized_user_file.return_value = (
            mock_creds
        )

        handler = OAuthHandler(
            client_secrets_file=self.client_secrets_file,
            token_file=self.token_file,
        )

        creds = handler.get_credentials()

        # Verify credentials were loaded from file
        mock_credentials_class.from_authorized_user_file.assert_called_once()
        self.assertEqual(creds, mock_creds)

    @patch("analytics_mcp.oauth_handler.Request")
    @patch("analytics_mcp.oauth_handler.Credentials")
    def test_get_credentials_with_expired_token(
        self, mock_credentials_class, mock_request
    ):
        """Tests getting credentials when token is expired but refreshable."""
        # Create a fake token file
        with open(self.token_file, "w") as f:
            f.write('{"token": "test", "refresh_token": "refresh"}')

        # Mock credentials
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh"
        mock_credentials_class.from_authorized_user_file.return_value = (
            mock_creds
        )

        # After refresh, credentials become valid
        def refresh_side_effect(request):
            mock_creds.valid = True

        mock_creds.refresh.side_effect = refresh_side_effect

        handler = OAuthHandler(
            client_secrets_file=self.client_secrets_file,
            token_file=self.token_file,
        )

        # Mock _save_credentials to avoid actual file I/O
        with patch.object(handler, "_save_credentials"):
            creds = handler.get_credentials()

        # Verify refresh was called
        mock_creds.refresh.assert_called_once()
        self.assertTrue(creds.valid)


if __name__ == "__main__":
    unittest.main()
