import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Users, UserPlus, Eye, Lock, Trash2, Power, Search, Pencil } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import userService from '../../services/userService';
import { UserStatusBadge } from '../../components/users/UserStatusBadge';
import { UserFormModal } from '../../components/users/UserFormModal';
import { useLanguage } from '../../context/LanguageContext';

export const UserManagementPage = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // all, active, inactive
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  // Fetch users
  const { data: users, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: () => userService.getAll(),
  });

  // Create user mutation
  const createMutation = useMutation({
    mutationFn: (data) => userService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
      setIsModalOpen(false);
    },
    onError: (error) => {
        alert("Erreur lors de la création : " + (error.response?.data?.detail || error.message));
    }
  });

  // Update user mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => userService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
      setIsModalOpen(false);
      setSelectedUser(null);
    },
    onError: (error) => {
        alert("Erreur lors de la mise à jour : " + (error.response?.data?.detail || error.message));
    }
  });

  // Toggle user status mutation
  const toggleStatusMutation = useMutation({
    mutationFn: (userId) => userService.toggleStatus(userId),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
    },
  });

  // Delete user mutation
  const deleteUserMutation = useMutation({
    mutationFn: (userId) => userService.delete(userId),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
    },
  });

  // Filter users
  const filteredUsers = users?.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = 
      statusFilter === 'all' ? true :
      statusFilter === 'active' ? user.is_active :
      !user.is_active;
    return matchesSearch && matchesStatus;
  }) || [];

  const handleCreate = () => {
    setSelectedUser(null);
    setIsModalOpen(true);
  };

  const handleEdit = (user) => {
    setSelectedUser(user);
    setIsModalOpen(true);
  };

  const handleSubmit = async (data) => {
    try {
        if (selectedUser) {
            await updateMutation.mutateAsync({ id: selectedUser.id, data });
        } else {
            await createMutation.mutateAsync(data);
        }
    } catch (e) {
        // Handled by onError
    }
  };

  const handleToggleStatus = async (userId, username) => {
    if (window.confirm(`Voulez-vous vraiment changer le statut de ${username} ?`)) {
      try {
        await toggleStatusMutation.mutateAsync(userId);
      } catch (error) {
        alert('Erreur lors du changement de statut: ' + error.message);
      }
    }
  };

  const handleDelete = async (userId, username) => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer ${username} ? Cette action peut être irréversible.`)) {
      try {
        await deleteUserMutation.mutateAsync(userId);
      } catch (error) {
        alert('Erreur lors de la suppression: ' + error.message);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">{t('loading')}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-600 dark:text-red-400 py-8">
        Erreur de chargement des utilisateurs
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Gestion des Utilisateurs</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {filteredUsers.length} utilisateur(s)
          </p>
        </div>
        <button
          onClick={handleCreate}
          className="btn btn-primary flex items-center gap-2"
        >
          <UserPlus className="w-5 h-5" />
          Nouvel Utilisateur
        </button>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher par nom d'utilisateur..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input pl-10 w-full"
            />
          </div>

          {/* Status Filter */}
          <div className="flex gap-2">
            <button
              onClick={() => setStatusFilter('all')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === 'all'
                  ? 'bg-primary text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Tous
            </button>
            <button
              onClick={() => setStatusFilter('active')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === 'active'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Actifs
            </button>
            <button
              onClick={() => setStatusFilter('inactive')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === 'inactive'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Inactifs
            </button>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                  Utilisateur
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                  Rôle
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                  Statut
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                  Créé le
                </th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredUsers.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 text-primary font-semibold">
                        {user.username.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{user.username}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">ID: {user.id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      user.role === 'admin'
                        ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-400'
                        : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400'
                    }`}>
                      {user.role === 'admin' ? 'Administrateur' : 'Pharmacien'}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <UserStatusBadge isActive={user.is_active} />
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                    {new Date(user.created_at).toLocaleDateString('fr-FR')}
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center justify-end gap-2">
                      {/* Edit */}
                      <button
                        onClick={() => handleEdit(user)}
                        className="p-2 hover:bg-primary-50 rounded-lg text-primary transition-colors"
                        title="Modifier"
                      >
                         <Pencil className="w-4 h-4" />
                      </button>

                      {/* View Stats */}
                      <button
                        onClick={() => navigate(`/users/${user.id}/stats`)}
                        className="p-2 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                        title="Voir les statistiques"
                      >
                        <Eye className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                      </button>

                      {/* Toggle Status */}
                      <button
                        onClick={() => handleToggleStatus(user.id, user.username)}
                        className="p-2 hover:bg-orange-50 dark:hover:bg-orange-900/20 rounded-lg transition-colors"
                        title={user.is_active ? 'Désactiver' : 'Activer'}
                        disabled={toggleStatusMutation.isLoading}
                      >
                        <Power className={`w-4 h-4 ${
                          user.is_active 
                            ? 'text-orange-600 dark:text-orange-400' 
                            : 'text-green-600 dark:text-green-400'
                        }`} />
                      </button>

                      {/* Delete */}
                      {user.role !== 'admin' && (
                        <button
                          onClick={() => handleDelete(user.id, user.username)}
                          className="p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                          title="Supprimer"
                          disabled={deleteUserMutation.isLoading}
                        >
                          <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredUsers.length === 0 && (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500 dark:text-gray-400">Aucun utilisateur trouvé</p>
            </div>
          )}
        </div>
      </div>

      <UserFormModal
        isOpen={isModalOpen}
        onClose={() => {
            setIsModalOpen(false);
            setSelectedUser(null);
        }}
        onSubmit={handleSubmit}
        user={selectedUser}
        isSubmitting={createMutation.isLoading || updateMutation.isLoading}
      />
    </div>
  );
};
