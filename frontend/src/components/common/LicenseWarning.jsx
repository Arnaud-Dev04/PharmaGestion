import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ShieldAlert, X } from 'lucide-react';
import adminService from '../../services/adminService';
import settingsService from '../../services/settingsService';

export const LicenseWarning = () => {
    const [showWarning, setShowWarning] = useState(false);
    const [timeLeft, setTimeLeft] = useState(0);
    const [hasSeenWarning, setHasSeenWarning] = useState(false);

    // Fetch License Status
    const { data: license } = useQuery({
        queryKey: ['license'],
        queryFn: adminService.getLicense,
        staleTime: 1000 * 60 * 60, // Check once per hour or session
        retry: false
    });

    // Fetch Settings
    const { data: settings } = useQuery({
        queryKey: ['settings'],
        queryFn: settingsService.getSettings,
        staleTime: 1000 * 60 * 60,
        retry: false
    });

    useEffect(() => {
        if (license && settings && !hasSeenWarning) {
            const warningDays = settings.license_warning_bdays ?? 60;
            const daysRemaining = license.days_remaining;

            // Trigger if within threshold AND license is valid (if expired, backend blocks anyway, or we show a different screen)
            // Assuming we only warn if it's NOT yet expired but close.
            if (daysRemaining <= warningDays && daysRemaining > 0) {
                setShowWarning(true);
                setTimeLeft(settings.license_warning_duration ?? 30);
                setHasSeenWarning(true); // Show only once per session reload
            }
        }
    }, [license, settings, hasSeenWarning]);

    useEffect(() => {
        if (showWarning && timeLeft > 0) {
            const timer = setInterval(() => {
                setTimeLeft((prev) => prev - 1);
            }, 1000);
            return () => clearInterval(timer);
        } else if (timeLeft === 0 && showWarning) {
            // Auto close after time end? Or allow closing?
            // "Notification de 30 sec" -> User implies it appears for 30s.
            // Behaving as auto-close is less annoying than blocking for 30s then manual close.
            // But blocking ensures they see it. Let's Auto-close or show 'Close' button.
            // Let's AUTO-CLOSE to respect "Notification de 30 sec".
            const timer = setTimeout(() => {
                setShowWarning(false);
            }, 1000);
             return () => clearTimeout(timer);
        }
    }, [showWarning, timeLeft]);

    if (!showWarning) return null;

    return (
        <div className="fixed inset-0 bg-black/80 z-[9999] flex items-center justify-center p-4 backdrop-blur-sm">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-lg w-full overflow-hidden border-2 border-yellow-500 animate-in fade-in zoom-in duration-300">
                <div className="bg-yellow-500 p-4 flex items-center gap-3">
                    <ShieldAlert className="w-8 h-8 text-white animate-pulse" />
                    <h2 className="text-xl font-bold text-white">Attention : Besoin de mise à jour Logiciel</h2>
                </div>
                
                <div className="p-8 text-center space-y-6">
                    <div className="space-y-2">
                        <p className="text-lg font-medium text-gray-900 dark:text-white">
                            {settings?.license_warning_message || "Ce logiciel nécessite une mise à jour importante."}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                             Expiration dans : <span className="font-bold text-red-500">{license?.days_remaining} jours</span>
                        </p>
                    </div>

                    <div className="flex justify-center">
                        <div className="w-20 h-20 rounded-full border-4 border-yellow-500 flex items-center justify-center mb-2">
                            <span className="text-2xl font-bold">{timeLeft}s</span>
                        </div>
                    </div>
                    
                    <p className="text-xs text-gray-400">Cette fenêtre se fermera automatiquement.</p>
                </div>
            </div>
        </div>
    );
};
