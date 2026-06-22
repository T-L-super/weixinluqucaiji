# 完成时间：2026-03-19 01:30 UTC

# 🚀 大学录取信息整理系统 - 部署文档

## 📋 目录

1. [系统要求](#系统要求)
2. [快速部署](#快速部署)
3. [生产环境部署](#生产环境部署)
4. [配置说明](#配置说明)
5. [运维管理](#运维管理)
6. [故障排查](#故障排查)

---

## 系统要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 1 核 | 2 核 + |
| 内存 | 512MB | 1GB+ |
| 磁盘 | 1GB | 5GB+ |
| 网络 | 10Mbps | 100Mbps+ |

### 软件要求

- Docker 20.10+
- Docker Compose 2.0+
- 操作系统：Linux (Ubuntu 20.04+, CentOS 7+) / macOS / Windows

---

## 快速部署

### 1. 克隆项目

```bash
git clone <repository-url> admission-system
cd admission-system
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，根据实际需求修改配置
```

### 3. 启动服务

```bash
# 使用 Docker Compose 启动
docker-compose up -d
```

### 4. 验证部署

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f app

# 测试 API
curl http://localhost/api/health
```

### 5. 访问系统

- **前端页面**: http://localhost
- **API 文档**: http://localhost/docs
- **健康检查**: http://localhost/api/health

---

## 生产环境部署

### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 安全配置

```bash
# 配置防火墙（仅开放 80 和 443 端口）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 配置 SSL（使用 Let's Encrypt）
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### 3. 部署应用

```bash
# 创建部署目录
sudo mkdir -p /opt/admission-system
cd /opt/admission-system

# 上传项目文件
# ... (上传代码或使用 git clone)

# 配置环境变量
cp .env.example .env
# 编辑 .env，设置生产环境配置

# 启动服务
sudo docker-compose up -d

# 设置开机自启
sudo docker-compose start
```

### 4. Nginx 反向代理（可选）

如果需要 HTTPS 或更复杂的路由配置：

```nginx
# /etc/nginx/sites-available/admission-system
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `ENVIRONMENT` | 运行环境 | `development` | 否 |
| `PORT` | 应用端口 | `8000` | 否 |
| `DATABASE_URL` | 数据库连接 | `sqlite:///./data/admission_system.db` | 否 |
| `REDIS_URL` | Redis 连接 | `redis://localhost:6379/0` | 否 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 否 |
| `TZ` | 时区 | `Asia/Shanghai` | 否 |

### 目录结构

```
admission-system/
├── data/              # 数据目录（需持久化）
│   ├── admission_system.db  # SQLite 数据库
│   └── uploads/       # 上传文件
├── logs/              # 日志目录
│   ├── access.log     # 访问日志
│   └── error.log      # 错误日志
├── backend/           # 后端代码
├── frontend/          # 前端代码
├── Dockerfile         # Docker 镜像构建
├── docker-compose.yml # Docker 编排
└── .env               # 环境变量配置
```

---

## 运维管理

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs app

# 实时查看日志
docker-compose logs -f app

# 查看最近 100 行
docker-compose logs --tail=100 app
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart app

# 重新构建并启动
docker-compose up -d --build
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（谨慎使用！）
docker-compose down -v
```

### 备份数据

```bash
# 备份数据库
docker-compose exec app tar czf /tmp/data-backup.tar.gz /app/data
docker-compose cp app:/tmp/data-backup.tar.gz ./backups/

# 备份日志
docker-compose exec app tar czf /tmp/logs-backup.tar.gz /app/logs
docker-compose cp app:/tmp/logs-backup.tar.gz ./backups/
```

### 恢复数据

```bash
# 恢复数据库
docker-compose cp ./backups/data-backup.tar.gz app:/tmp/
docker-compose exec app tar xzf /tmp/data-backup.tar.gz -C /
```

### 扩容配置

编辑 `docker-compose.yml`：

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '4.0'      # CPU 限制
          memory: 2G       # 内存限制
        reservations:
          cpus: '1.0'
          memory: 512M
```

---

## 故障排查

### 容器无法启动

```bash
# 查看容器状态
docker-compose ps

# 查看详细日志
docker-compose logs app

# 检查端口占用
sudo netstat -tlnp | grep :8000

# 检查 Docker 服务
sudo systemctl status docker
```

### 数据库连接失败

```bash
# 检查数据库文件
ls -la data/

# 检查文件权限
sudo chown -R 1000:1000 data/

# 重建数据库
docker-compose exec app rm -f /app/data/admission_system.db
docker-compose restart app
```

### API 响应缓慢

```bash
# 查看资源使用
docker stats

# 检查日志中的慢查询
docker-compose logs app | grep "slow"

# 优化数据库
docker-compose exec app sqlite3 /app/data/admission_system.db "VACUUM;"
```

### 内存溢出

```bash
# 增加内存限制
# 编辑 docker-compose.yml，调整 memory 限制

# 重启服务
docker-compose restart app
```

### 常见问题

| 问题 | 解决方案 |
|------|---------|
| 端口被占用 | 修改 `docker-compose.yml` 中的端口映射 |
| 权限错误 | `sudo chown -R 1000:1000 data/ logs/` |
| 数据库锁定 | 重启容器或检查是否有未提交的事务 |
| 日志文件过大 | 配置日志轮转或定期清理 |

---

## 更新升级

### 应用更新

```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose up -d --build

# 验证更新
curl http://localhost/api/health
```

### 数据库迁移

如有数据库结构变更：

```bash
# 备份数据
docker-compose exec app tar czf /tmp/backup.tar.gz /app/data

# 执行迁移
docker-compose exec app python backend/app/migrations.py

# 验证
docker-compose logs app
```

---

## 技术支持

- **文档**: `/docs` (Swagger UI)
- **日志**: `docker-compose logs -f`
- **健康检查**: `http://localhost/api/health`

---

**版本**: v1.0  
**更新日期**: 2026-03-19  
**维护团队**: 大学录取信息整理系统开发组
