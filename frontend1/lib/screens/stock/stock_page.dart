import 'package:flutter/material.dart';
import 'package:frontend1/core/theme.dart';
import 'package:frontend1/models/medicine.dart';
import 'package:frontend1/services/stock_service.dart';
import 'package:frontend1/screens/stock/add_medicine_wizard.dart';
import 'package:frontend1/providers/language_provider.dart';
import 'package:frontend1/providers/auth_provider.dart';
import 'package:provider/provider.dart';
import 'package:frontend1/screens/medicine_pricing/medicine_pricing_page.dart';

/// Page de gestion du stock des médicaments
/// Avec onglets Stock et Gestion des Prix
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
    _searchController.addListener(_onSearchChanged);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged() {
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

  /// Ouvre le nouveau wizard d'ajout/édition de médicament
  Future<void> _showMedicineDialog({Medicine? medicine}) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => const AddMedicineWizard(),
      barrierDismissible: false,
      barrierColor: Colors.black.withOpacity(0.6),
    );

    if (result == true) {
      _loadMedicines();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Row(
              children: [
                Icon(Icons.check_circle_rounded, color: Colors.white, size: 18),
                SizedBox(width: 10),
                Text('Médicament enregistré avec succès !'),
              ],
            ),
            backgroundColor: AppTheme.successColor,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            duration: const Duration(seconds: 3),
          ),
        );
      }
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
        _buildHeader(languageProvider, isAdmin),
        const SizedBox(height: 24),
        _buildSearchBar(languageProvider),
        const SizedBox(height: 24),
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
        Row(
          children: [
            // Bouton Journal des Mouvements
            OutlinedButton.icon(
              onPressed: () {
                Navigator.of(context).pushNamed('/stock-movements');
              },
              icon: const Icon(Icons.swap_vert, size: 18),
              label: const Text('Journal Mouvements'),
            ),
            const SizedBox(width: 12),
            // Bouton Gestion des Prix
            OutlinedButton.icon(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => const MedicinePricingPage(),
                  ),
                );
              },
              icon: const Icon(Icons.price_change, size: 18),
              label: const Text('Gestion des Prix'),
            ),
            if (isAdmin) ...[
              const SizedBox(width: 12),
              ElevatedButton.icon(
                onPressed: () => _showMedicineDialog(),
                icon: const Icon(Icons.add),
                label: Text(languageProvider.translate('addMedicine')),
              ),
            ],
          ],
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

    final colWidths = <int, TableColumnWidth>{
      0: const FlexColumnWidth(2.5), // Nom
      1: const FlexColumnWidth(1.2), // Fournisseur
      2: const FlexColumnWidth(1.3), // Date d'expiration
      3: const FlexColumnWidth(1.8), // Quantité restante
      4: const FlexColumnWidth(1.5), // Prix de vente
      5: const FlexColumnWidth(1),   // Statut
      if (isAdmin) 6: const FixedColumnWidth(100), // Actions
    };

    return Column(
      children: [
        // ─── En-tête FIXE (ne scrolle pas) ───
        Table(
          columnWidths: colWidths,
          children: [
            _buildTableHeader(languageProvider, isAdmin, isDark),
          ],
        ),

        // ─── Corps scrollable ───
        Expanded(
          child: SingleChildScrollView(
            child: Table(
              columnWidths: colWidths,
              border: TableBorder(
                horizontalInside: BorderSide(
                  color: isDark ? AppTheme.darkBorder : AppTheme.lightBorder,
                ),
              ),
              children: [
                ..._medicines.map(
                  (medicine) =>
                      _buildTableRow(medicine, languageProvider, isAdmin, isDark),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  TableRow _buildTableHeader(
    LanguageProvider languageProvider,
    bool isAdmin,
    bool isDark,
  ) {
    return TableRow(
      decoration: BoxDecoration(
        color: isDark
            ? AppTheme.primaryColor.withValues(alpha: 0.15)
            : AppTheme.primaryColor.withValues(alpha: 0.08),
        border: Border(
          bottom: BorderSide(
            color: AppTheme.primaryColor.withValues(alpha: 0.4),
            width: 2,
          ),
        ),
      ),
      children: [
        _buildHeaderCell('Nom du médicament'),
        _buildHeaderCell('Fournisseur'),
        _buildHeaderCell('Date d\'expiration'),
        _buildHeaderCell('Quantité restante', align: TextAlign.right),
        _buildHeaderCell('Prix de vente', align: TextAlign.right),
        _buildHeaderCell('Statut'),
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
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
      child: Text(
        text.toUpperCase(),
        textAlign: align,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
          fontWeight: FontWeight.w700,
          fontSize: 11,
          letterSpacing: 0.5,
          color: AppTheme.primaryColor,
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
    // Calcul jours avant expiration
    int? joursRestants;
    if (medicine.expiryDate != null) {
      joursRestants = medicine.expiryDate!.difference(DateTime.now()).inDays;
    }

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
        // ── Nom du médicament ──
        _buildCell(
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                medicine.name,
                style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                overflow: TextOverflow.ellipsis,
              ),
              if (medicine.dci != null && medicine.dci!.isNotEmpty)
                Text(
                  medicine.dci!,
                  style: TextStyle(fontSize: 11, color: Colors.grey[500], fontStyle: FontStyle.italic),
                  overflow: TextOverflow.ellipsis,
                ),
              Row(
                children: [
                  if (medicine.dosageForm != null) ...[
                    Container(
                      margin: const EdgeInsets.only(top: 2),
                      padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                      decoration: BoxDecoration(
                        color: Colors.blue.withValues(alpha: 0.08),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        medicine.dosageForm!,
                        style: const TextStyle(fontSize: 10, color: Colors.blue),
                      ),
                    ),
                    const SizedBox(width: 4),
                  ],
                  if (medicine.code.isNotEmpty)
                    Container(
                      margin: const EdgeInsets.only(top: 2),
                      padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                      decoration: BoxDecoration(
                        color: Colors.grey.withValues(alpha: 0.08),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        medicine.code,
                        style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),

        // ── Fournisseur ──
        _buildCell(
          Text(
            medicine.fournisseur ?? '-',
            style: TextStyle(fontSize: 12, color: Colors.grey[700]),
            overflow: TextOverflow.ellipsis,
          ),
        ),

        // ── Date d'expiration ──
        _buildCell(
          medicine.expiryDate != null
              ? Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      '${medicine.expiryDate!.day.toString().padLeft(2, '0')}/${medicine.expiryDate!.month.toString().padLeft(2, '0')}/${medicine.expiryDate!.year}',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                        color: medicine.isExpired
                            ? AppTheme.dangerColor
                            : (joursRestants != null && joursRestants <= 90)
                                ? AppTheme.warningColor
                                : null,
                      ),
                    ),
                    Container(
                      margin: const EdgeInsets.only(top: 2),
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: medicine.isExpired
                            ? AppTheme.dangerColor.withValues(alpha: 0.1)
                            : (joursRestants != null && joursRestants <= 90)
                                ? AppTheme.warningColor.withValues(alpha: 0.1)
                                : AppTheme.successColor.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        medicine.isExpired
                            ? 'Expiré'
                            : (joursRestants != null && joursRestants <= 90)
                                ? '$joursRestants j restants'
                                : '$joursRestants j',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w600,
                          color: medicine.isExpired
                              ? AppTheme.dangerColor
                              : (joursRestants != null && joursRestants <= 90)
                                  ? AppTheme.warningColor
                                  : AppTheme.successColor,
                        ),
                      ),
                    ),
                  ],
                )
              : Text('-', style: TextStyle(color: Colors.grey[400])),
        ),

        // ── Quantité restante (décomposée par conditionnement) ──
        _buildCell(
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                medicine.formatStock(),
                style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 12),
                textAlign: TextAlign.right,
              ),
              Text(
                '${medicine.quantity} unités total',
                style: TextStyle(fontSize: 10, color: Colors.grey[500]),
                textAlign: TextAlign.right,
              ),
              if (medicine.batchCount > 0)
                Container(
                  margin: const EdgeInsets.only(top: 2),
                  padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryColor.withValues(alpha: 0.08),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    '${medicine.batchCount} lot${medicine.batchCount > 1 ? 's' : ''}',
                    style: const TextStyle(fontSize: 9, color: AppTheme.primaryColor),
                  ),
                ),
            ],
          ),
          align: Alignment.centerRight,
        ),

        // ── Prix de vente (par conditionnement) ──
        _buildCell(
          _buildPricingLevels(medicine),
          align: Alignment.centerRight,
        ),

        // ── Statut ──
        _buildCell(_buildStatusBadges(medicine, languageProvider)),

        // ── Actions (admin) ──
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
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      alignment: align,
      child: child,
    );
  }

  /// Affiche les prix de vente par conditionnement
  Widget _buildPricingLevels(Medicine medicine) {
    String fmt(double v) {
      if (v <= 0) return '-';
      if (v >= 1000) return '${(v / 1000).toStringAsFixed(v % 1000 == 0 ? 0 : 1)}k';
      return v.toStringAsFixed(v == v.roundToDouble() ? 0 : 1);
    }

    Widget priceLine(String label, Color color, double pv) {
      if (pv <= 0) return const SizedBox.shrink();
      return Padding(
        padding: const EdgeInsets.only(bottom: 3),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.end,
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                label,
                style: TextStyle(fontSize: 9, fontWeight: FontWeight.w600, color: color),
              ),
            ),
            const SizedBox(width: 6),
            Text(
              '${fmt(pv)} FBu',
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
            ),
          ],
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      mainAxisSize: MainAxisSize.min,
      children: [
        priceLine('Unité', Colors.teal, medicine.prixVenteUnite),
        priceLine('Plaq.', Colors.indigo, medicine.prixVentePlaquette),
        priceLine('Boîte', Colors.deepPurple, medicine.prixVenteBoite),
        priceLine('Carton', Colors.brown, medicine.prixVenteCarton),
      ],
    );
  }

  /// Calcule et affiche le bénéfice (marge) par niveau de conditionnement
  Widget _buildMarginColumn(Medicine medicine) {
    String fmt(double v) {
      if (v <= 0) return '-';
      if (v >= 1000) return '${(v / 1000).toStringAsFixed(v % 1000 == 0 ? 0 : 1)}k';
      return v.toStringAsFixed(v == v.roundToDouble() ? 0 : 1);
    }

    // Calcul marge par unité (base)
    double margeUnite = 0;
    if (medicine.prixVenteUnite > 0 && medicine.prixAchatUnite > 0) {
      margeUnite = medicine.prixVenteUnite - medicine.prixAchatUnite;
    }

    // Bénéfice total estimé = marge par unité × quantité totale
    final beneficeTotal = margeUnite * medicine.quantity;
    final margePercent = medicine.prixAchatUnite > 0
        ? (margeUnite / medicine.prixAchatUnite * 100)
        : 0.0;

    final isPositive = beneficeTotal > 0;
    final color = isPositive ? AppTheme.successColor : AppTheme.dangerColor;

    if (margeUnite <= 0 && beneficeTotal <= 0) {
      return Text(
        '-',
        style: TextStyle(color: Colors.grey[400], fontSize: 12),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      mainAxisSize: MainAxisSize.min,
      children: [
        // Marge par unité
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              isPositive ? Icons.trending_up : Icons.trending_down,
              size: 14,
              color: color,
            ),
            const SizedBox(width: 4),
            Text(
              '${fmt(margeUnite)} /u',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w500,
                color: color,
              ),
            ),
          ],
        ),
        const SizedBox(height: 2),
        // Pourcentage de marge
        Text(
          '${margePercent.toStringAsFixed(1)}%',
          style: TextStyle(
            fontSize: 10,
            color: color.withValues(alpha: 0.8),
          ),
        ),
        const SizedBox(height: 2),
        // Bénéfice total
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            '${fmt(beneficeTotal)} FBu',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatusBadges(Medicine medicine, LanguageProvider lp) {
    return Wrap(
      spacing: 4,
      runSpacing: 4,
      children: [
        if (medicine.batchCount > 0)
          _buildBadge('${medicine.batchCount} lot${medicine.batchCount > 1 ? 's' : ''}', AppTheme.primaryColor),
        if (medicine.isLowStock)
          _buildBadge(lp.translate('lowStock'), AppTheme.dangerColor),
        if (medicine.isExpired)
          _buildBadge(lp.translate('expired'), AppTheme.warningColor),
        if (!medicine.isLowStock && !medicine.isExpired && medicine.batchCount == 0)
          _buildBadge('OK', AppTheme.successColor),
      ],
    );
  }

  Widget _buildBadge(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.3)),
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
