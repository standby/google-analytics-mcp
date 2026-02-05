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
 * MCP Server implementation for Google Analytics
 */

import { AnalyticsClient } from './analytics-client';

interface MCPRequest {
  jsonrpc: string;
  id: number | string;
  method: string;
  params?: any;
}

interface MCPResponse {
  jsonrpc: string;
  id: number | string;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

interface Tool {
  name: string;
  description: string;
  inputSchema: any;
}

export function createMCPServer(client: AnalyticsClient, kv: KVNamespace) {
  const tools: Tool[] = [
    {
      name: 'get_account_summaries',
      description: "Retrieves information about the user's Google Analytics accounts and properties.",
      inputSchema: {
        type: 'object',
        properties: {},
      },
    },
    {
      name: 'get_property_details',
      description: 'Returns details about a property.',
      inputSchema: {
        type: 'object',
        properties: {
          property_id: {
            type: 'string',
            description: 'The Google Analytics property ID (number or properties/NUMBER format)',
          },
        },
        required: ['property_id'],
      },
    },
    {
      name: 'list_google_ads_links',
      description: 'Returns a list of links to Google Ads accounts for a property.',
      inputSchema: {
        type: 'object',
        properties: {
          property_id: {
            type: 'string',
            description: 'The Google Analytics property ID (number or properties/NUMBER format)',
          },
        },
        required: ['property_id'],
      },
    },
    {
      name: 'run_report',
      description: 'Runs a Google Analytics report using the Data API.',
      inputSchema: {
        type: 'object',
        properties: {
          property_id: {
            type: 'string',
            description: 'The Google Analytics property ID',
          },
          dimensions: {
            type: 'array',
            items: { type: 'string' },
            description: 'Dimensions to include in the report',
          },
          metrics: {
            type: 'array',
            items: { type: 'string' },
            description: 'Metrics to include in the report',
          },
          date_ranges: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                start_date: { type: 'string' },
                end_date: { type: 'string' },
              },
            },
            description: 'Date ranges for the report',
          },
        },
        required: ['property_id', 'metrics'],
      },
    },
    {
      name: 'run_realtime_report',
      description: 'Runs a Google Analytics realtime report using the Data API.',
      inputSchema: {
        type: 'object',
        properties: {
          property_id: {
            type: 'string',
            description: 'The Google Analytics property ID',
          },
          dimensions: {
            type: 'array',
            items: { type: 'string' },
            description: 'Dimensions to include in the report',
          },
          metrics: {
            type: 'array',
            items: { type: 'string' },
            description: 'Metrics to include in the report',
          },
        },
        required: ['property_id', 'metrics'],
      },
    },
    {
      name: 'get_custom_dimensions_and_metrics',
      description: 'Retrieves the custom dimensions and metrics for a specific property.',
      inputSchema: {
        type: 'object',
        properties: {
          property_id: {
            type: 'string',
            description: 'The Google Analytics property ID',
          },
        },
        required: ['property_id'],
      },
    },
  ];

  async function handleRequest(request: MCPRequest): Promise<MCPResponse> {
    const { jsonrpc, id, method, params } = request;

    try {
      switch (method) {
        case 'initialize':
          return {
            jsonrpc: '2.0',
            id,
            result: {
              protocolVersion: '2024-11-05',
              serverInfo: {
                name: 'Google Analytics MCP Server (Cloudflare)',
                version: '0.1.0',
              },
              capabilities: {
                tools: {},
              },
            },
          };

        case 'tools/list':
          return {
            jsonrpc: '2.0',
            id,
            result: {
              tools,
            },
          };

        case 'tools/call':
          return await handleToolCall(params, id);

        default:
          return {
            jsonrpc: '2.0',
            id,
            error: {
              code: -32601,
              message: `Method not found: ${method}`,
            },
          };
      }
    } catch (error: any) {
      return {
        jsonrpc: '2.0',
        id,
        error: {
          code: -32603,
          message: error.message || 'Internal error',
          data: error.stack,
        },
      };
    }
  }

  async function handleToolCall(params: any, id: number | string): Promise<MCPResponse> {
    const { name, arguments: args } = params;

    try {
      let result: any;

      switch (name) {
        case 'get_account_summaries':
          result = await client.getAccountSummaries();
          break;

        case 'get_property_details':
          result = await client.getPropertyDetails(args.property_id);
          break;

        case 'list_google_ads_links':
          result = await client.listGoogleAdsLinks(args.property_id);
          break;

        case 'run_report':
          const reportRequest = {
            dimensions: args.dimensions?.map((d: string) => ({ name: d })),
            metrics: args.metrics.map((m: string) => ({ name: m })),
            dateRanges: args.date_ranges?.map((dr: any) => ({
              startDate: dr.start_date,
              endDate: dr.end_date,
            })) || [{ startDate: '30daysAgo', endDate: 'today' }],
          };
          result = await client.runReport(args.property_id, reportRequest);
          break;

        case 'run_realtime_report':
          const realtimeRequest = {
            dimensions: args.dimensions?.map((d: string) => ({ name: d })),
            metrics: args.metrics.map((m: string) => ({ name: m })),
          };
          result = await client.runRealtimeReport(args.property_id, realtimeRequest);
          break;

        case 'get_custom_dimensions_and_metrics':
          result = await client.getCustomDimensionsAndMetrics(args.property_id);
          break;

        default:
          return {
            jsonrpc: '2.0',
            id,
            error: {
              code: -32602,
              message: `Unknown tool: ${name}`,
            },
          };
      }

      return {
        jsonrpc: '2.0',
        id,
        result: {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        },
      };
    } catch (error: any) {
      return {
        jsonrpc: '2.0',
        id,
        error: {
          code: -32603,
          message: `Tool execution failed: ${error.message}`,
          data: error.stack,
        },
      };
    }
  }

  return {
    handleRequest,
  };
}
