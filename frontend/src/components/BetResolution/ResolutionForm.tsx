import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { PlacedBet } from "@/services/api";
import { useBetResolution } from "@/hooks/useBetResolution";
import Toast from "@/components/Toast";

const ResolutionSchema = z.object({
  result: z.enum(["win", "loss", "push", "void"], {
    required_error: "Please select a result",
  }),
  resolution_notes: z.string().optional(),
  resolution_source: z.string().url("Please enter a valid URL").optional().or(z.literal("")),
});

type ResolutionFormData = z.infer<typeof ResolutionSchema>;

interface ResolutionFormProps {
  bet: PlacedBet;
  onSuccess: () => void;
  onCancel: () => void;
}

export const ResolutionForm: React.FC<ResolutionFormProps> = ({
  bet,
  onSuccess,
  onCancel,
}) => {
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  const { resolveBet, isResolving } = useBetResolution();

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<ResolutionFormData>({
    resolver: zodResolver(ResolutionSchema),
    defaultValues: {
      result: undefined,
      resolution_notes: "",
      resolution_source: "",
    },
  });

  const selectedResult = watch("result");

  const onSubmit = async (data: ResolutionFormData) => {
    try {
      await resolveBet(bet.id, {
        result: data.result,
        resolution_notes: data.resolution_notes || undefined,
        resolution_source: data.resolution_source || undefined,
      });

      setToast({
        message: "Bet resolved successfully!",
        type: "success",
      });

      // Close modal after a short delay
      setTimeout(() => {
        onSuccess();
      }, 1500);
    } catch (error) {
      setToast({
        message: error instanceof Error ? error.message : "Failed to resolve bet",
        type: "error",
      });
    }
  };

  const getResultDescription = (result: string) => {
    switch (result) {
      case "win":
        return "The bet won - payout will be processed";
      case "loss":
        return "The bet lost - stake is forfeited";
      case "push":
        return "The bet pushed - stake will be refunded";
      case "void":
        return "The bet is void - stake will be refunded";
      default:
        return "";
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Result Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Bet Result *
          </label>
          <div className="space-y-3">
            {[
              { value: "win", label: "Win", color: "text-green-600" },
              { value: "loss", label: "Loss", color: "text-red-600" },
              { value: "push", label: "Push", color: "text-yellow-600" },
              { value: "void", label: "Void", color: "text-gray-600" },
            ].map((option) => (
              <label
                key={option.value}
                className="flex items-center space-x-3 cursor-pointer"
              >
                <input
                  type="radio"
                  value={option.value}
                  {...register("result")}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span className={`text-sm font-medium ${option.color}`}>
                  {option.label}
                </span>
              </label>
            ))}
          </div>
          {errors.result && (
            <p className="mt-2 text-sm text-red-600">{errors.result.message}</p>
          )}
        </div>

        {/* Result Description */}
        {selectedResult && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-sm text-blue-800">
              {getResultDescription(selectedResult)}
            </p>
          </div>
        )}

        {/* Resolution Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Resolution Notes
          </label>
          <textarea
            {...register("resolution_notes")}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Optional notes about the resolution..."
          />
          {errors.resolution_notes && (
            <p className="mt-2 text-sm text-red-600">
              {errors.resolution_notes.message}
            </p>
          )}
        </div>

        {/* Resolution Source */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Resolution Source
          </label>
          <input
            type="url"
            {...register("resolution_source")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="https://example.com/result (optional)"
          />
          <p className="mt-1 text-xs text-gray-500">
            URL or source that confirms the result
          </p>
          {errors.resolution_source && (
            <p className="mt-2 text-sm text-red-600">
              {errors.resolution_source.message}
            </p>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-3 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            disabled={isResolving}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isResolving || !selectedResult}
            className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isResolving ? "Resolving..." : "Resolve Bet"}
          </button>
        </div>
      </form>

      {/* Toast Notification */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
};
