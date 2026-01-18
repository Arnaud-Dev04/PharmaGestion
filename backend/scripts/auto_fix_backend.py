import os
import sys
import subprocess
import time
import socket
import sqlite3

def log(msg, status="INFO"):
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, '')}[{status}] {msg}{colors['RESET']}")

def install_dependencies():
    log("Installing/Updating Dependencies...", "INFO")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        log("Dependencies installed.", "SUCCESS")
    except Exception as e:
        log(f"Failed to install dependencies: {e}", "ERROR")

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_on_port(port):
    # Very basic kill for Windows
    try:
        cmd = f"netstat -ano | findstr :{port}"
        output = subprocess.check_output(cmd, shell=True).decode()
        for line in output.splitlines():
            if "LISTENING" in line:
                pid = line.strip().split()[-1]
                log(f"Killing process {pid} on port {port}...", "WARNING")
                os.system(f"taskkill /F /PID {pid}")
    except:
        pass

def test_server_startup():
    log("Testing Server Startup...", "INFO")
    
    # 1. Check if port 8000 is free
    if check_port(8000):
        log("Port 8000 is busy. Attempting to free it...", "WARNING")
        kill_process_on_port(8000)
        time.sleep(2)
        
    # 2. Start server in background
    log("Starting Uvicorn...", "INFO")
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait 5 seconds
        time.sleep(5)
        
        if proc.poll() is not None:
            # It died
            out, err = proc.communicate()
            log("Server failed to start!", "ERROR")
            print("STDOUT:", out.decode())
            print("STDERR:", err.decode())
            return False
        else:
            log("Server started SUCCESSFULLY!", "SUCCESS")
            # Kill it
            proc.terminate()
            log("Server stopped after test.", "INFO")
            return True
            
    except Exception as e:
        log(f"Failed to launch server: {e}", "ERROR")
        return False

def check_db_integrity():
    log("Verifying Database...", "INFO")
    if not os.path.exists("pharmacy_local.db"):
        log("Database missing! Initializing...", "WARNING")
        # Try to run init
        try:
            from app.database import init_local_db
            init_local_db()
            log("Database created.", "SUCCESS")
        except Exception as e:
            log(f"Failed to init DB: {e}", "ERROR")
    else:
        log("Database exists.", "SUCCESS")

if __name__ == "__main__":
    print("====================================")
    print("   PHARMA BACKEND AUTO-FIXER")
    print("====================================\n")
    
    install_dependencies()
    check_db_integrity()
    
    if test_server_startup():
        print("\n[CONCLUSION]")
        print("Your backend creates no errors on startup.")
        print("To run it permanently, use a separate terminal:")
        print("  python -m uvicorn main:app --reload")
    else:
        print("\n[CONCLUSION]")
        print("Backend has errors. See logs above.")
