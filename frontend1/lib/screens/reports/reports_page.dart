import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import 'package:frontend1/services/reports_service.dart';
import 'package:open_file/open_file.dart';
import 'package:provider/provider.dart';
import 'package:frontend1/providers/language_provider.dart';

class ReportsPage extends StatefulWidget {
  const ReportsPage({super.key});

  @override
  State<ReportsPage> createState() => _ReportsPageState();
}

class _ReportsPageState extends State<ReportsPage> {
  final ReportsService _reportsService = ReportsService();

  bool _loadingStock = false;
  bool _loadingSales = false;
  bool _loadingFinancial = false;

  final _salesStart = TextEditingController();
  final _salesEnd = TextEditingController();
  final _finStart = TextEditingController();
  final _finEnd = TextEditingController();

  Future<void> _dl(
    String t,
    Future<String?> Function() f,
    Function(bool) s,
    LanguageProvider lp,
  ) async {
    s(true);
    try {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('${lp.translate('generating')} $t...')),
      );

      final path = await f();

      if (path != null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(lp.translate('fileSavedSuccess')),
              backgroundColor: Colors.green,
              action: SnackBarAction(
                label: lp.translate('open'),
                textColor: Colors.white,
                onPressed: () => OpenFile.open(path),
              ),
            ),
          );
          // Optionnel: Ouvrir directement
          // OpenFile.open(path);
        }
      } else {
        // Annulation utilisateur
        if (mounted)
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(lp.translate('downloadCancelled')),
              backgroundColor: Colors.orange,
            ),
          );
      }
    } catch (e) {
      if (mounted)
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${lp.translate('error')}: $e'),
            backgroundColor: Colors.red,
          ),
        );
    } finally {
      if (mounted) s(false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final lp = Provider.of<LanguageProvider>(context);
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            lp.translate('reports'),
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),
          Wrap(
            spacing: 24,
            runSpacing: 24,
            children: [
              _card(
                lp.translate('stock'),
                Icons.inventory,
                Colors.blue,
                _loadingStock,
                lp,
                downloadRow: _buildDownloadRow(
                  'Stock',
                  _reportsService.downloadStockPDF,
                  _reportsService.downloadStockExcel,
                  _reportsService.downloadStockWord,
                  (v) => setState(() => _loadingStock = v),
                  _loadingStock,
                  lp,
                ),
              ),
              _card(
                lp.translate('sales'),
                Icons.shopping_bag,
                Colors.green,
                _loadingSales,
                lp,
                extra: _dts(_salesStart, _salesEnd, lp),
                downloadRow: _buildDownloadRow(
                  'Ventes',
                  () => _reportsService.downloadSalesPDF(
                    _salesStart.text,
                    _salesEnd.text,
                  ),
                  () => _reportsService.downloadSalesExcel(
                    _salesStart.text,
                    _salesEnd.text,
                  ),
                  () => _reportsService.downloadSalesWord(
                    _salesStart.text,
                    _salesEnd.text,
                  ),
                  (v) => setState(() => _loadingSales = v),
                  _loadingSales,
                  lp,
                ),
              ),
              _card(
                lp.translate('financial'),
                Icons.attach_money,
                Colors.orange,
                _loadingFinancial,
                lp,
                extra: _dts(_finStart, _finEnd, lp),
                downloadRow: _buildDownloadRow(
                  'Financier',
                  () => _reportsService.generateFinancialPDF(
                    _finStart.text,
                    _finEnd.text,
                  ),
                  () => _reportsService.generateFinancialExcel(
                    _finStart.text,
                    _finEnd.text,
                  ),
                  () => _reportsService.generateFinancialWord(
                    _finStart.text,
                    _finEnd.text,
                  ),
                  (v) => setState(() => _loadingFinancial = v),
                  _loadingFinancial,
                  lp,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _card(
    String t,
    IconData i,
    Color c,
    bool l,
    // VoidCallback? a, // REMOVED: Action is now handled via extra or downloadRow
    LanguageProvider lp, {
    Widget? extra,
    Widget? downloadRow, // Added: Custom download row
  }) {
    return SizedBox(
      width: 300,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Icon(i, size: 40, color: c),
              Text(
                t,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (extra != null)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  child: extra,
                ),
              const SizedBox(height: 16),
              // If a custom download row is provided, use it. Otherwise no button (or we could keep fallback)
              // Since we are refactoring all cards to use specific rows, we can just render downloadRow.
              if (downloadRow != null) downloadRow,
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDownloadRow(
    String labelPrefix,
    Future<String?> Function() pdfFunc,
    Future<String?> Function() excelFunc,
    Future<String?> Function() wordFunc,
    void Function(bool) setLoading,
    bool isLoading,
    LanguageProvider lp,
  ) {
    if (isLoading) return const CircularProgressIndicator();

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _iconBtn(
          Icons.picture_as_pdf,
          Colors.red,
          'PDF',
          () => _dl('$labelPrefix PDF', pdfFunc, setLoading, lp),
        ),
        _iconBtn(
          Icons.table_chart,
          Colors.green,
          'Excel',
          () => _dl('$labelPrefix Excel', excelFunc, setLoading, lp),
        ),
        _iconBtn(
          Icons.description,
          Colors.blue,
          'Word',
          () => _dl('$labelPrefix Word', wordFunc, setLoading, lp),
        ),
      ],
    );
  }

  Widget _dts(
    TextEditingController s,
    TextEditingController e,
    LanguageProvider lp,
  ) => Column(
    children: [
      _d(s, lp.translate('start')),
      const SizedBox(height: 8),
      _d(e, lp.translate('end')),
    ],
  );
  Widget _d(TextEditingController c, String l) => TextField(
    controller: c,
    decoration: InputDecoration(
      labelText: l,
      isDense: true,
      border: const OutlineInputBorder(),
    ),
    readOnly: true,
    onTap: () async {
      final d = await showDatePicker(
        context: context,
        initialDate: DateTime.now(),
        firstDate: DateTime(2020),
        lastDate: DateTime(2030),
      );
      if (d != null) c.text = DateFormat('yyyy-MM-dd').format(d);
    },
  );

  Widget _iconBtn(
    IconData icon,
    Color color,
    String tooltip,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: _loadingFinancial ? null : onTap,
      child: Tooltip(
        message: tooltip,
        child: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: color.withOpacity(0.5)),
          ),
          child: Column(
            children: [
              Icon(icon, color: color),
              const SizedBox(height: 4),
              Text(tooltip, style: TextStyle(color: color, fontSize: 12)),
            ],
          ),
        ),
      ),
    );
  }
}
