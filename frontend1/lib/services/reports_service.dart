import 'dart:io';
import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:frontend1/services/api_service.dart';
import 'package:excel/excel.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';

class FinancialReportItem {
  final String name;
  final int quantity;
  final double buyPrice;
  final double sellPrice; // Current sell price (approx)
  final double revenue;
  final double profit;

  FinancialReportItem({
    required this.name,
    required this.quantity,
    required this.buyPrice,
    required this.sellPrice,
    required this.revenue,
    required this.profit,
  });
}

class ReportsService {
  final ApiService _apiService = ApiService();

  Future<String?> _saveFile(List<int> bytes, String defaultName) async {
    String? outputFile = await FilePicker.platform.saveFile(
      dialogTitle: 'Enregistrer le rapport',
      fileName: defaultName,
    );

    if (outputFile == null) return null;

    try {
      final file = File(outputFile);
      await file.writeAsBytes(bytes);
      return outputFile;
    } catch (e) {
      print('[ReportsService] Error saving file: $e');
      rethrow;
    }
  }

  // --- Data Fetching ---

  Future<List<FinancialReportItem>> _fetchFinancialData(
    String? startDate,
    String? endDate,
  ) async {
    // 1. Fetch Sales Stats
    final params = <String, dynamic>{};
    if (startDate != null && startDate.isNotEmpty)
      params['start_date'] = startDate;
    if (endDate != null && endDate.isNotEmpty) params['end_date'] = endDate;

    final statsResponse = await _apiService.get(
      '/sales/medicine-stats',
      queryParameters: params,
    );
    final statsList = (statsResponse.data as List).cast<Map<String, dynamic>>();

    if (statsList.isEmpty) return [];

    // 2. Fetch Medicines (to get Buy Price)
    // Optimization: If list is huge, this is heavy. But per user constraint "changes only for flutter", we do this.
    // Ideally we batch fetch or cache. For now, fetch all (high limit).
    final medicinesResponse = await _apiService.get(
      '/stock/medicines',
      queryParameters: {'limit': 10000},
    );
    final medicinesList = (medicinesResponse.data['items'] as List)
        .cast<Map<String, dynamic>>();

    // Create Map for quick lookup
    final medicineMap = {for (var m in medicinesList) m['id']: m};

    // 3. Join and Calculate
    List<FinancialReportItem> items = [];

    for (var stat in statsList) {
      final id = stat['id'];
      final qty = stat['total_quantity'] as int;
      final revenue = (stat['total_revenue'] as num).toDouble();

      final medicine = medicineMap[id];
      double buyPrice = 0.0;
      double sellPrice = 0.0; // Current sell price

      if (medicine != null) {
        buyPrice = (medicine['price_buy'] as num).toDouble();
        sellPrice = (medicine['price_sell'] as num).toDouble();
      }

      // Profit = Revenue - (Qty * BuyPrice)
      // Note: This assumes buy price was constant.
      double cost = qty * buyPrice;
      double profit = revenue - cost;

      items.add(
        FinancialReportItem(
          name: stat['name'],
          quantity: qty,
          buyPrice: buyPrice,
          sellPrice:
              sellPrice, // This is current unit sell price, or we could calc avg from revenue/qty
          revenue: revenue,
          profit: profit,
        ),
      );
    }

    return items;
  }

  // --- Generators ---

  // PDF
  // PDF
  Future<String?> generateFinancialPDF(
    String? startDate,
    String? endDate,
  ) async {
    final params = <String, dynamic>{};
    if (startDate != null && startDate.isNotEmpty)
      params['start_date'] = startDate;
    if (endDate != null && endDate.isNotEmpty) params['end_date'] = endDate;

    try {
      final response = await _apiService.get(
        '/reports/financial/pdf',
        queryParameters: params,
        options: Options(responseType: ResponseType.bytes),
      );

      final fileName =
          'rapport_financier_${startDate ?? "start"}_${endDate ?? "end"}.pdf';
      return await _saveFile(response.data as List<int>, fileName);
    } catch (e) {
      print('[ReportsService] Erreur generateFinancialPDF: $e');
      rethrow;
    }
  }

