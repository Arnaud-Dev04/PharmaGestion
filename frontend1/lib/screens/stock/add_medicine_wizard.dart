import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:ui';
import 'package:frontend1/core/theme.dart';
import 'package:frontend1/models/medicine_pricing.dart';
import 'package:frontend1/services/medicine_pricing_service.dart';

// ============================================================================
// WIZARD D'AJOUT DE MÉDICAMENT — Multi-étapes moderne
// 4 étapes : Identification → Conditionnement → Prix → Stock
// ============================================================================

class AddMedicineWizard extends StatefulWidget {
  final MedicinePricing? existing;
  const AddMedicineWizard({super.key, this.existing});

  @override
  State<AddMedicineWizard> createState() => _AddMedicineWizardState();
}

class _AddMedicineWizardState extends State<AddMedicineWizard>
    with TickerProviderStateMixin {
  final _pageController = PageController();
  final _service = MedicinePricingService();

  int _currentStep = 0;
  bool _isSubmitting = false;

  // Clés de formulaire par étape
  final _step1Key = GlobalKey<FormState>();
  final _step2Key = GlobalKey<FormState>();
  final _step3Key = GlobalKey<FormState>();
  final _step4Key = GlobalKey<FormState>();

  // ── Étape 1 — Identification ───────────────────────────────────────────────
  final _nomCtrl            = TextEditingController();
  final _dciCtrl            = TextEditingController();
  final _formeCtrl          = TextEditingController();
  final _dosageCtrl         = TextEditingController();
  final _lotCtrl            = TextEditingController(text: 'LOT-001');
  final _fournisseurCtrl    = TextEditingController();
  final _bonLivraisonCtrl   = TextEditingController();
  DateTime? _dateReception;
  DateTime? _datePeremption;
  String _ordonnance = OrdonnanceType.non.value; // stocké comme String

  // ── Étape 2 — Conditionnement ──────────────────────────────────────────────
  final _nbCartonsCtrl           = TextEditingController(text: '1');
  final _boitesParCartonCtrl     = TextEditingController(text: '1');
  final _plaquettesParBoiteCtrl  = TextEditingController(text: '1');
  final _comprimesParPlaquetteCtrl = TextEditingController(text: '1');

  // ── Étape 3 — Prix ────────────────────────────────────────────────────────
  final _achatCartonCtrl    = TextEditingController();
  final _venteCartonCtrl    = TextEditingController();
  final _margePctCtrl       = TextEditingController(text: '20');
  PricingMode _pricingMode  = PricingMode.pctMarge;

  // ── Étape 4 — Stock ───────────────────────────────────────────────────────
  final _seuilAlerteCtrl  = TextEditingController(text: '10');
  final _emplacementCtrl  = TextEditingController();
  final _alerteJoursCtrl  = TextEditingController(text: '30');
  bool _alertePeremption  = true;

  // ── Suggestions ──────────────────────────────────────────────────────────
  static const _dciBase = [
    'Paracétamol','Amoxicilline','Amoxicilline + Acide clavulanique',
    'Ibuprofène','Diclofénac','Oméprazole','Métronidazole',
    'Ciprofloxacine','Azithromycine','Doxycycline','Céfixime',
    'Céftriaxone','Cotrimoxazole','Érythromycine','Gentamicine',
    'Métformine','Glibenclamide','Amlodipine','Captopril','Enalapril',
    'Losartan','Atenolol','Furosémide','Hydrochlorothiazide',
    'Salbutamol','Prednisolone','Dexaméthasone','Hydrocortisone',
    'Fer + Acide folique','Acide folique','Vitamine C','Vitamine B complexe',
    'Albendazole','Mébendazole','Artéméther + Luméfantrine','Quinine',
    'Chloroquine','Artésunate','Tramadol','Codéine','Morphine',
    'Diazépam','Phénobarbital','Carbamazépine','Insuline',
    'Nifédipine','Ranitidine','Lopéramide','ORS (SRO)',
    'Rifampicine','Isoniazide','Pyrazinamide','Éthambutol','Fluconazole',
  ];

  static const _formesBase = [
    'Comprimé','Comprimé pelliculé','Comprimé effervescent',
    'Comprimé orodispersible','Gélule','Capsule molle',
    'Sirop','Suspension buvable','Solution buvable',
    'Solution injectable','Poudre pour injection',
    'Pommade','Crème','Gel','Lotion',
    'Collyre','Gouttes auriculaires','Suppositoire','Ovule',
    'Patch transdermique','Sachet','Spray nasal','Aérosol',
  ];

  static const _dosagesBase = [
    '100mg','125mg','200mg','250mg','400mg','500mg','1g',
    '50mg','75mg','150mg','300mg','600mg','800mg',
    '5mg','10mg','20mg','25mg','40mg','80mg',
    '125mg/5ml','250mg/5ml','100mg/5ml',
    '1%','2%','5%','0.5%',
  ];

  // ── Getters calculés ──────────────────────────────────────────────────────
  int get _nbCartons => int.tryParse(_nbCartonsCtrl.text) ?? 0;
  int get _bpc       => int.tryParse(_boitesParCartonCtrl.text) ?? 0;
  int get _ppb       => int.tryParse(_plaquettesParBoiteCtrl.text) ?? 0;
  int get _cpp       => int.tryParse(_comprimesParPlaquetteCtrl.text) ?? 0;

  int get _totalBoites     => _nbCartons * _bpc;
  int get _totalPlaquettes => _totalBoites * _ppb;
  int get _totalComprimes  => _totalPlaquettes * _cpp;

  double get _achat  => double.tryParse(_achatCartonCtrl.text) ?? 0;
  double get _marge  => double.tryParse(_margePctCtrl.text) ?? 0;
  double get _venteCartonCalc {
    if (_pricingMode == PricingMode.pctMarge) {
      return _achat * (1 + _marge / 100);
    }
    return double.tryParse(_venteCartonCtrl.text) ?? 0;
  }
  double get _beneficeEstime =>
      (_venteCartonCalc - _achat) * _nbCartons;

  @override
  void initState() {
    super.initState();
    if (widget.existing != null) _prefill(widget.existing!);
    for (final c in [
      _achatCartonCtrl, _margePctCtrl, _venteCartonCtrl,
      _nbCartonsCtrl, _boitesParCartonCtrl,
      _plaquettesParBoiteCtrl, _comprimesParPlaquetteCtrl,
    ]) {
      c.addListener(() => setState(() {}));
    }
  }

  void _prefill(MedicinePricing e) {
    _nomCtrl.text          = e.nom;
    _dciCtrl.text          = e.dci ?? '';
    _formeCtrl.text        = e.forme ?? '';
    _dosageCtrl.text       = e.dosage ?? '';
    _lotCtrl.text          = e.lot;
    _fournisseurCtrl.text  = e.fournisseur ?? '';
    _bonLivraisonCtrl.text = e.bonLivraison ?? '';
    _dateReception         = e.dateReception;
    _datePeremption        = e.datePeremption;
    _ordonnance            = e.ordonnance;
    _nbCartonsCtrl.text            = e.nbCartons.toString();
    _boitesParCartonCtrl.text      = e.boitesParCarton.toString();
    _plaquettesParBoiteCtrl.text   = e.plaquettesParBoite.toString();
    _comprimesParPlaquetteCtrl.text = e.comprimesParPlaquette.toString();
    _achatCartonCtrl.text  = e.achatCarton.toStringAsFixed(0);
    _margePctCtrl.text     = (e.margePct ?? 20).toStringAsFixed(0);
    _pricingMode           = PricingMode.fromString(e.prixMode);
    _seuilAlerteCtrl.text  = e.seuilAlerte.toString();
    _emplacementCtrl.text  = e.emplacement ?? '';
    _alertePeremption      = e.alertePeremption;
    _alerteJoursCtrl.text  = (e.alerteJours ?? 30).toString();
  }

  @override
  void dispose() {
    _pageController.dispose();
    for (final c in [
      _nomCtrl, _dciCtrl, _formeCtrl, _dosageCtrl, _lotCtrl,
      _fournisseurCtrl, _bonLivraisonCtrl,
      _nbCartonsCtrl, _boitesParCartonCtrl, _plaquettesParBoiteCtrl,
      _comprimesParPlaquetteCtrl, _achatCartonCtrl, _venteCartonCtrl,
      _margePctCtrl, _seuilAlerteCtrl, _emplacementCtrl, _alerteJoursCtrl,
    ]) { c.dispose(); }
    super.dispose();
  }

  // ── Navigation ────────────────────────────────────────────────────────────
  Future<void> _next() async {
    final keys = [_step1Key, _step2Key, _step3Key, _step4Key];
    if (!(keys[_currentStep].currentState?.validate() ?? false)) return;
    if (_currentStep == 3) { await _submit(); return; }
    setState(() => _currentStep++);
    _pageController.animateToPage(_currentStep,
        duration: const Duration(milliseconds: 380),
        curve: Curves.easeInOutCubic);
  }

  void _prev() {
    if (_currentStep == 0) { Navigator.of(context).pop(false); return; }
    setState(() => _currentStep--);
    _pageController.animateToPage(_currentStep,
        duration: const Duration(milliseconds: 380),
        curve: Curves.easeInOutCubic);
  }

  /// Extrait le message lisible depuis une erreur Dio (422, 400, 500…)
  String _extractErrorMessage(Object e) {
    final raw = e.toString();
    // DioException contient la réponse Pydantic dans son message
    final match = RegExp(r'detail["\s]*:["\s]*(.{0,300})', caseSensitive: false).firstMatch(raw);
    if (match != null) return match.group(1)?.replaceAll(RegExp(r'[\[\]"\\]'), '').trim() ?? raw;
    return raw;
  }

  Future<void> _submit() async {
    // Vérification pré-soumission : achat obligatoirement > 0
    if (_achat <= 0) {
      setState(() => _currentStep = 2);
      _pageController.animateToPage(2,
          duration: const Duration(milliseconds: 300), curve: Curves.easeInOut);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('⚠️ Veuillez saisir le prix d\'achat (> 0)'),
        backgroundColor: AppTheme.warningColor,
        behavior: SnackBarBehavior.floating,
      ));
      return;
    }
    if (_pricingMode == PricingMode.pctMarge && _marge <= 0) {
      setState(() => _currentStep = 2);
      _pageController.animateToPage(2,
          duration: const Duration(milliseconds: 300), curve: Curves.easeInOut);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('⚠️ La marge doit être supérieure à 0%'),
        backgroundColor: AppTheme.warningColor,
        behavior: SnackBarBehavior.floating,
      ));
      return;
    }

    setState(() => _isSubmitting = true);
    try {
      final venteCarton    = _venteCartonCalc;
      final venteBoite     = _bpc > 0 ? venteCarton / _bpc : 0.0;
      final ventePlaquette = _ppb > 0 ? venteBoite / _ppb : 0.0;
      final venteComprime  = _cpp > 0 ? ventePlaquette / _cpp : 0.0;

      final payload = <String, dynamic>{
        'nom': _nomCtrl.text.trim(),
        'dci': _dciCtrl.text.trim().isNotEmpty ? _dciCtrl.text.trim() : null,
        'forme': _formeCtrl.text.trim().isNotEmpty ? _formeCtrl.text.trim() : null,
        'dosage': _dosageCtrl.text.trim().isNotEmpty ? _dosageCtrl.text.trim() : null,
        'lot': _lotCtrl.text.trim().isNotEmpty ? _lotCtrl.text.trim() : 'LOT-001',
        'fournisseur': _fournisseurCtrl.text.trim().isNotEmpty ? _fournisseurCtrl.text.trim() : null,
        'bon_livraison': _bonLivraisonCtrl.text.trim().isNotEmpty ? _bonLivraisonCtrl.text.trim() : null,
        'date_reception': _dateReception?.toIso8601String().split('T').first,
        'date_peremption': _datePeremption?.toIso8601String().split('T').first,
        'ordonnance': _ordonnance,
        'nb_cartons': _nbCartons,
        'boites_par_carton': _bpc,
        'plaquettes_par_boite': _ppb,
        'comprimes_par_plaquette': _cpp,
        'prix_mode': _pricingMode.value,
        'achat_carton': _achat,
        'achat_boite': _bpc > 0 ? _achat / _bpc : 0.0,
        'achat_plaquette': _ppb > 0 ? _achat / _bpc / _ppb : 0.0,
        'achat_comprime': _cpp > 0 ? _achat / _bpc / _ppb / _cpp : 0.0,
        'vente_carton': venteCarton,
        'vente_boite': venteBoite,
        'vente_plaquette': ventePlaquette,
        'vente_comprime': venteComprime,
        'marge_pct': _marge,
        'seuil_alerte': int.tryParse(_seuilAlerteCtrl.text) ?? 10,
        'emplacement': _emplacementCtrl.text.trim().isNotEmpty ? _emplacementCtrl.text.trim() : null,
        'alerte_peremption': _alertePeremption,
        'alerte_jours': int.tryParse(_alerteJoursCtrl.text) ?? 30,
      };

      if (widget.existing != null) {
        await _service.updatePricing(widget.existing!.id, payload);
      } else {
        await _service.createPricing(payload);
      }

      if (mounted) Navigator.of(context).pop(true);
    } catch (e) {
      if (mounted) {
        setState(() => _isSubmitting = false);
        final msg = _extractErrorMessage(e);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Row(children: [
            const Icon(Icons.error_outline_rounded, color: Colors.white, size: 18),
            const SizedBox(width: 10),
            Expanded(child: Text(msg, maxLines: 3, overflow: TextOverflow.ellipsis)),
          ]),
          backgroundColor: AppTheme.dangerColor,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          duration: const Duration(seconds: 6),
        ));
      }
    }
  }

  // ── Build ─────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final card   = isDark ? AppTheme.darkCard : AppTheme.lightCard;

    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(24),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
          child: Container(
            width: 700,
            constraints: const BoxConstraints(maxHeight: 760),
            decoration: BoxDecoration(
              color: card.withValues(alpha: isDark ? 0.97 : 0.98),
              borderRadius: BorderRadius.circular(24),
              border: Border.all(
                color: AppTheme.primaryColor.withValues(alpha: 0.2),
                width: 1.5,
              ),
              boxShadow: [BoxShadow(
                color: AppTheme.primaryColor.withValues(alpha: 0.15),
                blurRadius: 40,
                spreadRadius: -5,
              )],
            ),
            child: Column(children: [
              _buildHeader(isDark),
              _buildStepBar(isDark),
              Expanded(
                child: PageView(
                  controller: _pageController,
                  physics: const NeverScrollableScrollPhysics(),
                  children: [
                    _StepIdent(
                      formKey: _step1Key,
                      nomCtrl: _nomCtrl, dciCtrl: _dciCtrl,
                      formeCtrl: _formeCtrl, dosageCtrl: _dosageCtrl,
                      lotCtrl: _lotCtrl, fournisseurCtrl: _fournisseurCtrl,
                      bonLivraisonCtrl: _bonLivraisonCtrl,
                      dateReception: _dateReception,
                      datePeremption: _datePeremption,
                      onDateReception: (d) => setState(() => _dateReception = d),
                      onDatePeremption: (d) => setState(() => _datePeremption = d),
                      ordonnance: _ordonnance,
                      onOrdonnance: (v) => setState(() => _ordonnance = v),
                      dciList: _dciBase,
                      formeList: _formesBase,
                      dosageList: _dosagesBase,
                      isDark: isDark,
                    ),
                    _StepCond(
                      formKey: _step2Key,
                      nbCartonsCtrl: _nbCartonsCtrl,
                      bpcCtrl: _boitesParCartonCtrl,
                      ppbCtrl: _plaquettesParBoiteCtrl,
                      cppCtrl: _comprimesParPlaquetteCtrl,
                      totalBoites: _totalBoites,
                      totalComprimes: _totalComprimes,
                      isDark: isDark,
                    ),
                    _StepPrix(
                      formKey: _step3Key,
                      achatCtrl: _achatCartonCtrl,
                      venteCtrl: _venteCartonCtrl,
                      margeCtrl: _margePctCtrl,
                      mode: _pricingMode,
                      onMode: (m) => setState(() => _pricingMode = m),
                      venteCalc: _venteCartonCalc,
                      benefice: _beneficeEstime,
                      nbCartons: _nbCartons,
                      isDark: isDark,
                    ),
                    _StepStock(
                      formKey: _step4Key,
                      seuilCtrl: _seuilAlerteCtrl,
                      emplacementCtrl: _emplacementCtrl,
                      joursCtrl: _alerteJoursCtrl,
                      alertePeremption: _alertePeremption,
                      onAlerte: (v) => setState(() => _alertePeremption = v),
                      totalComprimes: _totalComprimes,
                      benefice: _beneficeEstime,
                      nom: _nomCtrl.text,
                      isDark: isDark,
                    ),
                  ],
                ),
              ),
              _buildFooter(isDark),
            ]),
          ),
        ),
      ),
    );
  }

  // ── Header ────────────────────────────────────────────────────────────────
  Widget _buildHeader(bool isDark) {
    const titles = ['🏷️  Identification','📦  Conditionnement','💰  Tarification','🏪  Stock & Alertes'];
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 22, 16, 0),
      child: Row(children: [
        Container(
          width: 44, height: 44,
          decoration: BoxDecoration(
            gradient: LinearGradient(colors: [
              AppTheme.primaryColor,
              AppTheme.primaryColor.withValues(alpha: 0.7),
            ], begin: Alignment.topLeft, end: Alignment.bottomRight),
            borderRadius: BorderRadius.circular(12),
          ),
          child: const Icon(Icons.medication_rounded, color: Colors.white, size: 24),
        ),
        const SizedBox(width: 14),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(
            widget.existing != null ? 'Modifier le médicament' : 'Nouveau médicament',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700,
              color: isDark ? AppTheme.darkForeground : AppTheme.lightForeground),
          ),
          Text('Étape ${_currentStep + 1}/4 · ${titles[_currentStep]}',
            style: const TextStyle(fontSize: 13, color: AppTheme.primaryColor, fontWeight: FontWeight.w500)),
        ])),
        IconButton(
          icon: Icon(Icons.close_rounded,
            color: isDark ? AppTheme.darkForeground.withValues(alpha: 0.4) : Colors.grey[400]),
          onPressed: () => Navigator.of(context).pop(false),
        ),
      ]),
    );
  }

  // ── Step bar ──────────────────────────────────────────────────────────────
  Widget _buildStepBar(bool isDark) {
    const labels = ['Infos','Cond.','Prix','Stock'];
    const icons  = [Icons.info_outline_rounded, Icons.inventory_2_outlined,
                    Icons.attach_money_rounded, Icons.store_outlined];
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 18, 24, 6),
      child: Column(children: [
        Row(children: List.generate(labels.length, (i) {
          final done   = i < _currentStep;
          final active = i == _currentStep;
          return Expanded(child: Row(children: [
            Expanded(child: GestureDetector(
              onTap: done ? () {
                setState(() => _currentStep = i);
                _pageController.animateToPage(i,
                    duration: const Duration(milliseconds: 350),
                    curve: Curves.easeInOut);
              } : null,
              child: Column(children: [
                AnimatedContainer(
                  duration: const Duration(milliseconds: 280),
                  width: 42, height: 42,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: (active || done) ? LinearGradient(colors: done
                      ? [AppTheme.successColor, AppTheme.successColor.withValues(alpha: 0.8)]
                      : [AppTheme.primaryColor, AppTheme.primaryColor.withValues(alpha: 0.7)],
                      begin: Alignment.topLeft, end: Alignment.bottomRight,
                    ) : null,
                    color: (active || done) ? null
                      : (isDark ? AppTheme.darkBorder : AppTheme.lightBorder),
                    boxShadow: active ? [BoxShadow(
                      color: AppTheme.primaryColor.withValues(alpha: 0.4),
                      blurRadius: 12, spreadRadius: 2,
                    )] : null,
                  ),
                  child: Icon(
                    done ? Icons.check_rounded : icons[i],
                    color: (active || done) ? Colors.white
                      : (isDark ? AppTheme.darkForeground.withValues(alpha: 0.35) : Colors.grey[400]),
                    size: 20,
                  ),
                ),
                const SizedBox(height: 5),
                Text(labels[i], style: TextStyle(
                  fontSize: 11,
                  fontWeight: active ? FontWeight.w700 : FontWeight.w400,
                  color: active ? AppTheme.primaryColor
                    : done ? AppTheme.successColor
                    : (isDark ? AppTheme.darkForeground.withValues(alpha: 0.35) : Colors.grey[400]),
                )),
              ]),
            )),
            if (i < labels.length - 1)
              Expanded(child: AnimatedContainer(
                duration: const Duration(milliseconds: 350),
                height: 2,
                margin: const EdgeInsets.only(bottom: 22),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(1),
                  color: i < _currentStep ? AppTheme.successColor
                    : (isDark ? AppTheme.darkBorder : AppTheme.lightBorder),
                ),
              )),
          ]));
        })),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: (_currentStep + 1) / 4,
            backgroundColor: isDark ? AppTheme.darkBorder : AppTheme.lightBorder,
            valueColor: const AlwaysStoppedAnimation<Color>(AppTheme.primaryColor),
            minHeight: 3,
          ),
        ),
      ]),
    );
  }

  // ── Footer ────────────────────────────────────────────────────────────────
  Widget _buildFooter(bool isDark) {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 14, 24, 22),
      decoration: BoxDecoration(border: Border(top: BorderSide(
        color: isDark ? AppTheme.darkBorder : AppTheme.lightBorder, width: 1))),
      child: Row(children: [
        TextButton.icon(
          onPressed: _isSubmitting ? null : _prev,
          icon: const Icon(Icons.arrow_back_ios_rounded, size: 15),
          label: Text(_currentStep == 0 ? 'Annuler' : 'Retour'),
          style: TextButton.styleFrom(
            foregroundColor: isDark
                ? AppTheme.darkForeground.withValues(alpha: 0.6) : Colors.grey[500],
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          ),
        ),
        const Spacer(),
        Text('Étape ${_currentStep + 1} / 4',
          style: TextStyle(fontSize: 12,
            color: isDark ? AppTheme.darkForeground.withValues(alpha: 0.35) : Colors.grey[400])),
        const SizedBox(width: 16),
        ElevatedButton.icon(
          onPressed: _isSubmitting ? null : _next,
          icon: _isSubmitting
            ? const SizedBox(width: 16, height: 16,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
            : Icon(_currentStep == 3
                ? Icons.check_circle_rounded : Icons.arrow_forward_ios_rounded, size: 16),
          label: Text(
            _isSubmitting ? 'Enregistrement…'
              : _currentStep == 3 ? 'Enregistrer' : 'Suivant',
            style: const TextStyle(fontWeight: FontWeight.w600)),
          style: ElevatedButton.styleFrom(
            backgroundColor: _currentStep == 3 ? AppTheme.successColor : AppTheme.primaryColor,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 13),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            elevation: 0,
          ),
        ),
      ]),
    );
  }
}

