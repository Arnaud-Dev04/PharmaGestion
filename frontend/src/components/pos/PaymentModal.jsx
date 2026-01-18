import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { X, Download, CheckCircle } from 'lucide-react';
import salesService from '../../services/salesService';

const PAYMENT_METHODS = [
  { value: 'cash', label: 'Espèces' },
  { value: 'insurance_card', label: "Carte d'assurance maladie" },
];

export const PaymentModal = ({ cart, customerData, totalAmount, onClose, onSuccess }) => {
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [saleId, setSaleId] = useState(null);
  const [success, setSuccess] = useState(false);
  
  // Insurance State
  const [insuranceProvider, setInsuranceProvider] = useState('');
  const [insuranceCardId, setInsuranceCardId] = useState('');
  const [coveragePercent, setCoveragePercent] = useState(80); // Default 80%?

  const createSaleMutation = useMutation({
    mutationFn: (saleData) => salesService.createSale(saleData),
    onSuccess: (data) => {
      setSaleId(data.id);
      setSuccess(true);
    },
    onError: (error) => {
      alert(`Erreur lors de la création de la vente: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleConfirmPayment = () => {
    // Validation for Insurance
    if (paymentMethod === 'insurance_card') {
        if (!insuranceProvider || !insuranceCardId) {
            alert("Veuillez remplir les informations de l'assurance (Nom et Numéro de carte).");
            return;
        }
    }

    // Prepare sale data
    const saleData = {
      items: cart.map((item) => ({
        medicine_id: item.medicine.id,
        quantity: item.quantity,
        is_bonus: item.isBonus, 
      })),
      payment_method: paymentMethod,
      customer_phone: customerData?.phone || null,
      customer_first_name: customerData?.firstName || null,
      customer_last_name: customerData?.lastName || null,
      
      // Add Insurance Details
      insurance_provider: paymentMethod === 'insurance_card' ? insuranceProvider : null,
      insurance_card_id: paymentMethod === 'insurance_card' ? insuranceCardId : null,
      coverage_percent: paymentMethod === 'insurance_card' ? coveragePercent : 0,
    };

    createSaleMutation.mutate(saleData);
  };

  const handleDownloadInvoice = async () => {
    if (saleId) {
      try {
        await salesService.downloadInvoice(saleId);
      } catch (error) {
        alert('Erreur lors du téléchargement de la facture');
      }
    }
  };

  const handleClose = () => {
    if (success) {
      onSuccess();
    }
    onClose();
  };

  if (success) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
          <div className="p-8 text-center">
            <CheckCircle className="w-16 h-16 text-success mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Vente réussie !</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">La vente a été enregistrée avec succès</p>
            
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 mb-6">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Montant total</p>
              <p className="text-3xl font-bold text-primary">F{totalAmount.toFixed(2)}</p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleDownloadInvoice}
                className="flex-1 btn btn-secondary flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" />
                Télécharger facture
              </button>
              <button
                onClick={handleClose}
                className="flex-1 btn btn-primary"
              >
                Terminer
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border flex-shrink-0">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Paiement</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto">
          {/* Total Amount */}
          <div className="bg-primary-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-primary-700 mb-1">Montant à payer</p>
            <p className="text-3xl font-bold text-primary">F{totalAmount.toFixed(2)}</p>
          </div>

          {/* Payment Method Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Mode de paiement
            </label>
            <div className="space-y-2 mb-4">
              {PAYMENT_METHODS.map((method) => (
                <label
                  key={method.value}
                  className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    paymentMethod === method.value
                      ? 'border-primary bg-primary-50'
                      : 'border-border hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="paymentMethod"
                    value={method.value}
                    checked={paymentMethod === method.value}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-4 h-4 text-primary"
                  />
                  <span className="ml-3 text-sm font-medium text-gray-900 dark:text-white">{method.label}</span>
                </label>
              ))}
            </div>

            {/* Insurance Details Form */}
            {paymentMethod === 'insurance_card' && (
                <div className="bg-gray-50 dark:bg-gray-700/30 rounded-lg p-4 space-y-3 border border-gray-200 dark:border-gray-600">
                    <h4 className="font-medium text-gray-900 dark:text-white text-sm border-b border-gray-200 pb-2 mb-2">Détails Assurance</h4>
                    
                    <div>
                        <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Nom de l'assurance / Mutuelle</label>
                        <input 
                            type="text"
                            value={insuranceProvider}
                            onChange={(e) => setInsuranceProvider(e.target.value)}
                            className="input text-sm w-full"
                            placeholder="Ex: MUPEMENET, ASCOMA..."
                        />
                    </div>
                    
                    <div>
                        <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">N° Carte / Matricule</label>
                        <input 
                            type="text"
                            value={insuranceCardId}
                            onChange={(e) => setInsuranceCardId(e.target.value)}
                            className="input text-sm w-full"
                            placeholder="Numéro de la carte"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Taux de couverture (%)</label>
                        <div className="flex items-center gap-4">
                            <input 
                                type="number"
                                min="0"
                                max="100"
                                value={coveragePercent}
                                onChange={(e) => setCoveragePercent(parseFloat(e.target.value) || 0)}
                                className="input text-sm w-24"
                            />
                            <div className="flex-1 text-right text-sm">
                                <p className="text-gray-500">Part Assurance: <span className="font-bold text-success">F{((totalAmount * coveragePercent) / 100).toFixed(0)}</span></p>
                                <p className="text-gray-500">Part Patient: <span className="font-bold text-primary">F{(totalAmount - ((totalAmount * coveragePercent) / 100)).toFixed(0)}</span></p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
          </div>

          {/* Cart Summary */}
          <div className="mb-6">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Résumé de la commande</p>
            <div className="space-y-2">
              {cart.map((item) => (
                <div key={item.medicine.id} className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {item.medicine.name} x{item.quantity}
                  </span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    F{(item.medicine.price_sell * item.quantity).toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 btn btn-secondary"
              disabled={createSaleMutation.isPending}
            >
              Annuler
            </button>
            <button
              onClick={handleConfirmPayment}
              className="flex-1 btn btn-primary"
              disabled={createSaleMutation.isPending}
            >
              {createSaleMutation.isPending ? 'Traitement...' : 'Confirmer'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
