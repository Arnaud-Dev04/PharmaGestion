import 'package:flutter/material.dart';
import 'package:frontend1/core/theme.dart';
import 'package:frontend1/providers/cart_provider.dart';
import 'package:frontend1/providers/language_provider.dart';
import 'package:frontend1/services/sales_service.dart';
import 'package:provider/provider.dart';

class PaymentModal extends StatefulWidget {
  final double totalAmount;
  final VoidCallback onSuccess;

  const PaymentModal({
    super.key,
    required this.totalAmount,
    required this.onSuccess,
  });

  @override
  State<PaymentModal> createState() => _PaymentModalState();
}

class _PaymentModalState extends State<PaymentModal> {
  final SalesService _salesService = SalesService();

  String _paymentMethod = 'cash'; // 'cash' ou 'insurance_card'
  bool _isProcessing = false;

  // Champs Assurance
  final _insuranceProviderController = TextEditingController();
  final _insuranceCardIdController = TextEditingController();
  final _coveragePercentController = TextEditingController(text: '80');

  @override
  void dispose() {
    _insuranceProviderController.dispose();
    _insuranceCardIdController.dispose();
    _coveragePercentController.dispose();
    super.dispose();
  }

  Future<void> _processPayment() async {
    final cartProvider = Provider.of<CartProvider>(context, listen: false);

    // Validation Assurance
    if (_paymentMethod == 'insurance_card') {
      if (_insuranceProviderController.text.isEmpty ||
          _insuranceCardIdController.text.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Veuillez remplir les infos assurance')),
        );
        return;
      }
    }

    setState(() => _isProcessing = true);

    try {
      // Préparation des données pour le backend
      final saleData = {
        'items': cartProvider.items
            .map(
              (item) => {
                'medicine_id': item.medicine.id,
                'quantity':
                    item.totalUnits, // IMPORTANT: Envoi en unités globales
                'unit_price': item.effectiveUnitPrice, // Prix unitaire appliqué
                'total_price': item.totalAmount,
              },
            )
            .toList(),
        'total_amount': widget.totalAmount,
        'payment_method': _paymentMethod,
        'customer_id': cartProvider.customerId,
        'customer_phone': cartProvider.customerPhone.isNotEmpty
            ? cartProvider.customerPhone
            : null,
        'customer_first_name': cartProvider.customerFirstName.isNotEmpty
            ? cartProvider.customerFirstName
            : null,
        'customer_last_name': cartProvider.customerLastName.isNotEmpty
            ? cartProvider.customerLastName
            : null,

        // Assurance
        'insurance_provider': _paymentMethod == 'insurance_card'
            ? _insuranceProviderController.text
            : null,
        'insurance_card_id': _paymentMethod == 'insurance_card'
            ? _insuranceCardIdController.text
            : null,
        'coverage_percent': _paymentMethod == 'insurance_card'
            ? double.tryParse(_coveragePercentController.text) ?? 0
            : 0,
      };

      await _salesService.createSale(saleData);

      if (mounted) {
        widget.onSuccess(); // Callback succès (vider panier, fermer modal)
        Navigator.of(context).pop(); // Fermer modal

        // Modal de succès
        showDialog(
          context: context,
          builder: (ctx) => AlertDialog(
            title: const Row(
              children: [
                Icon(Icons.check_circle, color: AppTheme.successColor),
                SizedBox(width: 8),
                Text('Vente réussie !'),
              ],
            ),
            content: Text(
              'Montant enregistré : F${widget.totalAmount.toStringAsFixed(0)}',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(ctx).pop(),
                child: const Text('Fermer'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erreur: ${e.toString()}'),
            backgroundColor: AppTheme.dangerColor,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isProcessing = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final languageProvider = Provider.of<LanguageProvider>(context);

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        width: 500,
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  languageProvider.translate('checkout'),
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                IconButton(
                  onPressed: () => Navigator.of(context).pop(),
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Montant Total
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.primaryColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  const Text(
                    'Montant à payer',
                    style: TextStyle(color: AppTheme.primaryColor),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'F${widget.totalAmount.toStringAsFixed(0)}',
                    style: const TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.primaryColor,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Méthode de Paiement
            Text(
              languageProvider.translate('paymentMethod'),
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _buildPaymentOption('cash', 'Espèces', Icons.payments),
                const SizedBox(width: 12),
                _buildPaymentOption(
                  'insurance_card',
                  'Assurance',
                  Icons.card_membership,
                ),
              ],
            ),

            // Formulaire Assurance
            if (_paymentMethod == 'insurance_card') ...[
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[50],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey[200]!),
                ),
                child: Column(
                  children: [
                    TextField(
                      controller: _insuranceProviderController,
                      decoration: const InputDecoration(
                        labelText: 'Nom de l\'assurance / Mutuelle',
                        isDense: true,
                        hintText: 'Ex: MUGEFCI, AXA...',
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _insuranceCardIdController,
                      decoration: const InputDecoration(
                        labelText: 'N° Carte / Matricule',
                        isDense: true,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _coveragePercentController,
                            keyboardType: TextInputType.number,
                            decoration: const InputDecoration(
                              labelText: 'Taux couvert (%)',
                              isDense: true,
                            ),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          flex: 2,
                          child: Builder(
                            builder: (context) {
                              final percent =
                                  double.tryParse(
                                    _coveragePercentController.text,
                                  ) ??
                                  0;
                              final partAssurance =
                                  (widget.totalAmount * percent) / 100;
                              final partPatient =
                                  widget.totalAmount - partAssurance;
                              return Column(
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  Text(
                                    'Assurance: F${partAssurance.toStringAsFixed(0)}',
                                    style: const TextStyle(
                                      color: AppTheme.successColor,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  Text(
                                    'Patient: F${partPatient.toStringAsFixed(0)}',
                                    style: const TextStyle(
                                      color: AppTheme.primaryColor,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              );
                            },
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 32),

            // Actions
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: Text(languageProvider.translate('cancel')),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _isProcessing ? null : _processPayment,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: _isProcessing
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          )
                        : Text(languageProvider.translate('pay')),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPaymentOption(String value, String label, IconData icon) {
    final isSelected = _paymentMethod == value;
    return Expanded(
      child: InkWell(
        onTap: () => setState(() => _paymentMethod = value),
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected
                ? AppTheme.primaryColor.withValues(alpha: 0.1)
                : Colors.transparent,
            border: Border.all(
              color: isSelected ? AppTheme.primaryColor : Colors.grey[300]!,
              width: 2,
            ),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: [
              Icon(
                icon,
                color: isSelected ? AppTheme.primaryColor : Colors.grey,
              ),
              const SizedBox(height: 4),
              Text(
                label,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: isSelected ? AppTheme.primaryColor : Colors.grey[700],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
