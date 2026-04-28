param(
    [switch]$WithNgrok,
    [switch]$SkipInstall,
    [switch]$AuthAndShapeOnly
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$logsDir = Join-Path $root 'logs'
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

function Stop-PortProcesses {
    param([int[]]$Ports)

    foreach ($port in $Ports) {
        try {
            $pids = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty OwningProcess -Unique
            foreach ($pid in $pids) {
                if ($pid -and $pid -ne $PID) {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                }
            }
        } catch {
            # Ignore non-fatal cleanup errors
        }
    }

    Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

function Assert-Python {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        throw "Python executable not found: $Path"
    }
}

function Get-SystemPython {
    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCmd) {
        return @('py', @('-3'))
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        return @('python', @())
    }

    throw 'Neither py nor python is available in PATH. Install Python 3 first.'
}

function Ensure-VenvAndDeps {
    param(
        [string]$ServiceName,
        [string]$ServiceDir,
        [string]$VenvDir,
        [string]$RequirementsPath,
        [switch]$EditableInstall
    )

    $venvPython = Join-Path $ServiceDir "$VenvDir\Scripts\python.exe"
    $systemPython = Get-SystemPython
    $sysExe = $systemPython[0]
    $sysArgs = $systemPython[1]

    if (-not (Test-Path $venvPython)) {
        Write-Host "[$ServiceName] Creating virtual environment..." -ForegroundColor Yellow
        & $sysExe @sysArgs -m venv (Join-Path $ServiceDir $VenvDir) | Out-Null
    }

    if (-not $SkipInstall) {
        Write-Host "[$ServiceName] Installing dependencies..." -ForegroundColor Yellow
        & $venvPython -m pip install --upgrade pip | Out-Null
        if ($EditableInstall) {
            try {
                & $venvPython -m pip install -e $ServiceDir | Out-Null
            }
            catch {
                if ($RequirementsPath -and (Test-Path $RequirementsPath)) {
                    Write-Host "[$ServiceName] Editable install failed, falling back to requirements.txt" -ForegroundColor Yellow
                    & $venvPython -m pip install -r $RequirementsPath | Out-Null
                }
                else {
                    throw
                }
            }
        }
        elseif ($RequirementsPath -and (Test-Path $RequirementsPath)) {
            & $venvPython -m pip install -r $RequirementsPath | Out-Null
        }
    }

    return $venvPython
}