// ============================================================================
// ÉTAPE 1 — IDENTIFICATION
// ============================================================================
class _StepIdent extends StatelessWidget {
  final GlobalKey<FormState> formKey;
  final TextEditingController nomCtrl, dciCtrl, formeCtrl, dosageCtrl;
  final TextEditingController lotCtrl, fournisseurCtrl, bonLivraisonCtrl;
  final DateTime? dateReception, datePeremption;
  final ValueChanged<DateTime?> onDateReception, onDatePeremption;
  final String ordonnance;
  final ValueChanged<String> onOrdonnance;
  final List<String> dciList, formeList, dosageList;
  final bool isDark;

  const _StepIdent({
    required this.formKey,
    required this.nomCtrl, required this.dciCtrl,
    required this.formeCtrl, required this.dosageCtrl,
    required this.lotCtrl, required this.fournisseurCtrl,
    required this.bonLivraisonCtrl,
    required this.dateReception, required this.datePeremption,
    required this.onDateReception, required this.onDatePeremption,
    required this.ordonnance, required this.onOrdonnance,
    required this.dciList, required this.formeList, required this.dosageList,
    required this.isDark,
  });

  @override
  Widget build(BuildContext context) {
    return Form(
      key: formKey,
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(24, 10, 24, 10),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          _Field(label: 'Nom commercial *', ctrl: nomCtrl,
            hint: 'Ex: Doliprane 500mg', icon: Icons.medication_rounded, isDark: isDark,
            validator: (v) => (v == null || v.trim().isEmpty) ? 'Champ obligatoire' : null),
          const SizedBox(height: 12),
          _AutoField(label: 'DCI (Principe actif)', ctrl: dciCtrl,
            hint: 'Ex: Paracétamol', icon: Icons.science_outlined,
            suggestions: dciList, isDark: isDark),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(flex: 2, child: _AutoField(label: 'Forme galénique', ctrl: formeCtrl,
              hint: 'Ex: Comprimé', icon: Icons.category_outlined,
              suggestions: formeList, isDark: isDark)),
            const SizedBox(width: 10),
            Expanded(child: _AutoField(label: 'Dosage', ctrl: dosageCtrl,
              hint: 'Ex: 500mg', icon: Icons.tune_rounded,
              suggestions: dosageList, isDark: isDark)),
          ]),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(child: _Field(label: 'N° de lot', ctrl: lotCtrl,
              hint: 'LOT-001', icon: Icons.qr_code_rounded, isDark: isDark)),
            const SizedBox(width: 10),
            Expanded(child: _Field(label: 'Fournisseur', ctrl: fournisseurCtrl,
              hint: 'Nom fournisseur', icon: Icons.local_shipping_outlined, isDark: isDark)),
          ]),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(child: _Field(label: 'Bon de livraison', ctrl: bonLivraisonCtrl,
              hint: 'N° BL', icon: Icons.receipt_long_outlined, isDark: isDark)),
            const SizedBox(width: 10),
            Expanded(child: _DateField(
              label: 'Date réception', date: dateReception,
              onPicked: onDateReception, isDark: isDark,
              firstDate: DateTime(2020), lastDate: DateTime.now())),
          ]),
          const SizedBox(height: 12),
          _DateField(
            label: 'Date de péremption *', date: datePeremption,
            onPicked: onDatePeremption, isDark: isDark,
            firstDate: DateTime.now(), lastDate: DateTime(2035),
            isRequired: true),
          const SizedBox(height: 14),
          _SecTitle('Type d\'ordonnance', isDark),
          const SizedBox(height: 8),
          _OrdonnanceSelector(current: ordonnance, onChanged: onOrdonnance, isDark: isDark),
        ]),
      ),
    );
  }
}

