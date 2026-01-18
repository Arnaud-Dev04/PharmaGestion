import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useLanguage } from '../../context/LanguageContext';

export const SalesChart = ({ data }) => {
  const { t } = useLanguage();

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        Pas de données disponibles pour la période sélectionnée
      </div>
    );
  }

  // Format date for display (dd/MM)
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
  };

  // Format currency
  const formatCurrency = (value) => {
    return `F${value.toLocaleString()}`;
  };

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{
            top: 10,
            right: 10,
            left: 0,
            bottom: 0,
          }}
        >
          <defs>
            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
          <XAxis 
            dataKey="date" 
            tickFormatter={formatDate}
            tick={{ fill: '#6B7280', fontSize: 12 }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis 
            tickFormatter={(value) => `F${value}`}
            tick={{ fill: '#6B7280', fontSize: 12 }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip 
            formatter={(value) => [formatCurrency(value), t('revenue')]}
            labelFormatter={formatDate}
            contentStyle={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                borderRadius: '8px', 
                border: 'none', 
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' 
            }}
          />
          <Area
            type="monotone"
            dataKey="amount"
            stroke="#3B82F6"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorRevenue)"
            activeDot={{ r: 6, strokeWidth: 0 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
