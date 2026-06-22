# 完成时间：2026-03-19 00:30 UTC
"""
大学录取信息整理系统 - 采集器测试
测试数据采集模块的功能
"""
import pytest
import sys
import os
import json
import tempfile
import sqlite3

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))

from collector import AdmissionCollector, create_collector


@pytest.fixture
def collector():
    """创建测试用采集器"""
    # 创建临时数据库
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    collector = AdmissionCollector(temp_db.name)
    
    # 初始化数据库表
    conn = collector.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admission_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            student_id TEXT UNIQUE NOT NULL,
            university TEXT NOT NULL,
            major TEXT NOT NULL,
            admission_type TEXT,
            score REAL,
            province TEXT,
            year INTEGER,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    
    yield collector
    
    # 清理临时数据库
    if os.path.exists(temp_db.name):
        os.remove(temp_db.name)


@pytest.fixture
def sample_records():
    """示例录取记录列表"""
    return [
        {
            "student_name": "张三",
            "student_id": "2026001",
            "university": "北京大学",
            "major": "计算机科学",
            "admission_type": "统招",
            "score": 650.5,
            "province": "北京",
            "year": 2026,
            "status": "confirmed"
        },
        {
            "student_name": "李四",
            "student_id": "2026002",
            "university": "清华大学",
            "major": "物理学",
            "admission_type": "统招",
            "score": 680.0,
            "province": "上海",
            "year": 2026,
            "status": "pending"
        },
        {
            "student_name": "王五",
            "student_id": "2026003",
            "university": "复旦大学",
            "major": "数学",
            "admission_type": "自主招生",
            "score": 670.5,
            "province": "浙江",
            "year": 2026,
            "status": "confirmed"
        }
    ]


class TestTextParsing:
    """文本解析测试"""
    
    def test_parse_simple_text(self, collector):
        """测试解析简单文本"""
        text = "张三，学号：2026001，北京大学计算机专业"
        records = collector.parse_admission_text(text)
        
        assert len(records) == 1
        assert records[0]["student_name"] == "张三"
        assert records[0]["student_id"] == "2026001"
        assert records[0]["university"] == "北京大学"
        assert records[0]["major"] == "计算机"
    
    def test_parse_multiple_records(self, collector):
        """测试解析多条记录"""
        text = "张三，学号：2026001，北京大学计算机专业；李四，学号：2026002，清华大学物理专业"
        records = collector.parse_admission_text(text)
        
        assert len(records) == 2
        assert records[0]["student_name"] == "张三"
        assert records[1]["student_name"] == "李四"
    
    def test_parse_pipe_separated(self, collector):
        """测试解析管道符分隔的文本"""
        text = "张三 | 2026001 | 北京大学 | 计算机专业"
        records = collector.parse_admission_text(text)
        
        assert len(records) == 1
        assert records[0]["student_name"] == "张三"
        assert records[0]["student_id"] == "2026001"
    
    def test_parse_empty_text(self, collector):
        """测试解析空文本"""
        records = collector.parse_admission_text("")
        assert len(records) == 0
    
    def test_parse_invalid_text(self, collector):
        """测试解析无效文本"""
        text = "这是一段没有录取信息的普通文本"
        records = collector.parse_admission_text(text)
        assert len(records) == 0


class TestBatchImport:
    """批量导入测试"""
    
    def test_batch_import_success(self, collector, sample_records):
        """测试批量导入成功"""
        result = collector.batch_import(sample_records)
        
        assert result["success"] == 3
        assert result["failed"] == 0
        assert result["duplicate"] == 0
        assert result["total"] == 3
    
    def test_batch_import_with_duplicates(self, collector, sample_records):
        """测试批量导入包含重复记录"""
        # 第一次导入
        collector.batch_import(sample_records)
        
        # 再次导入相同的记录
        result = collector.batch_import(sample_records)
        
        assert result["success"] == 0
        assert result["duplicate"] == 3
    
    def test_batch_import_partial_duplicates(self, collector, sample_records):
        """测试批量导入部分重复"""
        # 先导入前两条
        collector.batch_import(sample_records[:2])
        
        # 再导入全部三条
        result = collector.batch_import(sample_records)
        
        assert result["success"] == 1  # 只有第三条是新记录
        assert result["duplicate"] == 2  # 前两条是重复的
    
    def test_batch_import_empty_list(self, collector):
        """测试批量导入空列表"""
        result = collector.batch_import([])
        assert result["success"] == 0
        assert result["total"] == 0


