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

"""Common utilities used by the MCP server."""

import os
import threading
from typing import Any, Dict, Optional

from google.analytics import admin_v1beta, data_v1beta, admin_v1alpha
from google.api_core.gapic_v1.client_info import ClientInfo
from importlib import metadata
import google.auth
import proto


def _get_package_version_with_fallback():
    """Returns the version of the package.

    Falls back to 'unknown' if the version can't be resolved.
    """
    try:
        return metadata.version("analytics-mcp")
    except:
        return "unknown"


# Client information that adds a custom user agent to all API requests.
_CLIENT_INFO = ClientInfo(
    user_agent=f"analytics-mcp/{_get_package_version_with_fallback()}"
)

# Read-only scope for Analytics Admin API and Analytics Data API.
_READ_ONLY_ANALYTICS_SCOPE = (
    "https://www.googleapis.com/auth/analytics.readonly"
)

# Global credentials cache for OAuth mode
_oauth_credentials: Optional[google.auth.credentials.Credentials] = None
_oauth_credentials_lock = threading.Lock()


def _create_credentials() -> google.auth.credentials.Credentials:
    """Returns credentials with read-only scope.

    Supports both OAuth (user authentication) and ADC (Application Default Credentials).

    By default, OAuth user authentication is used, which prompts users to authenticate
    with their Google account. This allows different users to connect with their own
    Google accounts and access their Google Analytics properties.

    OAuth mode requires the GOOGLE_OAUTH_CLIENT_SECRETS environment variable to be set
    to the path of your OAuth client secrets JSON file.

    ADC mode can be explicitly enabled by setting GOOGLE_ANALYTICS_USE_ADC=true.
    This is useful for automation, service accounts, and server-to-server authentication.
    """
    global _oauth_credentials

    # Check if ADC mode is explicitly requested
    use_adc = os.environ.get("GOOGLE_ANALYTICS_USE_ADC", "").lower() == "true"

    if use_adc:
        # Use Application Default Credentials (for automation/service accounts)
        credentials, _ = google.auth.default(
            scopes=[_READ_ONLY_ANALYTICS_SCOPE]
        )
        return credentials

    # Default to OAuth user authentication
    if not os.environ.get("GOOGLE_OAUTH_CLIENT_SECRETS"):
        # OAuth is the default, provide helpful error message
        raise ValueError(
            "\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  Google Analytics MCP Server - Authentication Required\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "This server requires user authentication to access Google Analytics.\n"
            "Please set up OAuth 2.0 authentication:\n\n"
            "1. Create OAuth 2.0 credentials in Google Cloud Console:\n"
            "   https://console.cloud.google.com/apis/credentials\n\n"
            "2. Download the client secrets JSON file\n\n"
            "3. Set the GOOGLE_OAUTH_CLIENT_SECRETS environment variable:\n"
            "   export GOOGLE_OAUTH_CLIENT_SECRETS=/path/to/client_secrets.json\n\n"
            "4. Add it to your MCP client configuration (e.g., ~/.gemini/settings.json):\n"
            "   {\n"
            '     "mcpServers": {\n'
            '       "analytics-mcp": {\n'
            '         "command": "pipx",\n'
            '         "args": ["run", "analytics-mcp"],\n'
            '         "env": {\n'
            '           "GOOGLE_OAUTH_CLIENT_SECRETS": "/path/to/client_secrets.json"\n'
            "         }\n"
            "       }\n"
            "     }\n"
            "   }\n\n"
            "For detailed setup instructions, see:\n"
            "https://github.com/googleanalytics/google-analytics-mcp/blob/main/docs/OAUTH_SETUP.md\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "For automation/service accounts, you can use ADC instead:\n"
            "Set GOOGLE_ANALYTICS_USE_ADC=true to use Application Default Credentials\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )

    # Use OAuth user authentication with thread-safe caching
    with _oauth_credentials_lock:
        if _oauth_credentials is None:
            from analytics_mcp.oauth_handler import OAuthHandler

            handler = OAuthHandler()
            _oauth_credentials = handler.get_credentials()
        return _oauth_credentials


def create_admin_api_client() -> admin_v1beta.AnalyticsAdminServiceAsyncClient:
    """Returns a properly configured Google Analytics Admin API async client.

    Uses Application Default Credentials with read-only scope.
    """
    return admin_v1beta.AnalyticsAdminServiceAsyncClient(
        client_info=_CLIENT_INFO, credentials=_create_credentials()
    )


def create_data_api_client() -> data_v1beta.BetaAnalyticsDataAsyncClient:
    """Returns a properly configured Google Analytics Data API async client.

    Uses Application Default Credentials with read-only scope.
    """
    return data_v1beta.BetaAnalyticsDataAsyncClient(
        client_info=_CLIENT_INFO, credentials=_create_credentials()
    )


def create_admin_alpha_api_client() -> (
    admin_v1alpha.AnalyticsAdminServiceAsyncClient
):
    """Returns a properly configured Google Analytics Admin API (alpha) async client.
    Uses Application Default Credentials with read-only scope.
    """
    return admin_v1alpha.AnalyticsAdminServiceAsyncClient(
        client_info=_CLIENT_INFO, credentials=_create_credentials()
    )


def construct_property_rn(property_value: int | str) -> str:
    """Returns a property resource name in the format required by APIs."""
    property_num = None
    if isinstance(property_value, int):
        property_num = property_value
    elif isinstance(property_value, str):
        property_value = property_value.strip()
        if property_value.isdigit():
            property_num = int(property_value)
        elif property_value.startswith("properties/"):
            numeric_part = property_value.split("/")[-1]
            if numeric_part.isdigit():
                property_num = int(numeric_part)
    if property_num is None:
        raise ValueError(
            (
                f"Invalid property ID: {property_value}. "
                "A valid property value is either a number or a string starting "
                "with 'properties/' and followed by a number."
            )
        )

    return f"properties/{property_num}"


def proto_to_dict(obj: proto.Message) -> Dict[str, Any]:
    """Converts a proto message to a dictionary."""
    return type(obj).to_dict(
        obj, use_integers_for_enums=False, preserving_proto_field_name=True
    )


def proto_to_json(obj: proto.Message) -> str:
    """Converts a proto message to a JSON string."""
    return type(obj).to_json(obj, indent=None, preserving_proto_field_name=True)
