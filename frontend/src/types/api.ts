export interface Champion {
  name: string;
  stars: number;
  items: string[];
  position?: Position;
}

export interface Position {
  row: number;
  col: number;
}

export interface GameSnapshot {
  set_version: string;
  stage: string;
  level: number;
  gold: number;
  health: number;
  board: Champion[];
  bench: Champion[];
  available_augments: string[];
  shop_champions: string[];
  active_traits: string[];
  context?: string;
}

export interface StrategicOption {
  rank: number;
  title: string;
  description: string;
  reasoning: string;
  key_stats: Record<string, any>;
  confidence: number;
}

export interface StrategicAdvice {
  snapshot: GameSnapshot;
  options: StrategicOption[];
  general_advice: string;
  retrieved_context: string[];
}

export interface HealthStatus {
  status: string;
  version: string;
  database_connected: boolean;
  riot_api_configured: boolean;
}
