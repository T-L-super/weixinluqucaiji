import requests

response = requests.get('http://localhost:8000/api/records?page=1&page_size=3')
if response.status_code == 200:
    data = response.json()
    records = data.get('records', [])
    
    print("API 返回的数据:")
    print(f"总记录数: {data.get('total', 0)}")
    print(f"返回记录数: {len(records)}")
    
    for i, record in enumerate(records):
        print(f"\n记录 {i+1}:")
        print(f"  ID: {record.get('id')}")
        print(f"  学生姓名: {record.get('student_name_cn')}")
        print(f"  数据来源: '{record.get('data_source')}'")
        print(f"  国家: {record.get('country')}")
        print(f"  录取大学: {record.get('university_cn')}")
        
else:
    print(f"请求失败: {response.status_code}")