import axios from 'axios';
import { GameSnapshot, StrategicAdvice, HealthStatus } from '../types/api';

const API_BASE_URL = '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health check
  async checkHealth(): Promise<HealthStatus> {
    const response = await apiClient.get<HealthStatus>('/health');
    return response.data;
  },

  // Get strategic advice
  async getAdvice(snapshot: GameSnapshot): Promise<StrategicAdvice> {
    const response = await apiClient.post<StrategicAdvice>('/advice', snapshot);
    return response.data;
  },

  // Data ingestion endpoints
  async ingestPlayerData(puuid: string, count: number = 20) {
    const response = await apiClient.post('/data/ingest/player', null, {
      params: { puuid, count }
    });
    return response.data;
  },

  async ingestHighEloData(
    platform: string = 'na1',
    matchesPerPlayer: number = 10,
    maxPlayers: number = 50
  ) {
    const response = await apiClient.post('/data/ingest/high-elo', null, {
      params: {
        platform,
        matches_per_player: matchesPerPlayer,
        max_players: maxPlayers
      }
    });
    return response.data;
  },

  async computeStats(patch: string) {
    const response = await apiClient.post('/data/compute-stats', null, {
      params: { patch }
    });
    return response.data;
  },

  // Playbook management
  async addPlaybook(title: string, content: string, tags: string[] = []) {
    const response = await apiClient.post('/playbooks/add', null, {
      params: { title, content, tags: tags.join(',') }
    });
    return response.data;
  },

  // Query stats
  async queryCompositions(query: string, nResults: number = 5, patch?: string) {
    const response = await apiClient.get('/stats/compositions', {
      params: { query, n_results: nResults, patch }
    });
    return response.data;
  },

  async queryAugments(query: string, nResults: number = 5, patch?: string) {
    const response = await apiClient.get('/stats/augments', {
      params: { query, n_results: nResults, patch }
    });
    return response.data;
  },
};
