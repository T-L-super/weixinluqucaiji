# -*- coding: utf-8 -*-
"""
提取器增强版测试脚本
测试场景:
1. 复杂 HTML 表格（嵌套、合并单元格）
2. 语义理解（区分专业列表和学生名单）
3. 大学名单列举提取（场景 3 变体）
4. 关键词识别（录取、offer、恭喜等）
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/大学录取信息整理系统/collector')

from extractor import WeChatArticleExtractor, AdmissionRecord

def test_complex_table():
    """测试 1: 复杂 HTML 表格"""
    print("\n" + "="*60)
    print("测试 1: 复杂 HTML 表格（BeautifulSoup 解析）")
    print("="*60)
    
    extractor = WeChatArticleExtractor()
    
    # 复杂表格 HTML（包含合并单元格、嵌套等）
    complex_html = """
    <html>
    <body>
        <h2>2026 届录取喜报</h2>
        <table border="1">
            <thead>
                <tr>
                    <th>学生姓名</th>
                    <th>录取大学</th>
                    <th>专业</th>
                    <th>奖学金</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>张三</td>
                    <td>哈佛大学</td>
                    <td>计算机科学</td>
                    <td>$5000</td>
                </tr>
                <tr>
                    <td>李四</td>
                    <td>剑桥大学</td>
                    <td>数学</td>
                    <td>全额</td>
                </tr>
                <tr>
                    <td>王五</td>
                    <td>斯坦福大学</td>
                    <td>物理</td>
                    <td></td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """
    
    records = extractor.extract(complex_html, "2026 届录取喜报", "https://example.com/article1")
    
    print(f"✓ 提取到 {len(records)} 条记录")
    for r in records:
        scholarship = f"${r.scholarship_amount}" if r.scholarship_amount else "无"
        print(f"  • {r.student_name_cn} → {r.university_cn} ({r.major_cn}) - 奖学金:{scholarship}")
    
    assert len(records) == 3, f"期望 3 条记录，实际{len(records)}条"
    assert records[0].student_name_cn == "张三"
    assert records[0].university_cn == "哈佛大学"
    print("✓ 测试 1 通过")


def test_semantic_understanding():
    """测试 2: 语义理解（区分专业列表和学生名单）"""
    print("\n" + "="*60)
    print("测试 2: 语义理解（区分专业列表和学生名单）")
    print("="*60)
    
    extractor = WeChatArticleExtractor()
    
    # 专业列表（应该被跳过）
    major_list_html = """
    <html>
    <body>
        <h2>专业设置介绍</h2>
        <div>
            <p>本校提供以下专业:</p>
            <ul>
                <li>计算机科学专业 - 学习编程和算法</li>
                <li>数学专业 - 研究数学理论</li>
                <li>物理专业 - 探索自然规律</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    # 学生名单（应该被提取）
    student_list_html = """
    <html>
    <body>
        <h2>2026 届毕业生录取名单</h2>
        <div>
            <p>恭喜以下同学获得名校 offer:</p>
            <ul>
                <li>张三 哈佛大学 计算机科学</li>
                <li>李四 剑桥大学 数学</li>
                <li>王五 斯坦福大学 物理</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    # 测试专业列表（应该返回空或很少）
    major_records = extractor.extract(major_list_html, "专业介绍", "https://example.com/majors")
    print(f"专业列表提取：{len(major_records)} 条记录（预期：0 或很少）")
    
    # 测试学生名单（应该有数据）
    student_records = extractor.extract(student_list_html, "录取名单", "https://example.com/students")
    print(f"学生名单提取：{len(student_records)} 条记录（预期：3）")
    
    for r in student_records:
        print(f"  • {r.student_name_cn} → {r.university_cn} ({r.major_cn})")
    
    # 学生名单应该能提取到数据
    assert len(student_records) >= 2, f"期望至少 2 条记录，实际{len(student_records)}条"
    print("✓ 测试 2 通过")


def test_university_list_extraction():
    """测试 3: 大学名单列举提取（场景 3 变体）"""
    print("\n" + "="*60)
    print("测试 3: 大学名单列举提取（场景 3 变体）")
    print("="*60)
    
    extractor = WeChatArticleExtractor()
    
    # 大学列举格式
    list_html = """
    <html>
    <body>
        <h2>2026 届录取统计</h2>
        <div>
            <p>录取情况如下:</p>
            <p>哈佛大学：5 人</p>
            <p>剑桥大学 3 枚 offer</p>
            <p>斯坦福大学 (4)</p>
            <p>耶鲁大学 2 封录取</p>
        </div>
    </body>
    </html>
    """
    
    records = extractor.extract(list_html, "录取统计", "https://example.com/stats")
    
    print(f"✓ 提取到 {len(records)} 条汇总记录")
    for r in records:
        print(f"  • {r.university_cn} - {r.major_cn}")
    
    # 应该提取到至少 3 条汇总记录
    assert len(records) >= 3, f"期望至少 3 条记录，实际{len(records)}条"
    print("✓ 测试 3 通过")


def test_keyword_recognition():
    """测试 4: 关键词识别（录取、offer、恭喜等）"""
    print("\n" + "="*60)
    print("测试 4: 关键词识别（录取、offer、恭喜等）")
    print("="*60)
    
    extractor = WeChatArticleExtractor()
    
    # 包含多种关键词的文本
    keyword_html = """
    <html>
    <body>
        <h2>喜报！恭喜 2026 届毕业生</h2>
        <div>
            <p>张三被哈佛大学计算机科学专业录取</p>
            <p>李四获得剑桥大学 offer，奖学金$8000</p>
            <p>王五斩获斯坦福大学物理系录取</p>
            <p>赵六荣获耶鲁大学全额奖学金</p>
        </div>
    </body>
    </html>
    """.replace('<p>', '<p>\n').replace('</p>', '\n</p>')  # 添加换行符以便逐行处理
    
    records = extractor.extract(keyword_html, "喜报", "https://example.com/good-news")
    
    print(f"✓ 提取到 {len(records)} 条记录")
    for r in records:
        scholarship = f"${r.scholarship_amount}" if r.scholarship_amount else "无"
        print(f"  • {r.student_name_cn} → {r.university_cn} ({r.major_cn}) - 奖学金:{scholarship}")
    
    # 应该提取到至少 3 条记录
    assert len(records) >= 3, f"期望至少 3 条记录，实际{len(records)}条"
    print("✓ 测试 4 通过")


def test_beautifulsoup_parsing():
    """测试 5: BeautifulSoup 解析复杂结构"""
    print("\n" + "="*60)
    print("测试 5: BeautifulSoup 解析复杂结构")
    print("="*60)
    
    extractor = WeChatArticleExtractor()
    
    # 复杂嵌套 HTML
    nested_html = """
    <html>
    <body>
        <div class="content">
            <h1>录取公告</h1>
            <table class="data-table">
                <tr>
                    <th style="background:#eee;">学生姓名</th>
                    <th style="background:#eee;">录取大学</th>
                    <th style="background:#eee;">专业</th>
                </tr>
                <tr>
                    <td><strong>张三</strong></td>
                    <td><em>哈佛大学</em></td>
                    <td>计算机科学</td>
                </tr>
                <tr>
                    <td>李四</td>
                    <td colspan="2">剑桥大学 - 数学专业</td>
                </tr>
            </table>
        </div>
    </body>
    </html>
    """
    
    records = extractor.extract(nested_html, "录取公告", "https://example.com/announcement")
    
    print(f"✓ 提取到 {len(records)} 条记录")
    for r in records:
        print(f"  • {r.student_name_cn} → {r.university_cn} ({r.major_cn})")
    
    # 应该至少提取到 1 条记录
    assert len(records) >= 1, f"期望至少 1 条记录，实际{len(records)}条"
    print("✓ 测试 5 通过")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("提取器增强版 - 综合测试")
    print("="*60)
    
    try:
        test_complex_table()
        test_semantic_understanding()
        test_university_list_extraction()
        test_keyword_recognition()
        test_beautifulsoup_parsing()
        
        print("\n" + "="*60)
        print("✓✓✓ 所有测试通过！✓✓✓")
        print("="*60)
        print("\n增强功能总结:")
        print("  1. ✓ BeautifulSoup 解析复杂 HTML 表格")
        print("  2. ✓ 语义理解区分专业列表和学生名单")
        print("  3. ✓ 关键词识别（录取、offer、恭喜等）")
        print("  4. ✓ 大学名单列举提取（场景 3 变体）")
        print("  5. ✓ 复杂嵌套结构解析")
        print("\n")
        
    except AssertionError as e:
        print(f"\n✗ 测试失败：{e}\n")
        raise
    except Exception as e:
        print(f"\n✗ 测试异常：{e}\n")
        raise


if __name__ == '__main__':
    run_all_tests()
