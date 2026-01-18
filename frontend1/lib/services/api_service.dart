import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:frontend1/core/constants.dart';
import 'package:frontend1/main.dart'; // For scaffoldMessengerKey
import 'package:flutter/material.dart'; // For SnackBar colors

/// Service API centralisé utilisant Dio
/// Gère les intercepteurs JWT pour l'authentification
class ApiService {
  late final Dio _dio;
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();

  // Singleton pattern
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  ApiService._internal() {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConstants.apiBaseUrl,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Ajouter les intercepteurs
    _dio.interceptors.add(_AuthInterceptor(_secureStorage));
    _dio.interceptors.add(_ErrorInterceptor());
    _dio.interceptors.add(
      LogInterceptor(
        request: true,
        requestHeader: true,
        requestBody: true,
        responseHeader: false,
        responseBody: true,
        error: true,
        logPrint: (obj) => print('[API] $obj'),
      ),
    );
  }

  /// Instance Dio pour accès direct si nécessaire
  Dio get dio => _dio;

  /// GET request
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await _dio.get(
      path,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// POST request
  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await _dio.post(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// PUT request
  Future<Response> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await _dio.put(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// DELETE request
  Future<Response> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await _dio.delete(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// PATCH request
  Future<Response> patch(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await _dio.patch(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }
}

/// Intercepteur pour ajouter le token JWT aux requêtes
class _AuthInterceptor extends Interceptor {
  final FlutterSecureStorage _storage;

  _AuthInterceptor(this._storage);

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Récupérer le token depuis le secure storage
    final token = await _storage.read(key: 'auth_token');

    if (token != null) {
      // Ajouter le header Authorization
      options.headers['Authorization'] = 'Bearer $token';
    }

    handler.next(options);
  }
}

/// Intercepteur pour gérer les erreurs globalement
class _ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // Gérer les erreurs 401 Unauthorized
    if (err.response?.statusCode == 401) {
      print('[API] 401 Unauthorized - Token invalide ou expiré');
      // La déconnexion sera gérée par AuthProvider
      // qui écoute les erreurs 401
    }

    // Gérer les erreurs réseau
    if (err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.receiveTimeout ||
        err.type == DioExceptionType.sendTimeout) {
      print('[API] Erreur de connexion : ${err.message}');
    }

    if (err.type == DioExceptionType.connectionError) {
      print('[API] Impossible de se connecter au serveur');
    }

    String errorMessage = "Une erreur est survenue";
    Color bgColor = Colors.red;

    // Gérer les codes d'erreur spécifiques
    if (err.response != null) {
      if (err.response?.statusCode == 400) {
        // Bad Request - Souvent un message de validation du backend
        errorMessage = err.response?.data['detail'] ?? "Requête invalide (400)";
        bgColor = Colors.orange;
      } else if (err.response?.statusCode == 401) {
        errorMessage = "Session expirée. Veuillez vous reconnecter.";
        bgColor = Colors.blueGrey;
      } else if (err.response?.statusCode == 403) {
        errorMessage = "Accès refusé (403)";
        bgColor = Colors.orangeAccent;
      } else if (err.response?.statusCode == 404) {
        errorMessage =
            err.response?.data['detail'] ?? "Ressource introuvable (404)";
        bgColor = Colors.grey;
      } else if (err.response?.statusCode == 500) {
        errorMessage = "Erreur serveur interne (500). Contactez le support.";
        bgColor = Colors.red[900]!;
      }
    } else {
      // Erreurs réseau (pas de réponse)
      if (err.type == DioExceptionType.connectionTimeout ||
          err.type == DioExceptionType.receiveTimeout) {
        errorMessage = "Délai d'attente dépassé.";
      } else if (err.type == DioExceptionType.connectionError) {
        errorMessage =
            "Impossible de joindre le serveur. Vérifiez votre connexion.";
      }
    }

    // Afficher le message (si la vue est montée)
    final messenger = scaffoldMessengerKey.currentState;
    if (messenger != null) {
      messenger.showSnackBar(
        SnackBar(
          content: Text(
            errorMessage,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          backgroundColor: bgColor,
          behavior: SnackBarBehavior.floating, // Flottant pour être plus joli
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
          margin: const EdgeInsets.all(10),
          duration: const Duration(seconds: 4),
        ),
      );
    }

    handler.next(err);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    // Log les réponses réussies (optionnel en production)
    if (response.statusCode == 200 || response.statusCode == 201) {
      print(
        '[API] ✅ ${response.requestOptions.method} ${response.requestOptions.path} - Success',
      );
    }

    handler.next(response);
  }
}
