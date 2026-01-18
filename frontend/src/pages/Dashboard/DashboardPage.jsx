import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Package, ShoppingCart, Truck, AlertTriangle, AlertCircle, DollarSign, TrendingUp, Calendar, XCircle } from 'lucide-react';
import { StatsCard } from '../../components/dashboard/StatsCard';
import { SalesChart } from '../../components/dashboard/SalesChart';
import { DetailModal } from '../../components/dashboard/DetailModal';
import dashboardService from '../../services/dashboardService';

import { useLanguage } from '../../context/LanguageContext';

export const DashboardPage = () => {
  const { t } = useLanguage();
  const [period, setPeriod] = useState(7);
  const [activeModal, setActiveModal] = useState(null);

  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboardStats', period],

    queryFn: () => dashboardService.getDashboardStats(period),
  });

  const { data: cancelledSales, isLoading: loadingCancelled } = useQuery({
    queryKey: ['cancelledSales'],
    queryFn: dashboardService.getCancelledSales,
    enabled: activeModal === 'cancelledSales',
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">{t('loading')}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <AlertCircle className="w-16 h-16 text-danger mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{t('loadingError')}</h3>
          <p className="text-gray-600 dark:text-gray-400">
            {t('loadingErrorMessage')}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('dashboard')}</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">{t('overview')}</p>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatsCard
          icon={Package}
          label={t('totalSales')}
          value={stats?.total_medicines || 0}
          iconBgColor="bg-blue-500"
          iconColor="text-white"
          onClick={() => setActiveModal('totalSales')}
        />
        <StatsCard
          icon={ShoppingCart}
          label={t('revenue')}
          value={stats?.weekly_sales || 0}
          iconBgColor="bg-success"
          iconColor="text-white"
          onClick={() => setActiveModal('weeklySales')}
        />
        <StatsCard
          icon={Truck}
          label={t('suppliers')}
          value={stats?.total_suppliers || 1}
          iconBgColor="bg-purple-500"
          iconColor="text-white"
          onClick={() => setActiveModal('suppliers')}
        />
        <StatsCard
          icon={AlertTriangle}
          label={t('expiringSoon')}
          value={stats?.expired_medicines || 0}
          iconBgColor="bg-warning"
          iconColor="text-white"
          onClick={() => setActiveModal('expiringSoon')}
        />
        <StatsCard
          icon={AlertCircle}
          label={t('lowStock')}
          value={stats?.low_stock_medicines || 0}
          iconBgColor="bg-danger"
          iconColor="text-white"
          onClick={() => setActiveModal('lowStock')}
        />
        <StatsCard
          icon={DollarSign}
          label={t('totalRevenue')}
          value={`F${stats?.total_revenue?.toFixed(2) || '0.00'}`}
          iconBgColor="bg-teal-500"
          iconColor="text-white"
          onClick={() => setActiveModal('totalRevenue')}
        />
        <StatsCard
          icon={XCircle}
          label={t('cancelledSales')}
          value={stats?.cancelled_sales || 0}
          iconBgColor="bg-red-500"
          iconColor="text-white"
          onClick={() => setActiveModal('cancelledSales')}
        />
      </div>
    
      {/* Revenue Chart Section */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              {t('revenue')} ({period} {t('days')})
            </h2>
          </div>
          
          <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setPeriod(7)}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                period === 7
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
              }`}
            >
              7 {t('days')}
            </button>
            <button
              onClick={() => setPeriod(30)}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                period === 30
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
              }`}
            >
              30 {t('days')}
            </button>
            <button
              onClick={() => setPeriod(90)}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                period === 90
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
              }`}
            >
              90 {t('days')}
            </button>
          </div>
        </div>
        
        <SalesChart data={stats?.revenue_chart || []} />
      </div>

      {/* Recent Sales Section */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{t('recentSales')}</h2>
          <a href="/sales-history" className="text-sm text-primary hover:text-primary-600 font-medium">
            {t('actions')} →
          </a>
        </div>

        {stats?.recent_sales && stats.recent_sales.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('date')}</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('price')}</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_sales.map((sale) => (
                  <tr key={sale.code} className="border-b border-border hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                      {new Date(sale.date).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-3 px-4 text-sm font-semibold text-right text-success">
                      F{sale.total_amount?.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-center text-gray-500 dark:text-gray-400 py-8">{t('noRecentSales')}</p>
        )}
      </div>

      {/* Top Selling Products Section */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-success" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{t('topSellingProducts')}</h2>
        </div>

        {stats?.top_selling_products && stats.top_selling_products.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('name')}</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('code')}</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('soldQuantity')}</th>
                </tr>
              </thead>
              <tbody>
                {stats.top_selling_products.map((product) => (
                  <tr key={product.id} className="border-b border-border hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="py-3 px-4 text-sm font-medium text-gray-900 dark:text-white">{product.name}</td>
                    <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{product.code}</td>
                    <td className="py-3 px-4 text-sm text-right font-semibold text-success">
                      {product.total_sold}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-center text-gray-500 dark:text-gray-400 py-8">{t('noSalesData')}</p>
        )}
      </div>

      {/* Expiring Medicines Section */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-5 h-5 text-warning" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{t('expiringSoon')}</h2>
        </div>

        {stats?.expiring_soon && stats.expiring_soon.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('name')}</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('code')}</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('expiryDate')}</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('quantity')}</th>
                </tr>
              </thead>
              <tbody>
                {stats.expiring_soon.map((medicine) => (
                  <tr key={medicine.code} className="border-b border-border hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="py-3 px-4 text-sm font-medium text-gray-900 dark:text-white">{medicine.name}</td>
                    <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{medicine.code}</td>
                    <td className="py-3 px-4 text-sm text-warning font-medium">
                      {new Date(medicine.expiry_date).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="py-3 px-4 text-sm text-right text-gray-900 dark:text-white">{medicine.quantity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">{t('noMedicinesExpiring')}</p>
          </div>
        )}
      </div>

      {/* Modals for detailed views */}
      
      {/* Modal: Ventes Totales */}
      <DetailModal
        isOpen={activeModal === 'totalSales'}
        onClose={() => setActiveModal(null)}
        title={t('totalSales')}
        icon={Package}
        iconColor="text-blue-500"
      >
        <div className="space-y-4">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">{t('totalMedicinesInStock')}</p>
            <p className="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-2">
              {stats?.total_medicines || 0}
            </p>
          </div>
          {stats?.top_selling_products && stats.top_selling_products.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3">{t('topSellingProductsTitle')}</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('name')}</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('code')}</th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('soldQuantity')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.top_selling_products.map((product) => (
                      <tr key={product.id} className="border-b border-border hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <td className="py-3 px-4 text-sm font-medium text-gray-900 dark:text-white">{product.name}</td>
                        <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{product.code}</td>
                        <td className="py-3 px-4 text-sm text-right font-semibold text-success">
                          {product.total_sold}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </DetailModal>

      {/* Modal: Ventes Hebdomadaires */}
      <DetailModal
        isOpen={activeModal === 'weeklySales'}
        onClose={() => setActiveModal(null)}
        title={t('weeklySales')}
        icon={ShoppingCart}
        iconColor="text-green-500"
      >
        <div className="space-y-4">
          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">{t('totalWeeklySales')}</p>
            <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">
              {stats?.weekly_sales || 0}
            </p>
          </div>
          {stats?.recent_sales && stats.recent_sales.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3">{t('recentSalesTitle')}</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('date')}</th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('amount')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.recent_sales.map((sale) => (
                      <tr key={sale.code} className="border-b border-border hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                          {new Date(sale.date).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                        </td>
                        <td className="py-3 px-4 text-sm font-semibold text-right text-success">
                          F{sale.total_amount?.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </DetailModal>

      {/* Modal: Fournisseurs */}
      <DetailModal
        isOpen={activeModal === 'suppliers'}
        onClose={() => setActiveModal(null)}
        title={t('suppliers')}
        icon={Truck}
        iconColor="text-purple-500"
      >
        <div className="space-y-4">
          <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">{t('totalSuppliers')}</p>
            <p className="text-3xl font-bold text-purple-600 dark:text-purple-400 mt-2">
              {stats?.total_suppliers || 0}
            </p>
          </div>
          <div className="text-center py-8">
            <p className="text-gray-600 dark:text-gray-400">
              {t('viewSuppliers')}{' '}
              <a href="/suppliers" className="text-purple-600 dark:text-purple-400 hover:underline font-medium">
                {t('suppliersPage')}
              </a>
            </p>
          </div>
        </div>
      </DetailModal>

      {/* Modal: Produits Bientôt Périmés */}
      <DetailModal
        isOpen={activeModal === 'expiringSoon'}
        onClose={() => setActiveModal(null)}
        title={t('expiringSoon')}
        icon={AlertTriangle}
        iconColor="text-warning"
      >
        <div className="space-y-4">
          <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg border border-orange-200 dark:border-orange-800">
            <p className="text-sm text-gray-600 dark:text-gray-400">{t('expiringIn30Days')}</p>
            <p className="text-3xl font-bold text-warning mt-2">
              {stats?.expired_medicines || 0}
            </p>
          </div>
          {stats?.expiring_soon && stats.expiring_soon.length > 0 ? (
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3">{t('productsList')}</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('name')}</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('code')}</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('expirationDate')}</th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('quantity')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.expiring_soon.map((medicine) => (
                      <tr key={medicine.code} className="border-b border-border hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <td className="py-3 px-4 text-sm font-medium text-gray-900 dark:text-white">{medicine.name}</td>
                        <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{medicine.code}</td>
                        <td className="py-3 px-4 text-sm text-warning font-medium">
                          {new Date(medicine.expiry_date).toLocaleDateString('fr-FR')}
                        </td>
                        <td className="py-3 px-4 text-sm text-right text-gray-900 dark:text-white">{medicine.quantity}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500 dark:text-gray-400">{t('noProductsExpiring')}</p>
            </div>
          )}
        </div>
      </DetailModal>

      {/* Modal: Stock Faible */}
      <DetailModal
        isOpen={activeModal === 'lowStock'}
        onClose={() => setActiveModal(null)}
        title={t('lowStock')}
        icon={AlertCircle}
        iconColor="text-danger"
      >
        <div className="space-y-4">
          <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
            <p className="text-sm text-gray-600 dark:text-gray-400">{t('lowStockProducts')}</p>
            <p className="text-3xl font-bold text-danger mt-2">
              {stats?.low_stock_medicines || 0}
            </p>
          </div>
          <div className="text-center py-8">
            <p className="text-gray-600 dark:text-gray-400">
              {t('viewStockPage')}{' '}
              <a href="/stock" className="text-danger hover:underline font-medium">
                {t('stockPage')}
              </a>
            </p>
          </div>
        </div>
      </DetailModal>

      {/* Modal: Revenus */}
      <DetailModal
        isOpen={activeModal === 'totalRevenue'}
        onClose={() => setActiveModal(null)}
        title={t('totalRevenue')}
        icon={DollarSign}
        iconColor="text-teal-500"
      >
        <div className="space-y-4">
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">{t('totalRevenueAmount')}</p>
            <p className="text-3xl font-bold text-teal-600 dark:text-teal-400 mt-2">
              F{stats?.total_revenue?.toFixed(2) || '0.00'}
            </p>
          </div>
          {stats?.revenue_chart && stats.revenue_chart.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3">{t('revenueEvolution')}</h3>
              <SalesChart data={stats.revenue_chart} />
            </div>
          )}
          {stats?.recent_sales && stats.recent_sales.length > 0 && (
            <div className="mt-6">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3">{t('recentSalesTitle')}</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('date')}</th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('amount')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.recent_sales.slice(0, 5).map((sale) => (
                      <tr key={sale.code} className="border-b border-border hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                          {new Date(sale.date).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                        </td>
                        <td className="py-3 px-4 text-sm font-semibold text-right text-success">
                          F{sale.total_amount?.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </DetailModal>

      {/* Modal: Ventes Annulées */}
      <DetailModal
        isOpen={activeModal === 'cancelledSales'}
        onClose={() => setActiveModal(null)}
        title={t('cancelledSales')}
        icon={XCircle}
        iconColor="text-red-500"
      >
        <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">{t('totalCancelledSales')}</p>
            <p className="text-3xl font-bold text-red-600 dark:text-red-400 mt-2">
              {stats?.cancelled_sales || 0}
            </p>
          </div>
          
          {loadingCancelled ? (
            <div className="text-center py-4">{t('loadingText')}</div>
          ) : cancelledSales && cancelledSales.length > 0 ? (
           <div className="overflow-x-auto">
             <table className="w-full">
               <thead>
                 <tr className="border-b border-border">
                   <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('userColumn')}</th>
                   <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('dateTimeColumn')}</th>
                   <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('medicinesColumn')}</th>
                   <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('amount')}</th>
                 </tr>
               </thead>
               <tbody>
                 {cancelledSales.map((sale) => (
                   <tr key={sale.id} className="border-b border-border hover:bg-gray-50 dark:hover:bg-gray-700/50">
                     <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{sale.user_name || sale.user_id}</td>
                     <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                       {sale.cancelled_at 
                         ? new Date(sale.cancelled_at).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
                         : new Date(sale.date).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
                        }
                     </td>
                     <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                        {sale.items && sale.items.map(i => `${i.medicine_name}`).join(', ')}
                     </td>
                     <td className="py-3 px-4 text-sm font-semibold text-right text-success">
                       F{sale.total_amount?.toFixed(2)}
                     </td>
                   </tr>
                 ))}
               </tbody>
             </table>
           </div>
          ) : (
            <p className="text-center py-4 text-gray-500">{t('noCancelledSales')}</p>
          )}
        </div>
      </DetailModal>
    </div>
  );
};
