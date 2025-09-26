import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/utils/api'

export function useMyBets(){
  return useQuery({ queryKey:['me','bets'], queryFn: api.myBets })
}

export function useCreateBet(){
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.createBet,
    onSuccess: () => { qc.invalidateQueries({ queryKey:['me','bets'] }) }
  })
}
