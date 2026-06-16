import os
import subprocess
import sys
import time
import shutil

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
    frontend_dir = part2_dir 

    # 2. Define operating system execution structures dynamically
    IS_WIN = sys.platform.startswith("win")
    venv_folder = os.path.join(root_dir, ".venv") 
    venv_bin_dir = os.path.join(venv_folder, "Scripts" if IS_WIN else "bin")

    # 3. Prevent cross-platform .venv corruption
    if os.path.exists(venv_folder):
        expected_indicator = "activate.bat" if IS_WIN else "activate"
        if not os.path.exists(os.path.join(venv_bin_dir, expected_indicator)):
            print("⚠️  [WARN] Cross-platform .venv corruption detected (e.g. Windows env on Mac/Linux).")
            print("    -> Automatically rebuilding a clean virtual environment for the current host...")
            try:
                shutil.rmtree(venv_folder)
                time.sleep(1)
            except Exception as e:
                print(f"❌ Could not clear corrupted environment: {e}. Please delete the root .venv directory manually.")
                sys.exit(1)

    # 4. Dynamic executable addressing mapping
    python_path = os.path.join(venv_bin_dir, "python.exe" if IS_WIN else "python")
    pip_path = os.path.join(venv_bin_dir, "pip.exe" if IS_WIN else "pip")
    
    PYTHON_EXE = f'"{python_path}"'
    PIP_EXE = f'"{pip_path}"'

    # 5. Setup Backend Virtual Environment cleanly if missing
    if not os.path.exists(venv_folder):
        if IS_WIN:
            venv_cmd = "py -m venv .venv"
        else:
            venv_cmd = "python3 -m venv .venv"
        run_step("Creating Clean Python Virtual Environment (.venv)", venv_cmd, cwd=root_dir)
    else:
        print("💡 [INFO] Virtual environment verified and matching current host architecture.")

    # 6. Install Python Dependencies directly from the root directory
    run_step("Installing Backend Requirements from root requirements.txt", f'{PIP_EXE} install -r requirements.txt --quiet --disable-pip-version-check', cwd=root_dir)

    # 7. Provision and Seed Database Schema
    run_step("Initializing Database and Syncing Mock Data Telemetry", f'{PYTHON_EXE} create_db.py', cwd=backend_dir)

    # 8. Check Node.js and Install Frontend Node Dependencies safely
    print("\n⚙️  [STEP] Checking Node.js Environment for UI Component...")
    node_check_cmd = "node -v" if IS_WIN else "command -v node"
    node_check = subprocess.run(node_check_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if node_check.returncode == 0:
        run_step("Installing Frontend Node Dependencies (npm install)", "npm install --no-audit --no-fund --quiet", cwd=frontend_dir)
        run_frontend = True
    else:
        RED = "\033[1;31m"
        RESET = "\033[0m"
        print(RED + "\n" + "!" * 75)
        print("💡 [NOTICE] NODE.JS RUNTIME NOT DETECTED ON THIS MACHINE")
        print("!" * 75)
        print(" -> The React UI Dashboard requires Node.js execution layers.")
        print(" -> BYPASSING FRONTEND BOOT SEQUENCE UPON HOST ARCHITECTURE RESTRICTIONS.")
        print(" -> SUCCESS: Central FastAPI Framework & Swagger Workspace remain 100% stable.")
        print("!" * 75 + "\n" + RESET)
        run_frontend = False

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
        
        # Start Vite/React frontend engine only if Node.js is present
        if run_frontend:
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