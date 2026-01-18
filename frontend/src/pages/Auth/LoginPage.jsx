import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Eye, EyeOff, User, Lock, Sun, Moon } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';

// Validation schema
const loginSchema = z.object({
  username: z.string().min(1, 'Le nom d\'utilisateur est requis'),
  password: z.string().min(1, 'Le mot de passe est requis'),
});

export const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { theme, toggleTheme, isDark } = useTheme();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data) => {
    try {
      setIsLoading(true);
      setError('');
      await login(data.username, data.password);
      navigate('/dashboard');
    } catch (err) {
      console.error('Login error:', err);
      setError(
        err.response?.data?.detail || 
        'Identifiants incorrects. Veuillez réessayer.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-background">
      {/* Left Panel - Brand */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent"></div>
        <div className="relative z-10 flex flex-col items-center justify-center w-full p-12 text-gray-900 dark:text-white">
          {/* Logo */}
          <div className="mb-8">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-primary to-success rounded-xl flex items-center justify-center">
                <svg 
                  className="w-8 h-8 text-white" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" 
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold">Pharmac+</h1>
                <p className="text-sm text-gray-600 dark:text-gray-300">Mode Administrateur</p>
              </div>
            </div>
          </div>

          {/* Welcome text */}
          <div className="text-center max-w-md mt-8">
            <h2 className="text-2xl font-semibold mb-4">
              Bienvenue sur votre plateforme de gestion
            </h2>
            <p className="text-gray-600 dark:text-gray-300">
              Gérez votre pharmacie efficacement avec un système moderne et intuitif.
              Suivez vos stocks, vos ventes et vos fournisseurs en temps réel.
            </p>
          </div>

          {/* Decorative elements */}
          <div className="absolute bottom-0 left-0 right-0 h-64 bg-gradient-to-t from-sidebar-bg to-transparent"></div>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-background">
        <div className="w-full max-w-md">
          {/* Theme toggle - mobile */}
          <div className="flex justify-between items-center mb-8 lg:hidden">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-primary to-success rounded-lg"></div>
              <span className="text-xl font-bold">Pharmac+</span>
            </div>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {isDark ? (
                <Sun className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              ) : (
                <Moon className="w-5 h-5 text-gray-600" />
              )}
            </button>
          </div>

          {/* Theme toggle - desktop */}
          <div className="hidden lg:flex justify-end mb-8">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {isDark ? (
                <Sun className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              ) : (
                <Moon className="w-5 h-5 text-gray-600" />
              )}
            </button>
          </div>

          {/* Login form */}
          <div>
            <h2 className="text-3xl font-bold mb-2">Connexion</h2>
            <p className="text-gray-500 dark:text-gray-400 mb-8">
              Entrez vos identifiants pour accéder à votre compte
            </p>

            {error && (
              <div className="mb-6 p-4 bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-lg">
                <p className="text-sm text-danger-700 dark:text-danger-300">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Username */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Nom d'utilisateur
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    {...register('username')}
                    type="text"
                    className="input pl-11"
                    placeholder="Entrez votre nom d'utilisateur"
                    autoComplete="username"
                  />
                </div>
                {errors.username && (
                  <p className="mt-1 text-sm text-danger">{errors.username.message}</p>
                )}
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Mot de passe
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    {...register('password')}
                    type={showPassword ? 'text' : 'password'}
                    className="input pl-11 pr-11"
                    placeholder="Entrez votre mot de passe"
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    {showPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
                {errors.password && (
                  <p className="mt-1 text-sm text-danger">{errors.password.message}</p>
                )}
              </div>

              {/* Remember me & Forgot password */}
              <div className="flex items-center justify-between">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="w-4 h-4 border-gray-300 rounded text-primary focus:ring-primary"
                  />
                  <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                    Se souvenir de moi
                  </span>
                </label>
              </div>

              {/* Submit button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full btn btn-primary h-12 text-base font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                    <span className="ml-2">Connexion...</span>
                  </div>
                ) : (
                  'Se connecter'
                )}
              </button>
            </form>

            {/* Footer text */}
            <p className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
              Version 1.0.0 • © 2025 Developped by ArnaudDev
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
