# 微信录取信息采集系统

基于 FastAPI 的大学录取信息整理系统，支持从微信公众号文章中批量采集录取数据。

## 功能特性

- **数据采集**: 从微信文章链接批量提取录取信息
- **数据管理**: 录取记录的增删改查、批量操作
- **数据统计**: 按国家、大学、专业等维度统计
- **用户权限**: 支持多角色用户系统
- **数据导出**: 支持 Excel/CSV 格式导出

## 技术栈

- **后端**: FastAPI + Uvicorn
- **数据库**: SQLite（开发）/ MySQL（生产）
- **前端**: 原生 HTML/CSS/JavaScript

## 快速开始

### 1. 安装依赖

```bash
cd weixinluqucaiji
pip install -r backend/requirements.txt
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件，修改必要的配置
```

### 3. 初始化数据库

```bash
python backend/data/init_db.py
```

### 4. 启动服务

```bash
python backend/run.py
```

服务启动后访问 http://localhost:8001

## 项目结构

```
weixinluqucaiji/
├── backend/
│   ├── app/              # 核心应用代码
│   ├── api/              # API 模块
│   ├── data/             # 数据文件和数据库
│   ├── collector/        # 采集模块
│   └── ...
├── database/             # 数据库脚本
├── frontend/             # 前端资源
└── ...
```

## 默认账号

- 用户名: admin
- 密码: 需通过 API 或直接修改数据库设置

## API 文档

启动服务后访问 http://localhost:8001/docs 查看完整的 API 文档。

## 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| / | GET | 管理后台首页 |
| /api/records | GET/POST | 录取记录管理 |
| /api/collection-tasks | GET/POST | 采集任务管理 |
| /api/stats/overview | GET | 数据统计概览 |
| /api/records/export | GET | 导出数据 |
