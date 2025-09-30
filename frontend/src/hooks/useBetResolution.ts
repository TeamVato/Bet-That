import { useState } from "react";
import { 
  api, 
  BetResolveRequest, 
  BetDisputeRequest, 
  BetResolutionHistory, 
  BetResolutionHistoryResponse 
} from "@/services/api";

// Re-export types from API service
export type { BetResolveRequest, BetDisputeRequest, BetResolutionHistory, BetResolutionHistoryResponse };

export function useBetResolution() {
  const [isResolving, setIsResolving] = useState(false);
  const [isDisputing, setIsDisputing] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  const resolveBet = async (betId: string, request: BetResolveRequest) => {
    setIsResolving(true);
    try {
      return await api.resolveBet(betId, request);
    } finally {
      setIsResolving(false);
    }
  };

  const disputeBet = async (betId: string, request: BetDisputeRequest) => {
    setIsDisputing(true);
    try {
      return await api.disputeBet(betId, request);
    } finally {
      setIsDisputing(false);
    }
  };

  const getResolutionHistory = async (
    betId: string,
    page: number = 1,
    perPage: number = 10
  ): Promise<BetResolutionHistoryResponse> => {
    setIsLoadingHistory(true);
    try {
      return await api.getBetResolutionHistory(betId, page, perPage);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const getPendingResolutionBets = async (
    page: number = 1,
    perPage: number = 20
  ) => {
    return await api.getPendingResolutionBets(page, perPage);
  };

  const resolveDispute = async (
    betId: string,
    result: "win" | "loss" | "push" | "void",
    resolutionNotes?: string
  ) => {
    setIsResolving(true);
    try {
      return await api.resolveDispute(betId, result, resolutionNotes);
    } finally {
      setIsResolving(false);
    }
  };

  return {
    resolveBet,
    disputeBet,
    getResolutionHistory,
    getPendingResolutionBets,
    resolveDispute,
    isResolving,
    isDisputing,
    isLoadingHistory,
  };
}
