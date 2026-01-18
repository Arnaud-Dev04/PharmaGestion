import 'package:flutter/material.dart';
import 'package:frontend1/screens/placeholder_page.dart';

/// Pages placeholders pour toutes les sections de l'application







// Suppliers Page
class SuppliersPage extends StatelessWidget {
  const SuppliersPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const PlaceholderPage(
      pageName: 'Fournisseurs',
      icon: Icons.local_shipping,
      description: 'La gestion des fournisseurs sera ajoutée prochainement.',
    );
  }
}

// Users Page
class UsersPage extends StatelessWidget {
  const UsersPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const PlaceholderPage(
      pageName: 'Utilisateurs',
      icon: Icons.people,
      description:
          'La gestion des utilisateurs sera implémentée dans l\'Étape 8.',
    );
  }
}





// Super Admin Page
class SuperAdminPage extends StatelessWidget {
  const SuperAdminPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const PlaceholderPage(
      pageName: 'Super Admin',
      icon: Icons.admin_panel_settings,
      description:
          'Le panneau Super Admin est réservé aux Super Administrateurs.',
    );
  }
}
