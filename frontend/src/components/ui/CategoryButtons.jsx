const CategoryButtons = ({ categories, onSelect, disabled }) => {
  return (
    <div className="space-y-2">
      {categories.map((cat) => (
        <button
          key={cat.id}
          onClick={() => onSelect(cat)}
          disabled={disabled}
          className="w-full p-4 text-left bg-white border-2 border-purple-200 rounded-xl hover:border-purple-500 hover:bg-purple-50 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3"
        >
          <span className="text-2xl">{cat.emoji}</span>
          <span className="font-medium text-gray-800">{cat.label}</span>
        </button>
      ))}
    </div>
  );
};

export default CategoryButtons;