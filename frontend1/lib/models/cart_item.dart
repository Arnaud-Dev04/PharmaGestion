import 'package:frontend1/models/medicine.dart';

enum SaleType {
  unit,
  blister,
  packaging, // Boîte standard
  carton,
}

class CartItem {
  final Medicine medicine;
  int quantity;            // Quantité saisie (ex: 2 cartons)
  SaleType saleType;       // Type de vente
  double discountPercent;  // Remise (0-100)

  CartItem({
    required this.medicine,
    this.quantity = 1,
    this.saleType = SaleType.packaging,
    this.discountPercent = 0.0,
  });

  /// Prix unitaire de base selon le type (avant remise)
  double get baseUnitTestPrice {
    final unitsPerPackaging = medicine.unitsPerPackaging > 0 ? medicine.unitsPerPackaging : 1;
    final unitPrice = medicine.priceSell / unitsPerPackaging;

    switch (saleType) {
      case SaleType.unit:
        return unitPrice;
      case SaleType.blister:
        return unitPrice * (medicine.unitsPerBlister > 0 ? medicine.unitsPerBlister : 1);
      case SaleType.packaging:
        return medicine.priceSell;
      case SaleType.carton:
        return medicine.priceSell * (medicine.boxesPerCarton > 0 ? medicine.boxesPerCarton : 1);
    }
  }

  /// Prix unitaire après remise
  double get effectiveUnitPrice {
    return baseUnitTestPrice * (1 - (discountPercent / 100));
  }

  /// Total pour cet item (prix * quantité)
  double get totalAmount {
    return effectiveUnitPrice * quantity;
  }

  /// Conversion de la quantité saisie en UNITÉS TOTALES pour le backend
  /// C'est ici que la correction logique s'opère pour sécuriser le stock
  int get totalUnits {
    int multiplier = 1;

    switch (saleType) {
      case SaleType.unit:
        multiplier = 1;
        break;
      case SaleType.blister:
        multiplier = medicine.unitsPerBlister > 0 ? medicine.unitsPerBlister : 1;
        break;
      case SaleType.packaging:
        // 1 Boîte = X Plaquettes * Y Unités ( = unitsPerPackaging)
        multiplier = medicine.unitsPerPackaging > 0 ? medicine.unitsPerPackaging : 1;
        break;
      case SaleType.carton:
        // 1 Carton = Z Boîtes * (Unités par Boîte)
        final unitsPerBox = medicine.unitsPerPackaging > 0 ? medicine.unitsPerPackaging : 1;
        multiplier = (medicine.boxesPerCarton > 0 ? medicine.boxesPerCarton : 1) * unitsPerBox;
        break;
    }

    return quantity * multiplier;
  }

  CartItem copyWith({
    Medicine? medicine,
    int? quantity,
    SaleType? saleType,
    double? discountPercent,
  }) {
    return CartItem(
      medicine: medicine ?? this.medicine,
      quantity: quantity ?? this.quantity,
      saleType: saleType ?? this.saleType,
      discountPercent: discountPercent ?? this.discountPercent,
    );
  }
}
