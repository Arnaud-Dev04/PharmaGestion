import 'package:flutter/material.dart';
import 'package:frontend1/core/theme.dart';
import 'package:frontend1/models/medicine.dart';
import 'package:frontend1/services/stock_service.dart';
import 'package:frontend1/widgets/stock/medicine_form_dialog.dart';
import 'package:frontend1/providers/language_provider.dart';
import 'package:frontend1/providers/auth_provider.dart';
import 'package:provider/provider.dart';

/// Page de gestion du stock des médicaments
/// Reproduit exactement StockPage.jsx avec tableau 7 colonnes
class StockPage extends StatefulWidget {
  const StockPage({super.key});

  @override
  State<StockPage> createState() => _StockPageState();
}

class _StockPageState extends State<StockPage> {
  final StockService _stockService = StockService();
  final TextEditingController _searchController = TextEditingController();

  List<Medicine> _medicines = [];
  int _currentPage = 1;
  int _totalPages = 1;
  int _totalItems = 0;
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadMedicines();

    // Debounce pour la recherche
    _searchController.addListener(_onSearchChanged);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged() {
    // Simple debounce : attendre que l'utilisateur arrête de taper
    Future.delayed(const Duration(milliseconds: 500), () {
      if (mounted) {
        _currentPage = 1;
        _loadMedicines();
      }
    });
  }

  Future<void> _loadMedicines() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final response = await _stockService.getMedicines(
        page: _currentPage,
        search: _searchController.text.trim().isNotEmpty
            ? _searchController.text.trim()
            : null,
      );

