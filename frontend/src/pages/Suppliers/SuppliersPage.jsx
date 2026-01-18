import { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Pencil, Trash2, AlertCircle } from 'lucide-react';
import supplierService from '../../services/supplierService';
import { Pagination } from '../../components/common/Pagination';
import { SupplierModal } from '../../components/suppliers/SupplierModal';

export const SuppliersPage = () => {
  const { t } = useLanguage();
  const [page, setPage] = useState(1);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState(null);
  
  const queryClient = useQueryClient();

  // Fetch suppliers
  const { data, isLoading, error } = useQuery({
    queryKey: ['suppliers', page],
    queryFn: () => supplierService.getSuppliers({ page }),
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: supplierService.deleteSupplier,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
    },
  });

  const handleEdit = (supplier) => {
    setSelectedSupplier(supplier);
    setIsModalOpen(true);
  };

  const handleDelete = async (supplier) => {
    if (window.confirm(`${t('confirmDeleteSupplier')} ${supplier.name}?`)) {
      try {
        await deleteMutation.mutateAsync(supplier.id);
      } catch (error) {
        alert(t('deleteError'));
      }
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedSupplier(null);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('suppliersTitle')}</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">{t('suppliersSubtitle')}</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          <span>{t('addSupplier')}</span>
        </button>
      </div>

      {/* Suppliers Table */}
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
              <AlertCircle className="w-16 h-16 text-danger mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{t('loadingError')}</h3>
              <p className="text-gray-600 dark:text-gray-400">{t('errorLoadingSuppliers')}</p>
            </div>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-border">
                  <tr>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('name')}</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('contact')}</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('phone')}</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('email')}</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('address')}</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.items && data.items.length > 0 ? (
                    data.items.map((supplier) => (
                      <tr key={supplier.id} className="border-b border-border hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <td className="py-3 px-4 text-sm font-medium text-gray-900 dark:text-white">{supplier.name}</td>
                        <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{supplier.contact || '-'}</td>
                        <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{supplier.phone || '-'}</td>
                        <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{supplier.email || '-'}</td>
                        <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400 max-w-xs truncate">
                          {supplier.address || '-'}
                        </td>
                        <td className="py-3 px-4 text-sm text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleEdit(supplier)}
                              className="p-1.5 hover:bg-primary-50 rounded text-primary transition-colors"
                            >
                              <Pencil className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(supplier)}
                              className="p-1.5 hover:bg-danger-50 rounded text-danger transition-colors"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="6" className="py-12 text-center text-gray-500">
                        {t('noSuppliers')}
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

      {/* Supplier Modal */}
      {isModalOpen && (
        <SupplierModal
          supplier={selectedSupplier}
          onClose={handleCloseModal}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['suppliers'] });
            handleCloseModal();
          }}
        />
      )}
    </div>
  );
};
