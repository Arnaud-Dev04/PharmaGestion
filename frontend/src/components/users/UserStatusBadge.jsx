export const UserStatusBadge = ({ isActive }) => {
  return (
    <span 
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
        isActive 
          ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
          : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400'
      }`}
    >
      <span className={`mr-1.5 h-2 w-2 rounded-full ${isActive ? 'bg-green-500' : 'bg-red-500'}`} />
      {isActive ? 'Actif' : 'Inactif'}
    </span>
  );
};
