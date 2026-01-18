import 'package:flutter/material.dart';
import 'package:frontend1/core/constants.dart';
import 'package:frontend1/core/theme.dart';
import 'package:frontend1/models/user.dart';
import 'package:frontend1/providers/auth_provider.dart';
import 'package:frontend1/providers/language_provider.dart';
import 'package:frontend1/widgets/header/notifications_button.dart';
import 'package:frontend1/widgets/header/theme_toggle_button.dart';
import 'package:frontend1/widgets/header/language_selector_button.dart';
import 'package:frontend1/widgets/header/user_avatar_widget.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';

/// Header de l'application avec date, actions et infos utilisateur
class AppHeader extends StatelessWidget {
  const AppHeader({super.key});

  /// Formate la date actuelle selon la langue
  String _formatDate(BuildContext context) {
    final languageProvider = Provider.of<LanguageProvider>(context);
    final now = DateTime.now();

    if (languageProvider.languageCode == 'fr') {
      // Format français : "lundi 27 décembre 2025"
      final dayName = languageProvider.translate(_getDayKey(now.weekday));
      final monthName = languageProvider.translate(_getMonthKey(now.month));
      return '$dayName ${now.day} $monthName ${now.year}';
    } else {
      // Format anglais : "Monday, December 27, 2025"
      return DateFormat('EEEE, MMMM d, yyyy', 'en_US').format(now);
    }
  }

  String _getDayKey(int weekday) {
    const days = [
      'monday',
      'tuesday',
      'wednesday',
      'thursday',
      'friday',
      'saturday',
      'sunday',
    ];
    return days[weekday - 1];
  }

  String _getMonthKey(int month) {
    const months = [
      'january',
      'february',
      'march',
      'april',
      'may',
      'june',
      'july',
      'august',
      'september',
      'october',
      'november',
      'december',
    ];
    return months[month - 1];
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final languageProvider = Provider.of<LanguageProvider>(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final User? user = authProvider.user;
    final isAdmin = user?.isAdmin ?? false;

    return Container(
      height: 64,
      padding: const EdgeInsets.symmetric(horizontal: 24),
      decoration: BoxDecoration(
        color: isDark ? AppTheme.darkCard : AppTheme.lightCard,
        border: Border(
          bottom: BorderSide(
            color: isDark ? AppTheme.darkBorder : AppTheme.lightBorder,
          ),
        ),
      ),
      child: Row(
        children: [
          // Section gauche : Date + Rôle
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Date
                Text(
                  _formatDate(context),
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: isDark
                        ? AppTheme.darkSidebarText
                        : AppTheme.lightSidebarText,
                    textBaseline: TextBaseline.alphabetic,
                  ),
                ),
                const SizedBox(height: 2),

                // Rôle
                Text(
                  languageProvider.translate(
                    isAdmin ? 'adminMode' : 'pharmacistMode',
                  ),
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: AppTheme.primaryColor,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),

          // Section droite : Actions
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Notifications
              const NotificationsButton(),
              SizedBox(width: AppConstants.spacingMd),

              // Toggle thème
              const ThemeToggleButton(),
              SizedBox(width: AppConstants.spacingMd),

              // Sélecteur langue
              const LanguageSelectorButton(),
              SizedBox(width: AppConstants.spacingMd),

              // Avatar utilisateur
              const UserAvatarWidget(),
            ],
          ),
        ],
      ),
    );
  }
}
