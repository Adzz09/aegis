# AEGIS Local Dev Launcher
# Runs all Python services and the React dashboard natively.
# Prerequisite: docker compose -f docker-compose.infra.yml up -d

$ROOT = "d:\aegis"
$PYTHON = "$ROOT\.venv\Scripts\python.exe"
$UVICORN = "$ROOT\.venv\Scripts\uvicorn.exe"
$LOGS = "$ROOT\logs"

# Shared env
$env:PYTHONPATH    = $ROOT
$env:KAFKA_BROKERS = "localhost:19092"
$env:REDIS_URL     = "redis://localhost:6379"
$env:DATABASE_URL  = "postgresql://postgres:postgres@localhost:5432/postgres"

New-Item -ItemType Directory -Force $LOGS | Out-Null

function Start-Service($name, $exe, $args, $cwd) {
    Write-Host "Starting $name..." -ForegroundColor Cyan
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = $exe
    $pinfo.Arguments = $args
    $pinfo.WorkingDirectory = $cwd
    $pinfo.UseShellExecute = $false
    $pinfo.RedirectStandardOutput = $true
    $pinfo.RedirectStandardError  = $true
    $pinfo.EnvironmentVariables["PYTHONPATH"]    = $env:PYTHONPATH
    $pinfo.EnvironmentVariables["KAFKA_BROKERS"] = $env:KAFKA_BROKERS
    $pinfo.EnvironmentVariables["REDIS_URL"]     = $env:REDIS_URL
    $pinfo.EnvironmentVariables["DATABASE_URL"]  = $env:DATABASE_URL
    $p = [System.Diagnostics.Process]::Start($pinfo)
    # Async log capture
    $p.BeginOutputReadLine()
    $p.BeginErrorReadLine()
    Write-Host "  PID $($p.Id)" -ForegroundColor Green
    return $p
}

# 1. API Gateway
$gw = Start-Process -PassThru -FilePath $UVICORN `
    -ArgumentList "src.main:app --host 0.0.0.0 --port 8000" `
    -WorkingDirectory "$ROOT\api-gateway" `
    -RedirectStandardOutput "$LOGS\gateway.log" `
    -RedirectStandardError  "$LOGS\gateway.err" `
    -WindowStyle Hidden

Write-Host "API Gateway PID $($gw.Id)" -ForegroundColor Green
Start-Sleep -Seconds 3

# 2. Sim Engine
$sim = Start-Process -PassThru -FilePath $PYTHON `
    -ArgumentList "-m src.main" `
    -WorkingDirectory "$ROOT\sim-engine" `
    -RedirectStandardOutput "$LOGS\sim.log" `
    -RedirectStandardError  "$LOGS\sim.err" `
    -WindowStyle Hidden

Write-Host "Sim Engine PID $($sim.Id)" -ForegroundColor Green

# 3. Fusion Engine
$fusion = Start-Process -PassThru -FilePath $PYTHON `
    -ArgumentList "-m src.main" `
    -WorkingDirectory "$ROOT\fusion-engine" `
    -RedirectStandardOutput "$LOGS\fusion.log" `
    -RedirectStandardError  "$LOGS\fusion.err" `
    -WindowStyle Hidden

Write-Host "Fusion Engine PID $($fusion.Id)" -ForegroundColor Green

# 4. AI Classifier
$clf = Start-Process -PassThru -FilePath $PYTHON `
    -ArgumentList "src/main.py" `
    -WorkingDirectory "$ROOT\ai-classifier" `
    -RedirectStandardOutput "$LOGS\classifier.log" `
    -RedirectStandardError  "$LOGS\classifier.err" `
    -WindowStyle Hidden

Write-Host "AI Classifier PID $($clf.Id)" -ForegroundColor Green

# 5. Optimizer
$opt = Start-Process -PassThru -FilePath $PYTHON `
    -ArgumentList "src/main.py" `
    -WorkingDirectory "$ROOT\optimizer" `
    -RedirectStandardOutput "$LOGS\optimizer.log" `
    -RedirectStandardError  "$LOGS\optimizer.err" `
    -WindowStyle Hidden

Write-Host "Optimizer PID $($opt.Id)" -ForegroundColor Green

Write-Host ""
Write-Host "All backend services started. Launching dashboard..." -ForegroundColor Yellow
Write-Host "  Gateway:    http://localhost:8000/api/health"
Write-Host "  Dashboard:  http://localhost:5173"
Write-Host "  Kafka UI:   http://localhost:8080"
Write-Host ""

# 6. Dashboard (runs in foreground so you see Vite output)
Set-Location "$ROOT\dashboard"
npm run dev
