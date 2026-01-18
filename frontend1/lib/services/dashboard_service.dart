import 'package:frontend1/services/api_service.dart';
import 'package:frontend1/models/dashboard_stats.dart';

/// Service pour les données du Dashboard
class DashboardService {
  final ApiService _apiService = ApiService();

  /// Récupère les statistiques du dashboard
  /// [period] : Nombre de jours (7, 30, ou 90)
  Future<DashboardStats> getDashboardStats(
    int period, {
    String? startDate,
    String? endDate,
  }) async {
    try {
      final Map<String, dynamic> queryParams = {'days': period};
      if (startDate != null) queryParams['start_date'] = startDate;
      if (endDate != null) queryParams['end_date'] = endDate;

      final response = await _apiService.get(
        '/dashboard/stats',
        queryParameters: queryParams,
      );

      return DashboardStats.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      print('[DashboardService] Erreur getDashboardStats: $e');
      rethrow;
    }
  }

  /// Récupère la liste des ventes annulées
  Future<List<CancelledSale>> getCancelledSales({
    String? startDate,
    String? endDate,
  }) async {
    try {
      final Map<String, dynamic> queryParams = {};
      if (startDate != null) queryParams['start_date'] = startDate;
      if (endDate != null) queryParams['end_date'] = endDate;

      final response = await _apiService.get(
        '/dashboard/cancelled-sales',
        queryParameters: queryParams,
      );

      return (response.data as List)
          .map((json) => CancelledSale.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      print('[DashboardService] Erreur getCancelledSales: $e');
      rethrow;
    }
  }
}