// ============================================================================
// ÉTAPE 2 — CONDITIONNEMENT
// ============================================================================
class _StepCond extends StatelessWidget {
  final GlobalKey<FormState> formKey;
  final TextEditingController nbCartonsCtrl, bpcCtrl, ppbCtrl, cppCtrl;
  final int totalBoites, totalComprimes;
  final bool isDark;

  const _StepCond({
    required this.formKey,
    required this.nbCartonsCtrl, required this.bpcCtrl,
    required this.ppbCtrl, required this.cppCtrl,
    required this.totalBoites, required this.totalComprimes,
    required this.isDark,
  });

  @override
  Widget build(BuildContext context) {
    return Form(key: formKey, child: SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 14, 24, 14),
      child: Column(children: [
        // Hiérarchie visuelle
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppTheme.primaryColor.withValues(alpha: 0.06),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: AppTheme.primaryColor.withValues(alpha: 0.15)),
          ),
          child: Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [
            for (final item in [
              ('📦','Carton',const Color(0xFF6366F1)),
              ('🗂️','Boîtes',AppTheme.primaryColor),
              ('💊','Plaquettes',AppTheme.warningColor),
              ('⚪','Unités',AppTheme.successColor),
            ]) ...[
              Column(children: [
                Text(item.$1, style: const TextStyle(fontSize: 22)),
                const SizedBox(height: 3),
                Text(item.$2, style: TextStyle(fontSize: 11,
                  fontWeight: FontWeight.w600, color: item.$3)),
              ]),
              if (item != ('⚪','Unités',AppTheme.successColor))
                Icon(Icons.chevron_right_rounded, color: Colors.grey[400], size: 20),
            ],
          ]),
        ),
        const SizedBox(height: 18),
        _SecTitle('Quantités reçues', isDark),
        const SizedBox(height: 10),
        for (final row in [
          (_nbCartonsRow(context),),
          (_bpcRow(context),),
          (_ppbRow(context),),
          (_cppRow(context),),
        ]) ...[row.$1, const SizedBox(height: 10)],
        const SizedBox(height: 8),
        // Résumé
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            gradient: LinearGradient(colors: [
              AppTheme.successColor.withValues(alpha: 0.1),
              AppTheme.primaryColor.withValues(alpha: 0.05),
            ]),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: AppTheme.successColor.withValues(alpha: 0.3)),
          ),
          child: Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [
            _Metric('🗂️', totalBoites.toString(), 'Total boîtes', AppTheme.primaryColor),
            Container(width: 1, height: 36, color: AppTheme.successColor.withValues(alpha: 0.2)),
            _Metric('⚪', totalComprimes.toString(), 'Total unités', AppTheme.successColor),
          ]),
        ),
      ]),
    ));
  }

  Widget _condRow(BuildContext ctx, String emoji, String label, String sub,
      Color color, TextEditingController ctrl) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Row(children: [
        Text(emoji, style: const TextStyle(fontSize: 20)),
        const SizedBox(width: 10),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600,
            color: isDark ? AppTheme.darkForeground : AppTheme.lightForeground)),
          Text(sub, style: TextStyle(fontSize: 11,
            color: isDark ? AppTheme.darkForeground.withValues(alpha: 0.45) : Colors.grey[500])),
        ])),
        _Stepper(ctrl: ctrl, color: color),
      ]),
    );
  }

  Widget _nbCartonsRow(BuildContext ctx) =>
      _condRow(ctx,'📦','Nombre de cartons','Cartons reçus',const Color(0xFF6366F1),nbCartonsCtrl);
  Widget _bpcRow(BuildContext ctx) =>
      _condRow(ctx,'🗂️','Boîtes par carton','Boîtes dans 1 carton',AppTheme.primaryColor,bpcCtrl);
  Widget _ppbRow(BuildContext ctx) =>
      _condRow(ctx,'💊','Plaquettes par boîte','Plaquettes dans 1 boîte',AppTheme.warningColor,ppbCtrl);
  Widget _cppRow(BuildContext ctx) =>
      _condRow(ctx,'⚪','Comprimés par plaquette','Unités dans 1 plaquette',AppTheme.successColor,cppCtrl);
}