  // Excel
  Future<String?> generateFinancialExcel(
    String? startDate,
    String? endDate,
  ) async {
    try {
      final data = await _fetchFinancialData(startDate, endDate);
      var excel = Excel.createExcel();
      Sheet sheet = excel['Rapport'];

      // Headers
      sheet.appendRow([
        TextCellValue('Article'),
        TextCellValue('Quantité'),
        TextCellValue('P. Achat Total'),
        TextCellValue('P. Vente Total'),
        TextCellValue('Bénéfice'),
      ]);

      int totalQty = 0;
      double totalBuy = 0;
      double totalRev = 0;
      double totalProfit = 0;

      for (var item in data) {
        totalQty += item.quantity;
        totalBuy += (item.quantity * item.buyPrice);
        totalRev += item.revenue;
        totalProfit += item.profit;

        sheet.appendRow([
          TextCellValue(item.name),
          IntCellValue(item.quantity),
          DoubleCellValue(item.quantity * item.buyPrice),
          DoubleCellValue(item.revenue),
          DoubleCellValue(item.profit),
        ]);
      }

      // Total Row
      sheet.appendRow([
        TextCellValue('TOTAL'),
        IntCellValue(totalQty),
        DoubleCellValue(totalBuy),
        DoubleCellValue(totalRev),
        DoubleCellValue(totalProfit),
      ]);

      final bytes = excel.encode();
      if (bytes == null) return null;

      final name =
          'rapport_financier_${startDate ?? "start"}_${endDate ?? "end"}.xlsx';
      return await _saveFile(bytes, name);
    } catch (e) {
      print('[Reports] Excel Error: $e');
      rethrow;
    }
  }

  // Word (HTML method)
  Future<String?> generateFinancialWord(
    String? startDate,
    String? endDate,
  ) async {
    try {
      final data = await _fetchFinancialData(startDate, endDate);

      int totalQty = 0;
      double totalBuy = 0;
      double totalRev = 0;
      double totalProfit = 0;

      StringBuffer html = StringBuffer();
      html.write("""
      <html>
      <head><meta charset="UTF-8"></head>
      <body>
        <h1>Rapport Financier</h1>
        <p>Période: ${startDate ?? 'Début'} - ${endDate ?? 'Fin'}</p>
        <table border="1" style="border-collapse: collapse; width: 100%;">
          <tr style="background-color: #eee;">
            <th>Article</th>
            <th>Quantité</th>
            <th>P. Achat Total</th>
            <th>P. Vente Total</th>
            <th>Bénéfice</th>
          </tr>
      """);

      for (var item in data) {
        totalQty += item.quantity;
        totalBuy += (item.quantity * item.buyPrice);
        totalRev += item.revenue;
        totalProfit += item.profit;

        html.write("""
          <tr>
            <td>${item.name}</td>
            <td style="text-align: right;">${item.quantity}</td>
            <td style="text-align: right;">${(item.quantity * item.buyPrice).toStringAsFixed(2)}</td>
            <td style="text-align: right;">${item.revenue.toStringAsFixed(2)}</td>
            <td style="text-align: right;">${item.profit.toStringAsFixed(2)}</td>
          </tr>
        """);
      }

      html.write("""
          <tr style="font-weight: bold; background-color: #eee;">
            <td>TOTAL</td>
             <td style="text-align: right;">$totalQty</td>
             <td style="text-align: right;">${totalBuy.toStringAsFixed(2)}</td>
            <td style="text-align: right;">${totalRev.toStringAsFixed(2)}</td>
            <td style="text-align: right;">${totalProfit.toStringAsFixed(2)}</td>
          </tr>
        </table>
      </body>
      </html>
      """);

      final bytes = Uint8List.fromList(html.toString().codeUnits);
      final name =
          'rapport_financier_${startDate ?? "start"}_${endDate ?? "end"}.doc';
      return await _saveFile(bytes.toList(), name);
    } catch (e) {
      print('[Reports] Word Error: $e');
      rethrow;
    }
  }

