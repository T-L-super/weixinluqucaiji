#!/usr/bin/env python3
"""角色权限升级脚本 - 2026-05-15
- 超级管理员 → 系统管理员
- 管理员 → 数据管理员
- 新增：采集操作员
- 更新各角色权限定义
"""
import sqlite3, json

DB_PATH = "/root/.openclaw/workspace/大学录取信息整理系统/data/admission_system.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 更新角色名称
c.execute("UPDATE roles SET description='系统管理员' WHERE name='super_admin'")
c.execute("UPDATE roles SET description='数据管理员' WHERE name='data_admin'")

# 新增采集操作员
c.execute("SELECT id FROM roles WHERE name='collection_operator'")
if not c.fetchone():
    c.execute("INSERT INTO roles (name, description, permissions) VALUES (?, ?, ?)",
              ('collection_operator', '采集操作员', json.dumps(["records","tasks","stats"])))
    print("  ✅ 新增角色: 采集操作员")
else:
    c.execute("UPDATE roles SET description='采集操作员' WHERE name='collection_operator'")
    print("  ✅ 更新角色: 采集操作员")

# 更新权限定义
c.execute("UPDATE roles SET permissions=? WHERE name='super_admin'", (json.dumps(["*"]),))
c.execute("UPDATE roles SET permissions=? WHERE name='data_admin'", (json.dumps(["records","tasks","review","stats"]),))
c.execute("UPDATE roles SET permissions=? WHERE name='collection_operator'", (json.dumps(["records","tasks","stats"]),))
c.execute("UPDATE roles SET permissions=? WHERE name='normal_user'", (json.dumps(["records","stats"]),))

# 验证
c.execute("SELECT id, name, description, permissions FROM roles ORDER BY id")
print("\n📋 当前角色表:")
for row in c.fetchall():
    print(f"  ID={row[0]} | {row[1]} | {row[2]} | perms={row[3]}")

conn.commit()
conn.close()
print("\n✅ 角色权限迁移完成！")
