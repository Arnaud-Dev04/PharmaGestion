import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useLanguage } from '../../context/LanguageContext';
import { Search, Filter, Download, Eye, Calendar, XCircle } from 'lucide-react';
import salesService from '../../services/salesService';
import { Pagination } from '../../components/common/Pagination';
import { format } from 'date-fns';

export const SalesHistoryPage = () => {
  const { t } = useLanguage();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    minAmount: '',
    maxAmount: '',
  });

  const [statsFilters, setStatsFilters] = useState({
    startDate: '',
    endDate: '',
  });

  // Fetch sales history
  const { data, isLoading, error } = useQuery({
    queryKey: ['salesHistory', page, filters],
    queryFn: () => salesService.getSalesHistory({ page, ...filters }),
  });

  // Fetch medicine sales statistics
  const { data: medicineStats, isLoading: statsLoading } = useQuery({
    queryKey: ['medicineSalesStats', statsFilters],
    queryFn: () => salesService.getMedicineSalesStats(statsFilters),
  });

  // Cancel sale mutation
  const cancelSaleMutation = useMutation({
    mutationFn: (saleId) => salesService.cancelSale(saleId),
    onSuccess: () => {
      queryClient.invalidateQueries(['salesHistory']);
      queryClient.invalidateQueries(['medicineSalesStats']);
      // Also invalidate stock queries if possible, but they are on other pages
    },
    onError: (error) => {
      alert(t('errorCancelling') + ": " + (error.response?.data?.detail || error.message));
    }
  });

  const handleFilterChange = (field, value) => {
    setFilters({ ...filters, [field]: value });
    setPage(1); // Reset to first page when filters change
  };

  const handleDownloadInvoice = async (saleId) => {
    try {
      await salesService.downloadInvoice(saleId);
    } catch (error) {
      alert(t('errorDownloadingInvoice'));
    }
  };

  const handleCancelSale = (saleId) => {
    if (window.confirm(t('confirmCancelSale'))) {
      cancelSaleMutation.mutate(saleId);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('salesHistoryTitle')}</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">{t('salesHistorySubtitle')}</p>
      </div>
      </div>

      {/* Filters Card */}
      <div className="card p-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          <h3 className="font-medium text-gray-900 dark:text-white">{t('filters')}</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Date Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {t('startDate')}
            </label>
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => handleFilterChange('startDate', e.target.value)}
              className="input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {t('endDate')}
            </label>
            <input
              type="date"
              value={filters.endDate}
              onChange={(e) => handleFilterChange('endDate', e.target.value)}
              className="input"
            />
          </div>

          {/* Amount Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {t('minAmount')} (F)
            </label>
            <input
              type="number"
              value={filters.minAmount}
              onChange={(e) => handleFilterChange('minAmount', e.target.value)}
              className="input"
              placeholder="0"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {t('maxAmount')} (F)
            </label>
            <input
              type="number"
              value={filters.maxAmount}
              onChange={(e) => handleFilterChange('maxAmount', e.target.value)}
              className="input"
              placeholder={t('unlimited')}
            />
          </div>
        </div>

        {/* Reset Filters Button */}
        {(filters.startDate || filters.endDate || filters.minAmount || filters.maxAmount) && (
          <button
            onClick={() => setFilters({ startDate: '', endDate: '', minAmount: '', maxAmount: '' })}
            className="mt-4 text-sm text-primary hover:text-primary-600"
          >
            {t('resetFilters')}
          </button>
        )}
      </div>

      {/* Sales Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400">{t('loading')}</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <p className="text-danger mb-2">{t('loadingError')}</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">{t('errorLoadingSalesHistory')}</p>
            </div>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-900/50 border-b border-border">
                  <tr>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('medicines')}</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('date')}</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('price')}</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('statusLabel')}</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('user')}</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('client')}</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.items && data.items.length > 0 ? (
                    data.items.map((sale) => (
                      <tr key={sale.id} className={`border-b border-border hover:bg-gray-50 dark:hover:bg-gray-800 ${sale.status === 'cancelled' ? 'bg-red-50 dark:bg-red-900/10' : ''}`}>
                        <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                          {sale.items && sale.items.length > 0 ? (
                            <div className="flex flex-col gap-1">
                              {sale.items.map((item, idx) => (
                                <span key={idx} className="text-xs">
                                  {item.medicine_name} x{item.quantity}
                                </span>
                              ))}
                            </div>
                          ) : '-'}
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                          {sale.date ? format(new Date(sale.date), 'dd/MM/yyyy HH:mm') : '-'}
                        </td>
                        <td className="py-3 px-4 text-sm text-right font-medium text-gray-900 dark:text-white">
                          F{sale.total_amount?.toFixed(2) || '0.00'}
                        </td>
                        <td className="py-3 px-4 text-sm">
                          <span className={`px-2 py-1 rounded text-xs ${
                            sale.status === 'cancelled' 
                              ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' 
                              : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                          }`}>
                            {sale.status === 'cancelled' ? t('cancelled') : t('completed')}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                          {sale.user_name || sale.user_id || '-'}
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                          {sale.customer_phone || '-'}
                        </td>
                        <td className="py-3 px-4 text-sm text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleDownloadInvoice(sale.id)}
                              className="p-1.5 hover:bg-primary-50 rounded text-primary transition-colors"
                              title={t('downloadInvoice')}
                            >
                              <Download className="w-4 h-4" />
                            </button>
                            
                            {sale.status !== 'cancelled' && (
                              <button
                                onClick={() => handleCancelSale(sale.id)}
                                className="p-1.5 hover:bg-red-50 rounded text-red-600 transition-colors"
                                title={t('cancelSale')}
                                disabled={cancelSaleMutation.isLoading}
                              >
                                <XCircle className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" className="py-12 text-center text-gray-500">
                        {t('noSales')}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {data?.total > 0 && (
              <div className="px-4 pb-4">
                <Pagination
                  currentPage={page}
                  totalPages={data.total_pages}
                  totalItems={data.total}
                  onPageChange={setPage}
                />
              </div>
            )}
          </>
        )}
      </div>

      {/* Summary Card */}
      {data?.items && data.items.length > 0 && (
        <div className="card p-4 bg-primary-50 border border-primary-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-primary-700 font-medium">{t('totalSalesDisplayed')}</p>
              <p className="text-xs text-primary-600 mt-1">{data.total} {t('salesTotal')}</p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-primary">
                F{data.items.reduce((sum, sale) => sum + (sale.total_amount || 0), 0).toFixed(2)}
              </p>
              <p className="text-xs text-primary-600">{t('currentPage')}</p>
            </div>
          </div>
        </div>
      )}

      {/* Medicine Sales Statistics Section */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-primary" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{t('medicineSalesStats')}</h2>
        </div>

        {/* Period Filter */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {t('startDate')}
            </label>
            <input
              type="date"
              value={statsFilters.startDate}
              onChange={(e) => setStatsFilters({ ...statsFilters, startDate: e.target.value })}
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {t('endDate')}
            </label>
            <input
              type="date"
              value={statsFilters.endDate}
              onChange={(e) => setStatsFilters({ ...statsFilters, endDate: e.target.value })}
              className="input"
            />
          </div>
        </div>

        {/* Statistics Table */}
        {statsLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : medicineStats && medicineStats.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-900/50 border-b border-border">
                <tr>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('medicine')}</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('code')}</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('quantitySold')}</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('totalRevenue')}</th>
                </tr>
              </thead>
              <tbody>
                {medicineStats.map((med) => (
                  <tr key={med.id} className="border-b border-border hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="py-3 px-4 text-sm font-medium text-gray-900 dark:text-white">{med.name}</td>
                    <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{med.code}</td>
                    <td className="py-3 px-4 text-sm text-right font-semibold text-primary">
                      {med.total_quantity}
                    </td>
                    <td className="py-3 px-4 text-sm text-right font-semibold text-success">
                      F{med.total_revenue?.toFixed(2) || '0.00'}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="bg-gray-50 dark:bg-gray-900/50 border-t-2 border-border">
                <tr>
                  <td colSpan="2" className="py-3 px-4 text-sm font-bold text-gray-900 dark:text-white">TOTAL</td>
                  <td className="py-3 px-4 text-sm text-right font-bold text-primary">
                    {medicineStats.reduce((sum, m) => sum + m.total_quantity, 0)}
                  </td>
                  <td className="py-3 px-4 text-sm text-right font-bold text-success">
                    F{medicineStats.reduce((sum, m) => sum + m.total_revenue, 0).toFixed(2)}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        ) : (
          <p className="text-center text-gray-500 dark:text-gray-400 py-8">
            {t('noDataForPeriod')}
          </p>
        )}
      </div>
    </div>
  );
};
