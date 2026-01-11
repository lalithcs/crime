@echo off
echo ========================================
echo Crime Safety Platform - Quick Start
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo Docker is running
echo.

REM Create .env file if it doesn't exist
if not exist backend\.env (
    echo Creating backend\.env file...
    copy backend\.env.example backend\.env
    echo Created backend\.env - please update with your settings
)

echo.
echo Starting services with Docker Compose...
echo.
docker-compose up --build -d

echo.
echo Waiting for services to be ready...
timeout /t 15 /nobreak >nul

echo.
echo Running database migrations...
docker-compose exec backend python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"

echo.
echo Loading sample crime data...
docker-compose exec backend python scripts/ingest_data.py

echo.
echo ========================================
echo Platform is ready!
echo ========================================
echo.
echo Access the application:
echo   Frontend:    http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Docs:    http://localhost:8000/docs
echo.
echo To stop the platform:
echo   docker-compose down
echo.
echo To view logs:
echo   docker-compose logs -f
echo.
pause
