@echo off
setlocal
chcp 65001 >nul
title Sistema de Patrimônio
cd /d "%~dp0"

echo.
echo  ============================================
echo    SISTEMA DE PATRIMONIO - Gestao de Bens
echo  ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo  [ERRO] Python nao encontrado no PATH.
    echo  Instale o Python em https://www.python.org/downloads/
    echo  e marque a opcao "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

if not exist "backend\venv\Scripts\python.exe" (
    echo  [1/3] Criando ambiente virtual ^(primeira execucao^)...
    python -m venv backend\venv
    if errorlevel 1 (
        echo  [ERRO] Falha ao criar o ambiente virtual.
        pause
        exit /b 1
    )
)

set "PY=backend\venv\Scripts\python.exe"

"%PY%" -c "import fastapi, uvicorn, sqlalchemy" >nul 2>nul
if errorlevel 1 (
    echo  [2/3] Instalando dependencias...
    "%PY%" -m pip install --upgrade pip --quiet
    "%PY%" -m pip install -r backend\requirements.txt --quiet
    if errorlevel 1 (
        echo  [ERRO] Falha ao instalar as dependencias.
        pause
        exit /b 1
    )
)

echo  [3/3] Iniciando servidor...
echo.
echo   Acesse:  http://localhost:8000
echo   Usuario: admin   Senha: admin123
echo.
echo   (Ctrl+C para encerrar)
echo.

start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8000"

cd backend
"venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000

pause
