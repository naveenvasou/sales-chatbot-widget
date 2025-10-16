import React, { useState, useCallback } from 'react';
import { LogIn, Phone } from 'lucide-react';


const NumberConfirmation = ({ fields, onSubmit, disabled }) => {
  // We expect a single field definition from the 'fields' array
  const numberField = fields?.[0];

  if (!numberField || !numberField.options?.[0]) {
    // Basic guard clause for malformed data
    return <div className="text-red-500 p-4">Error: Invalid configuration for Number Confirmation component.</div>;
  }

  const confirmationOption = numberField.options[0];

  // Initialize state with the pre-filled number (the 'label' property)
  const [number, setNumber] = useState(numberField.label || '');

  const handleSubmit = (e) => {
    e.preventDefault();

    if (disabled || !number.trim()) return;

    // Construct the data payload to send back.
    // This sends the confirmed number and the confirmation action value.
    /* const submissionData = {
      [numberField.name]: number.trim(),
      [numberField.name + '_action']: confirmationOption.value,
    }; */
    const submissionData = number.trim()

    onSubmit(submissionData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white">
      <div className="relative">
        <label htmlFor={numberField.name} className="block text-sm font-medium text-gray-500 mb-1">
          Please confirm your phone number:
        </label>
        <input
          id={numberField.name}
          type="tel" // Use tel for better mobile keyboard experience
          value={number}
          onChange={(e) => setNumber(e.target.value)}
          placeholder="Enter your phone number"
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl text-lg font-mono focus:ring-2 focus:ring-purple-500 transition"
          disabled={disabled}
          required
        />
        <div className="absolute inset-y-0 left-0 flex items-center pl-3 pt-5 pointer-events-none">
            <LogIn className="w-5 h-5 text-gray-400" />
        </div>
      </div>

      <button
        type="submit"
        disabled={disabled || !number.trim()}
        className={`w-full py-3 rounded-xl font-bold transition duration-200
          ${disabled || !number.trim()
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-purple-600 text-white hover:bg-purple-700 shadow-md hover:shadow-lg'
          }`
        }
      >
        {confirmationOption.label || 'Confirm'}
      </button>
    </form>
  );
};

export default NumberConfirmation;