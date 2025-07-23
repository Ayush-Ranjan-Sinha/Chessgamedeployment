class TSPSolver {
  constructor() {
    this.memo = new Map();
  }

  // Held-Karp algorithm implementation
  solveTSP(distanceMatrix, startCity = 0) {
    const n = distanceMatrix.length;
    
    if (n <= 1) {
      return { route: [0], distance: 0 };
    }

    this.memo.clear();
    
    // Create bit mask for all cities except start
    const allCities = (1 << n) - 1;
    const otherCities = allCities ^ (1 << startCity);
    
    // Find minimum cost to visit all cities and return to start
    const minCost = this.heldKarp(distanceMatrix, otherCities, startCity);
    
    // Reconstruct the optimal path
    const optimalPath = this.reconstructPath(distanceMatrix, startCity, n);
    
    return {
      route: optimalPath,
      distance: minCost
    };
  }

  // Main Held-Karp recursive function
  heldKarp(distanceMatrix, mask, pos) {
    const n = distanceMatrix.length;
    
    // Base case: if all cities are visited, return cost to start
    if (mask === 0) {
      return distanceMatrix[pos][0];
    }

    // Check if already computed
    const key = `${mask}_${pos}`;
    if (this.memo.has(key)) {
      return this.memo.get(key);
    }

    let minCost = Infinity;
    
    // Try visiting each unvisited city
    for (let city = 0; city < n; city++) {
      if (mask & (1 << city)) {
        const newMask = mask ^ (1 << city);
        const cost = distanceMatrix[pos][city] + this.heldKarp(distanceMatrix, newMask, city);
        minCost = Math.min(minCost, cost);
      }
    }

    this.memo.set(key, minCost);
    return minCost;
  }

  // Reconstruct the optimal path
  reconstructPath(distanceMatrix, start, n) {
    const path = [start];
    let mask = (1 << n) - 1 - (1 << start);
    let pos = start;

    while (mask !== 0) {
      let nextCity = -1;
      let minCost = Infinity;

      for (let city = 0; city < n; city++) {
        if (mask & (1 << city)) {
          const newMask = mask ^ (1 << city);
          const key = `${newMask}_${city}`;
          const cost = distanceMatrix[pos][city] + (this.memo.get(key) || 0);
          
          if (cost < minCost) {
            minCost = cost;
            nextCity = city;
          }
        }
      }

      if (nextCity !== -1) {
        path.push(nextCity);
        mask ^= (1 << nextCity);
        pos = nextCity;
      } else {
        break;
      }
    }

    path.push(start); // Return to start
    return path;
  }

  // Alternative: Nearest Neighbor heuristic for larger datasets
  nearestNeighborTSP(distanceMatrix, startCity = 0) {
    const n = distanceMatrix.length;
    const visited = new Array(n).fill(false);
    const path = [startCity];
    let currentCity = startCity;
    let totalDistance = 0;
    
    visited[startCity] = true;

    for (let i = 1; i < n; i++) {
      let nearestCity = -1;
      let minDistance = Infinity;

      for (let city = 0; city < n; city++) {
        if (!visited[city] && distanceMatrix[currentCity][city] < minDistance) {
          minDistance = distanceMatrix[currentCity][city];
          nearestCity = city;
        }
      }

      if (nearestCity !== -1) {
        path.push(nearestCity);
        visited[nearestCity] = true;
        totalDistance += minDistance;
        currentCity = nearestCity;
      }
    }

    // Return to start
    path.push(startCity);
    totalDistance += distanceMatrix[currentCity][startCity];

    return {
      route: path,
      distance: totalDistance
    };
  }

  // Choose algorithm based on problem size
  solve(distanceMatrix, startCity = 0) {
    const n = distanceMatrix.length;
    
    // Use Held-Karp for small problems (n <= 15)
    // Use Nearest Neighbor for larger problems
    if (n <= 15) {
      return this.solveTSP(distanceMatrix, startCity);
    } else {
      return this.nearestNeighborTSP(distanceMatrix, startCity);
    }
  }
}

module.exports = { TSPSolver };