// ============================================================================
// ÉTAPE 3 — PRIX
// ============================================================================
class _StepPrix extends StatelessWidget {
  final GlobalKey<FormState> formKey;
  final TextEditingController achatCtrl, venteCtrl, margeCtrl;
  final PricingMode mode;
  final ValueChanged<PricingMode> onMode;
  final double venteCalc, benefice;
  final int nbCartons;
  final bool isDark;

  const _StepPrix({
    required this.formKey, required this.achatCtrl,
    required this.venteCtrl, required this.margeCtrl,
    required this.mode, required this.onMode,
    required this.venteCalc, required this.benefice,
    required this.nbCartons, required this.isDark,
  });

  @override
  Widget build(BuildContext context) {
    final achat = double.tryParse(achatCtrl.text) ?? 0;
    final margeAff = achat > 0
      ? '${((venteCalc - achat) / achat * 100).toStringAsFixed(1)}%' : '—';
    final profitColor = benefice >= 0 ? AppTheme.successColor : AppTheme.dangerColor;

    return Form(key: formKey, child: SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 14, 24, 14),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        _SecTitle('Mode de tarification', isDark),
        const SizedBox(height: 10),
        Row(children: [
          for (final m in PricingMode.values)
            if (m != PricingMode.manuel) ...[
              Expanded(child: GestureDetector(
                onTap: () => onMode(m),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  margin: const EdgeInsets.only(right: 8),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: mode == m
                      ? AppTheme.primaryColor.withValues(alpha: 0.12)
                      : (isDark ? AppTheme.darkBorder.withValues(alpha: 0.25) : AppTheme.lightBorder.withValues(alpha: 0.5)),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: mode == m ? AppTheme.primaryColor : Colors.transparent,
                      width: 1.5),
                  ),
                  child: Row(children: [
                    Icon(m == PricingMode.pctMarge
                      ? Icons.percent_rounded : Icons.price_change_outlined,
                      size: 18,
                      color: mode == m ? AppTheme.primaryColor : Colors.grey[400]),
                    const SizedBox(width: 8),
                    Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      Text(m == PricingMode.pctMarge ? '% Marge' : 'Prix fixe',
                        style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700,
                          color: mode == m ? AppTheme.primaryColor : Colors.grey[500])),
                      Text(m == PricingMode.pctMarge ? 'Saisir la marge' : 'Saisir le prix',
                        style: TextStyle(fontSize: 10,
                          color: mode == m
                            ? AppTheme.primaryColor.withValues(alpha: 0.65) : Colors.grey[400])),
                    ])),
                  ]),
                ),
              )),
            ],
        ]),
        const SizedBox(height: 16),
        _SecTitle('Prix d\'achat', isDark),
        const SizedBox(height: 8),
        _Field(label: 'Prix d\'achat / carton (FBu)',
          ctrl: achatCtrl, hint: 'Ex: 15000',
          icon: Icons.shopping_cart_outlined, isDark: isDark,
          inputType: TextInputType.number,
          inputFormatters: [FilteringTextInputFormatter.digitsOnly],
          validator: (v) => (v == null || v.trim().isEmpty) ? 'Requis' : null),
        const SizedBox(height: 16),
        _SecTitle('Prix de vente', isDark),
        const SizedBox(height: 8),
        if (mode == PricingMode.pctMarge)
          _Field(label: 'Marge (%)', ctrl: margeCtrl,
            hint: 'Ex: 20', icon: Icons.percent_rounded, isDark: isDark,
            suffix: '%', inputType: TextInputType.number,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly])
        else
          _Field(label: 'Prix de vente / carton (FBu)',
            ctrl: venteCtrl, hint: 'Ex: 18000',
            icon: Icons.sell_outlined, isDark: isDark,
            inputType: TextInputType.number,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly]),
        const SizedBox(height: 18),
        // Aperçu financier temps réel
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(colors: [
              AppTheme.primaryColor.withValues(alpha: 0.08),
              AppTheme.successColor.withValues(alpha: 0.04),
            ], begin: Alignment.topLeft, end: Alignment.bottomRight),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppTheme.primaryColor.withValues(alpha: 0.2)),
          ),
          child: Column(children: [
            Row(children: [
              const Icon(Icons.insights_rounded, color: AppTheme.primaryColor, size: 16),
              const SizedBox(width: 6),
              const Text('Aperçu financier en temps réel',
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700,
                  color: AppTheme.primaryColor)),
            ]),
            const SizedBox(height: 12),
            Row(children: [
              Expanded(child: _MiniCard('Achat/carton',
                '${achat.toStringAsFixed(0)} FBu', AppTheme.dangerColor, isDark)),
              Expanded(child: _MiniCard('Vente/carton',
                '${venteCalc.toStringAsFixed(0)} FBu', AppTheme.primaryColor, isDark)),
            ]),
            const SizedBox(height: 8),
            Row(children: [
              Expanded(child: _MiniCard('Marge réelle', margeAff, AppTheme.warningColor, isDark)),
              Expanded(child: _MiniCard('Bénéfice estimé',
                nbCartons > 0 ? '${benefice.toStringAsFixed(0)} FBu' : '—',
                profitColor, isDark, highlight: true)),
            ]),
          ]),
        ),
      ]),
    ));
  }
}

