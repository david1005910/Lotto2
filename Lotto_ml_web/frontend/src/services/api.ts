import axios from 'axios';
import type {
  APIResponse,
  PaginatedResults,
  LottoResult,
  Statistics,
  PredictionData,
  RecommendData,
  SystemStatus,
  SyncData,
  TrainData,
} from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 300000, // 5 minutes for long operations (full sync, training)
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Results
  results: {
    getAll: async (params?: {
      page?: number;
      limit?: number;
      sort?: 'asc' | 'desc';
      from_draw?: number;
      to_draw?: number;
    }): Promise<APIResponse<PaginatedResults>> => {
      const response = await client.get('/results', { params });
      return response.data;
    },

    getByDrawNo: async (drawNo: number): Promise<APIResponse<LottoResult>> => {
      const response = await client.get(`/results/${drawNo}`);
      return response.data;
    },
  },

  // Statistics
  statistics: {
    get: async (recent?: number): Promise<APIResponse<Statistics>> => {
      const response = await client.get('/statistics', {
        params: recent ? { recent } : undefined,
      });
      return response.data;
    },
  },

  // Predict
  predict: {
    get: async (): Promise<APIResponse<PredictionData>> => {
      const response = await client.get('/predict');
      return response.data;
    },
  },

  // Recommend
  recommend: {
    get: async (): Promise<APIResponse<RecommendData>> => {
      const response = await client.get('/recommend');
      return response.data;
    },
  },

  // Admin
  admin: {
    sync: async (): Promise<APIResponse<SyncData>> => {
      const response = await client.post('/sync');
      return response.data;
    },

    syncFull: async (): Promise<APIResponse<SyncData>> => {
      const response = await client.post('/sync/full');
      return response.data;
    },

    train: async (): Promise<APIResponse<TrainData>> => {
      const response = await client.post('/train');
      return response.data;
    },

    status: async (): Promise<APIResponse<SystemStatus>> => {
      const response = await client.get('/status');
      return response.data;
    },
  },
};

export default api;
