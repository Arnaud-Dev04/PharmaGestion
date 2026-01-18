import 'package:flutter/material.dart';
import 'package:frontend1/core/theme.dart';
import 'package:frontend1/models/cart_item.dart';
import 'package:frontend1/models/customer_model.dart';
import 'package:frontend1/providers/cart_provider.dart';
import 'package:frontend1/widgets/pos/customer_search_field.dart';
import 'package:frontend1/widgets/pos/payment_modal.dart';
import 'package:provider/provider.dart';

class CartPanel extends StatefulWidget {
  const CartPanel({super.key});

  @override
  State<CartPanel> createState() => _CartPanelState();
}

class _CartPanelState extends State<CartPanel> {
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _phoneController = TextEditingController();

  // Pour gérer l'affichage du popup de remise par item
  int? _activeDiscountItemId;

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  void _syncCustomerInfo() {
    final cart = Provider.of<CartProvider>(context, listen: false);
    cart.updateCustomerInfo(
      firstName: _firstNameController.text,
      lastName: _lastNameController.text,
      phone: _phoneController.text,
      // Note: customerId is updated directly on selection
    );
  }

  void _onCustomerSelected(Customer customer) {
    setState(() {
      _firstNameController.text = customer.firstName;
      _lastNameController.text = customer.lastName;
      _phoneController.text = customer.phone;
    });
    final cart = Provider.of<CartProvider>(context, listen: false);
    cart.updateCustomerInfo(
      firstName: customer.firstName,
      lastName: customer.lastName,
      phone: customer.phone,
      id: customer.id,
    );
  }