// ============================================================================
// ÉTAPE 4 — STOCK & ALERTES
// ============================================================================
class _StepStock extends StatelessWidget {
  final GlobalKey<FormState> formKey;
  final TextEditingController seuilCtrl, emplacementCtrl, joursCtrl;
  final bool alertePeremption;
  final ValueChanged<bool> onAlerte;
  final int totalComprimes;
  final double benefice;
  final String nom;
  final bool isDark;

  const _StepStock({
    required this.formKey, required this.seuilCtrl,
    required this.emplacementCtrl, required this.joursCtrl,
    required this.alertePeremption, required this.onAlerte,
    required this.totalComprimes, required this.benefice,
    required this.nom, required this.isDark,
  });

  @override
  Widget build(BuildContext context) {
    return Form(key: formKey, child: SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 14, 24, 14),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        // Carte récap finale
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(colors: [
              AppTheme.successColor.withValues(alpha: 0.1),
              AppTheme.primaryColor.withValues(alpha: 0.04),
            ]),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppTheme.successColor.withValues(alpha: 0.3), width: 1.5),
          ),
          child: Row(children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppTheme.successColor.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(10)),
              child: const Icon(Icons.check_circle_outline_rounded,
                color: AppTheme.successColor, size: 22)),
            const SizedBox(width: 12),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Text('Prêt à enregistrer',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700,
                  color: AppTheme.successColor)),
              Text(nom.isNotEmpty ? nom : '—',
                style: TextStyle(fontSize: 12,
                  color: isDark ? AppTheme.darkForeground.withValues(alpha: 0.55) : Colors.grey[600]),
                maxLines: 1, overflow: TextOverflow.ellipsis),
            ])),
            const SizedBox(width: 12),
            Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
              Text('$totalComprimes unités',
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700,
                  color: AppTheme.primaryColor)),
              Text(benefice > 0 ? '${benefice.toStringAsFixed(0)} FBu' : '—',
                style: TextStyle(fontSize: 12,
                  color: AppTheme.successColor.withValues(alpha: 0.8))),
            ]),
          ]),
        ),
        const SizedBox(height: 18),
        _SecTitle('Emplacement', isDark),
        const SizedBox(height: 8),
        _Field(label: 'Emplacement dans la pharmacie', ctrl: emplacementCtrl,
          hint: 'Ex: Rayon A3 / Réfrigérateur', icon: Icons.location_on_outlined, isDark: isDark),
        const SizedBox(height: 16),
        _SecTitle('Seuil d\'alerte stock', isDark),
        const SizedBox(height: 8),
        _Field(label: 'Alerter si stock < X comprimés', ctrl: seuilCtrl,
          hint: 'Ex: 50', icon: Icons.notifications_outlined, isDark: isDark,
          inputType: TextInputType.number,
          inputFormatters: [FilteringTextInputFormatter.digitsOnly]),
        const SizedBox(height: 16),
        _SecTitle('Alertes péremption', isDark),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: isDark
              ? AppTheme.darkBorder.withValues(alpha: 0.25)
              : AppTheme.lightBorder.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(children: [
            Row(children: [
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('Activer les alertes de péremption',
                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600,
                    color: isDark ? AppTheme.darkForeground : AppTheme.lightForeground)),
                Text('Recevez une alerte avant expiration',
                  style: TextStyle(fontSize: 11,
                    color: isDark
                      ? AppTheme.darkForeground.withValues(alpha: 0.45) : Colors.grey[500])),
              ])),
              Switch(
                value: alertePeremption,
                onChanged: onAlerte,
                activeThumbColor: AppTheme.primaryColor,
              ),
            ]),
            if (alertePeremption) ...[
              const SizedBox(height: 10),
              _Field(label: 'Alerter X jours avant expiration', ctrl: joursCtrl,
                hint: 'Ex: 30', icon: Icons.access_time_rounded, isDark: isDark,
                suffix: 'jours', inputType: TextInputType.number,
                inputFormatters: [FilteringTextInputFormatter.digitsOnly]),
            ],
          ]),
        ),
      ]),
    ));
  }
}

