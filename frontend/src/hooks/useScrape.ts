"use client";

import { useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export function useScrape() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const pollForResult = useCallback(async () => {
    for (let i = 0; i < 30; i++) {
      await new Promise((r) => setTimeout(r, 2000));
      try {
        const resp = await fetch(`${API_BASE}/scrape/status`);
        const status = await resp.json();
        if (!status.running && status.last_result) {
          const r = status.last_result;
          if (r.error) {
            setError(`Pipeline error: ${r.error}`);
          } else {
            setResult(
              `Done! Scraped ${r.scraped} posts, stored ${r.stored}, detected ${r.leaks} leaks`
            );
          }
          setLoading(false);
          queryClient.invalidateQueries({ queryKey: ["trending"] });
          queryClient.invalidateQueries({ queryKey: ["rumors"] });
          queryClient.invalidateQueries({ queryKey: ["posts"] });
          queryClient.invalidateQueries({ queryKey: ["stats"] });
          queryClient.invalidateQueries({ queryKey: ["velocity"] });
          queryClient.invalidateQueries({ queryKey: ["companyDist"] });
          queryClient.invalidateQueries({ queryKey: ["analytics"] });
          return;
        }
      } catch {
        // ignore poll errors
      }
    }
    setResult("Scrape is taking longer than expected. Refresh the page in a moment.");
    setLoading(false);
  }, [queryClient]);

  const runScrape = useCallback(async () => {
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const resp = await fetch(`${API_BASE}/scrape`, {
        method: "POST",
        signal: AbortSignal.timeout(60_000),
      });
      const data = await resp.json();
      if (!resp.ok) {
        setError(data.detail || data.message || "Scrape failed");
        setLoading(false);
        return;
      }
      if (data.scraped === 0) {
        setError(data.message || "No posts fetched");
        setLoading(false);
        return;
      }
      setResult(`Fetched ${data.scraped} posts. Classifying leaks...`);
      pollForResult();
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === "TimeoutError") {
        setError("Request timed out. The server may still be scraping. Refresh in a moment.");
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Scrape failed");
      }
      setLoading(false);
    }
  }, [pollForResult]);

  return { runScrape, loading, result, error };
}
