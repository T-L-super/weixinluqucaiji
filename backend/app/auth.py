# 完成时间：2026-03-20 15:45 UTC - Agent-10 用户权限管理
"""
用户认证与权限管理模块
支持 JWT Token 认证，三种角色权限控制：
- 超级管理员：全部权限
- 数据管理员：数据管理权限
- 普通用户：只读权限
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# JWT 配置
SECRET_KEY = "your-secret-key-change-in-production-2026"  # 生产环境请更改
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小时过期

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 认证
security = HTTPBearer(auto_error=False)


def get_db_connection():
    """获取数据库连接"""
    from app.db_config import get_db_connection as _get_db
    return _get_db()


def get_placeholder():
    """获取数据库占位符"""
    from app.db_config import DB_TYPE
    return "%s" if DB_TYPE == "mysql" else "?"


def init_auth_tables():
    """初始化用户认证相关表 - 兼容 MySQL 和 SQLite"""
    from app.db_config import DB_TYPE
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 根据数据库类型选择占位符
    placeholder = get_placeholder()
    
    # 初始化默认角色（如果不存在）
    default_roles = [
        ('super_admin', '系统管理员', '["*"]'),  # 全部权限
        ('data_admin', '数据管理员', '["read", "write", "delete", "manage_users"]'),  # 数据管理权限
        ('collection_operator', '采集操作员', '["read", "write"]'),  # 采集操作权限
        ('normal_user', '普通用户', '["read"]')  # 只读权限
    ]
    
    for role_name, description, permissions in default_roles:
        cursor.execute(f'SELECT id FROM roles WHERE name = {placeholder}', (role_name,))
        if not cursor.fetchone():
            cursor.execute(
                f'INSERT INTO roles (name, description, permissions) VALUES ({placeholder}, {placeholder}, {placeholder})',
                (role_name, description, permissions)
            )
    
    # 创建默认超级管理员账户（如果不存在）
    cursor.execute(f'SELECT id FROM users WHERE username = {placeholder}', ('admin',))
    if not cursor.fetchone():
        # 默认密码：admin123
        password_hash = pwd_context.hash("admin123")
        # MySQL 使用 hashed_password 字段名
        if DB_TYPE == "mysql":
            cursor.execute(
                f'INSERT INTO users (username, email, hashed_password, full_name, role_id) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})',
                ('admin', 'admin@beiyouschool.com', password_hash, '系统管理员', 1)
            )
        else:
            cursor.execute(
                f'INSERT INTO users (username, email, password_hash, full_name, role_id) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})',
                ('admin', 'admin@beiyouschool.com', password_hash, '系统管理员', 1)
            )
    
    conn.commit()
    conn.close()
    print("[OK] 用户认证表初始化完成")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Access Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """解码 JWT Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """认证用户"""
    from app.db_config import DB_TYPE
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    placeholder = get_placeholder()
    # MySQL 使用 hashed_password 字段名
    password_field = "hashed_password" if DB_TYPE == "mysql" else "password_hash"
    
    cursor.execute(
        f'''SELECT u.id, u.username, u.email, u.{password_field}, u.full_name, u.role_id, u.is_active,
                  r.name as role_name, r.permissions as role_permissions
           FROM users u
           LEFT JOIN roles r ON u.role_id = r.id
           WHERE u.username = {placeholder}''',
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    
    if not user or not verify_password(password, user[password_field]):
        return None
    
    if not user["is_active"]:
        return None
    
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role_id": user["role_id"],
        "role_name": user["role_name"],
        "permissions": user["role_permissions"] or "[]"
    }


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """通过 ID 获取用户信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    placeholder = get_placeholder()
    cursor.execute(
        f'''SELECT u.id, u.username, u.email, u.full_name, u.role_id, u.is_active,
                  r.name as role_name, r.permissions as role_permissions
           FROM users u
           LEFT JOIN roles r ON u.role_id = r.id
           WHERE u.id = {placeholder}''',
        (user_id,)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role_id": user["role_id"],
            "role_name": user["role_name"],
            "permissions": user["role_permissions"] or "[]",
            "is_active": bool(user["is_active"])
        }
    return None


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """通过用户名获取用户信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    placeholder = get_placeholder()
    cursor.execute(
        f'''SELECT u.id, u.username, u.email, u.full_name, u.role_id, u.is_active,
                  r.name as role_name, r.permissions as role_permissions
           FROM users u
           LEFT JOIN roles r ON u.role_id = r.id
           WHERE u.username = {placeholder}''',
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role_id": user["role_id"],
            "role_name": user["role_name"],
            "permissions": user["role_permissions"] or "[]",
            "is_active": bool(user["is_active"])
        }
    return None


