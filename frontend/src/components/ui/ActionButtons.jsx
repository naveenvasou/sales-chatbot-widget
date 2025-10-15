const ActionButtons = ({ options, onSelect, disabled }) => {
  return (
    <div className="space-y-2">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onSelect(option.value)}
          disabled={disabled}
          className="w-full px-4 py-3 bg-purple-100 text-purple-800 rounded-lg hover:bg-purple-200 transition font-medium disabled:opacity-50"
        >
          {option.label}
        </button>
      ))}
    </div>
  );
};

export default ActionButtons;