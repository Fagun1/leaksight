import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function usePosts(params?: { page?: number; per_page?: number; platform?: string; is_leak?: boolean }) {
  return useQuery({
    queryKey: ["posts", params],
    queryFn: () => api.getPosts(params),
  });
}
