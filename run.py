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
    print("      🐧 PENGUWAVE SYSTEM - GLOBAL LAUNCH SCRIPT 🐧")
    print("=" * 60)

    # 1. Establish strict global paths from the true repository root
    root_dir = os.path.abspath(os.path.dirname(__file__))
    part2_dir = os.path.join(root_dir, "part2-secure-portal")
    backend_dir = os.path.join(part2_dir, "backend")
    frontend_dir = part2_dir  # package.json sits inside part2-secure-portal

    # 2. Define operating system execution structures dynamically
    IS_WIN = sys.platform.startswith("win")
    venv_folder = os.path.join(backend_dir, ".venv")
    venv_bin_dir = os.path.join(venv_folder, "Scripts" if IS_WIN else "bin")

    # 3. Dynamic executable addressing mapping
    python_path = os.path.join(venv_bin_dir, "python.exe" if IS_WIN else "python")
    pip_path = os.path.join(venv_bin_dir, "pip.exe" if IS_WIN else "pip")
    
    PYTHON_EXE = f'"{python_path}"'
    PIP_EXE = f'"{pip_path}"'

    # 4. Setup Backend Virtual Environment cleanly if missing
    if not os.path.exists(venv_folder):
        run_step("Creating Clean Python Virtual Environment (.venv)", f'py -m venv .venv', cwd=backend_dir)
    else:
        print("💡 [INFO] Virtual environment verified.")

    # 5. Install Python Dependencies
    run_step("Installing Backend Requirements", f'{PIP_EXE} install -r requirements.txt --quiet --disable-pip-version-check', cwd=backend_dir)

    # 6. Provision and Seed Database Schema
    run_step("Initializing Database and Syncing Mock Data Telemetry", f'{PYTHON_EXE} create_db.py', cwd=backend_dir)

    # 7. Install Node Modules for the UI Layer
    run_step("Installing Frontend Node Dependencies (npm install)", "npm install --no-audit --no-fund --quiet", cwd=frontend_dir)

    print("\n🚀 [SUCCESS] Global environment built and verified smoothly!")
    print("Starting Part 2 Portal Services... Press Ctrl+C to terminate both servers.")
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
        
        # Start Vite/React frontend engine
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