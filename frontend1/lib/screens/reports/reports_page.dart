import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:intl/intl.dart';
import 'package:printing/printing.dart';
import 'package:pdf/pdf.dart';

import 'package:frontend1/services/reports_service.dart';
import 'package:open_file/open_file.dart';
import 'package:provider/provider.dart';
import 'package:frontend1/providers/language_provider.dart';

// ══════════════════════════════════════════════════════════════════
// Imports conditionnels pour le téléchargement web
// ══════════════════════════════════════════════════════════════════
import 'package:frontend1/services/reports_service_web.dart'
    if (dart.library.io) 'package:frontend1/services/reports_service_io.dart'
    as platform_save;

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

  // ══════════════════════════════════════════════════════════════════
  // DOWNLOAD HANDLER (existing logic preserved)
  // ══════════════════════════════════════════════════════════════════

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
          final isWebDownload = kIsWeb;
          final fileName = path.split('/').last.split('\\').last;

          ScaffoldMessenger.of(context).hideCurrentSnackBar();
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Row(
                children: [
                  const Icon(Icons.check_circle, color: Colors.white, size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isWebDownload
                              ? 'Téléchargement en cours...'
                              : 'Fichier sauvegardé et ouvert',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                        Text(
                          fileName,
                          style: const TextStyle(
                            fontSize: 11,
                            color: Colors.white70,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              backgroundColor: Colors.green[700],
              duration: const Duration(seconds: 5),
              action: isWebDownload
                  ? null
                  : SnackBarAction(
                      label: 'Rouvrir',
                      textColor: Colors.white,
                      onPressed: () => OpenFile.open(path),
                    ),
            ),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(lp.translate('downloadCancelled')),
              backgroundColor: Colors.orange,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${lp.translate('error')}: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) s(false);
    }
  }

  // ══════════════════════════════════════════════════════════════════
  // PDF PREVIEW — Opens a full-screen dialog with PDF viewer
  // ══════════════════════════════════════════════════════════════════

  Future<void> _previewPDF({
    required String title,
    required Future<Uint8List> Function() fetchPdfBytes,
    required Future<String?> Function() downloadPdf,
    required Function(bool) setLoading,
    required LanguageProvider lp,
  }) async {
    setLoading(true);
    try {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              ),
              const SizedBox(width: 12),
              Text('Génération du rapport $title...'),
            ],
          ),
          duration: const Duration(seconds: 10),
        ),
      );

      final pdfBytes = await fetchPdfBytes();

      if (!mounted) return;
      ScaffoldMessenger.of(context).hideCurrentSnackBar();

      // Open the PDF preview dialog
      await showDialog(
        context: context,
        barrierDismissible: false,
        builder: (ctx) => _PdfPreviewDialog(
          title: title,
          pdfBytes: pdfBytes,
          onDownload: () async {
            Navigator.of(ctx).pop();
            await _dl(
              '$title PDF',
              downloadPdf,
              setLoading,
              lp,
            );
          },
        ),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).hideCurrentSnackBar();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erreur: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) setLoading(false);
    }
  }

  // ══════════════════════════════════════════════════════════════════
  // BUILD
  // ══════════════════════════════════════════════════════════════════

  @override
  Widget build(BuildContext context) {
    final lp = Provider.of<LanguageProvider>(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Page header
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Colors.indigo.shade600, Colors.blue.shade500],
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.assessment, color: Colors.white, size: 28),
              ),
              const SizedBox(width: 16),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    lp.translate('reports'),
                    style: const TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    'Visualisez et téléchargez vos rapports',
                    style: TextStyle(
                      fontSize: 14,
                      color: isDark ? Colors.grey[400] : Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 8),

          // Info banner
          Container(
            margin: const EdgeInsets.only(bottom: 24),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.blue.shade50.withValues(alpha: isDark ? 0.1 : 1.0),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: Colors.blue.shade200.withValues(alpha: 0.5)),
            ),
            child: Row(
              children: [
                Icon(Icons.info_outline, color: Colors.blue.shade600, size: 20),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Cliquez sur 👁 Visualiser pour prévisualiser le PDF dans le navigateur, puis téléchargez-le si besoin.',
                    style: TextStyle(
                      fontSize: 13,
                      color: isDark ? Colors.blue.shade200 : Colors.blue.shade800,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Report cards
          Wrap(
            spacing: 24,
            runSpacing: 24,
            children: [
              // ── STOCK CARD ──
              _buildReportCard(
                title: lp.translate('stock'),
                subtitle: 'État actuel de l\'inventaire',
                icon: Icons.inventory_2_rounded,
                gradientColors: [Colors.blue.shade600, Colors.cyan.shade400],
                isLoading: _loadingStock,
                lp: lp,
                isDark: isDark,
                onPreview: () => _previewPDF(
                  title: 'Stock',
                  fetchPdfBytes: _reportsService.previewStockPDF,
                  downloadPdf: _reportsService.downloadStockPDF,
                  setLoading: (v) => setState(() => _loadingStock = v),
                  lp: lp,
                ),
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

              // ── SALES CARD ──
              _buildReportCard(
                title: lp.translate('sales'),
                subtitle: 'Historique des ventes par période',
                icon: Icons.shopping_bag_rounded,
                gradientColors: [Colors.green.shade600, Colors.teal.shade400],
                isLoading: _loadingSales,
                lp: lp,
                isDark: isDark,
                extra: _dts(_salesStart, _salesEnd, lp),
                onPreview: () => _previewPDF(
                  title: 'Ventes',
                  fetchPdfBytes: () => _reportsService.previewSalesPDF(
                    _salesStart.text,
                    _salesEnd.text,
                  ),
                  downloadPdf: () => _reportsService.downloadSalesPDF(
                    _salesStart.text,
                    _salesEnd.text,
                  ),
                  setLoading: (v) => setState(() => _loadingSales = v),
                  lp: lp,
                ),
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

              // ── FINANCIAL CARD ──
              _buildReportCard(
                title: lp.translate('financial'),
                subtitle: 'Bilan financier détaillé',
                icon: Icons.attach_money_rounded,
                gradientColors: [Colors.orange.shade600, Colors.amber.shade400],
                isLoading: _loadingFinancial,
                lp: lp,
                isDark: isDark,
                extra: _dts(_finStart, _finEnd, lp),
                onPreview: () => _previewPDF(
                  title: 'Financier',
                  fetchPdfBytes: () => _reportsService.previewFinancialPDF(
                    _finStart.text,
                    _finEnd.text,
                  ),
                  downloadPdf: () => _reportsService.generateFinancialPDF(
                    _finStart.text,
                    _finEnd.text,
                  ),
                  setLoading: (v) => setState(() => _loadingFinancial = v),
                  lp: lp,
                ),
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

  // ══════════════════════════════════════════════════════════════════
  // REPORT CARD WIDGET — Premium design with gradient header
  // ══════════════════════════════════════════════════════════════════

  Widget _buildReportCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required List<Color> gradientColors,
    required bool isLoading,
    required LanguageProvider lp,
    required bool isDark,
    required VoidCallback onPreview,
    Widget? extra,
    Widget? downloadRow,
  }) {
    return SizedBox(
      width: 340,
      child: Card(
        elevation: 4,
        shadowColor: gradientColors[0].withValues(alpha: 0.3),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Gradient header
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: gradientColors,
                ),
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(16),
                  topRight: Radius.circular(16),
                ),
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(icon, size: 28, color: Colors.white),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          title,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          subtitle,
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.white.withValues(alpha: 0.85),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Body
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  // Date filters (if any)
                  if (extra != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: extra,
                    ),

                  // Preview button — prominent
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: isLoading ? null : onPreview,
                      icon: isLoading
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.visibility_rounded, size: 20),
                      label: Text(
                        isLoading ? 'Chargement...' : '👁 Visualiser le PDF',
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                        ),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: gradientColors[0],
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                        elevation: 2,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Divider with label
                  Row(
                    children: [
                      Expanded(child: Divider(color: Colors.grey.shade300)),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 10),
                        child: Text(
                          'Télécharger',
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.grey.shade500,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                      Expanded(child: Divider(color: Colors.grey.shade300)),
                    ],
                  ),
                  const SizedBox(height: 10),

                  // Download row
                  if (downloadRow != null) downloadRow,
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ══════════════════════════════════════════════════════════════════
  // DOWNLOAD ROW — PDF / Excel / Word buttons
  // ══════════════════════════════════════════════════════════════════

  Widget _buildDownloadRow(
    String labelPrefix,
    Future<String?> Function() pdfFunc,
    Future<String?> Function() excelFunc,
    Future<String?> Function() wordFunc,
    void Function(bool) setLoading,
    bool isLoading,
    LanguageProvider lp,
  ) {
    if (isLoading) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 8),
        child: CircularProgressIndicator(),
      );
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _downloadBtn(
          Icons.picture_as_pdf_rounded,
          Colors.red.shade600,
          'PDF',
          () => _dl('$labelPrefix PDF', pdfFunc, setLoading, lp),
        ),
        _downloadBtn(
          Icons.table_chart_rounded,
          Colors.green.shade600,
          'Excel',
          () => _dl('$labelPrefix Excel', excelFunc, setLoading, lp),
        ),
        _downloadBtn(
          Icons.description_rounded,
          Colors.blue.shade600,
          'Word',
          () => _dl('$labelPrefix Word', wordFunc, setLoading, lp),
        ),
      ],
    );
  }

  // ══════════════════════════════════════════════════════════════════
  // DATE PICKER FIELDS
  // ══════════════════════════════════════════════════════════════════

  Widget _dts(
    TextEditingController s,
    TextEditingController e,
    LanguageProvider lp,
  ) =>
      Row(
        children: [
          Expanded(child: _d(s, lp.translate('start'))),
          const SizedBox(width: 10),
          Expanded(child: _d(e, lp.translate('end'))),
        ],
      );

  Widget _d(TextEditingController c, String l) => TextField(
        controller: c,
        decoration: InputDecoration(
          labelText: l,
          isDense: true,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
          prefixIcon: const Icon(Icons.calendar_today, size: 16),
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
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

  // ══════════════════════════════════════════════════════════════════
  // DOWNLOAD BUTTON
  // ══════════════════════════════════════════════════════════════════

  Widget _downloadBtn(
    IconData icon,
    Color color,
    String tooltip,
    VoidCallback onTap,
  ) {
    return Tooltip(
      message: 'Télécharger $tooltip',
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(10),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: color.withValues(alpha: 0.3)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 6),
              Text(
                tooltip,
                style: TextStyle(
                  color: color,
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ════════════════════════════════════════════════════════════════════
// PDF PREVIEW DIALOG — Full-screen PDF viewer with toolbar
// ════════════════════════════════════════════════════════════════════

class _PdfPreviewDialog extends StatelessWidget {
  final String title;
  final Uint8List pdfBytes;
  final VoidCallback onDownload;

  const _PdfPreviewDialog({
    required this.title,
    required this.pdfBytes,
    required this.onDownload,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Dialog(
      insetPadding: const EdgeInsets.all(16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: SizedBox(
        width: MediaQuery.of(context).size.width * 0.9,
        height: MediaQuery.of(context).size.height * 0.9,
        child: Column(
          children: [
            // ── Toolbar ──
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.indigo.shade700, Colors.blue.shade600],
                ),
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(16),
                  topRight: Radius.circular(16),
                ),
              ),
              child: Row(
                children: [
                  const Icon(Icons.picture_as_pdf, color: Colors.white, size: 24),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Rapport $title',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        Text(
                          'Aperçu PDF — ${DateFormat('dd/MM/yyyy HH:mm').format(DateTime.now())}',
                          style: TextStyle(
                            color: Colors.white.withValues(alpha: 0.8),
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Download button
                  _toolbarButton(
                    icon: Icons.download_rounded,
                    label: 'Télécharger',
                    color: Colors.green.shade400,
                    onTap: onDownload,
                  ),
                  const SizedBox(width: 8),
                  // Print button
                  _toolbarButton(
                    icon: Icons.print_rounded,
                    label: 'Imprimer',
                    color: Colors.orange.shade300,
                    onTap: () {
                      Printing.layoutPdf(
                        onLayout: (_) async => pdfBytes,
                        name: 'Rapport_$title',
                      );
                    },
                  ),
                  const SizedBox(width: 8),
                  // Close button
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white),
                    onPressed: () => Navigator.of(context).pop(),
                    tooltip: 'Fermer',
                    style: IconButton.styleFrom(
                      backgroundColor: Colors.white.withValues(alpha: 0.15),
                    ),
                  ),
                ],
              ),
            ),

            // ── PDF Viewer ──
            Expanded(
              child: Container(
                color: isDark ? Colors.grey.shade900 : Colors.grey.shade200,
                child: PdfPreview(
                  build: (_) async => pdfBytes,
                  canChangeOrientation: false,
                  canChangePageFormat: false,
                  canDebug: false,
                  allowPrinting: false,
                  allowSharing: false,
                  maxPageWidth: 700,
                  pdfFileName: 'rapport_$title.pdf',
                  loadingWidget: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        CircularProgressIndicator(
                          color: Colors.indigo.shade400,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Rendu du PDF en cours...',
                          style: TextStyle(
                            color: isDark ? Colors.grey.shade400 : Colors.grey.shade600,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _toolbarButton({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.white.withValues(alpha: 0.2)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: color, size: 18),
            const SizedBox(width: 6),
            Text(
              label,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 13,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
