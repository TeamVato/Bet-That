import { useQuery } from "@tanstack/react-query";
import { api } from "@/utils/api";

export function useOddsBest(market?: string) {
  return useQuery({
    queryKey: ["odds", "best", market || "all"],
    queryFn: () => api.oddsBest(market),
    refetchInterval: 15000,
  });
}