      if (mounted) {
        setState(() {
          _medicines = response.items;
          _totalPages = response.totalPages;
          _totalItems = response.total;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _showMedicineDialog({Medicine? medicine}) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => MedicineFormDialog(medicine: medicine),
      barrierDismissible: false,
    );

    if (result == true) {
      _loadMedicines(); // Recharger après ajout/modification
    }
  }

  Future<void> _deleteMedicine(Medicine medicine, LanguageProvider lp) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(lp.translate('confirmDelete')),
        content: Text(
          '${lp.translate('deleteConfirmation')} ${medicine.name}?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: Text(lp.translate('cancel')),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.dangerColor,
            ),
            child: Text(lp.translate('delete')),
          ),
        ],
      ),
    );

    if (confirm == true) {
      try {
        await _stockService.deleteMedicine(medicine.id);
        _loadMedicines();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(lp.translate('medicineDeleted'))),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('${lp.translate('error')}: ${e.toString()}'),
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
    final authProvider = Provider.of<AuthProvider>(context);
    final isAdmin = authProvider.user?.isAdmin ?? false;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        _buildHeader(languageProvider, isAdmin),
        const SizedBox(height: 24),

        // Search Bar
        _buildSearchBar(languageProvider),
        const SizedBox(height: 24),

        // Table
        Expanded(child: _buildTableCard(languageProvider, isAdmin)),
      ],
    );
  }

  Widget _buildHeader(LanguageProvider languageProvider, bool isAdmin) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              languageProvider.translate('stockManagement'),
              style: Theme.of(
                context,
              ).textTheme.headlineLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              languageProvider.translate('stockSubtitle'),
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).brightness == Brightness.dark
                    ? AppTheme.darkSidebarText
                    : AppTheme.lightSidebarText,
              ),
            ),
          ],
        ),
        if (isAdmin)
          ElevatedButton.icon(
            onPressed: () => _showMedicineDialog(),
            icon: const Icon(Icons.add),
            label: Text(languageProvider.translate('addMedicine')),
          ),
      ],
    );
  }

  Widget _buildSearchBar(LanguageProvider languageProvider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: TextField(
          controller: _searchController,
          decoration: InputDecoration(
            hintText: languageProvider.translate('search'),
            prefixIcon: const Icon(Icons.search),
            border: InputBorder.none,
            contentPadding: EdgeInsets.zero,
          ),
        ),
      ),
    );
  }

  Widget _buildTableCard(LanguageProvider languageProvider, bool isAdmin) {
    if (_isLoading) {
      return _buildLoadingView(languageProvider);
    }

    if (_error != null) {
      return _buildErrorView(languageProvider);
    }

    return Card(
      child: Column(
        children: [
          Expanded(
            child: _medicines.isEmpty
                ? _buildEmptyView(languageProvider)
                : _buildTable(languageProvider, isAdmin),
          ),
          if (_totalItems > 0) _buildPagination(languageProvider),
        ],
      ),
    );
  }

  Widget _buildTable(LanguageProvider languageProvider, bool isAdmin) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return SingleChildScrollView(
      child: Table(
        columnWidths: {
          0: const FlexColumnWidth(2), // Nom
          1: const FlexColumnWidth(1.5), // Forme & Cond.
          2: const FlexColumnWidth(1.5), // Détails
          3: const FlexColumnWidth(1), // Prix
          4: const FlexColumnWidth(1.5), // Quantité
          5: const FlexColumnWidth(1), // Statut
          if (isAdmin) 6: const FixedColumnWidth(120), // Actions
        },
        border: TableBorder(
          horizontalInside: BorderSide(
            color: isDark ? AppTheme.darkBorder : AppTheme.lightBorder,
          ),
        ),
        children: [
          // Header
          _buildTableHeader(languageProvider, isAdmin, isDark),

          // Rows
          ..._medicines.map(
            (medicine) =>
                _buildTableRow(medicine, languageProvider, isAdmin, isDark),
          ),
        ],
      ),
    );
  }

  TableRow _buildTableHeader(
    LanguageProvider languageProvider,
    bool isAdmin,
    bool isDark,
  ) {
    return TableRow(
      decoration: BoxDecoration(
        color: isDark ? AppTheme.darkInput : const Color(0xFFF9FAFB),
        border: Border(
          bottom: BorderSide(
            color: isDark ? AppTheme.darkBorder : AppTheme.lightBorder,
          ),
        ),
      ),
      children: [
        _buildHeaderCell(languageProvider.translate('name')),
        _buildHeaderCell(
          '${languageProvider.translate('form')} & ${languageProvider.translate('packaging')}',
        ),
        _buildHeaderCell(languageProvider.translate('details')),
        _buildHeaderCell(
          languageProvider.translate('price'),
          align: TextAlign.right,
        ),
        _buildHeaderCell(
          languageProvider.translate('quantity'),
          align: TextAlign.right,
        ),
        _buildHeaderCell(languageProvider.translate('status')),
        if (isAdmin)
          _buildHeaderCell(
            languageProvider.translate('actions'),
            align: TextAlign.right,
          ),
      ],
    );
  }

  Widget _buildHeaderCell(String text, {TextAlign align = TextAlign.left}) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Text(
        text,
        textAlign: align,
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
          fontWeight: FontWeight.w500,
          color: Theme.of(context).brightness == Brightness.dark
              ? AppTheme.darkSidebarText
              : AppTheme.lightSidebarText,
        ),
      ),
    );
  }

  TableRow _buildTableRow(
    Medicine medicine,
    LanguageProvider languageProvider,
    bool isAdmin,
    bool isDark,
  ) {
    return TableRow(
      decoration: BoxDecoration(
        color: Colors.transparent,
        border: Border(
          bottom: BorderSide(
            color: isDark ? AppTheme.darkBorder : AppTheme.lightBorder,
          ),
        ),
      ),
      children: [
        // Nom
        _buildCell(
          Text(
            medicine.name,
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
        ),

        // Forme & Conditionnement
        _buildCell(
          Text('${medicine.dosageForm ?? '-'} / ${medicine.packaging ?? '-'}'),
        ),

        // Détails
        _buildCell(
          Text(
            medicine.packaging != null
                ? '1 ${medicine.packaging} = ${medicine.unitsPerPackaging} un.'
                : '-',
          ),
        ),

        // Prix
        _buildCell(
          Text(
            'F${medicine.priceSell.toStringAsFixed(2)}',
            textAlign: TextAlign.right,
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
          align: Alignment.centerRight,
        ),

        // Quantité (formatée multi-niveaux)
        _buildCell(
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                medicine.formatStock(),
                style: const TextStyle(fontWeight: FontWeight.w500),
              ),
              Text(
                '(${medicine.quantity} ${languageProvider.translate('total')})',
                style: TextStyle(fontSize: 10, color: Colors.grey[600]),
              ),
            ],
          ),
          align: Alignment.centerRight,
        ),

        // Statut (badges)
        _buildCell(_buildStatusBadges(medicine, languageProvider)),

        // Actions (admin only)
        if (isAdmin)
          _buildCell(
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                IconButton(
                  onPressed: () => _showMedicineDialog(medicine: medicine),
                  icon: const Icon(Icons.edit, size: 18),
                  tooltip: languageProvider.translate('edit'),
                  color: AppTheme.primaryColor,
                ),
                IconButton(
                  onPressed: () => _deleteMedicine(medicine, languageProvider),
                  icon: const Icon(Icons.delete, size: 18),
                  tooltip: languageProvider.translate('delete'),
                  color: AppTheme.dangerColor,
                ),
              ],
            ),
            align: Alignment.centerRight,
          ),
      ],
    );
  }

  Widget _buildCell(Widget child, {Alignment align = Alignment.centerLeft}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      alignment: align,
      child: child,
    );
  }

  Widget _buildStatusBadges(Medicine medicine, LanguageProvider lp) {
    return Wrap(
      spacing: 8,
      children: [
        if (medicine.isLowStock)
          _buildBadge(lp.translate('lowStock'), AppTheme.dangerColor),
        if (medicine.isExpired)
          _buildBadge(lp.translate('expired'), AppTheme.warningColor),
        if (!medicine.isLowStock && !medicine.isExpired)
          _buildBadge('OK', AppTheme.successColor),
      ],
    );
  }

  Widget _buildBadge(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
        overflow: TextOverflow.ellipsis,
      ),
    );
  }

  Widget _buildPagination(LanguageProvider lp) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            '${lp.translate('total')}: $_totalItems ${lp.translate('medicines')}',
          ),
          Row(
            children: [
              IconButton(
                onPressed: _currentPage > 1
                    ? () {
                        setState(() => _currentPage--);
                        _loadMedicines();
                      }
                    : null,
                icon: const Icon(Icons.chevron_left),
              ),
              Text('${lp.translate('page')} $_currentPage / $_totalPages'),
              IconButton(
                onPressed: _currentPage < _totalPages
                    ? () {
                        setState(() => _currentPage++);
                        _loadMedicines();
                      }
                    : null,
                icon: const Icon(Icons.chevron_right),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingView(LanguageProvider languageProvider) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 16),
          Text(languageProvider.translate('loading')),
        ],
      ),
    );
  }

  Widget _buildErrorView(LanguageProvider lp) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.error_outline,
            size: 64,
            color: AppTheme.dangerColor,
          ),
          const SizedBox(height: 16),
          Text(lp.translate('loadingError')),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _loadMedicines,
            icon: const Icon(Icons.refresh),
            label: Text(lp.translate('tryAgain')),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyView(LanguageProvider lp) {
    return Center(child: Text(lp.translate('noMedicinesFound')));
  }
}
