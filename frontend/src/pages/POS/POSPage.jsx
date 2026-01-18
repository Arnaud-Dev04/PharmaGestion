import { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, Plus, Minus, Trash2, ShoppingCart, Percent, Box, Tablet, Package } from 'lucide-react';
import stockService from '../../services/stockService';
import salesService from '../../services/salesService';
import { PaymentModal } from '../../components/pos/PaymentModal';

export const POSPage = () => {
  const { t } = useLanguage();
  const [search, setSearch] = useState('');
  const [cart, setCart] = useState([]);
  const [customerPhone, setCustomerPhone] = useState('');
  const [customerFirstName, setCustomerFirstName] = useState('');
  const [customerLastName, setCustomerLastName] = useState('');
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [discountModalItem, setDiscountModalItem] = useState(null); // Item ID for discount modal

  const queryClient = useQueryClient();

  // Fetch medicines for catalog
  const { data: medicinesData, isLoading } = useQuery({
    queryKey: ['medicines', search],
    queryFn: () => stockService.getMedicines({ search, pageSize: 20 }),
  });

  const addToCart = (medicine) => {
    const existing = cart.find((item) => item.medicine.id === medicine.id);
    
    if (existing) {
      setCart(
        cart.map((item) =>
          item.medicine.id === medicine.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        )
      );
    } else {
      setCart([...cart, { 
        medicine, 
        quantity: 1, 
        sale_type: 'packaging', // Default to packaging
        discount_percent: 0.0 
      }]);
    }
  };

  const updateQuantity = (medicineId, delta) => {
    setCart(
      cart.map((item) => {
        if (item.medicine.id === medicineId) {
          const newQuantity = item.quantity + delta;
          if (newQuantity <= 0) {
            return null;
          }
          return { ...item, quantity: newQuantity };
        }
        return item;
      }).filter(Boolean)
    );
  };

  const updateSaleType = (medicineId, type) => {
    setCart(
      cart.map((item) => 
        item.medicine.id === medicineId 
          ? { ...item, sale_type: type } 
          : item
      )
    );
  };

  const updateDiscount = (medicineId, percent) => {
    setCart(
      cart.map((item) => 
        item.medicine.id === medicineId 
          ? { ...item, discount_percent: Math.min(100, Math.max(0, percent)) } 
          : item
      )
    );
  };

  const removeFromCart = (medicineId) => {
    setCart(cart.filter((item) => item.medicine.id !== medicineId));
  };

  const clearCart = () => {
    setCart([]);
    setCustomerPhone('');
    setCustomerFirstName('');
    setCustomerLastName('');
  };

  const calculateItemPrice = (item) => {
    let price = item.medicine.price_sell;
    const total_units = item.medicine.units_per_packaging || 1;
    const unit_price = price / total_units;
    
    // Determine price based on sale type
    if (item.sale_type === 'unit') {
      price = unit_price;
    } else if (item.sale_type === 'blister') {
      price = unit_price * (item.medicine.units_per_blister || 1);
    } else if (item.sale_type === 'carton') {
      // Carton Price = Box Price * Boxes per Carton
      price = item.medicine.price_sell * (item.medicine.boxes_per_carton || 1);
    } else {
      // Packaging / Box
      price = item.medicine.price_sell;
    }
    
    // Apply discount
    price = price * (1 - item.discount_percent / 100);
    
    return price;
  };

  const calculateTotal = () => {
    return cart.reduce((sum, item) => {
      return sum + (calculateItemPrice(item) * item.quantity);
    }, 0);
  };

  const handleCheckout = () => {
    if (cart.length === 0) {
      alert(t('cartIsEmpty'));
      return;
    }
    setShowPaymentModal(true);
  };

  return (
    <div className="h-full flex gap-6">
      {/* Left Column - Product Catalog */}
      <div className="flex-1 space-y-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('posTitle')}</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">{t('posSubtitle')}</p>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder={t('searchMedicine')}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-10"
          />
        </div>

        {/* Products Grid */}
        <div className="card p-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">{t('loading')}</p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
              {medicinesData?.items && medicinesData.items.length > 0 ? (
                medicinesData.items.map((medicine) => (
                  <button
                    key={medicine.id}
                    onClick={() => addToCart(medicine)}
                    disabled={medicine.quantity <= 0}
                    className="p-4 border border-border rounded-lg hover:border-primary hover:shadow-md transition-all text-left disabled:opacity-50 disabled:cursor-not-allowed group"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-medium text-gray-900 dark:text-white text-sm line-clamp-2">{medicine.name}</h3>
                      {medicine.packaging && (
                        <span className="text-[10px] bg-gray-100 px-1.5 py-0.5 rounded text-gray-600 dark:text-gray-400">
                           {medicine.packaging}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center justify-between mt-3">
                      <span className="text-lg font-bold text-primary">F{medicine.price_sell?.toFixed(0)}</span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {t('stockLevel')}: {parseFloat(medicine.quantity).toFixed(1).replace('.0', '')}
                      </span>
                    </div>
                    {medicine.units_per_packaging > 1 && (
                      <div className="text-[10px] text-gray-400 mt-1">
                        {medicine.blisters_per_box > 1 
                            ? `1 ${medicine.packaging || 'Boîte'} = ${medicine.blisters_per_box} Pliq. x ${medicine.units_per_blister} Unit. (${medicine.units_per_packaging} total)`
                            : `1 ${medicine.packaging || 'Boîte'} = ${medicine.units_per_packaging} unités`
                        }
                      </div>
                    )}
                  </button>
                ))
              ) : (
                <div className="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">
                  {t('noProducts')}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Right Column - Cart & Payment */}
      <div className="w-96 space-y-4">
        <div className="card p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <ShoppingCart className="w-5 h-5" />
              {t('cart')} ({cart.length})
            </h2>
            {cart.length > 0 && (
              <button
                onClick={clearCart}
                className="text-sm text-danger hover:text-danger-600"
              >
                {t('clearCart')}
              </button>
            )}
          </div>

          {/* Cart Items */}
          <div className="space-y-3 mb-4 max-h-[400px] overflow-y-auto">
            {cart.length === 0 ? (
              <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                <ShoppingCart className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p className="text-sm">{t('emptyCart')}</p>
              </div>
            ) : (
              cart.map((item) => (
                <div key={item.medicine.id} className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 border border-border">
                  {/* Header: Name and Remove */}
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate flex-1 mr-2">{item.medicine.name}</h4>
                    <button
                      onClick={() => removeFromCart(item.medicine.id)}
                      className="p-1 hover:bg-danger-50 rounded text-danger"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Pricing and Mode */}
                  <div className="text-sm mb-2">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-500 dark:text-gray-400 text-xs">{t('unitPrice')}:</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        F{calculateItemPrice(item).toFixed(0)}
                        {item.discount_percent > 0 && (
                           <span className="text-xs text-success ml-1">(-{item.discount_percent}%)</span>
                        )}
                      </span>
                    </div>
                  </div>

                  {/* Controls Row */}
                  <div className="flex items-center justify-between gap-2 mt-2">
                    
                    {/* Mode Selector */}
                    {(item.medicine.units_per_packaging > 1 || item.medicine.blisters_per_box > 1 || item.medicine.boxes_per_carton > 1) ? (
                       <div className="flex bg-white rounded border border-gray-200 p-0.5">
                         
                         {/* CARTON - Only if boxes_per_carton > 1 */}
                         {item.medicine.boxes_per_carton > 1 && (
                            <button
                                className={`p-1 rounded ${item.sale_type === 'carton' ? 'bg-primary-100 text-primary' : 'text-gray-400'}`}
                                onClick={() => updateSaleType(item.medicine.id, 'carton')}
                                title={item.medicine.carton_type || "Carton"}
                            >
                                <Package className="w-4 h-4" />
                            </button>
                         )}

                         {/* BOX */}
                         <button
                           className={`p-1 rounded ${item.sale_type === 'packaging' ? 'bg-primary-100 text-primary' : 'text-gray-400'}`}
                           onClick={() => updateSaleType(item.medicine.id, 'packaging')}
                           title={item.medicine.packaging || "Boîte"}
                         >
                           <Box className="w-4 h-4" />
                         </button>
                         
                         {/* BLISTER - Only if blisters > 1 */}
                         {item.medicine.blisters_per_box > 1 && (
                            <button
                                className={`p-1 rounded ${item.sale_type === 'blister' ? 'bg-primary-100 text-primary' : 'text-gray-400'}`}
                                onClick={() => updateSaleType(item.medicine.id, 'blister')}
                                title="Plaquette/Unités Interm."
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-grid"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>
                            </button>
                         )}

                         {/* UNIT */}
                         <button
                           className={`p-1 rounded ${item.sale_type === 'unit' ? 'bg-primary-100 text-primary' : 'text-gray-400'}`}
                           onClick={() => updateSaleType(item.medicine.id, 'unit')}
                           title="Détail"
                         >
                           <Tablet className="w-4 h-4" />
                         </button>
                       </div>
                    ) : (
                        <div className="w-[80px]"></div> /* spacer */
                    )}

                    {/* Quantity Controls */}
                    <div className="flex items-center bg-white border border-gray-200 rounded">
                      <button
                        onClick={() => updateQuantity(item.medicine.id, -1)}
                        className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400"
                      >
                        <Minus className="w-4 h-4" />
                      </button>
                      <span className="w-8 text-center text-sm font-medium">{item.quantity}</span>
                      <button
                        onClick={() => updateQuantity(item.medicine.id, 1)}
                        className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400"
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>

                    {/* Discount Button */}
                    <div className="relative">
                        <button 
                            onClick={() => setDiscountModalItem(discountModalItem === item.medicine.id ? null : item.medicine.id)}
                            className={`p-1.5 rounded border ${item.discount_percent > 0 ? 'bg-success-50 border-success text-success' : 'bg-white border-gray-200 text-gray-400'}`}
                        >
                            <Percent className="w-4 h-4" />
                        </button>
                        
                        {/* Inline Discount Popover */}
                        {discountModalItem === item.medicine.id && (
                            <div className="absolute bottom-full right-0 mb-2 p-2 bg-white shadow-xl border border-gray-200 rounded-lg w-32 z-10">
                                <label className="text-xs font-semibold text-gray-700 mb-1 block">{t('discount')} %</label>
                                <input 
                                    type="number" 
                                    min="0"
                                    max="100"
                                    className="input py-1 px-2 text-sm w-full"
                                    value={item.discount_percent}
                                    onChange={(e) => updateDiscount(item.medicine.id, parseFloat(e.target.value) || 0)}
                                    autoFocus
                                />
                                <button 
                                    className="text-xs text-primary mt-2 w-full text-center hover:underline"
                                    onClick={() => setDiscountModalItem(null)}
                                >
                                    {t('close')}
                                </button>
                            </div>
                        )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Customer Info */}
          <div className="space-y-3 mb-4 border-t border-border pt-4">
            <h3 className="text-sm font-medium text-gray-900 dark:text-white">{t('customerInfo')}</h3>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="text"
                value={customerFirstName}
                onChange={(e) => setCustomerFirstName(e.target.value)}
                className="input text-sm"
                placeholder={t('firstName')}
              />
              <input
                type="text"
                value={customerLastName}
                onChange={(e) => setCustomerLastName(e.target.value)}
                className="input text-sm"
                placeholder={t('lastName')}
              />
            </div>
            <input
              type="tel"
              value={customerPhone}
              onChange={(e) => setCustomerPhone(e.target.value)}
              className="input text-sm"
              placeholder={t('phone') + " (+225...)"}
            />
          </div>

          {/* Total */}
          <div className="border-t border-border pt-4 mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">{t('subtotal')}</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">F{calculateTotal().toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-base font-semibold text-gray-900 dark:text-white">{t('total')}</span>
              <span className="text-xl font-bold text-primary">F{calculateTotal().toFixed(0)}</span>
            </div>
          </div>

          {/* Checkout Button */}
          <button
            onClick={handleCheckout}
            disabled={cart.length === 0}
            className="w-full btn btn-primary py-3 text-base disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {t('checkout')}
          </button>
        </div>
      </div>

      {/* Payment Modal */}
      {showPaymentModal && (
        <PaymentModal
          cart={cart}
          customerData={{
            phone: customerPhone,
            firstName: customerFirstName,
            lastName: customerLastName
          }}
          totalAmount={calculateTotal()}
          onClose={() => setShowPaymentModal(false)}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['medicines'] });
            queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
            clearCart();
            setShowPaymentModal(false);
          }}
        />
      )}
    </div>
  );
};
