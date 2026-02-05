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

"""OAuth 2.0 authentication handler for user-based Google account authentication."""

import json
import os
import pathlib
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Read-only scope for Analytics Admin API and Analytics Data API.
_READ_ONLY_ANALYTICS_SCOPE = (
    "https://www.googleapis.com/auth/analytics.readonly"
)

# Default token file location
_DEFAULT_TOKEN_PATH = pathlib.Path.home() / ".analytics-mcp" / "token.json"


class OAuthHandler:
    """Handles OAuth 2.0 user authentication flow for Google Analytics."""

    def __init__(
        self,
        client_secrets_file: Optional[str] = None,
        token_file: Optional[str] = None,
    ):
        """Initializes the OAuth handler.

        Args:
            client_secrets_file: Path to OAuth client secrets JSON file.
                Falls back to GOOGLE_OAUTH_CLIENT_SECRETS environment variable.
            token_file: Path to store/load OAuth tokens.
                Defaults to ~/.analytics-mcp/token.json
        """
        self.client_secrets_file = client_secrets_file or os.environ.get(
            "GOOGLE_OAUTH_CLIENT_SECRETS"
        )
        self.token_file = token_file or os.environ.get(
            "GOOGLE_OAUTH_TOKEN_FILE", str(_DEFAULT_TOKEN_PATH)
        )

        if not self.client_secrets_file:
            raise ValueError(
                "OAuth client secrets file must be provided either via "
                "constructor argument or GOOGLE_OAUTH_CLIENT_SECRETS "
                "environment variable"
            )

    def get_credentials(self) -> Credentials:
        """Gets valid OAuth credentials, refreshing or prompting for auth if needed.

        Returns:
            Valid OAuth 2.0 credentials for Google Analytics API.

        Raises:
            Exception: If authentication fails.
        """
        creds = None

        # Load existing token if available
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_file, [_READ_ONLY_ANALYTICS_SCOPE]
                )
            except Exception as e:
                print(f"Warning: Could not load token file: {e}")
                creds = None

        # Refresh or obtain new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Warning: Could not refresh token: {e}")
                    creds = None

            # If still no valid credentials, start OAuth flow
            if not creds:
                creds = self._run_oauth_flow()

            # Save credentials for future use
            self._save_credentials(creds)

        return creds

    def _run_oauth_flow(self) -> Credentials:
        """Runs the OAuth 2.0 authorization flow.

        Returns:
            Fresh OAuth 2.0 credentials.
        """
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, [_READ_ONLY_ANALYTICS_SCOPE]
        )

        # Run local server flow (opens browser for user to authenticate)
        creds = flow.run_local_server(port=0)
        return creds

    def _save_credentials(self, creds: Credentials) -> None:
        """Saves credentials to token file.

        Args:
            creds: The credentials to save.
        """
        # Ensure directory exists
        token_path = pathlib.Path(self.token_file)
        token_path.parent.mkdir(parents=True, exist_ok=True)

        # Save token
        with open(self.token_file, "w") as token:
            token.write(creds.to_json())

    def clear_credentials(self) -> None:
        """Removes stored credentials, forcing re-authentication on next use."""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
