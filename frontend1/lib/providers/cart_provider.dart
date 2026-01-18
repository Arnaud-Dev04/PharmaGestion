import 'package:flutter/material.dart';
import 'package:frontend1/models/medicine.dart';
import 'package:frontend1/models/cart_item.dart';

class CartProvider extends ChangeNotifier {
  final List<CartItem> _items = [];

  // Infos client temporaires (pour la vente en cours)
  int? customerId;
  String customerPhone = '';
  String customerFirstName = '';
  String customerLastName = '';

  List<CartItem> get items => List.unmodifiable(_items);

  /// Ajouter un produit au panier
  void addToCart(Medicine medicine) {
    // Vérifier si le produit existe déjà
    final index = _items.indexWhere((item) => item.medicine.id == medicine.id);

    if (index >= 0) {
      // Si existe, incrémenter quantité
      _items[index].quantity++;
    } else {
      // Sinon, ajouter nouveau (défaut: par boîte/packaging)
      _items.add(
        CartItem(medicine: medicine, quantity: 1, saleType: SaleType.packaging),
      );
    }
    notifyListeners();
  }

  /// Retirer du panier
  void removeFromCart(int medicineId) {
    _items.removeWhere((item) => item.medicine.id == medicineId);
    notifyListeners();
  }

  /// Mettre à jour la quantité
  void updateQuantity(int medicineId, int delta) {
    final index = _items.indexWhere((item) => item.medicine.id == medicineId);
    if (index >= 0) {
      final newQty = _items[index].quantity + delta;
      if (newQty > 0) {
        _items[index].quantity = newQty;
      } else {
        // Optionnel : supprimer si quantité tombe à 0 ?
        // Pour l'instant on bloque à 1 ou on laisse l'utilisateur supprimer via la corbeille
        // Ici on retire si <= 0 pour simplicité comme React
        _items.removeAt(index);
      }
      notifyListeners();
    }
  }

  /// Changer le type de vente (Carton, Boîte, etc.)
  void updateSaleType(int medicineId, SaleType type) {
    final index = _items.indexWhere((item) => item.medicine.id == medicineId);
    if (index >= 0) {
      _items[index].saleType = type;
      notifyListeners();
    }
  }

  /// Appliquer une remise (0-100%)
  void updateDiscount(int medicineId, double percent) {
    final index = _items.indexWhere((item) => item.medicine.id == medicineId);
    if (index >= 0) {
      // Borner entre 0 et 100
      final validPercent = percent.clamp(0.0, 100.0);
      _items[index].discountPercent = validPercent;
      notifyListeners();
    }
  }

  /// Vider le panier
  void clearCart() {
    _items.clear();
    customerPhone = '';
    customerFirstName = '';
    customerLastName = '';
    customerId = null;
    notifyListeners();
  }

  /// Calcul du montant total
  double get totalAmount {
    return _items.fold(0.0, (sum, item) => sum + item.totalAmount);
  }

  /// Nombre total d'articles
  int get itemCount => _items.fold(0, (sum, item) => sum + item.quantity);

  /// Mettre à jour les infos client
  void updateCustomerInfo({
    String? phone,
    String? firstName,
    String? lastName,
    int? id,
  }) {
    if (phone != null) customerPhone = phone;
    if (firstName != null) customerFirstName = firstName;
    if (lastName != null) customerLastName = lastName;
    if (id != null) customerId = id;
    notifyListeners();
  }
}
