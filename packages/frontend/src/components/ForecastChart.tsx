/**
 * Forecast Chart Component
 * Line chart for demand predictions
 */

import React from 'react';
import { XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { format } from 'date-fns';

interface DailyPrediction {
  date: string;
  demandForecast: number;
  lowerBound: number;
  upperBound: number;
  festivalMultiplier?: number;
}

interface ForecastChartProps {
  predictions: DailyPrediction[];
  title?: string;
}

const ForecastChart: React.FC<ForecastChartProps> = ({ predictions, title = 'Demand Forecast' }) => {
  const chartData = predictions.map(p => ({
    date: format(new Date(p.date), 'MMM dd'),
    forecast: Math.round(p.demandForecast),
    lower: Math.round(p.lowerBound),
    upper: Math.round(p.upperBound),
  }));

  return (
    <div style={{ width: '100%', backgroundColor: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
      <h3 style={{ marginBottom: '1rem' }}>{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Area
            type="monotone"
            dataKey="upper"
            stackId="1"
            stroke="#82ca9d"
            fill="#82ca9d"
            fillOpacity={0.2}
            name="Upper Bound"
          />
          <Area
            type="monotone"
            dataKey="forecast"
            stackId="2"
            stroke="#1a73e8"
            fill="#1a73e8"
            fillOpacity={0.6}
            name="Forecast"
          />
          <Area
            type="monotone"
            dataKey="lower"
            stackId="3"
            stroke="#ff7300"
            fill="#ff7300"
            fillOpacity={0.2}
            name="Lower Bound"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ForecastChart;
