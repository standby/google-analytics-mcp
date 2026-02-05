/**
 * Copyright 2025 Google LLC All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * Authentication utilities for Google Analytics API
 */

interface ServiceAccountCredentials {
  type: string;
  project_id: string;
  private_key_id: string;
  private_key: string;
  client_email: string;
  client_id: string;
  auth_uri: string;
  token_uri: string;
  auth_provider_x509_cert_url: string;
  client_x509_cert_url: string;
}

interface TokenCache {
  access_token: string;
  expires_at: number;
}

const ANALYTICS_SCOPE = 'https://www.googleapis.com/auth/analytics.readonly';
const TOKEN_CACHE_KEY = 'google_access_token';

/**
 * Get or refresh Google OAuth access token using service account
 */
export async function getAccessToken(
  env: any,
  kv: KVNamespace
): Promise<string> {
  // Check cache first
  const cached = await kv.get<TokenCache>(TOKEN_CACHE_KEY, 'json');
  if (cached && cached.expires_at > Date.now()) {
    return cached.access_token;
  }

  // Parse service account credentials
  const credentials: ServiceAccountCredentials = JSON.parse(
    env.GOOGLE_SERVICE_ACCOUNT_KEY
  );

  // Create JWT
  const jwt = await createJWT(credentials);

  // Exchange JWT for access token
  const tokenResponse = await fetch(credentials.token_uri, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
      assertion: jwt,
    }),
  });

  if (!tokenResponse.ok) {
    throw new Error(`Failed to get access token: ${await tokenResponse.text()}`);
  }

  const tokenData = await tokenResponse.json() as any;

  // Cache the token
  const tokenCache: TokenCache = {
    access_token: tokenData.access_token,
    expires_at: Date.now() + (tokenData.expires_in - 60) * 1000, // 60s buffer
  };

  await kv.put(TOKEN_CACHE_KEY, JSON.stringify(tokenCache), {
    expirationTtl: tokenData.expires_in - 60,
  });

  return tokenData.access_token;
}

/**
 * Create JWT for service account authentication
 */
async function createJWT(credentials: ServiceAccountCredentials): Promise<string> {
  const now = Math.floor(Date.now() / 1000);
  const expiry = now + 3600;

  const header = {
    alg: 'RS256',
    typ: 'JWT',
  };

  const payload = {
    iss: credentials.client_email,
    scope: ANALYTICS_SCOPE,
    aud: credentials.token_uri,
    exp: expiry,
    iat: now,
  };

  const encodedHeader = base64UrlEncode(JSON.stringify(header));
  const encodedPayload = base64UrlEncode(JSON.stringify(payload));
  const unsignedToken = `${encodedHeader}.${encodedPayload}`;

  // Sign the token
  const signature = await signJWT(unsignedToken, credentials.private_key);

  return `${unsignedToken}.${signature}`;
}

/**
 * Sign JWT using RS256
 */
async function signJWT(data: string, privateKey: string): Promise<string> {
  // Remove header and footer from PEM
  const pemContents = privateKey
    .replace(/-----BEGIN PRIVATE KEY-----/, '')
    .replace(/-----END PRIVATE KEY-----/, '')
    .replace(/\s/g, '');

  // Decode base64 to get the DER-encoded key
  const binaryKey = base64Decode(pemContents);

  // Import the key
  const cryptoKey = await crypto.subtle.importKey(
    'pkcs8',
    binaryKey,
    {
      name: 'RSASSA-PKCS1-v1_5',
      hash: 'SHA-256',
    },
    false,
    ['sign']
  );

  // Sign the data
  const encoder = new TextEncoder();
  const signature = await crypto.subtle.sign(
    'RSASSA-PKCS1-v1_5',
    cryptoKey,
    encoder.encode(data)
  );

  return base64UrlEncode(signature);
}

/**
 * Base64 URL encode
 */
function base64UrlEncode(data: string | ArrayBuffer): string {
  let base64: string;
  
  if (typeof data === 'string') {
    base64 = btoa(data);
  } else {
    const bytes = new Uint8Array(data);
    const binary = Array.from(bytes, byte => String.fromCharCode(byte)).join('');
    base64 = btoa(binary);
  }

  return base64
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

/**
 * Base64 decode
 */
function base64Decode(base64: string): ArrayBuffer {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}
