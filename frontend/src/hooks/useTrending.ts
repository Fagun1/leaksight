import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useTrending(limit: number = 20) {
  return useQuery({
    queryKey: ["trending", limit],
    queryFn: () => api.getTrending(limit),
    refetchInterval: 60_000,
    staleTime: 30_000,
  });
}

export function useRumorTimeline(rumorId: string) {
  return useQuery({
    queryKey: ["rumor-timeline", rumorId],
    queryFn: () => api.getRumor(rumorId),
    enabled: !!rumorId,
  });
}
