import json
import time
import requests

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
def get_oauth2_code(session):
    response = session.post(BASE_URL + OAUTH2_CODE_URL, headers=HEADERS)
    response.raise_for_status()
    return response.json().get('token')  # 假设响应中token字段就是code

# 用code换取token
def get_token_with_code(session, code):
    data = {
        "username": "sulele89757",
        "password": "8848@kok",
        "token": code
    }
    response = session.post(BASE_URL + TOKEN_URL, headers=HEADERS, data=data)
    response.raise_for_status()
    return response.json().get('token')

# 进行签到
def sign_in(session, token):
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    headers["Cookie"] = f"b2_token={token};"

    try:
        print("开始签到...")
        sign_url = BASE_URL + SIGN_IN_URL
        print("签到URL: ", sign_url)
        response = session.post(sign_url, headers=headers)
        response.raise_for_status()
        print("签到状态码: ", response.status_code)
        data = response.json()
        print("签到响应: ", data)
        # 检查响应中的 code 字段
        if data.get('code') == 'user_error':
            # 如果 code 是 user_error，重新获取token
            print("需要重新登录...")
            code = get_oauth2_code(session)
            token = get_token_with_code(session, code)
            cache_token(token)
            return sign_in(session, token)

        return data

    except Exception as e:
        # 处理其他异常
        print(f"签到失败: ", str(e))
        raise e
def visit_mission_center(session, token):
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    headers["Cookie"] = f"b2_token={token};"

    try:
        print("开始访问任务中心...")
        sign_url = BASE_URL + "/mission/today"
        print("任务中心URL: ", sign_url)
        response = session.get(sign_url, headers=headers)
        response.raise_for_status()
        print("任务中心状态码: ", response.status_code)
        data = response.text
        # print("任务中心响应: ", data)
        return data

    except Exception as e:
        # 处理其他异常
        print(f"任务中心访问失败: ", str(e))
        raise e

def main():
    session = requests.Session()
    token = get_cached_token()
    print("缓存的token: ", token)

    if not token:
        code = get_oauth2_code(session)
        token = get_token_with_code(session, code)
        cache_token(token)
        print("获取新的token: ", token)

    max_retries = 5  # 设置最大重试次数
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = sign_in(session, token)
            print("签到结果:", response)
            QLAPI.notify('570vip签到失败', str(e))
            break  # 如果签到成功，跳出循环
        except Exception as e:
            print(f"签到失败，错误信息: {e}")
            # 判断如果是403 错误，则重试
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 403:
                print("token 失效，重新获取...")
                code = get_oauth2_code(session)
                token = get_token_with_code(session, code)
                cache_token(token)
                print("获取新的token: ", token)
                continue  # 重试
            # 其他错误，直接抛出异常
            retry_count += 1
            if retry_count < max_retries:
                print(f"将在 {retry_count} 秒后重试...")
                time.sleep(retry_count)  # 每次重试前等待一段时间
            else:
                print("达到最大重试次数，签到失败。")
                QLAPI.notify('570vip签到失败', str(e))

if __name__ == "__main__":
    main()
