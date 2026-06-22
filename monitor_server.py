import subprocess
import time
import os
import sys

def check_server():
    try:
        result = subprocess.run(
            ["netstat", "-ano", "|", "findstr", ":8000"],
            capture_output=True,
            text=True,
            shell=True
        )
        return ":8000" in result.stdout
    except:
        return False

def start_server():
    print("启动服务器...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(script_dir, "backend")
    python_path = os.path.join(backend_dir, ".venv", "Scripts", "python.exe")
    run_path = os.path.join(backend_dir, "run.py")
    
    subprocess.Popen(
        [python_path, run_path],
        cwd=backend_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    time.sleep(5)

def main():
    print("服务器监控脚本启动")
    print("按 Ctrl+C 停止监控")
    
    while True:
        if not check_server():
            print("服务器未运行，重新启动...")
            start_server()
        
        time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n监控脚本已停止")
        sys.exit(0)
