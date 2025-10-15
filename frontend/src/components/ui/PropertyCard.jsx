const PropertyCard = ({ property, onAction }) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden border border-gray-200 hover:shadow-lg transition">
      {/* Image */}
      <div className="h-40 bg-gradient-to-br from-purple-100 to-purple-200 flex items-center justify-center">
        {property.image_url ? (
          <img src={property.image_url} alt={property.name} className="w-full h-full object-cover" />
        ) : (
          <span className="text-5xl">🏡</span>
        )}
      </div>
      
      {/* Content */}
      <div className="p-4">
        <h3 className="font-semibold text-gray-800 mb-1">{property.name}</h3>
        <p className="text-sm text-gray-600 mb-2">📍 {property.location}</p>
        <p className="text-lg font-bold text-purple-600 mb-3">₹{property.price}</p>
        
        {/* Action Buttons */}
        <div className="flex gap-2">
          <button
            onClick={() => onAction('brochure', property.id)}
            className="flex-1 px-3 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition text-sm font-medium"
          >
            📋 Brochure
          </button>
          <button
            onClick={() => onAction('quote', property.id)}
            className="flex-1 px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm font-medium"
          >
            💰 Quote
          </button>
        </div>
      </div>
    </div>
  );
};

export default PropertyCard;