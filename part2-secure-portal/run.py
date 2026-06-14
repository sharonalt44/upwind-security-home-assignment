import os
import subprocess
import sys
import time

def run_step(description, command, cwd=None):
    print(f"\n⚙️  [STEP] {description}...")
    result = subprocess.run(command, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ [ERROR] '{description}' failed. Aborting startup sequence.")
        sys.exit(1)

def main():
    print("=" * 60)
    print("      🐧 PENGUWAVE SYSTEM - ENTIRETY LAUNCH SCRIPT 🐧")
    print("=" * 60)

    # 1. Establish absolute root paths matching the Flat Shared Root architecture
    root_dir = os.path.abspath(os.path.dirname(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = root_dir  # The frontend package.json sits directly in the root folder!

    # 2. Define operating system execution structures dynamically
    IS_WIN = sys.platform.startswith("win")
    venv_folder = os.path.join(backend_dir, ".venv")
    venv_bin_dir = os.path.join(venv_folder, "Scripts" if IS_WIN else "bin")

    # 3. Absolute executable addressing wrapped in secure string markers
    python_path = os.path.join(venv_bin_dir, "python.exe" if IS_WIN else "python")
    pip_path = os.path.join(venv_bin_dir, "pip.exe" if IS_WIN else "pip")
    
    PYTHON_EXE = f'"{python_path}"'
    PIP_EXE = f'"{pip_path}"'

    # 4. Setup Backend Virtual Environment safely if missing
    if not os.path.exists(venv_folder):
        run_step("Creating Python Virtual Environment (.venv)", f'"{sys.executable}" -m venv .venv', cwd=backend_dir)
    else:
        print("💡 [INFO] Virtual environment already exists. Skipping creation.")

    # 5. Install Python Dependencies with quiet execution to hide redundant status logs
    run_step("Installing Backend Requirements", f'{PIP_EXE} install -r requirements.txt --quiet --disable-pip-version-check', cwd=backend_dir)

    # 6. Provision and Seed Database Schema
    run_step("Initializing Database and Syncing Mock Data Telemetry", f'{PYTHON_EXE} create_db.py', cwd=backend_dir)

    # 7. Install Node Modules for the UI Layer with structural optimizations and quiet mode
    run_step("Installing Frontend Node Dependencies (npm install)", "npm install --no-audit --no-fund --quiet", cwd=frontend_dir)

    print("\n🚀 [SUCCESS] All environments built and validated securely!")
    print("Starting background service runtimes... Press Ctrl+C to terminate both servers.")
    time.sleep(1)

    backend_proc = None
    frontend_proc = None

    try:
        # Start FastAPI application server
        backend_proc = subprocess.Popen(
            f'{PYTHON_EXE} -m uvicorn app.main:app --reload --port 8000',
            shell=True,
            cwd=backend_dir
        )
        
        # Start Vite/React frontend engine directly from the root layout
        frontend_proc = subprocess.Popen(
            "npm run dev",
            shell=True,
            cwd=frontend_dir
        )

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Interception detected. Safely tearing down server execution runtimes...")
    finally:
        if backend_proc:
            backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()
        print("🔒 [STATUS] All core servers closed safely. Goodbye!")

if __name__ == "__main__":
    main()