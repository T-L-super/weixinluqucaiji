import requests

response = requests.get('http://localhost:8000/')
if response.status_code == 200:
    html = response.text
    
    has_data_source = '数据来源' in html
    has_source_school = '来源学校' in html
    has_th_data_source = '<th>数据来源</th>' in html
    
    print("=== 前端页面检查 ===")
    print(f"页面包含'数据来源': {has_data_source}")
    print(f"页面包含'来源学校': {has_source_school}")
    print(f"表格表头包含'<th>数据来源</th>': {has_th_data_source}")
    
    if has_data_source and not has_source_school and has_th_data_source:
        print("\n修改已生效！")
    else:
        print("\n修改未完全生效")
        
else:
    print(f"请求失败: {response.status_code}")