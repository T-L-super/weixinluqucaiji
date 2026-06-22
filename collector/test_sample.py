# -*- coding: utf-8 -*-
"""
测试文本格式提取器 - 使用示例文本测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extractor import WeChatArticleExtractor


def test_sample_data():
    """测试样本数据"""
    extractor = WeChatArticleExtractor()
    
    # 测试文本 - 模拟微信文章内容
    test_htmls = [
        # 格式 1: 空格分隔
        """
        <html><body>
        <p>2026 届录取喜报</p>
        <div>
            张三 哈佛大学 计算机科学<br>
            李华 斯坦福大学 电子工程<br>
            王芳 耶鲁大学 经济学
        </div>
        </body></html>
        """,
        
        # 格式 2: "被...录取"句式
        """
        <html><body>
        <p>恭喜以下同学：</p>
        <div>
            李明被剑桥大学数学专业录取<br>
            赵雷被牛津大学物理专业录取<br>
            陈静被帝国理工学院计算机专业录取
        </div>
        </body></html>
        """,
        
        # 格式 3: 含奖学金
        """
        <html><body>
        <p>录取佳绩：</p>
        <div>
            王芳 获得耶鲁大学 每年$5000 奖学金<br>
            刘强 斩获麻省理工学院 全额奖学金<br>
            周婷 拿到哥伦比亚大学 每年 3000 美元奖学金
        </div>
        </body></html>
        """,
        
        # 格式 4: 列表格式
        """
        <html><body>
        <ul>
            <li>吴京 普林斯顿大学</li>
            <li>郑爽 加州伯克利</li>
            <li>• 孙杨 多伦多大学</li>
        </ul>
        </body></html>
        """,
        
        # 格式 5: 混合格式
        """
        <html><body>
        <p>2026 届毕业班录取结果：</p>
        <div>
            张三 哈佛大学 计算机科学<br>
            李华被斯坦福大学电子工程专业录取<br>
            王芳 获得耶鲁大学 每年$5000 奖学金<br>
            • 赵敏 剑桥大学 数学<br>
            钱伟 麻省理工学院 物理专业
        </div>
        </body></html>
        """
    ]
    
    print("="*60)
    print("文本格式提取器 - 样本测试")
    print("="*60)
    
    total_records = 0
    
    for i, html in enumerate(test_htmls, 1):
        print(f"\n【测试 {i}】")
        print("-"*60)
        
        records = extractor.extract(html, article_title="2026 届录取喜报")
        
        print(f"提取到 {len(records)} 条记录:")
        for record in records:
            print(f"  • {record.student_name_cn} - {record.university_cn}", end="")
            if record.major_cn:
                print(f" - {record.major_cn}", end="")
            if record.scholarship_amount:
                print(f" (${record.scholarship_amount})", end="")
            print()
        
        total_records += len(records)
    
    print(f"\n{'='*60}")
    print(f"总计：{total_records} 条记录")
    print(f"{'='*60}")
    
    if total_records >= 3:
        print("✅ 测试通过！至少提取到 3 条记录")
        return True
    else:
        print(f"⚠️ 测试未达标：仅提取到 {total_records} 条记录")
        return False


if __name__ == '__main__':
    success = test_sample_data()
    sys.exit(0 if success else 1)
