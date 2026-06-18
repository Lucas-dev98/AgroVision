# AgroVision Local Development - Run Services without Docker
# This script starts all Go services with SQLite backend

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          🚀 AgroVision - Local Services Setup          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{ Name = "Property Service"; Port = "8081"; Path = "services/property-service" },
    @{ Name = "Production Service"; Port = "8082"; Path = "services/production-service" },
    @{ Name = "Financial Service"; Port = "8083"; Path = "services/financial-service" }
)

# Cleanup function
function Cleanup {
    Write-Host "`n⏹️  Stopping services..." -ForegroundColor Yellow
    Get-Job | Stop-Job
    exit
}

trap { Cleanup }

Write-Host "📋 Services to Start:" -ForegroundColor Green
$services | ForEach-Object {
    Write-Host "  ✓ $($_.Name) on port $($_.Port)" -ForegroundColor Gray
}
Write-Host ""

# Check Go installation
Write-Host "🔍 Checking Go installation..." -ForegroundColor Yellow
$goVersion = & go version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Go is not installed. Please install Go 1.21+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Go found: $goVersion" -ForegroundColor Green
Write-Host ""

# Start each service
Write-Host "🚀 Starting services..." -ForegroundColor Green
Write-Host ""

foreach ($service in $services) {
    $jobName = $service.Name
    $path = $service.Path
    $port = $service.Port
    
    Write-Host "  ▶ Starting $($service.Name)..." -ForegroundColor Cyan
    
    # Start service in background job
    $job = Start-Job -Name $jobName -ScriptBlock {
        param($servicePath, $port)
        Set-Location $servicePath
        
        # Set environment variables for SQLite mock mode
        $env:DATABASE_TYPE = "sqlite"
        $env:SQLITE_PATH = "dev.db"
        $env:SERVICE_PORT = $port
        
        # Run service
        & go run cmd/main.go
    } -ArgumentList $path, $port
    
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Yellow
Write-Host ""

# Monitor services
$counter = 0
while ($true) {
    $jobs = Get-Job
    $runningCount = ($jobs | Where-Object State -eq "Running" | Measure-Object).Count
    
    if ($runningCount -lt $services.Count) {
        Write-Host "⚠️  Some services stopped unexpectedly!" -ForegroundColor Red
        Write-Host ""
        $jobs | ForEach-Object {
            Write-Host "  - $($_.Name): $($_.State)" -ForegroundColor Yellow
            if ($_.State -eq "Failed") {
                Receive-Job $_ -ErrorAction Continue | Out-String | Write-Host -ForegroundColor Red
            }
        }
        Write-Host ""
        Write-Host "Press Ctrl+C to exit..." -ForegroundColor Yellow
    }
    
    # Show status every 30 seconds
    if ($counter % 6 -eq 0) {
        Clear-Host
        Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
        Write-Host "║          🚀 AgroVision - Local Services               ║" -ForegroundColor Cyan
        Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🌐 Available Endpoints:" -ForegroundColor Green
        $services | ForEach-Object {
            Write-Host "  • $($_.Name) → http://localhost:$($_.Port)" -ForegroundColor Gray
        }
        Write-Host ""
        Write-Host "📡 Service Status:" -ForegroundColor Yellow
        $jobs | ForEach-Object {
            $status = if ($_.State -eq "Running") { "✅ Running" } else { "❌ $($_.State)" }
            Write-Host "  $($_.Name): $status" -ForegroundColor Gray
        }
        Write-Host ""
        Write-Host "💡 Tips:" -ForegroundColor Cyan
        Write-Host "  - Test endpoints with: curl http://localhost:8081/health" -ForegroundColor Gray
        Write-Host "  - Press Ctrl+C to stop all services" -ForegroundColor Gray
        Write-Host ""
    }
    
    Start-Sleep -Seconds 5
    $counter++
}
