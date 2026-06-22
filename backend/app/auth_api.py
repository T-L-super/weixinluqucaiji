"""
用户认证 API
包含登录、注册、权限验证等功能
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Any
from passlib.context import CryptContext
from app.db_config import get_db_connection, DB_TYPE

router = APIRouter(prefix="/api/auth", tags=["认证"])

pwd_context = CryptContext(schemes=["bcrypt", "sha256_crypt"], deprecated="auto")

ROLE_MAP = {1: "super_admin", 2: "data_admin", 3: "collection_operator", 4: "normal_user"}

# ===== 工具函数 =====

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

def create_access_token(user_id: int, username: str, role: int, expires_delta: timedelta = None):
    """生成访问令牌"""
    import jwt
    from jwt.exceptions import InvalidTokenError
    
    to_encode = {
        "sub": username,
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + (expires_delta or timedelta(hours=24))
    }
    
    # 使用简单的密钥（生产环境应使用更安全的密钥管理）
    SECRET_KEY = "your-secret-key-here-change-in-production"
    ALGORITHM = "HS256"
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request):
    """获取当前登录用户"""
    import jwt
    
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="未提供认证令牌")
    
    # 移除 Bearer 前缀
    if token.startswith("Bearer "):
        token = token[7:]
    
    try:
        SECRET_KEY = "your-secret-key-here-change-in-production"
        ALGORITHM = "HS256"
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: int = payload.get("role")
        
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="无效的令牌")
        
        return {"id": user_id, "username": username, "role": role}
    
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="令牌验证失败")

# ===== API 端点 =====

@router.post("/login")
async def login(request: Request):
    """用户登录"""
    data = await request.json()
    username = data.get("username", "")
    password = data.get("password", "")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="请输入用户名和密码")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    placeholder = "%s" if DB_TYPE == "mysql" else "?"
    cursor.execute(f"SELECT id, username, hashed_password, role_id, is_active FROM users WHERE username = {placeholder}", [username])
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    user = dict(row)
    if user["is_active"] != 1:
        raise HTTPException(status_code=401, detail="用户已被禁用")
    
    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 更新最后登录时间
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = {placeholder}", [user["id"]])
    conn.commit()
    conn.close()
    
    # 生成令牌
    role = user["role_id"]
    access_token = create_access_token(user["id"], user["username"], role)
    
    return {
        "success": True,
        "token": access_token,
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": role,
            "role_id": role,
            "role_name": ROLE_MAP.get(role, "unknown")
        }
    }

@router.post("/logout")
async def logout(request: Request):
    """用户登出"""
    # 在无状态认证中，登出只需客户端丢弃令牌即可
    return {"success": True, "message": "登出成功"}

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "success": True,
        "user": {
            "id": current_user["id"],
            "username": current_user["username"],
            "role": current_user["role"],
            "role_name": ROLE_MAP.get(current_user["role"], "unknown")
        }
    }

@router.post("/change-password")
async def change_password(request: Request, current_user: dict = Depends(get_current_user)):
    """修改密码"""
    data = await request.json()
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")
    
    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="请提供旧密码和新密码")
    
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码长度至少为6位")
    
    # 验证旧密码
    conn = get_db_connection()
    cursor = conn.cursor()
    
    placeholder = "%s" if DB_TYPE == "mysql" else "?"
    cursor.execute(f"SELECT hashed_password FROM users WHERE id = {placeholder}", [current_user["id"]])
    row = cursor.fetchone()
    conn.close()
    
    if not row or not verify_password(old_password, row["hashed_password"] if isinstance(row, dict) else row[0]):
        raise HTTPException(status_code=401, detail="旧密码不正确")
    
    # 更新密码
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET hashed_password = {placeholder}, updated_at = CURRENT_TIMESTAMP WHERE id = {placeholder}", 
                  [get_password_hash(new_password), current_user["id"]])
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "密码修改成功"}
