class User {
  final int id;
  final String username;
  final String email;
  final String role; // 'admin', 'pharmacist'
  final bool isActive;
  final DateTime? createdAt;

  bool get isAdmin => role == 'admin' || role == 'super_admin';

  User({
    required this.id,
    required this.username,
    this.email = '',
    required this.role,
    this.isActive = true,
    this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int? ?? 0,
      username: json['username']?.toString() ?? 'Inconnu',
      email: json['email']?.toString() ?? '',
      role: json['role']?.toString() ?? 'pharmacist',
      isActive: json['is_active'] as bool? ?? true,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'].toString())
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'role': role,
      'is_active': isActive,
      'created_at': createdAt?.toIso8601String(),
    };
  }
}
