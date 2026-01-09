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
 * Google Analytics API client for Cloudflare Workers
 */

const ADMIN_API_BASE = 'https://analyticsadmin.googleapis.com/v1beta';
const DATA_API_BASE = 'https://analyticsdata.googleapis.com/v1beta';

export class AnalyticsClient {
  constructor(private accessToken: string) {}

  /**
   * Make authenticated request to Google Analytics API
   */
  private async makeRequest(url: string, options: RequestInit = {}): Promise<any> {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API request failed: ${response.status} ${error}`);
    }

    return response.json();
  }

  /**
   * Get account summaries
   */
  async getAccountSummaries(): Promise<any[]> {
    const url = `${ADMIN_API_BASE}/accountSummaries`;
    const response = await this.makeRequest(url);
    return response.accountSummaries || [];
  }

  /**
   * Get property details
   */
  async getPropertyDetails(propertyId: string): Promise<any> {
    const propertyName = this.constructPropertyName(propertyId);
    const url = `${ADMIN_API_BASE}/${propertyName}`;
    return this.makeRequest(url);
  }

  /**
   * List Google Ads links
   */
  async listGoogleAdsLinks(propertyId: string): Promise<any[]> {
    const propertyName = this.constructPropertyName(propertyId);
    const url = `${ADMIN_API_BASE}/${propertyName}/googleAdsLinks`;
    const response = await this.makeRequest(url);
    return response.googleAdsLinks || [];
  }

  /**
   * Run a report
   */
  async runReport(propertyId: string, request: any): Promise<any> {
    const propertyName = this.constructPropertyName(propertyId);
    const url = `${DATA_API_BASE}/${propertyName}:runReport`;
    return this.makeRequest(url, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Run a realtime report
   */
  async runRealtimeReport(propertyId: string, request: any): Promise<any> {
    const propertyName = this.constructPropertyName(propertyId);
    const url = `${DATA_API_BASE}/${propertyName}:runRealtimeReport`;
    return this.makeRequest(url, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Get custom dimensions and metrics
   */
  async getCustomDimensionsAndMetrics(propertyId: string): Promise<any> {
    const propertyName = this.constructPropertyName(propertyId);
    
    // Fetch custom dimensions
    const dimensionsUrl = `${ADMIN_API_BASE}/${propertyName}/customDimensions`;
    const dimensionsResponse = await this.makeRequest(dimensionsUrl);
    
    // Fetch custom metrics
    const metricsUrl = `${ADMIN_API_BASE}/${propertyName}/customMetrics`;
    const metricsResponse = await this.makeRequest(metricsUrl);

    return {
      customDimensions: dimensionsResponse.customDimensions || [],
      customMetrics: metricsResponse.customMetrics || [],
    };
  }

  /**
   * Construct property name from ID
   */
  private constructPropertyName(propertyId: string): string {
    if (propertyId.startsWith('properties/')) {
      return propertyId;
    }
    return `properties/${propertyId}`;
  }
}
