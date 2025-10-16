import json
from pathlib import Path
from typing import List, Dict, Optional

current_file_path = Path(__file__).resolve()
json_file_path = current_file_path.parent.parent.parent / 'data' / 'properties.json'

class PropertyService:
    def __init__(self):
        self.properties_file = Path(json_file_path)
        self.properties = self._load_properties()
    
    def _load_properties(self) -> List[Dict]:
        """Load properties from JSON file"""
        try:
            with open(self.properties_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Properties file not found: {self.properties_file}")
            return []
    
    def get_properties_by_type(self, property_type: str, limit: int = 6) -> List[Dict]:
        """Get properties filtered by type"""
        filtered = [p for p in self.properties if p.get("type") == property_type]
        return filtered[:limit]
    
    def filter_properties(self, property_type: str, budget: str = None, 
                         location: List[str] = None) -> List[Dict]:
        """Filter properties by multiple criteria"""
        filtered = [p for p in self.properties if p.get("type") == property_type]
        
        if location:
            filtered = [p for p in filtered if any(loc in p.get("location", "") for loc in location)]
        
        # Budget filtering can be added here based on your price format
        
        return filtered
    
    def get_property_by_id(self, property_id: str) -> Optional[Dict]:
        """Get single property by ID"""
        return next((p for p in self.properties if p.get("id") == property_id), None)

# Singleton
property_service = PropertyService()