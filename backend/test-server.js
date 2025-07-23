const axios = require('axios');

const BASE_URL = 'http://localhost:3001';

async function testAPI() {
  console.log('Testing TSP Route Optimizer API...\n');

  try {
    // Test 1: Check if server is running
    console.log('1. Testing server status...');
    const response = await axios.get(BASE_URL);
    console.log('✓ Server is running');
    console.log('Response:', response.data);
    console.log('');

    // Test 2: Get all cities
    console.log('2. Getting all cities...');
    const citiesResponse = await axios.get(`${BASE_URL}/api/cities`);
    console.log(`✓ Found ${citiesResponse.data.length} cities`);
    console.log('');

    // Test 3: Search for cities (this will fail without Google Maps API key)
    console.log('3. Searching for cities...');
    try {
      const searchResponse = await axios.get(`${BASE_URL}/api/search-cities?query=London`);
      console.log(`✓ Found ${searchResponse.data.length} suggestions`);
    } catch (error) {
      console.log('⚠ Search failed (expected without Google Maps API key)');
      console.log('Error:', error.response?.data?.error || error.message);
    }
    console.log('');

    // Test 4: Test TSP solver with mock data
    console.log('4. Testing TSP solver...');
    if (citiesResponse.data.length >= 2) {
      const cityIds = citiesResponse.data.slice(0, 2).map(city => city.id);
      try {
        const tspResponse = await axios.post(`${BASE_URL}/api/solve-tsp`, {
          cityIds: cityIds
        });
        console.log('✓ TSP solver working');
        console.log('Result:', {
          algorithm: tspResponse.data.algorithm,
          totalDistance: tspResponse.data.totalDistance,
          routeLength: tspResponse.data.route.length
        });
      } catch (error) {
        console.log('⚠ TSP solver failed');
        console.log('Error:', error.response?.data?.error || error.message);
      }
    } else {
      console.log('⚠ Need at least 2 cities to test TSP solver');
    }
    console.log('');

    console.log('✓ API tests completed!');
    
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    console.error('Make sure the backend server is running on port 3001');
  }
}

// Run the test
testAPI();
