import 'package:frontend1/services/api_service.dart';

class CustomerService {
  final ApiService _apiService = ApiService();

  Future<List<dynamic>> searchCustomers(String query) async {
    try {
      final response = await _apiService.get(
        '/customers',
        queryParameters: {'search': query, 'page_size': 10},
      );
      return response.data['items'] ?? [];
    } catch (e) {
      print('Error searching customers: $e');
      return [];
    }
  }

  Future<dynamic> createCustomer(Map<String, dynamic> data) async {
    try {
      final response = await _apiService.post('/customers/', data: data);
      return response.data;
    } catch (e) {
      print('Error creating customer: $e');
      rethrow;
    }
  }
}
