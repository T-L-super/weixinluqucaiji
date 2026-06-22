from flask import Flask, request, Response
from flask_ngrok import run_with_ngrok
import requests

app = Flask(__name__)
run_with_ngrok(app)

TARGET_URL = "http://localhost:8001"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    url = f"{TARGET_URL}/{path}"
    
    # 获取查询参数
    query_string = request.query_string.decode('utf-8')
    if query_string:
        url += f"?{query_string}"
    
    # 获取请求头
    headers = {key: value for key, value in request.headers.items() 
               if key != 'Host'}
    
    # 获取请求体
    data = request.get_data()
    
    try:
        # 转发请求
        response = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=data,
            allow_redirects=False
        )
        
        # 返回响应
        return Response(
            response.content,
            status=response.status_code,
            headers=dict(response.headers)
        )
    except Exception as e:
        return f"Proxy error: {str(e)}", 500

if __name__ == '__main__':
    app.run()