function Start-ServiceProcess {
    param(
        [string]$Name,
        [string]$WorkingDir,
        [string]$PythonPath,
        [string[]]$ArgList,
        [hashtable]$EnvVars = @{}
    )

    Assert-Python -Path $PythonPath

    $outFile = Join-Path $logsDir ("$Name.out.log")
    $errFile = Join-Path $logsDir ("$Name.err.log")

    $oldPyPath = $env:PYTHONPATH
    foreach ($key in $EnvVars.Keys) {
        Set-Item -Path "Env:$key" -Value $EnvVars[$key]
    }

    try {
        $cleanArgs = @($ArgList | Where-Object { $_ -ne $null -and $_ -ne '' })
        $proc = Start-Process -FilePath $PythonPath `
            -ArgumentList $cleanArgs `
            -WorkingDirectory $WorkingDir `
            -RedirectStandardOutput $outFile `
            -RedirectStandardError $errFile `
            -PassThru
    }
    finally {
        if ($EnvVars.ContainsKey('PYTHONPATH')) {
            $env:PYTHONPATH = $oldPyPath
        }
    }

    return [PSCustomObject]@{
        Name = $Name
        Process = $proc
        OutLog = $outFile
        ErrLog = $errFile
    }
}

Write-Host "=== Ganithamithura Windows Starter ===" -ForegroundColor Cyan
Write-Host "Root: $root"

Stop-PortProcesses -Ports @(8000, 8001, 8002, 8003, 8004, 8005, 4040)

$authDir = Join-Path $root 'auth_service'
$shapeDir = Join-Path $root 'shape_service'

$authPython = Ensure-VenvAndDeps -ServiceName 'auth' -ServiceDir $authDir -VenvDir '.venv' -RequirementsPath (Join-Path $authDir 'requirements.txt')
$shapePython = Ensure-VenvAndDeps -ServiceName 'shape' -ServiceDir $shapeDir -VenvDir '.venv' -RequirementsPath (Join-Path $shapeDir 'requirements.txt') -EditableInstall

$services = @()

$services += Start-ServiceProcess -Name 'auth' `
    -WorkingDir $authDir `
    -PythonPath $authPython `
    -ArgList @('-m', 'uvicorn', 'main:app', '--reload', '--host', '0.0.0.0', '--port', '8001')

$shapePyPath = "$root;$($env:PYTHONPATH)"
$services += Start-ServiceProcess -Name 'shape' `
    -WorkingDir $shapeDir `
    -PythonPath $shapePython `
    -ArgList @('-m', 'uvicorn', 'app.main:app', '--reload', '--host', '0.0.0.0', '--port', '8003') `
    -EnvVars @{ PYTHONPATH = $shapePyPath }

if (-not $AuthAndShapeOnly) {
    $symbolDir = Join-Path $root 'symbol-service'
    $numberDir = Join-Path $root 'number-service'
    $unitDir = Join-Path $root 'unit-rag-service'

    $symbolPython = Ensure-VenvAndDeps -ServiceName 'symbol' -ServiceDir $symbolDir -VenvDir 'venv' -RequirementsPath (Join-Path $symbolDir 'requirements.txt')
    $numberPython = Ensure-VenvAndDeps -ServiceName 'number' -ServiceDir $numberDir -VenvDir '.venv' -RequirementsPath (Join-Path $numberDir 'requirements.txt')
    $unitPython = Ensure-VenvAndDeps -ServiceName 'measurement' -ServiceDir $unitDir -VenvDir 'venv' -RequirementsPath (Join-Path $unitDir 'requirements.txt')

    if (-not $SkipInstall) {
        Write-Host "[gateway] Installing shared gateway dependencies in symbol-service venv..." -ForegroundColor Yellow
        & $symbolPython -m pip install fastapi uvicorn httpx websockets pyngrok requests python-dotenv
    }

    $services += Start-ServiceProcess -Name 'symbol' `
        -WorkingDir $symbolDir `
        -PythonPath $symbolPython `
        -ArgList @('-m', 'uvicorn', 'src.server:app', '--reload', '--host', '0.0.0.0', '--port', '8000')

    $services += Start-ServiceProcess -Name 'number' `
        -WorkingDir $numberDir `
        -PythonPath $numberPython `
        -ArgList @('-m', 'uvicorn', 'main:app', '--reload', '--host', '0.0.0.0', '--port', '8004')

    $services += Start-ServiceProcess -Name 'measurement' `
        -WorkingDir $unitDir `
        -PythonPath $unitPython `
        -ArgList @('-m', 'uvicorn', 'app.main:app', '--reload', '--host', '0.0.0.0', '--port', '8002')

    $services += Start-ServiceProcess -Name 'gateway' `
        -WorkingDir $root `
        -PythonPath $symbolPython `
        -ArgList @('gateway.py')

    if ($WithNgrok) {
        $services += Start-ServiceProcess -Name 'ngrok_updater' `
            -WorkingDir $root `
            -PythonPath $symbolPython `
            -ArgList @('start_tunnels.py')
    }
}

Write-Host ""
Write-Host "Started services:" -ForegroundColor Green
$services | ForEach-Object {
    Write-Host ("- {0} (PID {1})" -f $_.Name, $_.Process.Id)
    Write-Host ("  out: {0}" -f $_.OutLog)
    Write-Host ("  err: {0}" -f $_.ErrLog)
}

Write-Host ""
if ($AuthAndShapeOnly) {
    Write-Host "Auth docs:  http://localhost:8001/docs" -ForegroundColor Yellow
    Write-Host "Shape docs: http://localhost:8003/docs" -ForegroundColor Yellow
    Write-Host "Use this to stop auth+shape later:" -ForegroundColor Yellow
    Write-Host "  Get-NetTCPConnection -LocalPort 8001,8003 -State Listen | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object { Stop-Process -Id `$_ -Force }"
}
else {
    Write-Host "Gateway health: http://localhost:8005/health" -ForegroundColor Yellow
    Write-Host "Use this to stop all backend processes later:" -ForegroundColor Yellow
    Write-Host "  Get-NetTCPConnection -LocalPort 8000,8001,8002,8003,8004,8005 -State Listen | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object { Stop-Process -Id `$_ -Force }"
}
