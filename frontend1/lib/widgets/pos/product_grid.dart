import 'package:flutter/material.dart';
import 'package:frontend1/core/theme.dart';
import 'package:frontend1/models/medicine.dart';
import 'package:frontend1/providers/cart_provider.dart';
import 'package:frontend1/providers/language_provider.dart';
import 'package:frontend1/services/stock_service.dart';
import 'package:provider/provider.dart';

/// Widget affichant la grille des produits pour le POS
class ProductGrid extends StatefulWidget {
  const ProductGrid({super.key});

  @override
  State<ProductGrid> createState() => _ProductGridState();
}

class _ProductGridState extends State<ProductGrid> {
  final StockService _stockService = StockService();
  final TextEditingController _searchController = TextEditingController();

  List<Medicine> _medicines = [];
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadMedicines();
    _searchController.addListener(_onSearchChanged);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged() {
    Future.delayed(const Duration(milliseconds: 500), () {
      if (mounted) {
        _loadMedicines();
      }
    });
  }

  Future<void> _loadMedicines() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // On charge 20 items pour le POS, pas besoin de pagination complexe ici pour l'instant
      // Idéalement on ajouterait un "Load More" ou un scroll infini
      final response = await _stockService.getMedicines(
        page: 1,
        search: _searchController.text.trim().isNotEmpty
            ? _searchController.text.trim()
            : null,
      );

      if (mounted) {
        setState(() {
          _medicines = response.items;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final languageProvider = Provider.of<LanguageProvider>(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header & Search
        Text(
          languageProvider.translate('posTitle'),
          style: Theme.of(
            context,
          ).textTheme.headlineLarge?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(
          languageProvider.translate('posSubtitle'),
          style: Theme.of(
            context,
          ).textTheme.bodyMedium?.copyWith(color: Colors.grey),
        ),
        const SizedBox(height: 16),

        // Search Bar
        TextField(
          controller: _searchController,
          decoration: InputDecoration(
            hintText: languageProvider.translate('search'),
            prefixIcon: const Icon(Icons.search),
            filled: true,
            fillColor: Theme.of(context).cardColor,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide.none,
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Grid
        Expanded(
          child: _isLoading
              ? const Center(child: CircularProgressIndicator())
              : _error != null
              ? Center(child: Text('Erreur: $_error'))
              : _medicines.isEmpty
              ? Center(child: Text(languageProvider.translate('noProducts')))
              : _buildGridLines(),
        ),
      ],
    );
  }

  Widget _buildGridLines() {
    // Calcul responsive du nombre de colonnes
    final width = MediaQuery.of(context).size.width;
    int crossAxisCount = 2;
    if (width > 1200)
      crossAxisCount = 4;
    else if (width > 800)
      crossAxisCount = 3;

    return GridView.builder(
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        childAspectRatio:
            0.7, // Ratio plus petit = cartes plus hautes pour éviter overflow vertical
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: _medicines.length,
      itemBuilder: (context, index) {
        final medicine = _medicines[index];
        return _buildProductCard(medicine);
      },
    );
  }

  Widget _buildProductCard(Medicine medicine) {
    final cartProvider = Provider.of<CartProvider>(context, listen: false);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Card(
      elevation: 0,
      color: isDark ? AppTheme.darkCard : Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: isDark ? AppTheme.darkBorder : AppTheme.lightBorder,
        ),
      ),
      child: InkWell(
        onTap: medicine.quantity > 0
            ? () {
                cartProvider.addToCart(medicine);
                ScaffoldMessenger.of(context).hideCurrentSnackBar();
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('${medicine.name} ajouté au panier'),
                    duration: const Duration(seconds: 1),
                    behavior: SnackBarBehavior.floating,
                    width: 300,
                  ),
                );
              }
            : null,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header avec icône ou badge
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryColor.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(
                      Icons.medication,
                      color: AppTheme.primaryColor,
                      size: 20,
                    ),
                  ),
                  if (medicine.quantity <= 0)
                    Flexible(
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: AppTheme.dangerColor.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Text(
                          'Rupture',
                          style: TextStyle(
                            fontSize: 10,
                            color: AppTheme.dangerColor,
                            fontWeight: FontWeight.bold,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ),
                ],
              ),
              const Spacer(),

              // Nom du produit
              Text(
                medicine.name,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),

              // Conditionnement
              Text(
                medicine.packaging ?? 'Unité',
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
              const Spacer(),

              // Prix et Stock
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Flexible(
                    child: Text(
                      'F${medicine.priceSell.toStringAsFixed(0)}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primaryColor,
                        fontSize: 16,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Flexible(
                    child: Text(
                      '${medicine.quantity}',
                      style: TextStyle(
                        fontSize: 12,
                        color: medicine.quantity < 10
                            ? AppTheme.dangerColor
                            : Colors.grey,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
