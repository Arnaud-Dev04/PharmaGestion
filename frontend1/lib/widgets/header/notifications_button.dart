import 'package:flutter/material.dart';
import 'package:frontend1/core/theme.dart';
import 'package:frontend1/providers/language_provider.dart';
import 'package:provider/provider.dart';

/// Modèle pour une notification
class NotificationModel {
  final int id;
  final String title;
  final String message;
  final String time;

  const NotificationModel({
    required this.id,
    required this.title,
    required this.message,
    required this.time,
  });
}

/// Bouton avec dropdown pour afficher les notifications
class NotificationsButton extends StatefulWidget {
  const NotificationsButton({super.key});

  @override
  State<NotificationsButton> createState() => _NotificationsButtonState();
}

class _NotificationsButtonState extends State<NotificationsButton> {
  // Mock notifications (identiques au React)
  static const List<NotificationModel> _notifications = [
    NotificationModel(
      id: 1,
      title: 'Stock faible',
      message: 'Paracétamol 500mg (10 boîtes restantes)',
      time: '2 min',
    ),
    NotificationModel(
      id: 2,
      title: 'Nouvelle vente',
      message: 'Vente #1234 validée',
      time: '15 min',
    ),
    NotificationModel(
      id: 3,
      title: 'Rapport généré',
      message: 'Rapport journalier disponible',
      time: '1h',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final languageProvider = Provider.of<LanguageProvider>(context);

    return PopupMenuButton(
      offset: const Offset(0, 8),
      itemBuilder: (context) => [
        // Header
        PopupMenuItem(
          enabled: false,
          padding: EdgeInsets.zero,
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: isDark
                  ? AppTheme.darkSidebarHover
                  : AppTheme.lightSidebarHover,
              border: Border(
                bottom: BorderSide(
                  color: isDark ? AppTheme.darkBorder : AppTheme.lightBorder,
                ),
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  languageProvider.translate('notifications'),
                  style: Theme.of(
                    context,
                  ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600),
                ),
                Text(
                  languageProvider.translate('markAllAsRead'),
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: AppTheme.primaryColor,
                    decoration: TextDecoration.underline,
                  ),
                ),
              ],
            ),
          ),
        ),

        // Notifications list
        ..._notifications.map(
          (notif) => PopupMenuItem(
            padding: EdgeInsets.zero,
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                border: Border(
                  bottom: BorderSide(
                    color: isDark ? AppTheme.darkBorder : AppTheme.lightBorder,
                    width: 0.5,
                  ),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          notif.title,
                          style: Theme.of(context).textTheme.bodyMedium
                              ?.copyWith(fontWeight: FontWeight.w500),
                        ),
                      ),
                      Text(
                        notif.time,
                        style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: isDark
                              ? AppTheme.darkSidebarText
                              : AppTheme.lightSidebarText,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    notif.message,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: isDark
                          ? AppTheme.darkSidebarText
                          : AppTheme.lightSidebarText,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
      child: Stack(
        children: [
          IconButton(
            icon: Icon(
              Icons.notifications_outlined,
              size: 20,
              color: isDark
                  ? AppTheme.darkSidebarText
                  : AppTheme.lightSidebarText,
            ),
            onPressed: null, // Le popup gère le clic
            tooltip: languageProvider.translate('notifications'),
          ),
          // Badge rouge
          Positioned(
            right: 8,
            top: 8,
            child: Container(
              width: 8,
              height: 8,
              decoration: const BoxDecoration(
                color: AppTheme.dangerColor,
                shape: BoxShape.circle,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
