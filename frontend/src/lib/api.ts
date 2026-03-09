const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface ApiResponse<T> {
  data: T;
  total?: number;
  page?: number;
  per_page?: number;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: { "Content-Type": "application/json", ...options.headers },
      ...options,
    });
    if (!response.ok) {
      let msg = `${response.status} ${response.statusText}`;
      try {
        const errData = await response.json();
        msg = errData.detail || errData.message || (typeof errData === "string" ? errData : msg);
      } catch {
        // ignore
      }
      throw new Error(msg);
    }
    return response.json();
  }

  async getRumors(params?: { page?: number; per_page?: number; min_credibility?: number; category?: string; company?: string }) {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) searchParams.set(key, String(value));
      });
    }
    return this.request<ApiResponse<any[]>>(`/rumors?${searchParams.toString()}`);
  }

  async getRumor(id: string) {
    return this.request<any>(`/rumors/${id}`);
  }

  async getTrending(limit: number = 20) {
    return this.request<any>(`/trending?limit=${limit}`);
  }

  async getPosts(params?: { page?: number; per_page?: number; platform?: string; is_leak?: boolean }) {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) searchParams.set(key, String(value));
      });
    }
    return this.request<ApiResponse<any[]>>(`/posts?${searchParams.toString()}`);
  }

  async getEntities(type?: string, limit: number = 50) {
    const params = new URLSearchParams({ limit: String(limit) });
    if (type) params.set("type", type);
    return this.request<any>(`/entities?${params.toString()}`);
  }

  async getSources(limit: number = 20) {
    return this.request<any>(`/sources?limit=${limit}`);
  }

  async getAlerts() {
    return this.request<any>(`/alerts`);
  }

  async runScrape() {
    return this.request<any>(`/scrape`, { method: "POST" });
  }

  async getAnalyticsVelocity(days: number = 30, company?: string) {
    const params = new URLSearchParams({ days: String(days) });
    if (company) params.set("company", company);
    return this.request<{ data: { date: string; total: number }[] }>(`/analytics/velocity?${params}`);
  }

  async getCompanyDistribution() {
    return this.request<{ data: { company: string; count: number; avg_confidence: number }[] }>("/analytics/company-distribution");
  }

  async getCategoryDistribution() {
    return this.request<{ data: { category: string; count: number; percentage: number }[] }>("/analytics/category-distribution");
  }

  async getRumorSpread(rumorId: string) {
    return this.request<{ data: { date: string; cumulative_sources: number; platforms: Record<string, number> }[] }>(`/analytics/rumor/${rumorId}/spread`);
  }

  async getSeeds() {
    return this.request<any>("/seeds");
  }

  async addSeed(body: { url: string; domain: string; category?: string; priority?: number }) {
    return this.request<any>("/seeds", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }
}

export const api = new ApiClient(API_BASE);
