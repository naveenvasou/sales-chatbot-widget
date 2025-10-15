import { useState } from 'react';

const TextInput = ({ placeholder, optional, skipLabel, onSubmit, disabled }) => {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(text || 'No special requests');
  };

  const handleSkip = () => {
    onSubmit('No special requests');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={placeholder}
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 resize-none"
        rows={3}
        disabled={disabled}
      />
      <div className="flex gap-2">
        {optional && (
          <button
            type="button"
            onClick={handleSkip}
            disabled={disabled}
            className="flex-1 px-4 py-2 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
          >
            {skipLabel || 'Skip'}
          </button>
        )}
        <button
          type="submit"
          disabled={disabled}
          className="flex-1 bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition"
        >
          Submit
        </button>
      </div>
    </form>
  );
};

export default TextInput;