# 完成时间：2026-03-19 02:30 UTC
"""
大学录取信息整理系统 - API 测试
使用简单测试设置，避免数据库锁定问题
"""
import pytest
import sys
import os
import tempfile
import sqlite3

# 创建全局测试数据库
TEST_DB_FD, TEST_DB_PATH = tempfile.mkstemp(suffix='.db')
os.close(TEST_DB_FD)
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["DATA_DIR"] = os.path.dirname(TEST_DB_PATH)

# 添加项目路径
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
app_path = os.path.join(backend_path, 'app')
sys.path.insert(0, backend_path)
sys.path.insert(0, app_path)

from fastapi.testclient import TestClient
from app.main import app, init_db, DATA_DIR, get_db_connection
import json


def clear_db():
    """清空数据库"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admission_records")
        cursor.execute("DELETE FROM tasks")
        conn.commit()
        conn.close()
    except:
        pass


@pytest.fixture(scope="module")
def client():
    """创建测试客户端"""
    init_db()
    with TestClient(app) as test_client:
        yield test_client
    # 清理
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except:
            pass


@pytest.fixture(autouse=True)
def setup_teardown():
    """每个测试前后清空数据库"""
    clear_db()
    yield
    clear_db()


@pytest.fixture
def sample_record():
    return {
        "student_name": "张三",
        "student_id": "2026001",
        "university": "北京大学",
        "major": "计算机科学",
        "admission_type": "统招",
        "score": 650.5,
        "province": "北京",
        "year": 2026,
        "status": "confirmed",
        "notes": "测试数据"
    }


class TestHealthCheck:
    def test_health_endpoint(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestRecordsAPI:
    def test_create_record(self, client, sample_record):
        response = client.post("/api/records", json=sample_record)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["message"] == "记录创建成功"
        assert data["record"]["student_name"] == "张三"
    
    def test_create_record_duplicate(self, client, sample_record):
        client.post("/api/records", json=sample_record)
        response = client.post("/api/records", json=sample_record)
        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]
    
    def test_create_record_missing_fields(self, client):
        response = client.post("/api/records", json={"student_name": "李四"})
        assert response.status_code == 400
    
    def test_get_record(self, client, sample_record):
        create_response = client.post("/api/records", json=sample_record)
        record_id = create_response.json()["record"]["id"]
        response = client.get(f"/api/records/{record_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["student_name"] == "张三"
    
    def test_get_record_not_found(self, client):
        response = client.get("/api/records/99999")
        assert response.status_code == 404
    
    def test_update_record(self, client, sample_record):
        create_response = client.post("/api/records", json=sample_record)
        record_id = create_response.json()["record"]["id"]
        update_data = {"score": 680.0}
        response = client.put(f"/api/records/{record_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "记录更新成功"
    
    def test_update_record_not_found(self, client):
        response = client.put("/api/records/99999", json={"score": 680.0})
        assert response.status_code == 404
    
    def test_delete_record(self, client, sample_record):
        create_response = client.post("/api/records", json=sample_record)
        record_id = create_response.json()["record"]["id"]
        response = client.delete(f"/api/records/{record_id}")
        assert response.status_code == 200
        get_response = client.get(f"/api/records/{record_id}")
        assert get_response.status_code == 404
    
    def test_get_records_list(self, client, sample_record):
        for i in range(5):
            record = sample_record.copy()
            record["student_id"] = f"202600{i+1}"
            client.post("/api/records", json=record)
        response = client.get("/api/records")
        assert response.status_code == 200
        data = response.json()
        assert "records" in data
        assert len(data["records"]) > 0
    
    def test_get_records_pagination(self, client, sample_record):
        for i in range(25):
            record = sample_record.copy()
            record["student_id"] = f"20260{i+1:03d}"
            client.post("/api/records", json=record)
        response = client.get("/api/records?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["records"]) == 10
    
    def test_get_records_filter_by_status(self, client, sample_record):
        record1 = sample_record.copy()
        record1["student_id"] = "2026101"
        record1["status"] = "confirmed"
        client.post("/api/records", json=record1)
        record2 = sample_record.copy()
        record2["student_id"] = "2026102"
        record2["status"] = "pending"
        client.post("/api/records", json=record2)
        response = client.get("/api/records?status=confirmed")
        assert response.status_code == 200
        data = response.json()
        for record in data["records"]:
            assert record["status"] == "confirmed"


class TestTasksAPI:
    def test_create_task(self, client):
        response = client.post("/api/tasks", json={"task_type": "data_import"})
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "任务创建成功"
    
    def test_create_task_missing_type(self, client):
        response = client.post("/api/tasks", json={"description": "测试"})
        assert response.status_code == 400
    
    def test_get_tasks(self, client):
        client.post("/api/tasks", json={"task_type": "test_task"})
        response = client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data


class TestRootEndpoint:
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200


class TestSPA:
    def test_unknown_route(self, client):
        response = client.get("/unknown/path")
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
