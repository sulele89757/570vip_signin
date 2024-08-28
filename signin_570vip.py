"""
任务名称
name: 570vip签到脚本
定时规则
cron: 11 9 * * *
"""

# 第一步：获取oauth2 code
# 获取oauth2 code http://www.570vip.com/wp-json/b2/v1/getRecaptcha
# headers
# Referer:http://www.570vip.com/guohua/1107/68.html
# User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36
# Accept:application/json, text/plain, */*
# Accept-Encoding:gzip, deflate
# Accept-Language:zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6
# Origin:http://www.570vip.com
# Pragma:no-cache
# 响应值中有个token，就是我们需要的code

# 第二步：用code换取token
# 用code换取token http://www.570vip.com/wp-json/jwt-auth/v1/token
# headers
# Referer:http://www.570vip.com/guohua/1107/68.html
# User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36
# Accept:application/json, text/plain, */*
# Accept-Encoding:gzip, deflate
# Accept-Language:zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6
# Origin:http://www.570vip.com
# Pragma:no-cache

# body
# username:sulele89757
# password:8848@kok
# token: 上一步获取到的token

# 响应值中有个token，就是我们需要的token

# 进行签到
# http://www.570vip.com/wp-json/b2/v1/userMission
# headers
# Authorization:Bearer {登录拿到的token}
# Cookie:b2_token={登录拿到的token}; order_id=E820149517740389; b2_back_url=http://www.570vip.com/vips; wordpress_test_cookie=WP%20Cookie%20check
# Referer:http://www.570vip.com/guohua/1107/68.html
# User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36
# Accept:application/json, text/plain, */*
# Accept-Encoding:gzip, deflate
# Accept-Language:zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6
# Origin:http://www.570vip.com
# Pragma:no-cache

# 得到类似下面的响应，就说明签到成功
# {
#     "date": "2024-08-21 08:39:14",
#     "credit": 193,
#     "mission": {
#         "date": "2024-08-21 08:39:14",
#         "credit": "193",
#         "always": "3",
#         "tk": {
#             "days": 0,
#             "credit": 0,
#             "bs": 3
#         },
#         "my_credit": "283",
#         "current_user": 6
#     }
# }

import json
import requests
import notify

# 配置日志
# logging.basicConfig(filename='sign_in.log', level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s',
#                     encoding='utf-8')

# 配置
BASE_URL = "http://www.570vip.com"
OAUTH2_CODE_URL = "/wp-json/b2/v1/getRecaptcha"
TOKEN_URL = "/wp-json/jwt-auth/v1/token"
SIGN_IN_URL = "/wp-json/b2/v1/userMission"
TOKEN_CACHE_FILE = "token_cache.json"

HEADERS = {
    "Referer": "http://www.570vip.com/mission/today",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
    "Origin": "http://www.570vip.com",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Referer-Policy": "strict-origin-when-cross-origin"
}

# 尝试从缓存文件中读取token
def get_cached_token():
    try:
        with open(TOKEN_CACHE_FILE, 'r') as f:
            data = json.load(f)
            return data.get('token')
    except FileNotFoundError:
        return None

# 缓存token到文件
def cache_token(token):
    with open(TOKEN_CACHE_FILE, 'w') as f:
        json.dump({'token': token}, f)

# 获取oauth2 code
def get_oauth2_code():
    response = requests.post(BASE_URL + OAUTH2_CODE_URL, headers=HEADERS)
    response.raise_for_status()
    return response.json().get('token')  # 假设响应中token字段就是code

# 用code换取token
def get_token_with_code(code):
    data = {
        "username": "sulele89757",
        "password": "8848@kok",
        "token": code
    }
    response = requests.post(BASE_URL + TOKEN_URL, headers=HEADERS, data=data)
    response.raise_for_status()
    return response.json().get('token')

# 进行签到
# 响应值中有个code，如果是user_error，说明需要先登录
# {
#     "code": "user_error",
#     "message": "请先登录",
#     "data": {
#         "status": 403
#     }
# }
def sign_in(token):
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    headers[
        "Cookie"] = f"b2_token={token};"

    try:
        print("开始签到...")
        sign_url = BASE_URL + SIGN_IN_URL
        print("签到URL: ", sign_url)
        response = requests.post(sign_url, headers=headers)
        response.raise_for_status()
        print("签到状态码: ", response.status_code)
        data = response.json()
        print("签到响应: ", data)
        # 检查响应中的 code 字段
        if data.get('code') == 'user_error':
            # 如果 code 是 user_error，重新获取token
            print("需要重新登录...")
            code = get_oauth2_code()
            token = get_token_with_code(code)
            cache_token(token)
            return sign_in(token)

        return data

    except requests.exceptions.HTTPError as e:
        # 处理 HTTP 错误
        print(f"签到失败: ", str(e))
        return str(e)
    except requests.exceptions.RequestException as e:
        # 处理其他类型的请求异常
        print(f"签到失败: ", str(e))
        return str(e)
    except Exception as e:
        # 处理其他异常
        print(f"签到失败: ", str(e))
        return str(e)


def main():
    token = get_cached_token()
    print("缓存的token: ", token)
    if not token:
        code = get_oauth2_code()
        token = get_token_with_code(code)
        cache_token(token)
        print("获取新的token: ", token)
    response = sign_in(token)
    print("签到结果:", response)
    # notify.send("570vip签到结果", response)

if __name__ == "__main__":
    main()