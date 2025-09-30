import React from "react";
import { 
  CheckCircle, 
  Clock, 
  TrendingUp, 
  Users, 
  AlertTriangle,
  Target,
  Timer
} from "lucide-react";
import { ResolutionAnalytics } from "@/services/api";

interface ResolutionStatsProps {
  analytics: ResolutionAnalytics;
  isLoading?: boolean;
}

export function ResolutionStats({ analytics, isLoading }: ResolutionStatsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  const stats = [
    {
      title: "Total Resolutions",
      value: analytics.total_resolutions.toLocaleString(),
      icon: CheckCircle,
      color: "text-green-600",
      bgColor: "bg-green-100",
    },
    {
      title: "Avg Resolution Time",
      value: `${analytics.average_resolution_time_hours.toFixed(1)}h`,
      icon: Clock,
      color: "text-blue-600",
      bgColor: "bg-blue-100",
    },
    {
      title: "Resolution Accuracy",
      value: `${analytics.resolution_accuracy_percentage.toFixed(1)}%`,
      icon: Target,
      color: "text-purple-600",
      bgColor: "bg-purple-100",
    },
    {
      title: "Dispute Rate",
      value: `${analytics.dispute_rate.toFixed(1)}%`,
      icon: AlertTriangle,
      color: "text-orange-600",
      bgColor: "bg-orange-100",
    },
    {
      title: "Avg Dispute Resolution",
      value: `${analytics.average_dispute_resolution_time_hours.toFixed(1)}h`,
      icon: Timer,
      color: "text-red-600",
      bgColor: "bg-red-100",
    },
    {
      title: "Win Rate",
      value: `${((analytics.outcome_distribution.win / analytics.total_resolutions) * 100).toFixed(1)}%`,
      icon: TrendingUp,
      color: "text-green-600",
      bgColor: "bg-green-100",
    },
    {
      title: "Loss Rate",
      value: `${((analytics.outcome_distribution.loss / analytics.total_resolutions) * 100).toFixed(1)}%`,
      icon: TrendingUp,
      color: "text-red-600",
      bgColor: "bg-red-100",
    },
    {
      title: "Active Resolvers",
      value: analytics.most_active_resolvers.length.toString(),
      icon: Users,
      color: "text-indigo-600",
      bgColor: "bg-indigo-100",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <div key={index} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className={`p-3 rounded-full ${stat.bgColor}`}>
                <Icon className={`h-6 w-6 ${stat.color}`} />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

