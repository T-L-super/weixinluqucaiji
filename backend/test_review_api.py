import requests

response = requests.get('http://localhost:8000/api/review/pending?page=1&page_size=3')
if response.status_code == 200:
    data = response.json()
    records = data.get('records', [])
    
    print("审核 API 返回的数据:")
    print(f"总记录数: {data.get('total', 0)}")
    print(f"返回记录数: {len(records)}")
    
    if records and len(records) > 0:
        first_record = records[0]
        print(f"\n第一条记录的字段: {list(first_record.keys())}")
        print(f"ID: {first_record.get('id')}")
        print(f"学生姓名: {first_record.get('student_name_cn')}")
        print(f"数据来源: '{first_record.get('data_source')}'")
        print(f"国家: {first_record.get('country')}")
        print(f"录取大学: {first_record.get('university_cn')}")
        
else:
    print(f"请求失败: {response.status_code}")
    print(response.text)