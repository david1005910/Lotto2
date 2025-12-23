// API Response wrapper
export interface APIResponse<T> {
  status: 'success' | 'error';
  data: T;
  message?: string;
}

// Lotto Result
export interface LottoResult {
  draw_no: number;
  draw_date: string;
  numbers: number[];
  bonus: number;
  prize_1st?: number;
}

// Pagination
export interface Pagination {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
}

export interface PaginatedResults {
  results: LottoResult[];
  pagination: Pagination;
}

// Statistics
export interface SumDistribution {
  ranges: string[];
  counts: number[];
}

export interface ConsecutiveStats {
  has_consecutive: number;
  no_consecutive: number;
}

export interface SectionStats {
  avg: number;
  distribution: Record<string, number>;
}

export interface Statistics {
  number_frequency: Record<string, number>;
  odd_even_distribution: Record<string, number>;
  sum_distribution: SumDistribution;
  consecutive_stats: ConsecutiveStats;
  section_distribution: {
    low_1_15: SectionStats;
    mid_16_30: SectionStats;
    high_31_45: SectionStats;
  };
  total_draws: number;
}

// Prediction
export interface ModelPrediction {
  numbers: number[];
  accuracy: number;
}

export interface PredictionData {
  predictions: {
    random_forest: ModelPrediction;
    gradient_boosting: ModelPrediction;
    neural_network: ModelPrediction;
  };
  disclaimer: string;
  last_trained?: string;
}

// Recommendation
export interface Recommendation {
  numbers: number[];
  description: string;
}

export interface RecommendData {
  recommendations: {
    high_frequency: Recommendation;
    low_frequency: Recommendation;
    balanced_odd_even: Recommendation;
    section_spread: Recommendation;
    optimal_sum: Recommendation;
  };
}

// Status
export interface DatabaseStatus {
  total_draws: number;
  latest_draw?: number;
  latest_date?: string;
}

export interface MLModelStatus {
  trained: boolean;
  last_trained?: string;
  models_available: string[];
}

export interface SystemStatus {
  database: DatabaseStatus;
  ml_models: MLModelStatus;
  last_sync?: string;
}

// Sync Response
export interface SyncData {
  synced_count: number;
  latest_draw: number;
}

// Train Response
export interface ModelTrainResult {
  train_accuracy: number;
  test_accuracy: number;
  trained: boolean;
}

export interface TrainData {
  models: Record<string, ModelTrainResult>;
  trained_at: string;
  training_samples: number;
  test_samples: number;
}
