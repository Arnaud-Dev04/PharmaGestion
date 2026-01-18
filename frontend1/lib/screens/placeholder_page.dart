import 'package:flutter/material.dart';

/// Page placeholder pour les écrans non encore implémentés
class PlaceholderPage extends StatelessWidget {
  final String pageName;
  final IconData icon;
  final String description;

  const PlaceholderPage({
    super.key,
    required this.pageName,
    required this.icon,
    this.description =
        'Cette page sera implémentée dans les prochaines étapes.',
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            icon,
            size: 80,
            color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.3),
          ),
          const SizedBox(height: 24),
          Text(
            pageName,
            style: Theme.of(
              context,
            ).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Text(
            description,
            style: Theme.of(
              context,
            ).textTheme.bodyMedium?.copyWith(color: Colors.grey),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
