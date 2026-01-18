import 'package:frontend1/models/app_settings.dart';
import 'package:frontend1/services/api_service.dart';

class SettingsService {
  final ApiService _apiService = ApiService();

  Future<AppSettings> getSettings() async {
    try {
      final response = await _apiService.get('/settings');
      return AppSettings.fromJson(response.data);
    } catch (e) {
      print('[SettingsService] Erreur getSettings: $e');
      rethrow;
    }
  }

  Future<AppSettings> updateSettings(Map<String, dynamic> data) async {
    try {
      final response = await _apiService.put(
        '/settings',
        data: data,
      ); // ou PUT selon backend, React utilise POST ou PUT
      return AppSettings.fromJson(response.data);
    } catch (e) {
      print('[SettingsService] Erreur updateSettings: $e');
      rethrow;
    }
  }
}

class AdminService {
  final ApiService _apiService = ApiService();

  Future<Map<String, dynamic>> resetData({
    bool sales = false,
    bool products = false,
    bool users = false,
  }) async {
    try {
      final response = await _apiService.post(
        '/admin/reset',
        data: {'sales': sales, 'products': products, 'users': users},
      );
      return response.data;
    } catch (e) {
      print('[AdminService] Erreur resetData: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getLicense() async {
    final response = await _apiService.get(
      '/admin/license',
    ); // Endpoint supposé
    return response.data;
  }

  Future<Map<String, dynamic>> updateLicense(String date) async {
    final response = await _apiService.post(
      '/admin/license',
      data: {'expiry_date': date},
    );
    return response.data;
  }
}
