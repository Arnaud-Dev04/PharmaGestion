import 'package:flutter/material.dart';
import 'package:data_table_2/data_table_2.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:frontend1/core/theme.dart';
import 'package:frontend1/models/sale.dart';
import 'package:frontend1/providers/language_provider.dart';
import 'package:frontend1/services/sales_service.dart';
// import 'package:frontend1/widgets/common/custom_pagination.dart';

class SalesHistoryPage extends StatefulWidget {
  const SalesHistoryPage({super.key});

  @override
  State<SalesHistoryPage> createState() => _SalesHistoryPageState();
}

class _SalesHistoryPageState extends State<SalesHistoryPage> {
  final SalesService _salesService = SalesService();

  // États Filtres
  final _startDateController = TextEditingController();
  final _endDateController = TextEditingController();
  final _minAmountController = TextEditingController();
  final _maxAmountController = TextEditingController();

  // États Statistiques Filtres
  final _statsStartDateController = TextEditingController();
  final _statsEndDateController = TextEditingController();

  // Données
  List<Sale> _sales = [];
  List<MedicineSaleStats> _medicineStats = [];
  int _totalSales = 0;
  int _totalPages = 1;
  int _currentPage = 1;
  bool _isLoadingSales = false;
  bool _isLoadingStats = false;

  @override
  void initState() {
    super.initState();
    _loadSales();
    _loadStats();
  }

  @override
  void dispose() {
    _startDateController.dispose();
    _endDateController.dispose();
    _minAmountController.dispose();
    _maxAmountController.dispose();
    _statsStartDateController.dispose();
    _statsEndDateController.dispose();
    super.dispose();
  }

  Future<void> _loadSales() async {
    setState(() => _isLoadingSales = true);
    try {
      final response = await _salesService.getSalesHistory(
        page: _currentPage,
        startDate: _startDateController.text,
        endDate: _endDateController.text,
        minAmount: double.tryParse(_minAmountController.text),
        maxAmount: double.tryParse(_maxAmountController.text),
      );
      if (mounted) {
        setState(() {
          _sales = response.items;
          _totalSales = response.total;
          _totalPages = response.totalPages;
          _isLoadingSales = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoadingSales = false);
      print('Erreur loadSales: $e');
    }
  }

  Future<void> _loadStats() async {
    setState(() => _isLoadingStats = true);
    try {
      final stats = await _salesService.getMedicineSalesStats(
        startDate: _statsStartDateController.text,
        endDate: _statsEndDateController.text,
      );
      if (mounted) {
        setState(() {
          _medicineStats = stats;
          _isLoadingStats = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoadingStats = false);
      print('Erreur loadStats: $e');
    }
  }

  Future<void> _downloadInvoice(int saleId, LanguageProvider lp) async {
    try {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(lp.translate('downloading'))));
      // TODO: Gérer le téléchargement réel du fichier (save file/open)
      // En Flutter Web, c'est spécifique (anchor element).
      // Pour l'instant on simule l'appel API qui retourne les bytes.
      await _salesService.downloadInvoice(saleId);
      // Si succès
      if (mounted) {
        ScaffoldMessenger.of(context).hideCurrentSnackBar();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(lp.translate('invoiceDownloaded'))),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${lp.translate('error')}: $e'),
          backgroundColor: AppTheme.dangerColor,
        ),
      );
    }
  }

