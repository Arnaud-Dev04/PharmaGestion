import { useState, useEffect } from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { LanguageProvider } from './context/LanguageContext';
import { ErrorProvider } from './context/ErrorContext';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { AdminRoute } from './components/common/AdminRoute';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { LoginPage } from './pages/Auth/LoginPage';
import { DashboardPage } from './pages/Dashboard/DashboardPage';
import { StockPage } from './pages/Stock/StockPage';
import { SuppliersPage } from './pages/Suppliers/SuppliersPage';
import { POSPage } from './pages/POS/POSPage';
import { SalesHistoryPage } from './pages/SalesHistory/SalesHistoryPage';
import { ReportsPage } from './pages/Reports/ReportsPage';
import { SettingsPage } from './pages/Settings/SettingsPage';
import { UserManagementPage } from './pages/Users/UserManagementPage';
import { UserStatsPage } from './pages/Users/UserStatsPage';
import SuperAdminPage from './pages/Admin/SuperAdminPage';
import licenseService from './services/licenseService';
import { LicenseAlert } from './components/common/LicenseAlert';
import GlobalErrorModal from './components/common/GlobalErrorModal';
import AxiosInterceptor from './components/common/AxiosInterceptor';

// Create QueryClient for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  const [licenseStatus, setLicenseStatus] = useState(null);

  useEffect(() => {
    const checkLicense = async () => {
      try {
        const status = await licenseService.checkStatus();
        setLicenseStatus(status);
      } catch (error) {
        console.error("Failed to check license:", error);
      }
    };
    checkLicense();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <LanguageProvider>
          <ErrorProvider>
            <AuthProvider>
              <AxiosInterceptor />
              <GlobalErrorModal />
            {licenseStatus && <LicenseAlert {...licenseStatus} />}
            <HashRouter>
              <Routes>
                {/* Public routes */}
                <Route path="/login" element={<LoginPage />} />

                {/* Protected routes with Dashboard Layout */}
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout />
                    </ProtectedRoute>
                  }
                >
                  <Route index element={<Navigate to="/dashboard" replace />} />

                  {/* Admin Only Routes */}
                  <Route
                    path="dashboard"
                    element={
                      <AdminRoute>
                        <DashboardPage />
                      </AdminRoute>
                    }
                  />
                  <Route
                    path="suppliers"
                    element={
                      <AdminRoute>
                        <SuppliersPage />
                      </AdminRoute>
                    }
                  />
                  <Route
                    path="reports"
                    element={
                      <AdminRoute>
                        <ReportsPage />
                      </AdminRoute>
                    }
                  />
                  <Route
                    path="settings"
                    element={
                      <AdminRoute>
                        <SettingsPage />
                      </AdminRoute>
                    }
                  />
                  <Route
                    path="users"
                    element={
                      <AdminRoute>
                        <UserManagementPage />
                      </AdminRoute>
                    }
                  />
                  <Route
                    path="users/:id/stats"
                    element={
                      <AdminRoute>
                        <UserStatsPage />
                      </AdminRoute>
                    }
                  />

                  {/* Super Admin Route */}
                  <Route path="super-admin" element={<SuperAdminPage />} />

                  {/* Common Routes (Pharmacist & Admin) */}
                  <Route path="stock" element={<StockPage />} />
                  <Route path="pos" element={<POSPage />} />
                  <Route path="sales-history" element={<SalesHistoryPage />} />
                </Route>

                {/* Catch all - redirect to dashboard */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </HashRouter>
            </AuthProvider>
          </ErrorProvider>
        </LanguageProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
