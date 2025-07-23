const express = require('express');
const { db } = require('./database');
const { googleMapsClient } = require('./googleMapsClient');
const { TSPSolver } = require('./tspSolver');

const router = express.Router();

// Search for cities using Google Places API
router.get('/search-cities', async (req, res) => {
  try {
    const { query } = req.query;
    if (!query) {
      return res.status(400).json({ error: 'Query parameter is required' });
    }

    const suggestions = await googleMapsClient.searchPlaces(query);
    res.json(suggestions);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Add a new city
router.post('/cities', async (req, res) => {
  try {
    const { place_id, name, formatted_address } = req.body;
    
    if (!place_id || !name) {
      return res.status(400).json({ error: 'place_id and name are required' });
    }

    // Get place details from Google Maps
    const placeDetails = await googleMapsClient.getPlaceDetails(place_id);
    
    // Insert city into database
    db.run(
      'INSERT INTO cities (name, latitude, longitude, country) VALUES (?, ?, ?, ?)',
      [placeDetails.name, placeDetails.latitude, placeDetails.longitude, placeDetails.formatted_address],
      function(err) {
        if (err) {
          res.status(500).json({ error: err.message });
        } else {
          const newCity = {
            id: this.lastID,
            name: placeDetails.name,
            latitude: placeDetails.latitude,
            longitude: placeDetails.longitude,
            country: placeDetails.formatted_address,
            place_id: place_id
          };
          res.status(201).json(newCity);
        }
      }
    );
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get all cities
router.get('/cities', (req, res) => {
  try {
    db.all('SELECT * FROM cities ORDER BY created_at DESC', (err, cities) => {
      if (err) {
        res.status(500).json({ error: err.message });
      } else {
        res.json(cities || []);
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Delete a city
router.delete('/cities/:id', (req, res) => {
  try {
    const { id } = req.params;
    db.run('DELETE FROM cities WHERE id = ?', [id], function(err) {
      if (err) {
        res.status(500).json({ error: err.message });
      } else if (this.changes === 0) {
        res.status(404).json({ error: 'City not found' });
      } else {
        res.json({ message: 'City deleted successfully' });
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Calculate distance matrix between cities
router.post('/distance-matrix', async (req, res) => {
  try {
    const { cityIds } = req.body;
    
    if (!cityIds || !Array.isArray(cityIds) || cityIds.length < 2) {
      return res.status(400).json({ error: 'At least 2 city IDs are required' });
    }

    // Get city coordinates
    const cities = [];
    for (const cityId of cityIds) {
      const city = db.prepare('SELECT * FROM cities WHERE id = ?').get(cityId);
      if (!city) {
        return res.status(404).json({ error: `City with ID ${cityId} not found` });
      }
      cities.push(city);
    }

    // Create distance matrix
    const distanceMatrix = [];
    
    for (let i = 0; i < cities.length; i++) {
      distanceMatrix[i] = [];
      for (let j = 0; j < cities.length; j++) {
        if (i === j) {
          distanceMatrix[i][j] = 0;
        } else {
          // Check cache first
          let cachedDistance = db.prepare(
            'SELECT distance FROM distance_cache WHERE from_city_id = ? AND to_city_id = ?'
          ).get(cities[i].id, cities[j].id);
          
          if (cachedDistance) {
            distanceMatrix[i][j] = cachedDistance.distance;
          } else {
            // Calculate using Haversine formula
            const distance = googleMapsClient.calculateHaversineDistance(
              cities[i].latitude,
              cities[i].longitude,
              cities[j].latitude,
              cities[j].longitude
            );
            
            distanceMatrix[i][j] = distance;
            
            // Cache the result
            try {
              db.prepare(
                'INSERT OR REPLACE INTO distance_cache (from_city_id, to_city_id, distance) VALUES (?, ?, ?)'
              ).run(cities[i].id, cities[j].id, distance);
            } catch (cacheError) {
              console.warn('Failed to cache distance:', cacheError.message);
            }
          }
        }
      }
    }

    res.json({
      cities: cities.map(city => ({
        id: city.id,
        name: city.name,
        latitude: city.latitude,
        longitude: city.longitude
      })),
      distanceMatrix
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Solve TSP using Held-Karp algorithm
router.post('/solve-tsp', async (req, res) => {
  try {
    const { cityIds, startCityId } = req.body;
    
    if (!cityIds || !Array.isArray(cityIds) || cityIds.length < 2) {
      return res.status(400).json({ error: 'At least 2 city IDs are required' });
    }

    // Get city coordinates
    const cities = [];
    for (const cityId of cityIds) {
      const city = db.prepare('SELECT * FROM cities WHERE id = ?').get(cityId);
      if (!city) {
        return res.status(404).json({ error: `City with ID ${cityId} not found` });
      }
      cities.push(city);
    }

    // Find start city index
    let startIndex = 0;
    if (startCityId) {
      startIndex = cities.findIndex(city => city.id === startCityId);
      if (startIndex === -1) {
        return res.status(400).json({ error: 'Start city not found in the provided cities' });
      }
    }

    // Create distance matrix
    const distanceMatrix = [];
    for (let i = 0; i < cities.length; i++) {
      distanceMatrix[i] = [];
      for (let j = 0; j < cities.length; j++) {
        if (i === j) {
          distanceMatrix[i][j] = 0;
        } else {
          // Check cache first
          let cachedDistance = db.prepare(
            'SELECT distance FROM distance_cache WHERE from_city_id = ? AND to_city_id = ?'
          ).get(cities[i].id, cities[j].id);
          
          if (cachedDistance) {
            distanceMatrix[i][j] = cachedDistance.distance;
          } else {
            // Calculate using Haversine formula
            const distance = googleMapsClient.calculateHaversineDistance(
              cities[i].latitude,
              cities[i].longitude,
              cities[j].latitude,
              cities[j].longitude
            );
            
            distanceMatrix[i][j] = distance;
            
            // Cache the result
            try {
              db.prepare(
                'INSERT OR REPLACE INTO distance_cache (from_city_id, to_city_id, distance) VALUES (?, ?, ?)'
              ).run(cities[i].id, cities[j].id, distance);
            } catch (cacheError) {
              console.warn('Failed to cache distance:', cacheError.message);
            }
          }
        }
      }
    }

    // Solve TSP
    const solver = new TSPSolver();
    const solution = solver.solve(distanceMatrix, startIndex);

    // Convert solution indices back to city objects
    const optimizedRoute = solution.route.map(index => cities[index]);

    // Store the result in database
    try {
      const stmt = db.prepare(`
        INSERT INTO routes (city_ids, total_distance, route_order, algorithm)
        VALUES (?, ?, ?, ?)
      `);
      
      stmt.run(
        JSON.stringify(cityIds),
        solution.distance,
        JSON.stringify(solution.route),
        cities.length <= 15 ? 'held-karp' : 'nearest-neighbor'
      );
    } catch (dbError) {
      console.warn('Failed to store route:', dbError.message);
    }

    res.json({
      route: optimizedRoute,
      totalDistance: solution.distance,
      algorithm: cities.length <= 15 ? 'held-karp' : 'nearest-neighbor',
      distanceMatrix
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get route history
router.get('/routes', (req, res) => {
  try {
    const routes = db.prepare('SELECT * FROM routes ORDER BY created_at DESC LIMIT 10').all();
    res.json(routes);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
