@echo off
REM ============================================================================
REM  Batch Script to Create a Scalable Flask Application Structure
REM ============================================================================

echo Creating project root folder: amazon_toolkit...
mkdir "C:\Projects\Amazon Toolkit"
cd "C:\Projects\Amazon Toolkit"

REM --- Create Core Application Folder ---
echo Creating app/ folder...
mkdir app
cd app

echo   - Creating app/__init__.py
type nul > __init__.py

echo   - Creating app/routes.py
type nul > routes.py

echo   - Creating app/models.py
type nul > models.py

REM --- Create Services for Business Logic ---
echo   - Creating app/services/ folder...
mkdir services
cd services
echo     - Creating services/__init__.py
type nul > __init__.py
echo     - Creating services/analysis_service.py
type nul > analysis_service.py
echo     - Creating services/normalization_service.py
type nul > normalization_service.py
cd ..

REM --- Create Folders for UI Files ---
echo   - Creating app/templates/ folder...
mkdir templates
cd templates
echo     - Creating templates/index.html
type nul > index.html
echo     - Creating templates/base.html
type nul > base.html
cd ..

echo   - Creating app/static/ folder...
mkdir static
cd static
mkdir css
mkdir js
mkdir images
cd ..

cd ..

REM --- Create Configuration Folder ---
echo Creating config/ folder...
mkdir config
cd config
echo   - Creating config/settings.py
type nul > settings.py
cd ..

REM --- Create Data Folder ---
echo Creating data/ folder...
mkdir data
cd data
echo   - Creating data/source/ folder
mkdir source
echo   - Creating data/processed/ folder
mkdir processed
cd ..

REM --- Create Scripts Folder for Helper Utilities ---
echo Creating scripts/ folder...
mkdir scripts
cd scripts
echo   - Creating scripts/run_normalization.py
type nul > run_normalization.py
cd ..

REM --- Create Tests Folder ---
echo Creating tests/ folder...
mkdir tests
cd tests
echo   - Creating tests/test_analysis.py
type nul > test_analysis.py
cd ..

REM --- Create Root Files ---
echo Creating root files...
echo   - Creating run.py
type nul > run.py

echo   - Creating requirements.txt
(
    echo flask
    echo pandas
    echo numpy
    echo openpyxl
) > requirements.txt

echo   - Creating .env file
(
    echo FLASK_APP=run.py
    echo FLASK_ENV=development
    echo SECRET_KEY=your_super_secret_key_here
) > .env

echo   - Creating .gitignore file
(
    echo # Byte-compiled / optimized / DLL files
    echo __pycache__/
    echo *.py[cod]
    echo *$py.class
    echo.
    echo # C extensions
    echo *.so
    echo.
    echo # Distribution / packaging
    echo .Python
    echo build/
    echo develop-eggs/
    echo dist/
    echo downloads/
    echo eggs/
    echo .eggs/
    echo lib/
    echo lib64/
    echo parts/
    echo sdist/
    echo var/
    echo wheels/
    echo *.egg-info/
    echo .installed.cfg
    echo *.egg
    echo MANIFEST
    echo.
    echo # PyInstaller
    echo *.spec
    echo.
    echo # Installer logs
    echo pip-log.txt
    echo pip-delete-this-directory.txt
    echo.
    echo # Unit test / coverage reports
    echo htmlcov/
    echo .tox/
    echo .nox/
    echo .coverage
    echo .coverage.*
    echo .cache
    echo nosetests.xml
    echo coverage.xml
    echo *.cover
    echo .hypothesis/
    echo .pytest_cache/
    echo.
    echo # Environments
    echo .env
    echo .venv
    echo env/
    echo venv/
    echo ENV/
    echo env.bak/
    echo venv.bak/
    echo.
    echo # Data files
    echo data/source/
    echo data/processed/
    echo.
    echo # IDE / Editor specific
    echo .idea/
    echo .vscode/
    echo *.sublime-workspace
) > .gitignore

echo   - Creating README.md
(
    echo # Amazon Toolkit Project
    echo.
    echo This application provides a suite of tools for working with Amazon data.
) > README.md

echo.
echo ============================================================================
echo Project structure created successfully in 'C:\Projects\Amazon Toolkit' folder.
echo ============================================================================
echo.

pause
