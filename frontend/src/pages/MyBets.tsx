import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useCreateBet, useMyBets } from "@/hooks/useBets";
import Toast from "@/components/Toast";
import { useState, useEffect } from "react";
import {
  BETA_VIEW_ONLY,
  BETA_DISCLAIMER,
  BETA_WARNING_TITLE,
} from "@/config/beta";
import { BetList } from "@/components/BetCard";
import { useRealTimeUpdates, BetResolutionUpdate } from "@/hooks/useRealTimeUpdates";
import { useToastNotifications, createBetResolutionNotification } from "@/components/Notifications/ToastNotification";
import { PlacedBet } from "@/services/api";

const BetSchema = z.object({
  game_id: z.string().min(3),
  market: z.enum(["spread", "total", "moneyline"]),
  selection: z.string().min(2),
  stake: z.number().min(1),
  odds: z.number().min(1.01),
});

type BetForm = z.infer<typeof BetSchema>;

export default function MyBets() {
  const viewOnly = BETA_VIEW_ONLY;
  const safetyNotice = BETA_DISCLAIMER;
  const bannerTitle = BETA_WARNING_TITLE;
  const { data: bets, refetch } = useMyBets();
  const createBet = useCreateBet();
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);
  
  // Real-time updates
  const { notifications, addNotification, removeNotification } = useToastNotifications();
  const [localBets, setLocalBets] = useState<PlacedBet[]>(bets?.bets || []);
  
  // Handle real-time bet updates
  const handleBetUpdate = (update: BetResolutionUpdate) => {
    // Update local bets state
    setLocalBets(prev => prev.map(bet => 
      bet.id === update.data.bet_id 
        ? { ...bet, status: update.data.status, settled_at: update.data.updated_at }
        : bet
    ));
    
    // Show toast notification
    const notification = createBetResolutionNotification(update);
    addNotification(notification);
    
    // Refetch data to ensure consistency
    refetch();
  };
  
  // Use real-time updates
  const { isConnected } = useRealTimeUpdates(undefined, handleBetUpdate);
  
  // Update local bets when data changes
  useEffect(() => {
    if (bets?.bets) {
      setLocalBets(bets.bets);
    }
  }, [bets]);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<BetForm>({
    resolver: zodResolver(BetSchema),
    defaultValues: {
      market: "spread",
      selection: "HOME",
      stake: 50,
      odds: 1.91,
    },
  });

  const onSubmit = (values: BetForm) => {
    if (viewOnly) {
      setToast({
        message:
          "Bet creation is disabled while we are in beta view-only mode.",
        type: "error",
      });
      return;
    }

    createBet.mutate(values, {
      onSuccess: () => {
        setToast({ message: "Bet created", type: "success" });
        reset();
      },
      onError: (err: any) => {
        setToast({ message: err?.message || "Error", type: "error" });
      },
    });
  };

  return (
    <section className="space-y-6">
      {/* Toast Notifications */}
      {notifications.length > 0 && (
        <div className="fixed right-4 top-4 z-50 space-y-2">
          {notifications.map((notification) => (
            <div
              key={notification.id}
              className="max-w-sm w-full bg-white rounded-lg border border-gray-200 p-4 shadow-lg"
            >
              <div className="flex items-start">
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-gray-900">
                    {notification.title}
                  </h4>
                  <p className="mt-1 text-sm text-gray-600">
                    {notification.message}
                  </p>
                  {notification.action && (
                    <div className="mt-3">
                      <button
                        onClick={notification.action.onClick}
                        className="text-sm font-medium text-blue-600 hover:text-blue-500"
                      >
                        {notification.action.label}
                      </button>
                    </div>
                  )}
                </div>
                <button
                  onClick={() => removeNotification(notification.id)}
                  className="ml-4 text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      
      <h1 className="text-xl font-semibold">My Bets</h1>

      {viewOnly && (
        <div
          className="card border-l-4 border-yellow-500 bg-yellow-50 p-4 text-yellow-800"
          role="alert"
        >
          <h2 className="font-semibold text-yellow-900">{bannerTitle}</h2>
          <p className="mt-2 text-sm">{safetyNotice}</p>
          <p className="mt-2 text-xs text-yellow-700">
            Bet creation is disabled while we verify data quality.
          </p>
        </div>
      )}

      <div className="card p-4">
        <form onSubmit={handleSubmit(onSubmit)}>
          <fieldset
            disabled={viewOnly}
            className="grid grid-cols-1 md:grid-cols-6 gap-3"
          >
            <div className="md:col-span-2">
              <label className="text-sm">Game ID</label>
              <input
                className="input"
                {...register("game_id")}
                placeholder="NE@DEN-2025-10-05"
              />
              {errors.game_id && (
                <p className="text-xs text-red-600">{errors.game_id.message}</p>
              )}
            </div>
            <div>
              <label className="text-sm">Market</label>
              <select
                className="select"
                {...register("market")}
                defaultValue="spread"
              >
                <option value="spread">spread</option>
                <option value="total">total</option>
                <option value="moneyline">moneyline</option>
              </select>
            </div>
            <div>
              <label className="text-sm">Selection</label>
              <select
                className="select"
                {...register("selection")}
                defaultValue="HOME"
              >
                <option value="HOME">HOME</option>
                <option value="AWAY">AWAY</option>
                <option value="Over">Over</option>
                <option value="Under">Under</option>
              </select>
            </div>
            <div>
              <label className="text-sm">Stake</label>
              <input
                type="number"
                step="1"
                className="input"
                {...register("stake", { valueAsNumber: true })}
              />
              {errors.stake && (
                <p className="text-xs text-red-600">{errors.stake.message}</p>
              )}
            </div>
            <div>
              <label className="text-sm">Odds (decimal)</label>
              <input
                type="number"
                step="0.01"
                className="input"
                {...register("odds", { valueAsNumber: true })}
              />
              {errors.odds && (
                <p className="text-xs text-red-600">{errors.odds.message}</p>
              )}
            </div>
            <div className="md:col-span-6 flex items-end justify-end">
              <button className="btn" type="submit">
                Create Bet
              </button>
            </div>
          </fieldset>
        </form>
      </div>

      <div className="card p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-medium">My Bets</h2>
          <div className="flex items-center space-x-2">
            <div className={`
              px-2 py-1 rounded-full text-xs font-medium
              ${isConnected 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
              }
            `}>
              {isConnected ? '🟢 Live' : '🔴 Offline'}
            </div>
            <span className="text-sm text-gray-600">
              {localBets.length} bet{localBets.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
        
        {localBets.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-600">No bets yet.</p>
            <p className="text-sm text-gray-500 mt-1">Create your first bet above!</p>
          </div>
        ) : (
          <BetList 
            bets={localBets} 
            onBetUpdate={(updatedBet) => {
              setLocalBets(prev => prev.map(bet => 
                bet.id === updatedBet.id ? updatedBet : bet
              ));
            }}
            showFilters={true}
          />
        )}
      </div>
    </section>
  );
}