class TestExport:
    """导出功能测试"""
    
    def test_export_json(self, collector, sample_records):
        """测试导出为 JSON"""
        # 先导入数据
        collector.batch_import(sample_records)
        
        # 导出到临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        temp_file.close()
        
        try:
            output_path = collector.export_records(temp_file.name, format="json")
            
            assert os.path.exists(output_path)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert len(data) == 3
            assert data[0]["student_name"] == "王五"  # 按创建时间倒序
        finally:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)
    
    def test_export_csv(self, collector, sample_records):
        """测试导出为 CSV"""
        # 先导入数据
        collector.batch_import(sample_records)
        
        # 导出到临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        temp_file.close()
        
        try:
            output_path = collector.export_records(temp_file.name, format="csv")
            
            assert os.path.exists(output_path)
            
            with open(output_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            
            assert len(lines) == 4  # 标题行 + 3 条数据
            assert "student_name" in lines[0]
        finally:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)
    
    def test_export_invalid_format(self, collector, sample_records):
        """测试导出无效格式"""
        collector.batch_import(sample_records)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        temp_file.close()
        
        try:
            # 应该使用默认格式或抛出异常
            output_path = collector.export_records(temp_file.name, format="invalid")
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)


class TestStatistics:
    """统计功能测试"""
    
    def test_get_statistics_empty(self, collector):
        """测试空数据库的统计"""
        stats = collector.get_statistics()
        
        assert stats["total"] == 0
        assert stats["by_status"] == {}
        assert stats["by_university"] == {}
    
    def test_get_statistics_with_data(self, collector, sample_records):
        """测试有数据时的统计"""
        collector.batch_import(sample_records)
        
        stats = collector.get_statistics()
        
        assert stats["total"] == 3
        assert "confirmed" in stats["by_status"]
        assert "pending" in stats["by_status"]
        assert "北京大学" in stats["by_university"]
        assert "清华大学" in stats["by_university"]
        assert "复旦大学" in stats["by_university"]
        assert "generated_at" in stats
    
    def test_get_statistics_by_year(self, collector, sample_records):
        """测试按年份统计"""
        collector.batch_import(sample_records)
        
        stats = collector.get_statistics()
        
        assert "2026" in stats["by_year"]
        assert stats["by_year"]["2026"] == 3


class TestCleanup:
    """清理功能测试"""
    
    def test_cleanup_duplicates(self, collector, sample_records):
        """测试清理重复记录"""
        # 导入原始数据
        collector.batch_import(sample_records)
        
        # 手动添加重复记录
        conn = collector.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO admission_records (student_name, student_id, university, major, status)
            VALUES (?, ?, ?, ?, ?)
        ''', ["张三重复", "2026001", "北京大学", "计算机", "pending"])
        conn.commit()
        conn.close()
        
        # 清理重复
        deleted_count = collector.cleanup_duplicates()
        
        assert deleted_count == 1
        
        # 验证只剩一条
        stats = collector.get_statistics()
        assert stats["total"] == 3
    
    def test_cleanup_no_duplicates(self, collector, sample_records):
        """测试没有重复记录时的清理"""
        collector.batch_import(sample_records)
        
        deleted_count = collector.cleanup_duplicates()
        assert deleted_count == 0


class TestCollectorCreation:
    """采集器创建测试"""
    
    def test_create_collector_function(self):
        """测试 create_collector 函数"""
        collector = create_collector()
        assert isinstance(collector, AdmissionCollector)
    
    def test_create_collector_with_db_path(self):
        """测试指定数据库路径创建采集器"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            collector = create_collector(temp_db.name)
            assert isinstance(collector, AdmissionCollector)
        finally:
            if os.path.exists(temp_db.name):
                os.remove(temp_db.name)


class TestEdgeCases:
    """边界情况测试"""
    
    def test_parse_special_characters(self, collector):
        """测试解析包含特殊字符的文本"""
        text = "张三 - 测试，学号：2026-001，北京大学 (计算机) 专业"
        records = collector.parse_admission_text(text)
        # 应该能处理或返回空
        assert isinstance(records, list)
    
    def test_parse_very_long_text(self, collector):
        """测试解析很长的文本"""
        text = "张三，学号：2026001，北京大学计算机专业" * 100
        records = collector.parse_admission_text(text)
        assert len(records) == 100
    
    def test_batch_import_large_dataset(self, collector):
        """测试批量导入大量数据"""
        large_dataset = [
            {
                "student_name": f"学生{i}",
                "student_id": f"2026{i:04d}",
                "university": "测试大学",
                "major": "测试专业",
                "year": 2026
            }
            for i in range(100)
        ]
        
        result = collector.batch_import(large_dataset)
        assert result["success"] == 100
        assert result["total"] == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
