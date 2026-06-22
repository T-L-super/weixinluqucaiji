# 完成时间：2026-03-19 01:00 UTC
# 大学录取信息整理系统 - Dockerfile
# 多阶段构建，优化镜像大小

# ==================== 阶段 1: 构建前端 ====================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端配置文件
COPY frontend/package*.json ./

# 安装依赖（如果 package.json 存在）
RUN if [ -f "package.json" ]; then npm ci; else echo "No package.json, skipping npm install"; fi

# 复制前端源码
COPY frontend/ ./

# 构建前端（如果存在构建脚本）
RUN if [ -f "package.json" ] && grep -q '"build"' package.json; then npm run build; else echo "No build script, skipping build"; fi

# ==================== 阶段 2: Python 依赖 ====================
FROM python:3.11-slim AS python-deps

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/requirements.txt ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# ==================== 阶段 3: 运行环境 ====================
FROM python:3.11-slim AS runtime

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    APP_HOME=/app \
    DATA_DIR=/app/data \
    LOGS_DIR=/app/logs

# 设置工作目录
WORKDIR /app

# 安装运行时系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && adduser --disabled-password --gecos '' appuser

# 从构建阶段复制 Python 依赖
COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=python-deps /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# 复制后端代码
COPY backend/ ./backend/

# 复制前端构建产物（从阶段 1 或本地）
COPY frontend/dist/ ./frontend/dist/ 2>/dev/null || echo "No frontend dist, will use API only"

# 创建数据目录
RUN mkdir -p ${DATA_DIR} ${LOGS_DIR} && \
    chown -R appuser:appuser ${APP_HOME}

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 启动命令（使用 Gunicorn + Uvicorn workers）
CMD ["sh", "-c", "gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --access-logfile ${LOGS_DIR}/access.log --error-logfile ${LOGS_DIR}/error.log"]

# ==================== 开发模式（可选） ====================
# 使用以下命令启动开发模式：
# docker run -p 8000:8000 -v $(pwd)/backend:/app/backend admission-system uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
