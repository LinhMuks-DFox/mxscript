import os
import subprocess
import sys
import requests
from pathlib import Path

# --- Configuration ---
VENV_PATH = Path(".venv")
REQUIREMENTS_FILE = "requirements.txt"

# C++ dependencies from GitHub (URL -> destination file)
CPP_DEPS = {
    "utf8.h": {
        "url": "https://raw.githubusercontent.com/sheredom/utf8.h/master/utf8.h",
        "dest": Path("runtime/third_party/utf8.h"),
    }
    # Add other C++ dependencies here in the future
    # "library_name": {
    #     "url": "...",
    #     "dest": Path("runtime/third_party/...")
    # }
}

def run_command(command, check=True):
    """Runs a command in the shell and checks for errors."""
    print(f"--- Running: {' '.join(command)}")
    try:
        subprocess.run(command, check=check, text=True, stderr=sys.stderr, stdout=sys.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"!!! Error running command: {' '.join(command)}")
        print(f"!!! {e}")
        sys.exit(1)

def create_venv():
    """Creates a Python virtual environment if it doesn't exist."""
    if VENV_PATH.exists():
        print(f"--- Virtual environment '{VENV_PATH}' already exists. Skipping.")
        return
    print(f"--- Creating Python virtual environment at '{VENV_PATH}'...")
    run_command([sys.executable, "-m", "venv", str(VENV_PATH)])

def get_pip_path():
    """Gets the path to the pip executable inside the virtual environment."""
    if sys.platform == "win32":
        return VENV_PATH / "Scripts" / "pip.exe"
    else:
        return VENV_PATH / "bin" / "pip"

def install_python_deps():
    """Installs Python dependencies from requirements.txt into the venv."""
    if not Path(REQUIREMENTS_FILE).exists():
        print(f"!!! '{REQUIREMENTS_FILE}' not found. Skipping Python dependency installation.")
        return

    print("--- Installing Python dependencies...")
    pip_executable = get_pip_path()
    run_command([str(pip_executable), "install", "-r", REQUIREMENTS_FILE])

def download_cpp_deps():
    """Downloads C++ dependencies from GitHub."""
    print("--- Downloading C/C++ dependencies...")
    for lib_name, info in CPP_DEPS.items():
        url = info["url"]
        dest_path = info["dest"]

        if dest_path.exists():
            print(f"--- Dependency '{lib_name}' already exists at '{dest_path}'. Skipping.")
            continue

        print(f"--- Downloading '{lib_name}' from {url}...")
        
        # Ensure the destination directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"--- Successfully saved to '{dest_path}'.")
        except requests.exceptions.RequestException as e:
            print(f"!!! Failed to download {lib_name}: {e}")
            sys.exit(1)

def main():
    """Main function to set up the environment."""
    print(">>> Starting Project Environment Setup <<<")
    
    # 1. Create virtual environment
    create_venv()
    
    # 2. Install Python packages
    install_python_deps()
    
    # 3. Download C++ dependencies
    download_cpp_deps()
    
    print("\n>>> Environment setup complete! <<<")
    print(f"You can now activate the virtual environment using:")
    if sys.platform == "win32":
        print(f"> .\\{VENV_PATH}\\Scripts\\activate")
    else:
        print(f"$ source {VENV_PATH}/bin/activate")

if __name__ == "__main__":
    main()