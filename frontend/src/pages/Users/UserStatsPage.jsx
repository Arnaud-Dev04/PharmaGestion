import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ShoppingCart, DollarSign, Users, TrendingUp, Package } from 'lucide-react';
import userService from '../../services/userService';
import { SalesChart } from '../../components/dashboard/SalesChart';
import { UserStatusBadge } from '../../components/users/UserStatusBadge';

export const UserStatsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [days, setDays] = useState(30);

  // Calculate date range
  const endDate = new Date().toISOString().split('T')[0];
  const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

  // Fetch user stats
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['userStats', id, days],
    queryFn: () => userService.getSalesStats(id, startDate, endDate),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Chargement...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-600 dark:text-red-400 py-8">
        Erreur de chargement des statistiques
      </div>
    );
  }

  // Prepare chart data
  const chartData = stats?.sales_by_date?.map(item => ({
    date: item.date,
    revenue: item.revenue || 0
  })) || [];

  return (
    <div className="space-y-6">
      {/* Back Button & Header */}
      <div>
        <button
          onClick={() => navigate('/users')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          Retour aux utilisateurs
        </button>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary font-bold text-2xl">
              {stats?.username?.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats?.username}
              </h1>
              <p className="text-gray-600 dark:text-gray-400">Statistiques de vente</p>
            </div>
          </div>

          {/* Period Selector */}
          <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setDays(7)}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                days === 7
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
              }`}
            >
              7 jours
            </button>
            <button
              onClick={() => setDays(30)}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                days === 30
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
              }`}
            >
              30 jours
            </button>
            <button
              onClick={() => setDays(90)}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                days === 90
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
              }`}
            >
              90 jours
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Sales */}
        <div className="card p-5">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                Nombre de Ventes
              </p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {stats?.total_sales || 0}
              </p>
            </div>
            <div className="bg-blue-500 text-white p-3 rounded-xl">
              <ShoppingCart className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Total Revenue */}
        <div className="card p-5">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                Revenu Généré
              </p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                F{stats?.total_revenue?.toFixed(0) || 0}
              </p>
            </div>
            <div className="bg-green-500 text-white p-3 rounded-xl">
              <DollarSign className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Average Sale */}
        <div className="card p-5">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                Ticket Moyen
              </p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                F{stats?.average_sale_amount?.toFixed(0) || 0}
              </p>
            </div>
            <div className="bg-purple-500 text-white p-3 rounded-xl">
              <TrendingUp className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Customers Served */}
        <div className="card p-5">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                Clients Servis
              </p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {stats?.customers_served || 0}
              </p>
            </div>
            <div className="bg-orange-500 text-white p-3 rounded-xl">
              <Users className="w-6 h-6" />
            </div>
          </div>
        </div>
      </div>

      {/* Revenue Chart */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-6">
          <TrendingUp className="w-5 h-5 text-primary" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Évolution des Ventes ({days} derniers jours)
          </h2>
        </div>
        <SalesChart data={chartData} />
      </div>

      {/* Top Products Sold */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <Package className="w-5 h-5 text-success" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Top 10 Produits Vendus
          </h2>
        </div>

        {stats?.top_products && stats.top_products.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                    #
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                    Nom
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                    Code
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                    Quantité Vendue
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                    Revenu Généré
                  </th>
                </tr>
              </thead>
              <tbody>
                {stats.top_products.map((product, index) => (
                  <tr key={product.medicine_id} className="border-b border-border hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="py-3 px-4 text-sm font-bold text-gray-900 dark:text-white">
                      {index + 1}
                    </td>
                    <td className="py-3 px-4 text-sm font-medium text-gray-900 dark:text-white">
                      {product.medicine_name}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                      {product.medicine_code}
                    </td>
                    <td className="py-3 px-4 text-sm text-right font-semibold text-blue-600 dark:text-blue-400">
                      {product.quantity_sold}
                    </td>
                    <td className="py-3 px-4 text-sm text-right font-semibold text-success">
                      F{product.revenue_generated?.toFixed(0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">Aucune vente pour cette période</p>
          </div>
        )}
      </div>
    </div>
  );
};
