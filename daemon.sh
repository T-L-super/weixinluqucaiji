#!/bin/bash
# 大学录取信息整理系统 - 守护进程脚本
# 用途：确保后端服务和轮询器持续运行，被 kill 后自动重启

BACKEND_DIR="/root/.openclaw/workspace/大学录取信息整理系统/backend"
LOG_DIR="/root/.openclaw/workspace/大学录取信息整理系统/logs"
BACKEND_LOG="$LOG_DIR/backend.log"
POLLER_LOG="$LOG_DIR/poller.log"
PID_FILE="/root/.openclaw/workspace/大学录取信息整理系统/system.pid"

mkdir -p "$LOG_DIR"

# 后端服务
start_backend() {
    if pgrep -f "uvicorn app.main:app" > /dev/null; then
        echo "✅ 后端服务已在运行 (PID: $(pgrep -f 'uvicorn app.main:app' | head -1))"
    else
        echo "🚀 启动后端服务..."
        cd "$BACKEND_DIR"
        nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info > "$BACKEND_LOG" 2>&1 &
        echo "后端 PID: $!"
        echo $! >> "$PID_FILE"
    fi
}

# 任务轮询器
start_poller() {
    if pgrep -f "poll_tasks.py" > /dev/null; then
        echo "✅ 任务轮询器已在运行 (PID: $(pgrep -f 'poll_tasks.py' | head -1))"
    else
        POLLER_SCRIPT="/root/.openclaw/workspace/skills/admission-task-poller/bin/poll_tasks.py"
        if [ -f "$POLLER_SCRIPT" ]; then
            echo "🚀 启动任务轮询器..."
            nohup python3 "$POLLER_SCRIPT" --interval 30 > "$POLLER_LOG" 2>&1 &
            echo "轮询器 PID: $!"
            echo $! >> "$PID_FILE"
        else
            echo "⚠️ 轮询器脚本不存在，跳过"
        fi
    fi
}

# 守护循环：每 10 秒检查一次
daemon_loop() {
    echo "========================================="
    echo "🛡️ 守护进程已启动"
    echo "========================================="
    echo "检查间隔: 10 秒"
    echo "后端端口: 8000"
    echo "日志目录: $LOG_DIR"
    echo "========================================="

    while true; do
        # 检查后端
        if ! pgrep -f "uvicorn app.main:app" > /dev/null; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 后端服务已停止，正在重启..."
            start_backend
            sleep 3
            if curl -s http://localhost:8000/api/health | grep -q "healthy"; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 后端服务重启成功"
            else
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ 后端服务启动异常，将在下次检查重试"
            fi
        fi

        # 检查轮询器（如果脚本存在）
        POLLER_SCRIPT="/root/.openclaw/workspace/skills/admission-task-poller/bin/poll_tasks.py"
        if [ -f "$POLLER_SCRIPT" ]; then
            if ! pgrep -f "poll_tasks.py" > /dev/null; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 任务轮询器已停止，正在重启..."
                nohup python3 "$POLLER_SCRIPT" --interval 30 > "$POLLER_LOG" 2>&1 &
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 轮询器已重启 (PID: $!)"
            fi
        fi

        sleep 10
    done
}

# 主流程
start_backend
start_poller
echo ""
echo "🛡️ 进入守护循环 (Ctrl+C 退出守护，服务会继续运行)"
echo ""
daemon_loop
