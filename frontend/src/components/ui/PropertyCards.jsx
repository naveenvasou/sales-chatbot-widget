import { useState, useEffect } from 'react';
import PropertyCard from './PropertyCard';
import axios from 'axios';

const PropertyCards = ({ propertyType, filtered, preferences, onAction, onShowMore }) => {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProperties();
  }, [propertyType, preferences]);

  const fetchProperties = async () => {
    setLoading(true);
    try {
      let response;
      if (filtered && preferences) {
        response = await axios.post('/api/v2/properties/filter', {
          property_type: propertyType,
          ...JSON.parse(preferences)
        });
      } else {
        response = await axios.get(`/api/v2/properties/${propertyType}?limit=6`);
      }
      setProperties(response.data.properties);
    } catch (error) {
      console.error('Error fetching properties:', error);
      setProperties([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-4 text-gray-500">Loading properties...</div>;
  }

  if (properties.length === 0) {
    return <div className="text-center py-4 text-gray-500">No properties found matching your criteria.</div>;
  }

  return (
    <div className="space-y-3">
      {/* Property Grid */}
      <div className="grid grid-cols-1 gap-3 max-h-96 overflow-y-auto">
        {properties.map((property) => (
          <PropertyCard key={property.id} property={property} onAction={onAction} />
        ))}
      </div>
      
      {/* Show More Button */}
      {properties.length >= 6 && !filtered && onShowMore && (
        <button
          onClick={onShowMore}
          className="w-full py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
        >
          Show More Properties
        </button>
      )}
    </div>
  );
};

export default PropertyCards;