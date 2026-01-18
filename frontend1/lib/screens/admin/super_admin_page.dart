import 'package:flutter/material.dart';
import 'package:frontend1/core/theme.dart';
import 'package:frontend1/services/settings_service.dart'; // AdminService is here

import 'package:frontend1/providers/language_provider.dart';
import 'package:provider/provider.dart';
import 'package:frontend1/providers/auth_provider.dart';
import 'package:frontend1/providers/license_provider.dart';

class SuperAdminPage extends StatefulWidget {
  const SuperAdminPage({super.key});

  @override
  State<SuperAdminPage> createState() => _SuperAdminPageState();
}

class _SuperAdminPageState extends State<SuperAdminPage> {
  final AdminService _adminService = AdminService();
  bool _isLoading = true;
  bool _isUpdating = false;

  // License Data
  String _expiryDate = '';
  bool _isValid = false;
  int _daysRemaining = 0;

  final TextEditingController _dateCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _checkAuthAndLoad();
  }

  Future<void> _checkAuthAndLoad() async {
    // Check Role
    final auth = Provider.of<AuthProvider>(context, listen: false);
    if (auth.user?.role != 'super_admin') {
      // Redirect or Show Error
      // Since we are in init, wait for build
      await Future.delayed(Duration.zero);
      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/dashboard');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              Provider.of<LanguageProvider>(
                context,
                listen: false,
              ).translate('accessDeniedSuperAdmin'),
            ),
            backgroundColor: Colors.red,
          ),
        );
      }
      return;
    }

    _loadLicense();
  }

  Future<void> _loadLicense() async {
    setState(() => _isLoading = true);
    try {
      final data = await _adminService.getLicense();
      setState(() {
        _expiryDate = data['expiry_date'] ?? '';
        _isValid = data['is_valid'] ?? false;
        _daysRemaining = data['days_remaining'] ?? 0;
        _dateCtrl.text = _expiryDate;
        _isLoading = false;
      });
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        final lp = Provider.of<LanguageProvider>(context, listen: false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${lp.translate('errorLoadingLicense')}: $e')),
        );
      }
    }
  }

  Future<void> _updateLicense() async {
    setState(() => _isUpdating = true);
    try {
      final data = await _adminService.updateLicense(_dateCtrl.text);
      if (mounted) {
        setState(() {
          _expiryDate = data['expiry_date'];
          _isValid = data['is_valid'];
          _daysRemaining = data['days_remaining'];
          _isUpdating = false;
        });
        final lp = Provider.of<LanguageProvider>(context, listen: false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(lp.translate('licenseUpdated')),
            backgroundColor: Colors.green,
          ),
        );
      }
      if (mounted) {
        Provider.of<LicenseProvider>(context, listen: false).checkLicense();
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isUpdating = false);
        final lp = Provider.of<LanguageProvider>(context, listen: false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${lp.translate('updateError')}: $e')),
        );
      }
    }
  }

  Future<void> _pickDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: _expiryDate.isNotEmpty
          ? DateTime.tryParse(_expiryDate) ?? now
          : now,
      firstDate: DateTime(2020),
      lastDate: DateTime(2050),
    );

    if (picked != null) {
      // Format YYYY-MM-DD
      final formatted =
          "${picked.year}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}";
      setState(() {
        _dateCtrl.text = formatted;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final lp = Provider.of<LanguageProvider>(context);
    return Column(
      children: [
        // Simple Header inside the layout
        Container(
          padding: const EdgeInsets.all(24),
          child: Row(
            children: [
              const Icon(Icons.shield, size: 32, color: AppTheme.primaryColor),
              const SizedBox(width: 16),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    lp.translate('superAdmin'),
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    lp.translate('softwareLicenseManagement'),
                    style: const TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            ],
          ),
        ),

        if (_isLoading)
          const Expanded(child: Center(child: CircularProgressIndicator()))
        else
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Center(
                child: Container(
                  constraints: const BoxConstraints(maxWidth: 600),
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(32),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Status Box
                          Container(
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: Colors.grey[100],
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: Colors.grey[300]!),
                            ),
                            child: Row(
                              children: [
                                Icon(Icons.warning, color: Colors.orange[800]),
                                const SizedBox(width: 16),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      lp.translate('currentLicenseStatus'),
                                      style: Theme.of(
                                        context,
                                      ).textTheme.titleMedium,
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      "${lp.translate('expiresOn')}: $_expiryDate",
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      _isValid
                                          ? "${lp.translate('valid')} (${_daysRemaining} ${lp.translate('daysRemaining')})"
                                          : lp.translate('expired'),
                                      style: TextStyle(
                                        color: _isValid
                                            ? Colors.green
                                            : Colors.red,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 32),

                          // Form
                          Text(
                            lp.translate('newExpirationDate'),
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 8),
                          InkWell(
                            onTap: _pickDate,
                            child: IgnorePointer(
                              child: TextField(
                                controller: _dateCtrl,
                                decoration: const InputDecoration(
                                  prefixIcon: Icon(Icons.calendar_today),
                                  border: OutlineInputBorder(),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 24),

                          SizedBox(
                            width: double.infinity,
                            height: 50,
                            child: ElevatedButton.icon(
                              onPressed: _isUpdating ? null : _updateLicense,
                              icon: const Icon(Icons.save),
                              label: _isUpdating
                                  ? const CircularProgressIndicator(
                                      color: Colors.white,
                                    )
                                  : Text(lp.translate('updateLicense')),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: AppTheme.primaryColor,
                                foregroundColor: Colors.white,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}
