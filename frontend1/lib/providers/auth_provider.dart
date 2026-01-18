import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:frontend1/models/user.dart';
import 'package:frontend1/services/auth_service.dart';

/// Provider pour gérer l'état d'authentification
/// Utilise ChangeNotifier pour notifier les widgets des changements d'état
class AuthProvider with ChangeNotifier {
  final AuthService _authService = AuthService();
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();

  // État
  User? _user;
  String? _token;
  bool _isLoading = true;
  String? _errorMessage;

  // Getters
  User? get user => _user;
  String? get token => _token;
  bool get isAuthenticated => _token != null && _user != null;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  /// Initialiser l'authentification au démarrage de l'app
  /// Vérifie si un token existe et s'il est valide
  Future<void> initAuth() async {
    _isLoading = true;
    notifyListeners();

    try {
      // Récupérer le token sauvegardé
      final savedToken = await _secureStorage.read(key: 'auth_token');

      if (savedToken != null) {
        _token = savedToken;

        // Vérifier si le token est valide en récupérant l'utilisateur
        try {
          final userData = await _authService.getCurrentUser();
          _user = userData;
        } catch (e) {
          // Token invalide ou expiré, on le supprime
          print('[AuthProvider] Token invalide: $e');
          await _clearAuthData();
        }
      }
    } catch (e) {
      print('[AuthProvider] Erreur lors de l\'initialisation: $e');
      await _clearAuthData();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Connexion avec username et password
  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // 1. Appeler l'API de login pour obtenir le token
      final accessToken = await _authService.login(username, password);
      _token = accessToken;

      // 2. Sauvegarder le token de manière sécurisée
      await _secureStorage.write(key: 'auth_token', value: accessToken);

      // 3. Récupérer les informations de l'utilisateur
      final userData = await _authService.getCurrentUser();
      _user = userData;

      // 4. Sauvegarder les données utilisateur (optionnel, pour affichage rapide)
      await _secureStorage.write(key: 'user_data', value: userData.toString());

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceFirst('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Déconnexion
  Future<void> logout() async {
    await _clearAuthData();
    notifyListeners();
  }

  /// Rafraîchir les données de l'utilisateur
  Future<void> refreshUser() async {
    if (!isAuthenticated) return;

    try {
      final userData = await _authService.getCurrentUser();
      _user = userData;
      notifyListeners();
    } catch (e) {
      print('[AuthProvider] Erreur lors du rafraîchissement: $e');
      // Si l'erreur est 401, déconnecter l'utilisateur
      if (e.toString().contains('Session expirée') ||
          e.toString().contains('401')) {
        await logout();
      }
    }
  }

  /// Supprimer toutes les données d'authentification
  Future<void> _clearAuthData() async {
    _user = null;
    _token = null;
    _errorMessage = null;
    await _secureStorage.delete(key: 'auth_token');
    await _secureStorage.delete(key: 'user_data');
  }

  /// Réinitialiser le message d'erreur
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
