const axios = require('axios');

async function testAPI() {
  try {
    console.log('Testing API connection...');
    
    // Test root endpoint
    const rootResponse = await axios.get('http://localhost:3001/');
    console.log('✓ Root endpoint working');
    
    // Test cities endpoint
    const citiesResponse = await axios.get('http://localhost:3001/api/cities');
    console.log('✓ Cities endpoint working');
    console.log('Cities found:', citiesResponse.data.length);
    
    // Test search endpoint
    try {
      const searchResponse = await axios.get('http://localhost:3001/api/search-cities?query=London');
      console.log('✓ Search endpoint working');
      console.log('Search results:', searchResponse.data.length);
    } catch (error) {
      console.log('⚠ Search endpoint failed (expected without proper Google API setup)');
    }
    
    console.log('\n✅ API is working! Frontend should be able to connect.');
    
  } catch (error) {
    console.error('❌ API test failed:', error.message);
    if (error.response) {
      console.error('Response:', error.response.data);
    }
  }
}

testAPI();
