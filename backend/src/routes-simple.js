const express = require('express');
const { db } = require('./database');
const { googleMapsClient } = require('./googleMapsClient');

const router = express.Router();

// Simple test route
router.get('/test', (req, res) => {
  res.json({ message: 'API is working!' });
});

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

// Get all cities (simplified)
router.get('/cities', (req, res) => {
  try {
    db.all('SELECT * FROM cities ORDER BY created_at DESC', (err, cities) => {
      if (err) {
        console.error('Database error:', err);
        res.status(500).json({ error: err.message });
      } else {
        res.json(cities || []);
      }
    });
  } catch (error) {
    console.error('Route error:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
