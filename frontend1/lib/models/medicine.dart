/// Modèle représentant un médicament dans le stock
class Medicine {
  final int id;
  final String code;
  final String name;
  final String? description;
  final String? dosageForm; // Forme (Comprimé, Sirop, etc.)
  final String? packaging; // Conditionnement (Boîte, Flacon, etc.)
  final String? cartonType; // Nom du carton (ex: "Carton")
  final int boxesPerCarton; // Boîtes par carton
  final int blistersPerBox; // Plaquettes par boîte
  final int unitsPerBlister; // Unités par plaquette
  final int unitsPerPackaging; // Calculé par backend
  final double priceBuy; // Prix d'achat par boîte
  final double priceSell; // Prix de vente par boîte
  final int quantity; // Quantité totale EN UNITÉS
  final int minStockAlert; // Seuil d'alerte stock
  final int expiryAlertThreshold; // Seuil d'alerte expiration (jours)
  final DateTime? expiryDate; // Date péremption
  final bool isLowStock; // Calculé par backend
  final bool isExpired; // Calculé par backend
  final int? familyId;
  final int? typeId;
  final DateTime createdAt;
  final DateTime updatedAt;

  Medicine({
    required this.id,
    required this.code,
    required this.name,
    this.description,
    this.dosageForm,
    this.packaging,
    this.cartonType,
    this.boxesPerCarton = 1,
    this.blistersPerBox = 1,
    this.unitsPerBlister = 1,
    this.unitsPerPackaging = 1,
    required this.priceBuy,
    required this.priceSell,
    required this.quantity,
    this.minStockAlert = 10,
    this.expiryAlertThreshold = 30,
    this.expiryDate,
    this.isLowStock = false,
    this.isExpired = false,
    this.familyId,
    this.typeId,
    required this.createdAt,
    required this.updatedAt,
  });

  // ... (formatStock kept implicitly by not touching it, but I must match regex or use context lines carefully)
  // Let me re-target larger chunks to be safe or use multi_replace if they were scattered.
  // The fields are close. Constructor is close.
  // fromJson is further down.

  // Helper method to format stock display
  String formatStock() {
    if (packaging != null && unitsPerPackaging > 1) {
      // Display in packaging units + remainder?
      // For now, simple display to unblock build.
      return "$quantity unités";
    }
    return "$quantity";
  }

  /// Serialization depuis JSON
  factory Medicine.fromJson(Map<String, dynamic> json) {
    return Medicine(
      id: json['id'] as int,
      code: json['code'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      dosageForm: json['dosage_form'] as String?,
      packaging: json['packaging'] as String?,
      cartonType: json['carton_type'] as String?,
      boxesPerCarton: json['boxes_per_carton'] as int? ?? 1,
      blistersPerBox: json['blisters_per_box'] as int? ?? 1,
      unitsPerBlister: json['units_per_blister'] as int? ?? 1,
      unitsPerPackaging: json['units_per_packaging'] as int? ?? 1,
      priceBuy: (json['price_buy'] as num).toDouble(),
      priceSell: (json['price_sell'] as num).toDouble(),
      quantity: (json['quantity'] as num).toInt(),
      minStockAlert: json['min_stock_alert'] as int? ?? 10,
      expiryAlertThreshold: json['expiry_alert_threshold'] as int? ?? 30,
      expiryDate: json['expiry_date'] != null
          ? DateTime.parse(json['expiry_date'] as String)
          : null,
      isLowStock: json['is_low_stock'] as bool? ?? false,
      isExpired: json['is_expired'] as bool? ?? false,
      familyId: json['family_id'] as int?,
      typeId: json['type_id'] as int?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  /// Serialization vers JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'code': code,
      'name': name,
      'description': description,
      'dosage_form': dosageForm,
      'packaging': packaging,
      'carton_type': cartonType,
      'boxes_per_carton': boxesPerCarton,
      'blisters_per_box': blistersPerBox,
      'units_per_blister': unitsPerBlister,
      'units_per_packaging': unitsPerPackaging,
      'price_buy': priceBuy,
      'price_sell': priceSell,
      'quantity': quantity,
      'min_stock_alert': minStockAlert,
      'expiry_alert_threshold': expiryAlertThreshold,
      'expiry_date': expiryDate?.toIso8601String(),
      'is_low_stock': isLowStock,
      'is_expired': isExpired,
      'family_id': familyId,
      'type_id': typeId,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  /// Copie avec modifications
  Medicine copyWith({
    int? id,
    String? code,
    String? name,
    String? description,
    String? dosageForm,
    String? packaging,
    String? cartonType,
    int? boxesPerCarton,
    int? blistersPerBox,
    int? unitsPerBlister,
    int? unitsPerPackaging,
    double? priceBuy,
    double? priceSell,
    int? quantity,
    int? minStockAlert,
    int? expiryAlertThreshold,
    DateTime? expiryDate,
    bool? isLowStock,
    bool? isExpired,
    int? familyId,
    int? typeId,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Medicine(
      id: id ?? this.id,
      code: code ?? this.code,
      name: name ?? this.name,
      description: description ?? this.description,
      dosageForm: dosageForm ?? this.dosageForm,
      packaging: packaging ?? this.packaging,
      cartonType: cartonType ?? this.cartonType,
      boxesPerCarton: boxesPerCarton ?? this.boxesPerCarton,
      blistersPerBox: blistersPerBox ?? this.blistersPerBox,
      unitsPerBlister: unitsPerBlister ?? this.unitsPerBlister,
      unitsPerPackaging: unitsPerPackaging ?? this.unitsPerPackaging,
      priceBuy: priceBuy ?? this.priceBuy,
      priceSell: priceSell ?? this.priceSell,
      quantity: quantity ?? this.quantity,
      minStockAlert: minStockAlert ?? this.minStockAlert,
      expiryAlertThreshold: expiryAlertThreshold ?? this.expiryAlertThreshold,
      expiryDate: expiryDate ?? this.expiryDate,
      isLowStock: isLowStock ?? this.isLowStock,
      isExpired: isExpired ?? this.isExpired,
      familyId: familyId ?? this.familyId,
      typeId: typeId ?? this.typeId,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'Medicine(id: $id, code: $code, name: $name, quantity: $quantity)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Medicine && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

/// Réponse paginée de la liste des médicaments
class StockResponse {
  final List<Medicine> items;
  final int total;
  final int totalPages;

  StockResponse({
    required this.items,
    required this.total,
    required this.totalPages,
  });

  factory StockResponse.fromJson(Map<String, dynamic> json) {
    return StockResponse(
      items: (json['items'] as List)
          .map((item) => Medicine.fromJson(item as Map<String, dynamic>))
          .toList(),
      total: json['total'] as int,
      totalPages: json['total_pages'] as int,
    );
  }
}
