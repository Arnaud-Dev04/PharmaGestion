import 'package:flutter/material.dart';

import 'package:frontend1/core/theme.dart';

import 'package:frontend1/services/settings_service.dart';
import 'package:frontend1/providers/language_provider.dart';
import 'package:provider/provider.dart';
import 'package:frontend1/providers/auth_provider.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  final SettingsService _settingsService = SettingsService();
  final AdminService _adminService = AdminService();

  // General Settings State

  bool _isLoadingSettings = false;
  final _formKey = GlobalKey<FormState>();

  // Controllers
  final _pharmacyNameCtrl = TextEditingController();
  final _addressCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _logoUrlCtrl = TextEditingController();
  final _currencyCtrl = TextEditingController();
  final _licenseDaysCtrl = TextEditingController();
  final _licenseDurationCtrl = TextEditingController();
  final _licenseMsgCtrl = TextEditingController();

  // Reset State
  bool _resetSales = false;
  bool _resetStock = false;
  bool _resetUsers = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  @override
  void dispose() {
    _pharmacyNameCtrl.dispose();
    _addressCtrl.dispose();
    _phoneCtrl.dispose();
    _logoUrlCtrl.dispose();
    _currencyCtrl.dispose();
    _licenseDaysCtrl.dispose();
    _licenseDurationCtrl.dispose();
    _licenseMsgCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadSettings() async {
    setState(() => _isLoadingSettings = true);
    try {
      final s = await _settingsService.getSettings();
      setState(() {
        _pharmacyNameCtrl.text = s.pharmacyName;
        _addressCtrl.text = s.pharmacyAddress;
        _phoneCtrl.text = s.pharmacyPhone;
        _logoUrlCtrl.text = s.logoUrl;
        _currencyCtrl.text = s.currency;
        _licenseDaysCtrl.text = s.licenseWarningDays.toString();
        _licenseDurationCtrl.text = s.licenseWarningDuration.toString();
        _licenseMsgCtrl.text = s.licenseWarningMessage;
        _isLoadingSettings = false;
      });
    } catch (e) {
      print('Erreur loadSettings: $e');
      setState(() => _isLoadingSettings = false);
    }
  }

  Future<void> _saveSettings() async {
    if (!_formKey.currentState!.validate()) return;
    try {
      final data = {
        'pharmacy_name': _pharmacyNameCtrl.text,
        'pharmacy_address': _addressCtrl.text,
        'pharmacy_phone': _phoneCtrl.text,
        'logo_url': _logoUrlCtrl.text,
        'currency': _currencyCtrl.text,
      };
      await _settingsService.updateSettings(data);
      if (mounted) {
        final lp = Provider.of<LanguageProvider>(context, listen: false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(lp.translate('settingsUpdated')),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        final lp = Provider.of<LanguageProvider>(context, listen: false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${lp.translate('errorUpdating')}: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _saveAdminSettings() async {
    // Pas de validation du form général ici
    try {
      final data = {
        'license_warning_bdays': int.tryParse(_licenseDaysCtrl.text) ?? 60,
        'license_warning_duration':
            int.tryParse(_licenseDurationCtrl.text) ?? 30,
        'license_warning_message': _licenseMsgCtrl.text,
      };
      await _settingsService.updateSettings(data);
      if (mounted) {
        // Force refresh license status if needed
        // Provider.of<LicenseProvider>(context, listen: false).checkLicense();
        final lp = Provider.of<LanguageProvider>(context, listen: false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(lp.translate('settingsUpdated')),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        final lp = Provider.of<LanguageProvider>(context, listen: false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${lp.translate('errorUpdating')}: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _resetData(bool sales, bool products, bool users) async {
    final lp = Provider.of<LanguageProvider>(context, listen: false);
    if (!await _confirm(
      lp.translate('deleteIrreversibleConfirm'),
      lp.translate('deleteDataConfirm'),
    ))
      return;
    try {
      await _adminService.resetData(
        sales: sales,
        products: products,
        users: users,
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(lp.translate('dataResetSuccess')),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur: $e'), backgroundColor: Colors.red),
      );
    }
  }

  Future<bool> _confirm(String title, String content) async {
    final lp = Provider.of<LanguageProvider>(context, listen: false);
    return await showDialog<bool>(
          context: context,
          builder: (c) => AlertDialog(
            title: Text(title),
            content: Text(content),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(c, false),
                child: Text(lp.translate('no')),
              ),
              TextButton(
                onPressed: () => Navigator.pop(c, true),
                child: Text(
                  lp.translate('yes'),
                  style: const TextStyle(color: Colors.red),
                ),
              ),
            ],
          ),
        ) ??
        false;
  }

  @override
  Widget build(BuildContext context) {
    final lp = Provider.of<LanguageProvider>(context);
    final isSuperAdmin =
        Provider.of<AuthProvider>(context).user?.role == 'super_admin';
    final tabCount = isSuperAdmin ? 2 : 1;

    return DefaultTabController(
      length: tabCount,
      child: Column(
        children: [
          // TabBar
          Container(
            color: Colors.white,
            child: TabBar(
              labelColor: AppTheme.primaryColor,
              unselectedLabelColor: Colors.grey,
              indicatorColor: AppTheme.primaryColor,
              tabs: [
                Tab(
                  icon: const Icon(Icons.business),
                  text: lp.translate('general'),
                ),
                if (isSuperAdmin)
                  Tab(
                    icon: const Icon(Icons.security),
                    text: lp.translate('administration'),
                  ),
              ],
            ),
          ),

          // Content
          Expanded(
            child: TabBarView(
              children: [
                // 1. General
                _isLoadingSettings
                    ? const Center(child: CircularProgressIndicator())
                    : SingleChildScrollView(
                        padding: const EdgeInsets.all(24),
                        child: Form(
                          key: _formKey,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                lp.translate('pharmacyIdentity'),
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 16),
                              _input(
                                lp.translate('pharmacyName'),
                                _pharmacyNameCtrl,
                              ),
                              _input(lp.translate('address'), _addressCtrl),
                              _input(lp.translate('phone'), _phoneCtrl),
                              _input(lp.translate('logoPath'), _logoUrlCtrl),
                              const SizedBox(height: 24),
                              Text(
                                lp.translate('salesConfig'),
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 16),
                              _input(lp.translate('currency'), _currencyCtrl),
                              const SizedBox(height: 32),
                              SizedBox(
                                width: double.infinity,
                                child: ElevatedButton.icon(
                                  onPressed: _saveSettings,
                                  icon: const Icon(Icons.save),
                                  label: Text(lp.translate('save')),
                                  style: ElevatedButton.styleFrom(
                                    padding: const EdgeInsets.all(16),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),

                // 3. Admin (Zone Danger)
                if (isSuperAdmin)
                  SingleChildScrollView(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Configuration Licence',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        _input(
                          'Jours avant alerte',
                          _licenseDaysCtrl,
                          numeric: true,
                        ),
                        _input(
                          'Durée alerte (sec)',
                          _licenseDurationCtrl,
                          numeric: true,
                        ),
                        _input('Message alerte', _licenseMsgCtrl, maxLines: 2),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _saveAdminSettings,
                          child: const Text('Enregistrer Config'),
                        ),

                        const Padding(
                          padding: EdgeInsets.symmetric(vertical: 24),
                          child: Divider(),
                        ),

                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.red[50],
                            border: Border.all(color: Colors.red[200]!),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  const Icon(Icons.warning, color: Colors.red),
                                  const SizedBox(width: 8),
                                  Text(
                                    lp.translate('dangerZone'),
                                    style: const TextStyle(
                                      color: Colors.red,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 18,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 16),
                              Text(lp.translate('irreversibleActions')),
                              const SizedBox(height: 16),
                              const SizedBox(height: 16),
                              Text(lp.translate('selectDataToDelete')),
                              const SizedBox(height: 8),
                              CheckboxListTile(
                                title: Text(lp.translate('clearSalesHistory')),
                                value: _resetSales,
                                onChanged: (v) =>
                                    setState(() => _resetSales = v ?? false),
                                activeColor: Colors.red,
                              ),
                              CheckboxListTile(
                                title: Text(lp.translate('clearStock')),
                                value: _resetStock,
                                onChanged: (v) =>
                                    setState(() => _resetStock = v ?? false),
                                activeColor: Colors.red,
                              ),
                              CheckboxListTile(
                                title: Text(lp.translate('clearUsers')),
                                value: _resetUsers,
                                onChanged: (v) =>
                                    setState(() => _resetUsers = v ?? false),
                                activeColor: Colors.red,
                              ),
                              const SizedBox(height: 16),
                              SizedBox(
                                width: double.infinity,
                                child: ElevatedButton.icon(
                                  onPressed:
                                      (_resetSales ||
                                          _resetStock ||
                                          _resetUsers)
                                      ? () => _resetData(
                                          _resetSales,
                                          _resetStock,
                                          _resetUsers,
                                        )
                                      : null,
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.red,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(
                                      vertical: 16,
                                    ),
                                  ),
                                  icon: const Icon(Icons.delete_forever),
                                  label: Text(
                                    lp.translate('confirmDeleteButton'),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _input(
    String label,
    TextEditingController ctrl, {
    bool numeric = false,
    int maxLines = 1,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: TextFormField(
        controller: ctrl,
        keyboardType: numeric ? TextInputType.number : TextInputType.text,
        maxLines: maxLines,
        decoration: InputDecoration(
          labelText: label,
          isDense: true,
          border: const OutlineInputBorder(),
        ),
        validator: (v) => v!.isEmpty ? 'Requis' : null,
      ),
    );
  }
}
