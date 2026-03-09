export interface TrendingRumor {
  rumor_id: string;
  title: string;
  summary: string;
  trend_score: number;
  velocity: number;
  acceleration: number;
  total_mentions: number;
  unique_sources: number;
  unique_platforms: number;
  credibility_score: number;
  first_seen: string;
  last_seen: string;
  category: string;
  entities: {
    companies: string[];
    products: string[];
    features: string[];
    timeframes: string[];
    specs: string[];
  };
}

export interface Rumor {
  _id: string;
  id?: string;
  title: string;
  summary: string;
  category: string;
  credibility_score: number;
  confidence?: number;
  grade?: string;
  status: string;
  first_seen: string;
  last_seen: string;
  last_updated?: string;
  post_ids: string[];
  source_count?: number;
  entities: { companies: string[]; products: string[]; features: string[] };
  timeline?: TimelineEvent[];
  credibility_breakdown?: Record<string, number>;
}

export interface TimelineEvent {
  type?: string;
  date?: string;
  timestamp?: string;
  source?: string;
  author?: string;
  description?: string;
  details?: string[];
  snippet?: string;
  engagement?: number;
  url?: string;
}
