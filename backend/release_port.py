import subprocess
import os

# 获取占用8000端口的进程ID
result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
for line in result.stdout.split('\n'):
    if ':8000' in line and 'LISTENING' in line:
        parts = line.split()
        pid = parts[-1]
        print(f"找到占用端口 8000 的进程: PID {pid}")
        # 杀死进程
        os.system(f'taskkill /F /PID {pid}')
        print(f"已终止进程 {pid}")
        break