  @override
  Widget build(BuildContext context) {
    final cart = Provider.of<CartProvider>(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      decoration: BoxDecoration(
        color: isDark ? AppTheme.darkCard : Colors.white,
        border: Border(
          left: BorderSide(
            color: isDark ? AppTheme.darkBorder : AppTheme.lightBorder,
          ),
        ),
      ),
      child: Column(
        children: [
          // Header Panier
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.shopping_cart_outlined),
                    const SizedBox(width: 8),
                    Text(
                      'Panier (${cart.itemCount})',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                  ],
                ),
                if (cart.items.isNotEmpty)
                  TextButton.icon(
                    onPressed: () {
                      cart.clearCart();
                      _firstNameController.clear();
                      _lastNameController.clear();
                      _phoneController.clear();
                    },
                    icon: const Icon(Icons.delete_outline, size: 18),
                    label: const Text('Vider'),
                    style: TextButton.styleFrom(
                      foregroundColor: AppTheme.dangerColor,
                    ),
                  ),
              ],
            ),
          ),
          const Divider(height: 1),

          // Liste Items
          Expanded(
            child: cart.items.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.shopping_basket_outlined,
                          size: 64,
                          color: Colors.grey[300],
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Votre panier est vide',
                          style: TextStyle(color: Colors.grey[500]),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(12),
                    itemCount: cart.items.length,
                    itemBuilder: (context, index) =>
                        _buildCartItem(cart, cart.items[index], isDark),
                  ),
          ),

          // Infos Client
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isDark ? Colors.black12 : Colors.grey[50],
              border: Border(
                top: BorderSide(
                  color: isDark ? AppTheme.darkBorder : AppTheme.lightBorder,
                ),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Informations Client',
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12),
                ),
                const SizedBox(height: 8),
                // Search Field
                SizedBox(
                  height: 40,
                  child: CustomerSearchField(onSelected: _onCustomerSelected),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: _buildSmallInput(
                        _firstNameController,
                        'Prénom',
                        Icons.person,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _buildSmallInput(
                        _lastNameController,
                        'Nom',
                        Icons.person,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                _buildSmallInput(_phoneController, 'Téléphone', Icons.phone),
              ],
            ),
          ),

          // Totaux & Actions
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              border: Border(
                top: BorderSide(
                  color: isDark ? AppTheme.darkBorder : AppTheme.lightBorder,
                ),
              ),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Total',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'F${cart.totalAmount.toStringAsFixed(0)}',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primaryColor,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: cart.items.isEmpty
                        ? null
                        : () {
                            _syncCustomerInfo();
                            showDialog(
                              context: context,
                              builder: (context) => PaymentModal(
                                totalAmount: cart.totalAmount,
                                onSuccess: () {
                                  cart.clearCart();
                                },
                              ),
                            );
                          },
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: const Text(
                      'Ecaisser',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCartItem(CartProvider cart, CartItem item, bool isDark) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 0,
      color: isDark ? AppTheme.darkCard : Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: BorderSide(
          color: isDark ? AppTheme.darkBorder : AppTheme.lightBorder,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            // Row 1: Nom et Remove
            Row(
              children: [
                Expanded(
                  child: Text(
                    item.medicine.name,
                    style: const TextStyle(fontWeight: FontWeight.w600),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                InkWell(
                  onTap: () => cart.removeFromCart(item.medicine.id),
                  child: const Padding(
                    padding: EdgeInsets.all(4),
                    child: Icon(
                      Icons.delete_outline,
                      size: 18,
                      color: AppTheme.dangerColor,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),

            // Row 2: Prix U et calculs
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Flexible(
                  child: Text(
                    'PU: F${item.effectiveUnitPrice.toStringAsFixed(0)}',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const SizedBox(width: 4),
                Flexible(
                  child: Text(
                    'F${item.totalAmount.toStringAsFixed(0)}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            if (item.discountPercent > 0)
              Align(
                alignment: Alignment.centerRight,
                child: Text(
                  'Remise -${item.discountPercent.toStringAsFixed(0)}%',
                  style: const TextStyle(
                    fontSize: 10,
                    color: AppTheme.successColor,
                  ),
                ),
              ),
            const SizedBox(height: 12),

            // Row 3: Controls (Type, Quantity, Discount)
            Row(
              children: [
                // Type Selector (Carton/Box/Unit)
                Container(
                  padding: const EdgeInsets.all(2),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey[300]!),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Carton
                      if ((item.medicine.boxesPerCarton) > 1)
                        _buildTypeBtn(
                          cart,
                          item,
                          SaleType.carton,
                          Icons.inventory_2,
                          'Carton',
                        ),
                      // Box
                      _buildTypeBtn(
                        cart,
                        item,
                        SaleType.packaging,
                        Icons.inbox,
                        'Boîte',
                      ),
                      // Blister
                      if ((item.medicine.blistersPerBox) > 1)
                        _buildTypeBtn(
                          cart,
                          item,
                          SaleType.blister,
                          Icons.grid_view,
                          'Plaquette',
                        ),
                      // Unit
                      _buildTypeBtn(
                        cart,
                        item,
                        SaleType.unit,
                        Icons.circle,
                        'Unité',
                      ),
                    ],
                  ),
                ),

                const Spacer(),

                // Quantity
                Container(
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey[300]!),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    children: [
                      _buildQtyBtn(
                        () => cart.updateQuantity(item.medicine.id, -1),
                        Icons.remove,
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 8),
                        child: Text(
                          '${item.quantity}',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                      _buildQtyBtn(
                        () => cart.updateQuantity(item.medicine.id, 1),
                        Icons.add,
                      ),
                    ],
                  ),
                ),

                const SizedBox(width: 8),

                // Discount Button
                Stack(
                  alignment: Alignment.center,
                  children: [
                    IconButton(
                      icon: Icon(
                        Icons.percent,
                        size: 16,
                        color: item.discountPercent > 0
                            ? AppTheme.successColor
                            : Colors.grey,
                      ),
                      style: IconButton.styleFrom(
                        padding: EdgeInsets.zero,
                        minimumSize: const Size(32, 32),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                          side: BorderSide(
                            color: item.discountPercent > 0
                                ? AppTheme.successColor
                                : Colors.grey[300]!,
                          ),
                        ),
                      ),
                      onPressed: () {
                        setState(() {
                          _activeDiscountItemId =
                              _activeDiscountItemId == item.medicine.id
                              ? null
                              : item.medicine.id;
                        });
                      },
                    ),
                    if (_activeDiscountItemId == item.medicine.id)
                      CompositedTransformTarget(
                        link:
                            LayerLink(), // Juste pour ancrage si besoin, ici on utilise un Overlay simpliste
                        child: Container(),
                      ),
                  ],
                ),
              ],
            ),

            // Inline Discount Input (visible if active)
            if (_activeDiscountItemId == item.medicine.id)
              Container(
                margin: const EdgeInsets.only(top: 8),
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.grey[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey[300]!),
                ),
                child: Row(
                  children: [
                    const Text('Remise % : ', style: TextStyle(fontSize: 12)),
                    SizedBox(
                      width: 60,
                      height: 30,
                      child: TextField(
                        // Pas idéal dans un ListView, mais functional pour small scale
                        keyboardType: TextInputType.number,
                        autofocus: true,
                        textAlign: TextAlign.center,
                        decoration: const InputDecoration(
                          contentPadding: EdgeInsets.zero,
                          border: OutlineInputBorder(),
                        ),
                        onChanged: (val) {
                          final p = double.tryParse(val) ?? 0;
                          cart.updateDiscount(item.medicine.id, p);
                        },
                      ),
                    ),
                    const Spacer(),
                    TextButton(
                      onPressed: () =>
                          setState(() => _activeDiscountItemId = null),
                      style: TextButton.styleFrom(
                        padding: EdgeInsets.zero,
                        minimumSize: const Size(40, 30),
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      child: const Text('OK', style: TextStyle(fontSize: 12)),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildTypeBtn(
    CartProvider cart,
    CartItem item,
    SaleType type,
    IconData icon,
    String tooltip,
  ) {
    final isSelected = item.saleType == type;
    return InkWell(
      onTap: () => cart.updateSaleType(item.medicine.id, type),
      child: Tooltip(
        message: tooltip,
        child: Container(
          padding: const EdgeInsets.all(6),
          color: isSelected
              ? AppTheme.primaryColor.withValues(alpha: 0.1)
              : Colors.transparent,
          child: Icon(
            icon,
            size: 16,
            color: isSelected ? AppTheme.primaryColor : Colors.grey[400],
          ),
        ),
      ),
    );
  }

  Widget _buildQtyBtn(VoidCallback onTap, IconData icon) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: const EdgeInsets.all(4),
        child: Icon(icon, size: 14, color: Colors.grey[700]),
      ),
    );
  }

  Widget _buildSmallInput(
    TextEditingController controller,
    String hint,
    IconData icon,
  ) {
    return TextField(
      controller: controller,
      onChanged: (value) => _syncCustomerInfo(),
      style: const TextStyle(fontSize: 13),
      decoration: InputDecoration(
        hintText: hint,
        isDense: true,
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
        prefixIcon: Icon(icon, size: 14, color: Colors.grey),
        prefixIconConstraints: const BoxConstraints(
          minWidth: 24,
          maxHeight: 24,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: Colors.grey[300]!),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: Colors.grey[300]!),
        ),
      ),
    );
  }
}
