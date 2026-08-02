import { useQuery } from "@tanstack/react-query"
import { getStages } from "@/api/stages"

export function useStages() {
  return useQuery({
    queryKey: ["stages"],
    queryFn: getStages,
  })
}
