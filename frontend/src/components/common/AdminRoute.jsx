import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const AdminRoute = ({ children }) => {
  const { user, isLoading } = useAuth();
  
  if (isLoading) {
    return <div className="p-4 text-center">Chargement...</div>;
  }
  
  if (!user) {
     return <Navigate to="/login" replace />;
  }

  const role = user.role?.toLowerCase();
  
  // Allow both 'admin' and 'super_admin'
  if (role !== 'admin' && role !== 'super_admin') {
    // Si pas admin ni super_admin, redirection vers POS
    return <Navigate to="/pos" replace />;
  }
  
  return children;
};
