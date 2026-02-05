#!/usr/bin/env python3

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

"""Example script demonstrating OAuth user authentication.

This script demonstrates how to use OAuth authentication to access Google Analytics.
It will prompt you to authenticate in your browser on first run, then save the token
for future use.

Prerequisites:
1. Create OAuth 2.0 credentials in Google Cloud Console
2. Download the client secrets JSON file
3. Set GOOGLE_OAUTH_CLIENT_SECRETS environment variable to point to the file

Usage:
    export GOOGLE_OAUTH_CLIENT_SECRETS=/path/to/client_secrets.json
    python examples/oauth_authentication_example.py
"""

import asyncio
import os
import sys


def check_oauth_setup():
    """Check if OAuth is properly configured."""
    client_secrets = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRETS")
    if not client_secrets:
        print("ERROR: GOOGLE_OAUTH_CLIENT_SECRETS environment variable not set")
        print()
        print("Please follow these steps:")
        print("1. Create OAuth 2.0 credentials in Google Cloud Console")
        print("2. Download the client secrets JSON file to a secure location")
        print("3. Set the environment variable:")
        print(
            "   export GOOGLE_OAUTH_CLIENT_SECRETS=/path/to/client_secrets.json"
        )
        print()
        print("For detailed instructions, see: docs/OAUTH_SETUP.md")
        return False

    if not os.path.exists(client_secrets):
        print(f"ERROR: Client secrets file not found: {client_secrets}")
        return False

    return True


async def test_oauth_authentication():
    """Test OAuth authentication by fetching account summaries."""
    print("=" * 70)
    print("Google Analytics MCP - OAuth Authentication Example")
    print("=" * 70)
    print()

    # Import after checking setup to avoid import errors
    from analytics_mcp.tools.admin.info import get_account_summaries

    print("Authenticating with Google Analytics...")
    print(
        "If this is your first time, a browser window will open for authentication."
    )
    print()

    try:
        # Call the tool which will trigger authentication
        summaries = await get_account_summaries()

        print("✓ Authentication successful!")
        print()
        print(f"Found {len(summaries)} account(s):")
        print()

        for i, summary in enumerate(summaries, 1):
            account_name = summary.get("account", "Unknown")
            account_display_name = summary.get(
                "display_name", "No display name"
            )
            properties = summary.get("property_summaries", [])

            print(f"{i}. Account: {account_display_name}")
            print(f"   Resource Name: {account_name}")
            print(f"   Properties: {len(properties)}")

            if properties:
                for j, prop in enumerate(properties[:3], 1):
                    prop_name = prop.get("property", "Unknown")
                    prop_display_name = prop.get(
                        "display_name", "No display name"
                    )
                    print(f"      {j}. {prop_display_name} ({prop_name})")

                if len(properties) > 3:
                    print(
                        f"      ... and {len(properties) - 3} more properties"
                    )
            print()

        print("=" * 70)
        print("OAuth authentication is working correctly!")
        print("=" * 70)

    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Ensure OAuth consent screen is configured")
        print("2. Ensure your account has access to GA properties")
        print("3. Check that the scope includes: analytics.readonly")
        print("4. See docs/OAUTH_SETUP.md for detailed instructions")
        return False

    return True


def main():
    """Main entry point."""
    if not check_oauth_setup():
        sys.exit(1)

    success = asyncio.run(test_oauth_authentication())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
