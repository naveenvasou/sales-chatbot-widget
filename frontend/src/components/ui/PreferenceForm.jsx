import { useState } from 'react';

const PreferenceForm = ({ fields, onSubmit, disabled }) => {
  const [formData, setFormData] = useState({});

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const renderField = (field) => {
    switch (field.type) {
      case 'dropdown':
        return (
          <select
            value={formData[field.name] || ''}
            onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            required={field.required}
          >
            <option value="">Select...</option>
            {field.options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        );

      case 'multiselect_chips':
        const selected = formData[field.name] || [];
        return (
          <div className="flex flex-wrap gap-2">
            {field.options.map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => {
                  const newSelected = selected.includes(option)
                    ? selected.filter((s) => s !== option)
                    : [...selected, option];
                  setFormData({ ...formData, [field.name]: newSelected });
                }}
                className={`px-4 py-2 rounded-full border-2 transition ${
                  selected.includes(option)
                    ? 'bg-purple-600 text-white border-purple-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:border-purple-400'
                }`}
              >
                {option}
              </button>
            ))}
          </div>
        );

      case 'buttons':
        return (
          <div className="grid grid-cols-2 gap-2">
            {field.options.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setFormData({ ...formData, [field.name]: opt.value })}
                className={`p-3 rounded-lg border-2 transition ${
                  formData[field.name] === opt.value
                    ? 'bg-purple-600 text-white border-purple-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:border-purple-400'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {fields.map((field) => (
        <div key={field.name}>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {field.label}
          </label>
          {renderField(field)}
        </div>
      ))}
      <button
        type="submit"
        disabled={disabled}
        className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 transition disabled:opacity-50 mt-4"
      >
        {fields[0]?.submit_label || 'Continue'}
      </button>
    </form>
  );
};

export default PreferenceForm;