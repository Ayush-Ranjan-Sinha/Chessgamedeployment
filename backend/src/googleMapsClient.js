const axios = require('axios');
const NodeCache = require('node-cache');

// Cache for API responses (1 hour TTL)
const cache = new NodeCache({ stdTTL: 3600 });

class GoogleMapsClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseURL = 'https://maps.googleapis.com/maps/api';
  }

  async searchPlaces(query) {
    const cacheKey = `search_${query}`;
    const cached = cache.get(cacheKey);
    
    if (cached) {
      return cached;
    }

    try {
      const response = await axios.get(`${this.baseURL}/place/textsearch/json`, {
        params: {
          query,
          key: this.apiKey,
          type: 'locality'
        }
      });

      const suggestions = response.data.results.slice(0, 5).map(place => ({
        place_id: place.place_id,
        name: place.name,
        formatted_address: place.formatted_address,
        geometry: place.geometry,
        types: place.types
      }));

      cache.set(cacheKey, suggestions);
      return suggestions;
    } catch (error) {
      console.error('Error searching places:', error.message);
      throw new Error('Failed to search places');
    }
  }

  async getPlaceDetails(placeId) {
    const cacheKey = `place_${placeId}`;
    const cached = cache.get(cacheKey);
    
    if (cached) {
      return cached;
    }

    try {
      const response = await axios.get(`${this.baseURL}/place/details/json`, {
        params: {
          place_id: placeId,
          key: this.apiKey,
          fields: 'geometry,name,formatted_address,types'
        }
      });

      const place = response.data.result;
      const details = {
        place_id: placeId,
        name: place.name,
        formatted_address: place.formatted_address,
        latitude: place.geometry.location.lat,
        longitude: place.geometry.location.lng,
        types: place.types
      };

      cache.set(cacheKey, details);
      return details;
    } catch (error) {
      console.error('Error getting place details:', error.message);
      throw new Error('Failed to get place details');
    }
  }

  async getDistanceMatrix(origins, destinations) {
    const cacheKey = `distance_${JSON.stringify(origins)}_${JSON.stringify(destinations)}`;
    const cached = cache.get(cacheKey);
    
    if (cached) {
      return cached;
    }

    try {
      const response = await axios.get(`${this.baseURL}/distancematrix/json`, {
        params: {
          origins: origins.join('|'),
          destinations: destinations.join('|'),
          key: this.apiKey,
          units: 'metric'
        }
      });

      const result = response.data;
      cache.set(cacheKey, result);
      return result;
    } catch (error) {
      console.error('Error getting distance matrix:', error.message);
      throw new Error('Failed to get distance matrix');
    }
  }

  calculateHaversineDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }
}

const googleMapsClient = new GoogleMapsClient(process.env.GOOGLE_MAPS_API_KEY);

module.exports = { googleMapsClient };