// ============================================================================
// WIDGETS COMMUNS
// ============================================================================

class _SecTitle extends StatelessWidget {
  final String title;
  final bool isDark;
  const _SecTitle(this.title, this.isDark);

  @override
  Widget build(BuildContext context) => Row(children: [
    Container(width: 3, height: 15,
      decoration: BoxDecoration(color: AppTheme.primaryColor, borderRadius: BorderRadius.circular(2))),
    const SizedBox(width: 8),
    Text(title, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, letterSpacing: 0.2,
      color: isDark ? AppTheme.darkForeground : AppTheme.lightForeground)),
  ]);
}

// Champ texte simple
class _Field extends StatelessWidget {
  final String label;
  final TextEditingController ctrl;
  final String hint;
  final IconData icon;
  final bool isDark;
  final String? Function(String?)? validator;
  final TextInputType? inputType;
  final String? suffix;
  final List<TextInputFormatter>? inputFormatters;

  const _Field({
    required this.label, required this.ctrl, required this.hint,
    required this.icon, required this.isDark,
    this.validator, this.inputType, this.suffix, this.inputFormatters,
  });

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(label, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600,
        color: isDark ? AppTheme.darkForeground.withValues(alpha: 0.65) : Colors.grey[700])),
      const SizedBox(height: 5),
      TextFormField(
        controller: ctrl, validator: validator,
        keyboardType: inputType, inputFormatters: inputFormatters,
        style: TextStyle(fontSize: 14,
          color: isDark ? AppTheme.darkForeground : AppTheme.lightForeground),
        decoration: _dec(hint, icon, isDark, suffix: suffix),
      ),
    ],
  );
}

