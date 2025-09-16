"""
Development and deployment scripts for the Healthcare Test Case Generation System
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def run_command(command: str, cwd: Path = None, shell: bool = True):
    """Run a command and handle output"""
    try:
        logger.info(f"Running: {command}")
        result = subprocess.run(
            command,
            shell=shell,
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Command output: {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        raise


def setup_backend():
    """Set up backend environment"""
    logger.info("Setting up backend environment...")
    
    # Create virtual environment if it doesn't exist
    venv_path = PROJECT_ROOT / "venv"
    if not venv_path.exists():
        logger.info("Creating virtual environment...")
        run_command(f"python -m venv {venv_path}")
    
    # Install backend dependencies
    pip_executable = venv_path / "Scripts" / "pip.exe"
    requirements_file = PROJECT_ROOT / "requirements.txt"
    
    if requirements_file.exists():
        logger.info("Installing backend dependencies...")
        run_command(f'"{pip_executable}" install -r "{requirements_file}"')
    else:
        logger.warning("requirements.txt not found, skipping dependency installation")


def setup_frontend():
    """Set up frontend environment"""
    logger.info("Setting up frontend environment...")
    
    if FRONTEND_DIR.exists():
        package_json = FRONTEND_DIR / "package.json"
        if package_json.exists():
            logger.info("Installing frontend dependencies...")
            run_command("npm install", cwd=FRONTEND_DIR)
        else:
            logger.warning("package.json not found in frontend directory")
    else:
        logger.warning("Frontend directory not found")


def run_backend():
    """Run the backend server"""
    logger.info("Starting backend server...")
    
    python_executable = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"
    main_file = BACKEND_DIR / "main.py"
    
    if not python_executable.exists():
        logger.error("Virtual environment not found. Please run setup first.")
        return
    
    if not main_file.exists():
        logger.error("Backend main.py not found.")
        return
    
    # Set environment variables
    os.environ["PYTHONPATH"] = str(PROJECT_ROOT)
    
    run_command(f'"{python_executable}" "{main_file}"')


def run_frontend():
    """Run the frontend development server"""
    logger.info("Starting frontend development server...")
    
    if not FRONTEND_DIR.exists():
        logger.error("Frontend directory not found")
        return
    
    run_command("npm start", cwd=FRONTEND_DIR)


def run_tests():
    """Run all tests"""
    logger.info("Running tests...")
    
    python_executable = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"
    
    if not python_executable.exists():
        logger.error("Virtual environment not found. Please run setup first.")
        return
    
    # Set environment variables
    os.environ["PYTHONPATH"] = str(PROJECT_ROOT)
    
    # Run backend tests
    test_dir = PROJECT_ROOT / "tests"
    if test_dir.exists():
        run_command(f'"{python_executable}" -m pytest "{test_dir}" -v')
    else:
        logger.warning("Tests directory not found")
    
    # Run frontend tests if available
    if FRONTEND_DIR.exists():
        package_json = FRONTEND_DIR / "package.json"
        if package_json.exists():
            run_command("npm test", cwd=FRONTEND_DIR)


def build_frontend():
    """Build frontend for production"""
    logger.info("Building frontend for production...")
    
    if not FRONTEND_DIR.exists():
        logger.error("Frontend directory not found")
        return
    
    run_command("npm run build", cwd=FRONTEND_DIR)


def setup_environment():
    """Set up the complete development environment"""
    logger.info("Setting up complete development environment...")
    
    try:
        setup_backend()
        setup_frontend()
        logger.info("Environment setup completed successfully!")
    except Exception as e:
        logger.error(f"Environment setup failed: {str(e)}")
        raise


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python run.py <command>")
        print("Commands:")
        print("  setup       - Set up development environment")
        print("  backend     - Run backend server")
        print("  frontend    - Run frontend development server")
        print("  test        - Run all tests")
        print("  build       - Build frontend for production")
        return
    
    command = sys.argv[1]
    
    try:
        if command == "setup":
            setup_environment()
        elif command == "backend":
            run_backend()
        elif command == "frontend":
            run_frontend()
        elif command == "test":
            run_tests()
        elif command == "build":
            build_frontend()
        else:
            logger.error(f"Unknown command: {command}")
            return
    except Exception as e:
        logger.error(f"Command failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()