def create_user(username: str, password: str, email: str = None, full_name: str = None, role_id: int = 3) -> Dict[str, Any]:
    """创建新用户"""
    from app.db_config import DB_TYPE
    import pymysql
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = get_password_hash(password)
        placeholder = get_placeholder()
        # MySQL 使用 hashed_password 字段名
        password_field = "hashed_password" if DB_TYPE == "mysql" else "password_hash"
        
        cursor.execute(
            f'''INSERT INTO users (username, email, {password_field}, full_name, role_id)
               VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})''',
            (username, email, password_hash, full_name, role_id)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return get_user_by_id(user_id)
    except (pymysql.IntegrityError, Exception) as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"用户名或邮箱已存在：{str(e)}")


def update_user_role(user_id: int, role_id: int) -> bool:
    """更新用户角色"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    placeholder = get_placeholder()
    cursor.execute(f'UPDATE users SET role_id = {placeholder} WHERE id = {placeholder}', (role_id, user_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    return affected > 0


def deactivate_user(user_id: int) -> bool:
    """停用用户"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    placeholder = get_placeholder()
    cursor.execute(f'UPDATE users SET is_active = 0 WHERE id = {placeholder}', (user_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    return affected > 0


def activate_user(user_id: int) -> bool:
    """激活用户"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    placeholder = get_placeholder()
    cursor.execute(f'UPDATE users SET is_active = 1 WHERE id = {placeholder}', (user_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    return affected > 0


def get_all_users() -> list:
    """获取所有用户列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        '''SELECT u.id, u.username, u.email, u.full_name, u.role_id, u.is_active, u.last_login, u.created_at,
                  r.name as role_name
           FROM users u
           LEFT JOIN roles r ON u.role_id = r.id
           ORDER BY u.created_at DESC'''
    )
    users = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role_id": user["role_id"],
            "role_name": user["role_name"],
            "is_active": bool(user["is_active"]),
            "last_login": user["last_login"],
            "created_at": user["created_at"]
        }
        for user in users
    ]


def get_all_roles() -> list:
    """获取所有角色列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, description, permissions FROM roles ORDER BY id')
    roles = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": role["id"],
            "name": role["name"],
            "description": role["description"],
            "permissions": role["permissions"] or "[]"
        }
        for role in roles
    ]


def has_permission(user: Dict[str, Any], required_permission: str) -> bool:
    """检查用户是否有指定权限"""
    import json
    try:
        permissions = json.loads(user.get("permissions", "[]"))
        # 超级管理员拥有所有权限
        if "*" in permissions:
            return True
        return required_permission in permissions
    except (json.JSONDecodeError, TypeError):
        return False


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """获取当前认证用户"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_id(int(user_id))
    if not user or not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已停用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def require_permission(required_permission: str):
    """权限要求装饰器"""
    async def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if not has_permission(current_user, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要：{required_permission}"
            )
        return current_user
    return permission_checker


def update_last_login(user_id: int):
    """更新最后登录时间"""
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()
    cursor.execute(f'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = {placeholder}', (user_id,))
    conn.commit()
    conn.close()


# 初始化认证表
init_auth_tables()


def delete_user(user_id: int) -> bool:
    """删除用户"""
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()
    cursor.execute(f'DELETE FROM users WHERE id = {placeholder}', (user_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0