// Champ avec auto-complétion
class _AutoField extends StatefulWidget {
  final String label, hint;
  final TextEditingController ctrl;
  final IconData icon;
  final List<String> suggestions;
  final bool isDark;
  const _AutoField({required this.label, required this.ctrl, required this.hint,
    required this.icon, required this.suggestions, required this.isDark});
  @override State<_AutoField> createState() => _AutoFieldState();
}
class _AutoFieldState extends State<_AutoField> {
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(widget.label, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600,
        color: widget.isDark ? AppTheme.darkForeground.withValues(alpha: 0.65) : Colors.grey[700])),
      const SizedBox(height: 5),
      Autocomplete<String>(
        optionsBuilder: (tv) {
          if (tv.text.isEmpty) return const [];
          return widget.suggestions
            .where((s) => s.toLowerCase().contains(tv.text.toLowerCase()));
        },
        onSelected: (v) => widget.ctrl.text = v,
        fieldViewBuilder: (_, internalCtrl, focusNode, onSubmit) {
          // Sync controllers
          if (internalCtrl.text != widget.ctrl.text) {
            internalCtrl.text = widget.ctrl.text;
          }
          internalCtrl.addListener(() {
            if (widget.ctrl.text != internalCtrl.text) {
              widget.ctrl.text = internalCtrl.text;
            }
          });
          return TextFormField(
            controller: internalCtrl, focusNode: focusNode,
            onFieldSubmitted: (_) => onSubmit(),
            style: TextStyle(fontSize: 14,
              color: widget.isDark ? AppTheme.darkForeground : AppTheme.lightForeground),
            decoration: _dec(widget.hint, widget.icon, widget.isDark,
              suffix2: const Icon(Icons.expand_more_rounded, size: 16)),
          );
        },
        optionsViewBuilder: (_, onSelected, options) => Align(
          alignment: Alignment.topLeft,
          child: Material(color: Colors.transparent, child: Container(
            constraints: const BoxConstraints(maxHeight: 180, maxWidth: 280),
            decoration: BoxDecoration(
              color: widget.isDark ? AppTheme.darkCard : Colors.white,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: AppTheme.primaryColor.withValues(alpha: 0.3)),
              boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.15),
                blurRadius: 14, offset: const Offset(0, 5))],
            ),
            child: ListView(
              padding: const EdgeInsets.symmetric(vertical: 4), shrinkWrap: true,
              children: options.map((o) => InkWell(
                onTap: () => onSelected(o),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
                  child: Row(children: [
                    Icon(Icons.arrow_forward_ios_rounded, size: 11,
                      color: AppTheme.primaryColor.withValues(alpha: 0.5)),
                    const SizedBox(width: 8),
                    Expanded(child: Text(o, style: TextStyle(fontSize: 13,
                      color: widget.isDark ? AppTheme.darkForeground : AppTheme.lightForeground))),
                  ]),
                ),
              )).toList(),
            ),
          )),
        ),
      ),
    ],
  );
}

// Champ date
class _DateField extends StatelessWidget {
  final String label;
  final DateTime? date;
  final ValueChanged<DateTime?> onPicked;
  final bool isDark, isRequired;
  final DateTime firstDate, lastDate;
  const _DateField({required this.label, required this.date, required this.onPicked,
    required this.isDark, required this.firstDate, required this.lastDate,
    this.isRequired = false});

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(label, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600,
        color: isDark ? AppTheme.darkForeground.withValues(alpha: 0.65) : Colors.grey[700])),
      const SizedBox(height: 5),
      GestureDetector(
        onTap: () async {
          final picked = await showDatePicker(
            context: context,
            initialDate: date ?? (firstDate.isBefore(DateTime.now()) ? DateTime.now() : firstDate),
            firstDate: firstDate, lastDate: lastDate,
            builder: (ctx, child) => Theme(
              data: Theme.of(ctx).copyWith(colorScheme: ColorScheme.dark(
                primary: AppTheme.primaryColor,
                surface: isDark ? AppTheme.darkCard : Colors.white,
              )),
              child: child!,
            ),
          );
          if (picked != null) onPicked(picked);
        },
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
          decoration: BoxDecoration(
            color: isDark ? AppTheme.darkBorder.withValues(alpha: 0.2) : AppTheme.lightBorder.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: (isRequired && date == null)
                ? AppTheme.dangerColor
                : (isDark ? AppTheme.darkBorder.withValues(alpha: 0.4) : AppTheme.lightBorder),
            ),
          ),
          child: Row(children: [
            Icon(Icons.calendar_today_outlined, size: 16,
              color: AppTheme.primaryColor.withValues(alpha: 0.7)),
            const SizedBox(width: 10),
            Text(
              date != null
                ? '${date!.year}-${date!.month.toString().padLeft(2,'0')}-${date!.day.toString().padLeft(2,'0')}'
                : 'Sélectionner une date',
              style: TextStyle(fontSize: 14,
                color: date != null
                  ? (isDark ? AppTheme.darkForeground : AppTheme.lightForeground)
                  : (isDark ? AppTheme.darkForeground.withValues(alpha: 0.3) : Colors.grey[400])),
            ),
          ]),
        ),
      ),
    ],
  );
}

