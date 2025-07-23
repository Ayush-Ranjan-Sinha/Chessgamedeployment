Write-Host "=== TSP Route Optimizer Status Check ===" -ForegroundColor Green
Write-Host ""

# Check Backend Server
Write-Host "Checking Backend Server (Port 3001)..." -ForegroundColor Yellow
try {
    $backendResponse = Invoke-RestMethod -Uri "http://localhost:3001/" -Method GET -TimeoutSec 5
    Write-Host "✅ Backend Server: RUNNING" -ForegroundColor Green
    Write-Host "   - Root API: OK" -ForegroundColor Green
    
    # Test cities endpoint
    try {
        $citiesResponse = Invoke-RestMethod -Uri "http://localhost:3001/api/cities" -Method GET -TimeoutSec 5
        Write-Host "   - Cities API: OK ($($citiesResponse.Count) cities)" -ForegroundColor Green
    } catch {
        Write-Host "   - Cities API: ERROR" -ForegroundColor Red
    }
    
    # Test search endpoint
    try {
        $searchResponse = Invoke-RestMethod -Uri "http://localhost:3001/api/search-cities?query=London" -Method GET -TimeoutSec 5
        Write-Host "   - Search API: OK ($($searchResponse.Count) results)" -ForegroundColor Green
    } catch {
        Write-Host "   - Search API: ERROR" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Backend Server: NOT RUNNING" -ForegroundColor Red
    Write-Host "   Please run: cd backend && npm start" -ForegroundColor Yellow
}

Write-Host ""

# Check Frontend Server
Write-Host "Checking Frontend Server (Port 3000)..." -ForegroundColor Yellow
$frontendRunning = netstat -an | Select-String ":3000.*LISTENING"
if ($frontendRunning) {
    Write-Host "✅ Frontend Server: RUNNING" -ForegroundColor Green
    Write-Host "   - Access: http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend Server: NOT RUNNING" -ForegroundColor Red
    Write-Host "   Please run: cd frontend && npm start" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Quick Start Instructions ===" -ForegroundColor Cyan
Write-Host "1. Make sure both servers are running" -ForegroundColor White
Write-Host "2. Open your browser to: http://localhost:3000" -ForegroundColor White
Write-Host "3. Navigate to 'Route Optimizer' page" -ForegroundColor White
Write-Host "4. Search for cities and start optimizing!" -ForegroundColor White
Write-Host ""
