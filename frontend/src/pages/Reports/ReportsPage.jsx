import { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { FileDown, FileSpreadsheet, FileText, Calendar } from 'lucide-react';
import reportsService from '../../services/reportsService';

export const ReportsPage = () => {
  const { t } = useLanguage();
  const [loading, setLoading] = useState({});
  const [salesDateRange, setSalesDateRange] = useState({
    startDate: '',
    endDate: '',
  });
  const [financialDateRange, setFinancialDateRange] = useState({
    startDate: '',
    endDate: '',
  });

  const handleDownload = async (type, downloadFn) => {
    setLoading({ ...loading, [type]: true });
    try {
      await downloadFn();
    } catch (error) {
      alert(`${t('errorDownloading')}: ${error.message}`);
    } finally {
      setLoading({ ...loading, [type]: false });
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('reports')}</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">{t('reportsSubtitle')}</p>
      </div>
      </div>

      {/* Reports Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* Stock Report Card */}
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-primary" />
            </div>
            <div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">{t('stockReport')}</h3>
              <p className="text-xs text-gray-500">{t('formatPDF')}</p>
            </div>
            </div>
          </div>
          
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {t('stockReportDesc')}
          </p>
          
          <button
            onClick={() => handleDownload('stock', () => reportsService.downloadStockPDF())}
            disabled={loading.stock}
            className="w-full btn btn-primary flex items-center justify-center gap-2"
          >
            {loading.stock ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>{t('downloading')}</span>
              </>
            ) : (
              <>
                <FileDown className="w-4 h-4" />
                <span>{t('downloadPDF')}</span>
              </>
            )}
          </button>
        </div>

        {/* Sales Report Card */}
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-success-50 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-success" />
            </div>
            <div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">{t('salesReport')}</h3>
              <p className="text-xs text-gray-500">{t('formatPDF')}</p>
            </div>
            </div>
          </div>
          
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {t('salesReportDesc')}
          </p>

          {/* Date Range Selector */}
          <div className="space-y-3 mb-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('startDate')}
              </label>
              <input
                type="date"
                value={salesDateRange.startDate}
                onChange={(e) => setSalesDateRange({ ...salesDateRange, startDate: e.target.value })}
                className="input text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('endDate')}
              </label>
              <input
                type="date"
                value={salesDateRange.endDate}
                onChange={(e) => setSalesDateRange({ ...salesDateRange, endDate: e.target.value })}
                className="input text-sm"
              />
            </div>
          </div>
          
          <button
            onClick={() => handleDownload('sales', () => 
              reportsService.downloadSalesPDF(salesDateRange.startDate, salesDateRange.endDate)
            )}
            disabled={loading.sales}
            className="w-full btn btn-primary flex items-center justify-center gap-2"
          >
            {loading.sales ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>{t('downloading')}</span>
              </>
            ) : (
              <>
                <FileDown className="w-4 h-4" />
                <span>{t('downloadPDF')}</span>
              </>
            )}
          </button>
        </div>

        {/* Financial Report Card */}
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-orange-50 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-orange-600" />
            </div>
            <div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">{t('financialReport')}</h3>
              <p className="text-xs text-gray-500">{t('formatPDF')}</p>
            </div>
            </div>
          </div>
          
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
           {t('financialReportDesc')}
          </p>

          {/* Date Range Selector */}
          <div className="space-y-3 mb-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('startDate')}
              </label>
              <input
                type="date"
                value={financialDateRange.startDate}
                onChange={(e) => setFinancialDateRange({ ...financialDateRange, startDate: e.target.value })}
                className="input text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('endDate')}
              </label>
              <input
                type="date"
                value={financialDateRange.endDate}
                onChange={(e) => setFinancialDateRange({ ...financialDateRange, endDate: e.target.value })}
                className="input text-sm"
              />
            </div>
          </div>
          
          <button
            onClick={() => handleDownload('financial', () => 
              reportsService.downloadFinancialPDF(financialDateRange.startDate, financialDateRange.endDate)
            )}
            disabled={loading.financial}
            className="w-full btn btn-primary flex items-center justify-center gap-2"
          >
            {loading.financial ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>{t('downloading')}</span>
              </>
            ) : (
              <>
                <FileDown className="w-4 h-4" />
                <span>{t('downloadPDF')}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Info Box */}
      <div className="card p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
        <div className="flex gap-3">
          <Calendar className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-1">{t('information')}</h4>
            <p className="text-sm text-blue-700 dark:text-blue-300">
              {t('reportInfo')}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