// Sélecteur d'ordonnance
class _OrdonnanceSelector extends StatelessWidget {
  final String current;
  final ValueChanged<String> onChanged;
  final bool isDark;
  const _OrdonnanceSelector({required this.current, required this.onChanged, required this.isDark});

  @override
  Widget build(BuildContext context) {
    final items = [
      (OrdonnanceType.non,   Icons.no_encryption_outlined, AppTheme.successColor),
      (OrdonnanceType.oui,   Icons.assignment_outlined,    AppTheme.warningColor),
      (OrdonnanceType.liste1,Icons.warning_amber_rounded,  AppTheme.dangerColor),
      (OrdonnanceType.stup,  Icons.lock_outlined,          const Color(0xFF8B5CF6)),
    ];
    return Wrap(spacing: 8, runSpacing: 8, children: items.map((item) {
      final selected = current == item.$1.value;
      return GestureDetector(
        onTap: () => onChanged(item.$1.value),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
          decoration: BoxDecoration(
            color: selected ? item.$3.withValues(alpha: 0.14) : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: selected ? item.$3 : (isDark ? AppTheme.darkBorder : AppTheme.lightBorder),
              width: selected ? 1.5 : 1),
          ),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            Icon(item.$2, size: 15,
              color: selected ? item.$3 : Colors.grey[400]),
            const SizedBox(width: 6),
            Text(item.$1.label, style: TextStyle(fontSize: 12,
              fontWeight: selected ? FontWeight.w700 : FontWeight.w400,
              color: selected ? item.$3 : Colors.grey[500])),
          ]),
        ),
      );
    }).toList());
  }
}

// Stepper +/-
class _Stepper extends StatelessWidget {
  final TextEditingController ctrl;
  final Color color;
  const _Stepper({required this.ctrl, required this.color});

  @override
  Widget build(BuildContext context) => Row(mainAxisSize: MainAxisSize.min, children: [
    GestureDetector(
      onTap: () {
        final v = int.tryParse(ctrl.text) ?? 1;
        if (v > 1) ctrl.text = (v - 1).toString();
      },
      child: Container(width: 30, height: 30,
        decoration: BoxDecoration(color: color.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(8)),
        child: Icon(Icons.remove_rounded, size: 16, color: color)),
    ),
    SizedBox(width: 50, child: TextFormField(
      controller: ctrl,
      textAlign: TextAlign.center,
      keyboardType: TextInputType.number,
      inputFormatters: [FilteringTextInputFormatter.digitsOnly],
      style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: color),
      decoration: InputDecoration(
        border: InputBorder.none, filled: true,
        fillColor: color.withValues(alpha: 0.07),
        contentPadding: const EdgeInsets.symmetric(vertical: 7),
        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: color.withValues(alpha: 0.2))),
        focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: color)),
      ),
    )),
    GestureDetector(
      onTap: () {
        final v = int.tryParse(ctrl.text) ?? 0;
        ctrl.text = (v + 1).toString();
      },
      child: Container(width: 30, height: 30,
        decoration: BoxDecoration(color: color.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(8)),
        child: Icon(Icons.add_rounded, size: 16, color: color)),
    ),
  ]);
}

// Métrique résumé
class _Metric extends StatelessWidget {
  final String emoji, value, label;
  final Color color;
  const _Metric(this.emoji, this.value, this.label, this.color);

  @override
  Widget build(BuildContext context) => Column(children: [
    Text(emoji, style: const TextStyle(fontSize: 20)),
    const SizedBox(height: 2),
    Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: color)),
    Text(label, style: TextStyle(fontSize: 10, color: color.withValues(alpha: 0.7))),
  ]);
}

// Mini carte financière
class _MiniCard extends StatelessWidget {
  final String label, value;
  final Color color;
  final bool isDark, highlight;
  const _MiniCard(this.label, this.value, this.color, this.isDark, {this.highlight = false});

  @override
  Widget build(BuildContext context) => Container(
    margin: const EdgeInsets.only(right: 8, bottom: 0),
    padding: const EdgeInsets.all(10),
    decoration: BoxDecoration(
      color: highlight
        ? color.withValues(alpha: 0.1)
        : (isDark ? AppTheme.darkBorder.withValues(alpha: 0.2) : AppTheme.lightBorder.withValues(alpha: 0.3)),
      borderRadius: BorderRadius.circular(10),
      border: highlight ? Border.all(color: color.withValues(alpha: 0.3)) : null,
    ),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(label, style: TextStyle(fontSize: 10,
        color: isDark ? AppTheme.darkForeground.withValues(alpha: 0.5) : Colors.grey[500])),
      const SizedBox(height: 2),
      Text(value, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: color)),
    ]),
  );
}

// Décoration commune pour TextFormField
InputDecoration _dec(String hint, IconData icon, bool isDark,
    {String? suffix, Widget? suffix2}) =>
  InputDecoration(
    hintText: hint,
    hintStyle: TextStyle(fontSize: 13,
      color: isDark ? AppTheme.darkForeground.withValues(alpha: 0.28) : Colors.grey[400]),
    prefixIcon: Icon(icon, size: 17, color: AppTheme.primaryColor.withValues(alpha: 0.65)),
    suffixText: suffix,
    suffixIcon: suffix2,
    suffixStyle: const TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.w600),
    filled: true,
    fillColor: isDark ? AppTheme.darkBorder.withValues(alpha: 0.18) : AppTheme.lightBorder.withValues(alpha: 0.28),
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide.none),
    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
      borderSide: BorderSide(
        color: isDark ? AppTheme.darkBorder.withValues(alpha: 0.38) : AppTheme.lightBorder, width: 1)),
    focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
      borderSide: const BorderSide(color: AppTheme.primaryColor, width: 1.5)),
    errorBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
      borderSide: const BorderSide(color: AppTheme.dangerColor)),
    focusedErrorBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
      borderSide: const BorderSide(color: AppTheme.dangerColor, width: 1.5)),
    contentPadding: const EdgeInsets.symmetric(horizontal: 13, vertical: 11),
  );
