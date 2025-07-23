const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { db } = require('./database');
const routes = require('./routes-simple');

dotenv.config();

const app = express();

const PORT = process.env.PORT || 3001;
const CORS_ORIGIN = process.env.CORS_ORIGIN || 'http://localhost:3000';

app.use(cors({ origin: CORS_ORIGIN }));
app.use(express.json());

app.get('/', (req, res) => {
  res.json({
    message: 'TSP Route Optimizer API',
    version: '1.0.0',
    endpoints: {
      'GET /api/cities': 'Get all cities',
      'POST /api/cities': 'Add a new city',
      'DELETE /api/cities/:id': 'Delete a city',
      'GET /api/search-cities': 'Search for cities',
      'POST /api/distance-matrix': 'Calculate distance matrix',
      'POST /api/solve-tsp': 'Solve TSP using Held-Karp algorithm',
      'GET /api/routes': 'Get route history'
    }
  });
});

// Use API routes
app.use('/api', routes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Handle 404
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
  console.log(`API endpoints available at http://localhost:${PORT}/api`);
}).on('error', (err) => {
  console.error('Server startup error:', err);
});

process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});
