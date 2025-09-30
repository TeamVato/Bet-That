import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
} from "recharts";
import { ResolutionAnalytics } from "@/services/api";

interface ResolutionChartProps {
  analytics: ResolutionAnalytics;
  isLoading?: boolean;
}

const COLORS = {
  win: "#10B981",
  loss: "#EF4444",
  push: "#F59E0B",
  void: "#6B7280",
};

export function ResolutionChart({ analytics, isLoading }: ResolutionChartProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  // Prepare data for outcome distribution pie chart
  const outcomeData = [
    { name: "Win", value: analytics.outcome_distribution.win, color: COLORS.win },
    { name: "Loss", value: analytics.outcome_distribution.loss, color: COLORS.loss },
    { name: "Push", value: analytics.outcome_distribution.push, color: COLORS.push },
    { name: "Void", value: analytics.outcome_distribution.void, color: COLORS.void },
  ].filter(item => item.value > 0);

  // Prepare data for most active resolvers bar chart
  const resolverData = analytics.most_active_resolvers
    .slice(0, 10)
    .map(resolver => ({
      name: resolver.user_name,
      resolutions: resolver.resolution_count,
    }));

  // Prepare data for resolution trends line chart
  const trendData = analytics.resolution_trends.map(trend => ({
    date: new Date(trend.date).toLocaleDateString("en-US", { 
      month: "short", 
      day: "numeric" 
    }),
    resolutions: trend.resolutions_count,
    avgTime: trend.average_time_hours,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Outcome Distribution Pie Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Outcome Distribution
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={outcomeData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {outcomeData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Most Active Resolvers Bar Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Most Active Resolvers
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={resolverData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="name" 
              angle={-45}
              textAnchor="end"
              height={80}
              fontSize={12}
            />
            <YAxis />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="resolutions" fill="#3B82F6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Resolution Trends Line Chart */}
      <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Resolution Trends
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar yAxisId="left" dataKey="resolutions" fill="#3B82F6" name="Resolutions" />
            <Line 
              yAxisId="right" 
              type="monotone" 
              dataKey="avgTime" 
              stroke="#EF4444" 
              strokeWidth={2}
              name="Avg Time (hours)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Resolution Time Distribution */}
      <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Resolution Time Distribution
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {analytics.average_resolution_time_hours.toFixed(1)}h
            </div>
            <div className="text-sm text-gray-600">Average Resolution Time</div>
          </div>
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {analytics.average_dispute_resolution_time_hours.toFixed(1)}h
            </div>
            <div className="text-sm text-gray-600">Average Dispute Resolution</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {analytics.resolution_accuracy_percentage.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Resolution Accuracy</div>
          </div>
        </div>
      </div>
    </div>
  );
}

