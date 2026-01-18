export const StatsCard = ({ icon: Icon, label, value, iconBgColor = 'bg-primary', iconColor = 'text-white', onClick }) => {
  return (
    <div 
      className={`card p-5 hover:shadow-lg transition-shadow duration-200 ${onClick ? 'cursor-pointer hover:scale-[1.02] transition-transform' : 'cursor-default'}`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{label}</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
        </div>
        <div className={`${iconBgColor} ${iconColor} p-3 rounded-xl`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
};
