import 'package:flutter/foundation.dart';
import 'package:frontend1/services/api_service.dart';

/// Service POS dédié — appelle les endpoints /pos/...
/// Gère la recherche produit, l'allocation FEFO, et le checkout avec lots.
class PosService {
  final ApiService _apiService = ApiService();

  // Singleton
  static final PosService _instance = PosService._internal();
  factory PosService() => _instance;
  PosService._internal();

  /// Rechercher des produits avec info lots (FEFO)
  Future<List<Map<String, dynamic>>> searchProducts(String query, {int limit = 20}) async {
    try {
      final response = await _apiService.get(
        '/pos/products/search',
        queryParameters: {'q': query, 'limit': limit},
      );
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      debugPrint('[PosService] Erreur searchProducts: $e');
      rethrow;
    }
  }

  /// Produits les plus vendus / fréquents
  Future<List<Map<String, dynamic>>> getTopProducts({int limit = 10}) async {
    try {
      final response = await _apiService.get(
        '/pos/products/top',
        queryParameters: {'limit': limit},
      );
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      debugPrint('[PosService] Erreur getTopProducts: $e');
      rethrow;
    }
  }

  /// Demander l'allocation FEFO pour un produit + quantité au niveau choisi
  Future<Map<String, dynamic>> cartAdd(int medicineId, int quantity, {String level = 'unite'}) async {
    try {
      final response = await _apiService.post(
        '/pos/cart/add',
        data: {
          'medicine_id': medicineId,
          'quantity': quantity,
          'level': level,
        },
      );
      return response.data as Map<String, dynamic>;
    } catch (e) {
      debugPrint('[PosService] Erreur cartAdd: $e');
      rethrow;
    }
  }

  /// Checkout final — crée la vente POS avec déduction stock par lot
  Future<Map<String, dynamic>> checkout(Map<String, dynamic> checkoutData) async {
    try {
      final response = await _apiService.post(
        '/pos/checkout',
        data: checkoutData,
      );
      return response.data as Map<String, dynamic>;
    } catch (e) {
      debugPrint('[PosService] Erreur checkout: $e');
      rethrow;
    }
  }

  /// Récupérer les détails d'une vente POS
  Future<Map<String, dynamic>> getSale(int saleId) async {
    try {
      final response = await _apiService.get('/pos/sale/$saleId');
      return response.data as Map<String, dynamic>;
    } catch (e) {
      debugPrint('[PosService] Erreur getSale: $e');
      rethrow;
    }
  }

  /// Annuler une vente POS et restaurer le stock par lot
  Future<Map<String, dynamic>> cancelSale(int saleId) async {
    try {
      final response = await _apiService.post('/pos/sale/$saleId/cancel');
      return response.data as Map<String, dynamic>;
    } catch (e) {
      debugPrint('[PosService] Erreur cancelSale: $e');
      rethrow;
    }
  }

  /// Historique des ventes POS
  Future<Map<String, dynamic>> getHistory({
    int page = 1,
    int pageSize = 50,
    String? startDate,
    String? endDate,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
      };
      if (startDate != null) queryParams['start_date'] = startDate;
      if (endDate != null) queryParams['end_date'] = endDate;

      final response = await _apiService.get(
        '/pos/history',
        queryParameters: queryParams,
      );
      return response.data as Map<String, dynamic>;
    } catch (e) {
      debugPrint('[PosService] Erreur getHistory: $e');
      rethrow;
    }
  }

  /// Créer un nouveau lot pour un médicament
  Future<Map<String, dynamic>> createBatch(Map<String, dynamic> batchData) async {
    try {
      final response = await _apiService.post(
        '/pos/batches',
        data: batchData,
      );
      return response.data as Map<String, dynamic>;
    } catch (e) {
      debugPrint('[PosService] Erreur createBatch: $e');
      rethrow;
    }
  }

  /// Récupérer les lots d'un médicament
  Future<List<Map<String, dynamic>>> getBatches(int medicineId, {bool includeEmpty = false}) async {
    try {
      final response = await _apiService.get(
        '/pos/batches/$medicineId',
        queryParameters: {'include_empty': includeEmpty},
      );
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      debugPrint('[PosService] Erreur getBatches: $e');
      rethrow;
    }
  }
}