  Future<void> _cancelSale(Sale sale, LanguageProvider lp) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(lp.translate('cancelSale')),
        content: Text(
          '${lp.translate('cancelSaleConfirm')} #${sale.code} ?\n${lp.translate('stockWillBeRestored')}.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(lp.translate('no')),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: AppTheme.dangerColor),
            child: Text(lp.translate('yesCancel')),
          ),
        ],
      ),
    );

    if (confirm == true) {
      try {
        await _salesService.cancelSale(sale.id);
        _loadSales(); // Recharger liste
        _loadStats(); // Recharger stats
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(lp.translate('saleCancelled')),
              backgroundColor: AppTheme.successColor,
            ),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('${lp.translate('error')}: $e'),
              backgroundColor: AppTheme.dangerColor,
            ),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final languageProvider = Provider.of<LanguageProvider>(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Text(
            languageProvider.translate('salesHistory'),
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          Text(
            languageProvider.translate('salesHistorySubtitle'),
            style: const TextStyle(color: Colors.grey),
          ),
          const SizedBox(height: 24),

          // Filtres
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    languageProvider.translate('filters'),
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 16,
                    runSpacing: 16,
                    children: [
                      _buildDateFilter(
                        languageProvider.translate('startDate'),
                        _startDateController,
                      ),
                      _buildDateFilter(
                        languageProvider.translate('endDate'),
                        _endDateController,
                      ),
                      _buildNumberFilter(
                        '${languageProvider.translate('min')} (F)',
                        _minAmountController,
                      ),
                      _buildNumberFilter(
                        '${languageProvider.translate('max')} (F)',
                        _maxAmountController,
                      ),
                      ElevatedButton.icon(
                        onPressed: () {
                          _currentPage = 1;
                          _loadSales();
                        },
                        icon: const Icon(Icons.filter_list),
                        label: Text(languageProvider.translate('filter')),
                      ),
                      TextButton(
                        onPressed: () {
                          _startDateController.clear();
                          _endDateController.clear();
                          _minAmountController.clear();
                          _maxAmountController.clear();
                          _currentPage = 1;
                          _loadSales();
                        },
                        child: Text(languageProvider.translate('reset')),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Summary Card
          if (_sales.isNotEmpty)
            Card(
              color: AppTheme.primaryColor.withValues(alpha: 0.1),
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
                side: BorderSide(
                  color: AppTheme.primaryColor.withValues(alpha: 0.2),
                ),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          languageProvider.translate('totalSalesDisplayed'),
                          style: const TextStyle(
                            color: AppTheme.primaryColor,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          '$_totalSales ${languageProvider.translate('sales')}',
                          style: const TextStyle(fontSize: 12),
                        ),
                      ],
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          'F${_sales.fold<double>(0, (sum, item) => sum + item.totalAmount).toStringAsFixed(0)}',
                          style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.primaryColor,
                          ),
                        ),
                        Text(
                          languageProvider.translate('totalOnThisPage'),
                          style: const TextStyle(
                            fontSize: 12,
                            color: AppTheme.primaryColor,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          if (_sales.isNotEmpty) const SizedBox(height: 24),

          // Tableau Ventes
          SizedBox(
            height: 500,
            child: Card(
              child: _isLoadingSales
                  ? const Center(child: CircularProgressIndicator())
                  : Column(
                      children: [
                        Expanded(
                          child: DataTable2(
                            columnSpacing: 12,
                            horizontalMargin: 12,
                            minWidth: 800,
                            columns: [
                              DataColumn2(
                                label: Text(
                                  languageProvider.translate('medicines'),
                                ),
                                size: ColumnSize.L,
                              ),
                              DataColumn2(
                                label: Text(languageProvider.translate('date')),
                                size: ColumnSize.M,
                              ),
                              DataColumn2(
                                label: Text(
                                  languageProvider.translate('price'),
                                ),
                                size: ColumnSize.S,
                                numeric: true,
                              ),
                              DataColumn2(
                                label: Text(
                                  languageProvider.translate('status'),
                                ),
                                size: ColumnSize.S,
                              ),
                              DataColumn2(
                                label: Text(languageProvider.translate('user')),
                                size: ColumnSize.M,
                              ),
                              DataColumn2(
                                label: Text(
                                  languageProvider.translate('client'),
                                ),
                                size: ColumnSize.M,
                              ),
                              DataColumn2(
                                label: Text(
                                  languageProvider.translate('actions'),
                                ),
                                size: ColumnSize.S,
                              ),
                            ],
                            rows: _sales
                                .map(
                                  (sale) => DataRow(
                                    color: sale.status == 'cancelled'
                                        ? WidgetStateProperty.all(
                                            Colors.red.withOpacity(0.05),
                                          )
                                        : null,
                                    cells: [
                                      DataCell(
                                        Column(
                                          mainAxisAlignment:
                                              MainAxisAlignment.center,
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: sale.items
                                              .take(2)
                                              .map(
                                                (i) => Text(
                                                  '${i.medicineName} x${i.quantity}',
                                                  style: const TextStyle(
                                                    fontSize: 12,
                                                  ),
                                                  overflow:
                                                      TextOverflow.ellipsis,
                                                ),
                                              )
                                              .toList(),
                                        ),
                                      ),
                                      DataCell(
                                        Text(
                                          DateFormat(
                                            'dd/MM HH:mm',
                                          ).format(sale.date),
                                        ),
                                      ),
                                      DataCell(
                                        Text(
                                          'F${sale.totalAmount.toStringAsFixed(0)}',
                                          style: const TextStyle(
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ),
                                      DataCell(
                                        Container(
                                          padding: const EdgeInsets.symmetric(
                                            horizontal: 8,
                                            vertical: 4,
                                          ),
                                          decoration: BoxDecoration(
                                            color: sale.status == 'cancelled'
                                                ? Colors.red[100]
                                                : Colors.green[100],
                                            borderRadius: BorderRadius.circular(
                                              12,
                                            ),
                                          ),
                                          child: sale.status == 'cancelled'
                                              ? GestureDetector(
                                                  onTap: () {
                                                    showDialog(
                                                      context: context,
                                                      builder: (ctx) => AlertDialog(
                                                        title: Row(
                                                          children: [
                                                            const Icon(
                                                              Icons
                                                                  .info_outline,
                                                              color:
                                                                  Colors.blue,
                                                            ),
                                                            const SizedBox(
                                                              width: 8,
                                                            ),
                                                            Text(
                                                              languageProvider
                                                                  .translate(
                                                                    'cancelledSaleDetails',
                                                                  ),
                                                            ),
                                                          ],
                                                        ),
                                                        content: Column(
                                                          mainAxisSize:
                                                              MainAxisSize.min,
                                                          crossAxisAlignment:
                                                              CrossAxisAlignment
                                                                  .start,
                                                          children: [
                                                            Text(
                                                              '${languageProvider.translate('cancelledBy')}: ${sale.cancelledBy ?? "N/A"}',
                                                              style:
                                                                  const TextStyle(
                                                                    fontSize:
                                                                        16,
                                                                  ),
                                                            ),
                                                            const SizedBox(
                                                              height: 8,
                                                            ),
                                                            Text(
                                                              '${languageProvider.translate('cancelledAt')}: ${sale.cancelledAt != null ? DateFormat('dd/MM/yyyy HH:mm').format(sale.cancelledAt!) : "N/A"}',
                                                              style:
                                                                  const TextStyle(
                                                                    fontSize:
                                                                        16,
                                                                  ),
                                                            ),
                                                          ],
                                                        ),
                                                        actions: [
                                                          TextButton(
                                                            onPressed: () =>
                                                                Navigator.pop(
                                                                  ctx,
                                                                ),
                                                            child: Text(
                                                              languageProvider
                                                                  .translate(
                                                                    'close',
                                                                  ),
                                                            ),
                                                          ),
                                                        ],
                                                      ),
                                                    );
                                                  },
                                                  child: Text(
                                                    languageProvider.translate(
                                                      'cancelled',
                                                    ),
                                                    style: const TextStyle(
                                                      color: Colors.red,
                                                      fontWeight:
                                                          FontWeight.bold,
                                                      decoration: TextDecoration
                                                          .underline,
                                                    ),
                                                  ),
                                                )
                                              : Text(
                                                  languageProvider.translate(
                                                    'completed',
                                                  ),
                                                  style: const TextStyle(
                                                    color: Colors.green,
                                                    fontWeight: FontWeight.bold,
                                                  ),
                                                ),
                                        ),
                                      ),
                                      DataCell(Text(sale.userName)),
                                      DataCell(Text(sale.customerPhone ?? '-')),
                                      DataCell(
                                        Row(
                                          children: [
                                            IconButton(
                                              icon: const Icon(
                                                Icons.download,
                                                size: 18,
                                                color: AppTheme.primaryColor,
                                              ),
                                              onPressed: () => _downloadInvoice(
                                                sale.id,
                                                languageProvider,
                                              ),
                                            ),
                                            if (sale.status != 'cancelled')
                                              IconButton(
                                                icon: const Icon(
                                                  Icons.cancel,
                                                  size: 18,
                                                  color: AppTheme.dangerColor,
                                                ),
                                                onPressed: () => _cancelSale(
                                                  sale,
                                                  languageProvider,
                                                ),
                                              ),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                )
                                .toList(),
                          ),
                        ),
                        // Packaging Pagination Simple
                        Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.end,
                            children: [
                              Text(
                                '${languageProvider.translate('page')} $_currentPage / $_totalPages',
                              ),
                              IconButton(
                                icon: const Icon(Icons.chevron_left),
                                onPressed: _currentPage > 1
                                    ? () {
                                        setState(() => _currentPage--);
                                        _loadSales();
                                      }
                                    : null,
                              ),
                              IconButton(
                                icon: const Icon(Icons.chevron_right),
                                onPressed: _currentPage < _totalPages
                                    ? () {
                                        setState(() => _currentPage++);
                                        _loadSales();
                                      }
                                    : null,
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
            ),
          ),
          const SizedBox(height: 24),

          // Stats Section
          Text(
            languageProvider.translate('medicineStats'),
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    children: [
                      _buildDateFilter(
                        languageProvider.translate('startDate'),
                        _statsStartDateController,
                      ),
                      const SizedBox(width: 16),
                      _buildDateFilter(
                        languageProvider.translate('endDate'),
                        _statsEndDateController,
                      ),
                      const SizedBox(width: 16),
                      ElevatedButton(
                        onPressed: _loadStats,
                        child: Text(languageProvider.translate('refresh')),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _isLoadingStats
                      ? const Padding(
                          padding: EdgeInsets.all(20),
                          child: CircularProgressIndicator(),
                        )
                      : SizedBox(
                          height: 300,
                          child: DataTable2(
                            columns: [
                              DataColumn2(
                                label: Text(
                                  languageProvider.translate('medicine'),
                                ),
                              ),
                              DataColumn2(
                                label: Text(languageProvider.translate('code')),
                              ),
                              DataColumn2(
                                label: Text(
                                  languageProvider.translate('qtSold'),
                                ),
                                numeric: true,
                              ),
                              DataColumn2(
                                label: Text(
                                  languageProvider.translate('totalRevenue'),
                                ),
                                numeric: true,
                              ),
                            ],
                            rows: _medicineStats
                                .map(
                                  (stat) => DataRow(
                                    cells: [
                                      DataCell(
                                        Text(
                                          stat.name,
                                          style: const TextStyle(
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ),
                                      DataCell(Text(stat.code)),
                                      DataCell(Text('${stat.totalQuantity}')),
                                      DataCell(
                                        Text(
                                          'F${stat.totalRevenue.toStringAsFixed(0)}',
                                          style: const TextStyle(
                                            color: AppTheme.successColor,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                )
                                .toList(),
                          ),
                        ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDateFilter(String label, TextEditingController controller) {
    return SizedBox(
      width: 150,
      child: TextField(
        controller: controller,
        decoration: InputDecoration(
          labelText: label,
          suffixIcon: const Icon(Icons.calendar_today, size: 16),
          isDense: true,
          border: const OutlineInputBorder(),
        ),
        readOnly: true,
        onTap: () async {
          final date = await showDatePicker(
            context: context,
            initialDate: DateTime.now(),
            firstDate: DateTime(2020),
            lastDate: DateTime(2030),
          );
          if (date != null) {
            controller.text = DateFormat('yyyy-MM-dd').format(date);
          }
        },
      ),
    );
  }

  Widget _buildNumberFilter(String label, TextEditingController controller) {
    return SizedBox(
      width: 100,
      child: TextField(
        controller: controller,
        keyboardType: TextInputType.number,
        decoration: InputDecoration(
          labelText: label,
          isDense: true,
          border: const OutlineInputBorder(),
        ),
      ),
    );
  }
}
