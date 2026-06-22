import requests

# 测试 API
response = requests.get('http://localhost:8000/api/records?page=1&page_size=5')
if response.status_code == 200:
    data = response.json()
    print("API 响应结构:")
    print(f"所有键: {list(data.keys())}")
    print(f"success: {data.get('success')}")
    print(f"message: {data.get('message')}")
    print(f"total: {data.get('total')}")
    print(f"page: {data.get('page')}")
    print(f"page_size: {data.get('page_size')}")
    print(f"total_pages: {data.get('total_pages')}")
    
    records = data.get('records')
    print(f"\nrecords 字段类型: {type(records)}")
    print(f"records 长度: {len(records) if records else 0}")
    
    if records and len(records) > 0:
        first_record = records[0]
        print(f"\n第一条记录的字段: {list(first_record.keys())}")
        print(f"ID: {first_record.get('id')}")
        print(f"学生姓名: {first_record.get('student_name_cn')}")
        print(f"数据来源: {first_record.get('data_source')}")
        print(f"国家: {first_record.get('country')}")
        print(f"录取大学: {first_record.get('university_cn')}")
        print(f"专业: {first_record.get('major_cn')}")
else:
    print(f"API 请求失败: {response.status_code}")
    print(response.text)