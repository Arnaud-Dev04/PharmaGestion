class Sale {
  final int id;
  final String code;
  final double totalAmount;
  final String paymentMethod;
  final DateTime date;
  final int? userId;
  final String userName;
  final String status; // 'completed', 'cancelled'
  final DateTime? cancelledAt;
  final String? cancelledBy;
  final int? customerId;
  final String? customerPhone;
  final List<SaleItem> items;
  final double bonusEarned;

  Sale({
    required this.id,
    required this.code,
    required this.totalAmount,
    required this.paymentMethod,
    required this.date,
    this.userId,
    required this.userName,
    required this.status,
    this.cancelledAt,
    this.cancelledBy,
    this.customerId,
    this.customerPhone,
    required this.items,
    this.bonusEarned = 0.0,
  });

  factory Sale.fromJson(Map<String, dynamic> json) {
    return Sale(
      id: json['id'],
      code: json['code'],
      totalAmount: (json['total_amount'] as num).toDouble(),
      paymentMethod: json['payment_method'] ?? 'cash',
      date: DateTime.parse(json['date']),
      userId: json['user_id'],
      userName: json['user_name'] ?? 'Inconnu',
      status: json['status'] ?? 'completed',
      cancelledAt: json['cancelled_at'] != null
          ? DateTime.parse(json['cancelled_at'])
          : null,
      cancelledBy: json['cancelled_by'],
      customerId: json['customer_id'],
      customerPhone:
          json['customer']?['phone'], // Extraction simplifiée depuis l'objet customer imbriqué
      items:
          (json['items'] as List?)?.map((i) => SaleItem.fromJson(i)).toList() ??
          [],
      bonusEarned: (json['bonus_earned'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class SaleItem {
  final int id;
  final int medicineId;
  final String medicineName;
  final String medicineCode;
  final int quantity;
  final double unitPrice;
  final double totalPrice;

  SaleItem({
    required this.id,
    required this.medicineId,
    required this.medicineName,
    required this.medicineCode,
    required this.quantity,
    required this.unitPrice,
    required this.totalPrice,
  });

  factory SaleItem.fromJson(Map<String, dynamic> json) {
    return SaleItem(
      id: json['id'],
      medicineId: json['medicine_id'],
      medicineName: json['medicine_name'] ?? '',
      medicineCode: json['medicine_code'] ?? '',
      quantity: (json['quantity'] as num).toInt(),
      unitPrice: (json['unit_price'] as num).toDouble(),
      totalPrice: (json['total_price'] as num).toDouble(),
    );
  }
}

class MedicineSaleStats {
  final int id;
  final String name;
  final String code;
  final int totalQuantity;
  final double totalRevenue;

  MedicineSaleStats({
    required this.id,
    required this.name,
    required this.code,
    required this.totalQuantity,
    required this.totalRevenue,
  });

  factory MedicineSaleStats.fromJson(Map<String, dynamic> json) {
    return MedicineSaleStats(
      id: json['id'],
      name: json['name'],
      code: json['code'],
      totalQuantity: json['total_quantity'],
      totalRevenue: (json['total_revenue'] as num).toDouble(),
    );
  }
}

class SalesHistoryResponse {
  final List<Sale> items;
  final int total;
  final int totalPages;

  SalesHistoryResponse({
    required this.items,
    required this.total,
    required this.totalPages,
  });

  factory SalesHistoryResponse.fromJson(Map<String, dynamic> json) {
    return SalesHistoryResponse(
      items: (json['items'] as List).map((i) => Sale.fromJson(i)).toList(),
      total: json['total'],
      totalPages: json['total_pages'],
    );
  }
}
