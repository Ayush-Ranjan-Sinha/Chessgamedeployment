# TSP Route Optimizer

A complete web application that solves the Traveling Salesman Problem (TSP) using the Held-Karp algorithm with Google Maps integration.

## Features

- **City Search**: Search and add cities using Google Maps Places API
- **Held-Karp Algorithm**: Optimal route calculation using dynamic programming
- **Distance Calculation**: Accurate distance calculations with caching
- **Route History**: Store and view past optimization results
- **Responsive UI**: Modern Material-UI interface
- **Real-time Search**: Autocomplete city suggestions

## Tech Stack

### Backend
- Node.js with Express
- SQLite database
- Google Maps API integration
- Held-Karp algorithm implementation

### Frontend
- React with TypeScript
- Material-UI components
- Axios for API calls
- React Router for navigation

## Project Structure

```
tsp-route-optimizer/
├── backend/
│   ├── src/
│   │   ├── app.js              # Express server setup
│   │   ├── database.js         # Database connection and schema
│   │   ├── googleMapsClient.js # Google Maps API client
│   │   ├── routes.js           # API routes
│   │   └── tspSolver.js        # Held-Karp algorithm implementation
│   ├── package.json
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── HomePage.tsx
│   │   │   ├── RouteOptimizer.tsx
│   │   │   └── RouteHistory.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   └── App.tsx
│   ├── package.json
│   └── .env
└── README.md
```

## Setup Instructions

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn
- Google Maps API key

### 1. Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Places API
   - Distance Matrix API
   - Geocoding API
4. Create credentials (API Key)
5. Restrict the API key to your domain (optional but recommended)

### 2. Backend Setup

```bash
cd backend
npm install
```

Create a `.env` file in the backend directory:
```
PORT=3001
NODE_ENV=development
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
DATABASE_URL=./database.db
CORS_ORIGIN=http://localhost:3000
```

Start the backend server:
```bash
npm run dev
```

The backend API will be available at `http://localhost:3001`

### 3. Frontend Setup

```bash
cd frontend
npm install
```

Create a `.env` file in the frontend directory:
```
REACT_APP_API_URL=http://localhost:3001/api
REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

Start the frontend development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Cities
- `GET /api/cities` - Get all cities
- `POST /api/cities` - Add a new city
- `DELETE /api/cities/:id` - Delete a city
- `GET /api/search-cities?query=<query>` - Search cities

### Route Optimization
- `POST /api/distance-matrix` - Calculate distance matrix
- `POST /api/solve-tsp` - Solve TSP using Held-Karp algorithm
- `GET /api/routes` - Get route history

## Algorithm Details

### Held-Karp Algorithm

The Held-Karp algorithm is a dynamic programming approach to solve the TSP optimally:

1. **Time Complexity**: O(n² × 2ⁿ)
2. **Space Complexity**: O(n × 2ⁿ)
3. **Optimal for**: Small to medium-sized problems (≤ 15 cities)

For larger datasets, the application falls back to the Nearest Neighbor heuristic.

### Distance Calculation

- Uses Google Maps Distance Matrix API for accurate distances
- Falls back to Haversine formula for basic distance calculations
- Implements caching to reduce API calls and improve performance

## Usage

1. **Add Cities**: Use the search bar to find and add cities
2. **Select Cities**: Choose cities from the list for route optimization
3. **Optimize Route**: Click "Optimize Route" to solve the TSP
4. **View Results**: See the optimized route with total distance
5. **View History**: Check past optimization results

## Deployment

### Backend Deployment
- Configure environment variables
- Set up production database
- Deploy to services like Heroku, AWS, or DigitalOcean

### Frontend Deployment
- Build the production bundle: `npm run build`
- Deploy to services like Netlify, Vercel, or AWS S3

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.