  Future<String?> downloadStockPDF() async {
    try {
      final response = await _apiService.get(
        '/reports/stock/pdf',
        options: Options(responseType: ResponseType.bytes),
      );

      final fileName =
          'stock_report_${DateTime.now().toString().split(' ')[0]}.pdf';
      return await _saveFile(response.data as List<int>, fileName);
    } catch (e) {
      print('[ReportsService] Erreur downloadStockPDF: $e');
      rethrow;
    }
  }

  Future<String?> downloadSalesPDF(String? startDate, String? endDate) async {
    final params = <String, dynamic>{};
    if (startDate != null && startDate.isNotEmpty)
      params['start_date'] = startDate;
    if (endDate != null && endDate.isNotEmpty) params['end_date'] = endDate;

    try {
      final response = await _apiService.get(
        '/reports/sales/pdf',
        queryParameters: params,
        options: Options(responseType: ResponseType.bytes),
      );

      final fileName =
          'sales_report_${startDate ?? "start"}_${endDate ?? "end"}.pdf';
      return await _saveFile(response.data as List<int>, fileName);
    } catch (e) {
      print('[ReportsService] Erreur downloadSalesPDF: $e');
      rethrow;
    }
  }

  // Stock Excel & Word
  Future<String?> downloadStockExcel() async {
    try {
      final response = await _apiService.get(
        '/reports/stock/excel',
        options: Options(responseType: ResponseType.bytes),
      );
      final fileName =
          'stock_report_${DateTime.now().toString().split(' ')[0]}.xlsx';
      return await _saveFile(response.data as List<int>, fileName);
    } catch (e) {
      print('[ReportsService] Erreur downloadStockExcel: $e');
      rethrow;
    }
  }

  Future<String?> downloadStockWord() async {
    try {
      final response = await _apiService.get(
        '/reports/stock/word',
        options: Options(responseType: ResponseType.bytes),
      );
      final fileName =
          'stock_report_${DateTime.now().toString().split(' ')[0]}.doc';
      return await _saveFile(response.data as List<int>, fileName);
    } catch (e) {
      print('[ReportsService] Erreur downloadStockWord: $e');
      rethrow;
    }
  }

  // Sales Excel & Word
  Future<String?> downloadSalesExcel(String? startDate, String? endDate) async {
    final params = <String, dynamic>{};
    if (startDate != null && startDate.isNotEmpty)
      params['start_date'] = startDate;
    if (endDate != null && endDate.isNotEmpty) params['end_date'] = endDate;

    try {
      final response = await _apiService.get(
        '/reports/sales/excel',
        queryParameters: params,
        options: Options(responseType: ResponseType.bytes),
      );
      final fileName =
          'sales_report_${startDate ?? "start"}_${endDate ?? "end"}.xlsx';
      return await _saveFile(response.data as List<int>, fileName);
    } catch (e) {
      print('[ReportsService] Erreur downloadSalesExcel: $e');
      rethrow;
    }
  }

  Future<String?> downloadSalesWord(String? startDate, String? endDate) async {
    final params = <String, dynamic>{};
    if (startDate != null && startDate.isNotEmpty)
      params['start_date'] = startDate;
    if (endDate != null && endDate.isNotEmpty) params['end_date'] = endDate;

    try {
      final response = await _apiService.get(
        '/reports/sales/word',
        queryParameters: params,
        options: Options(responseType: ResponseType.bytes),
      );
      final fileName =
          'sales_report_${startDate ?? "start"}_${endDate ?? "end"}.doc';
      return await _saveFile(response.data as List<int>, fileName);
    } catch (e) {
      print('[ReportsService] Erreur downloadSalesWord: $e');
      rethrow;
    }
  }
}
