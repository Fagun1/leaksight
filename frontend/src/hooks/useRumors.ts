import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useRumors(params?: { page?: number; per_page?: number; min_credibility?: number }) {
  return useQuery({
    queryKey: ["rumors", params],
    queryFn: () => api.getRumors(params),
  });
}
