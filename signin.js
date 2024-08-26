const fetch = require('node-fetch');
const fs = require('fs');

// 配置日志
const log = (msg) => console.log(msg);
const logInfo = (msg) => log(`INFO: ${msg}`);
const logError = (msg) => log(`ERROR: ${msg}`);

// 配置
const BASE_URL = "http://www.570vip.com";
const OAUTH2_CODE_URL = "/wp-json/b2/v1/getRecaptcha";
const TOKEN_URL = "/wp-json/jwt-auth/v1/token";
const SIGN_IN_URL = "/wp-json/b2/v1/userMission";
const TOKEN_CACHE_FILE = "token_cache.json";

const HEADERS = {
    "Referer": "http://www.570vip.com/guohua/1107/68.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
    "Origin": "http://www.570vip.com",
    "Pragma": "no-cache"
};

// 尝试从缓存文件中读取token
async function getCachedToken() {
    try {
        const data = await fs.promises.readFile(TOKEN_CACHE_FILE, 'utf8');
        const parsedData = JSON.parse(data);
        return parsedData.token;
    } catch (error) {
        if (error.code === 'ENOENT') {
            return null;
        }
        throw error;
    }
}

// 缓存token到文件
function cacheToken(token) {
    fs.writeFile(TOKEN_CACHE_FILE, JSON.stringify({ token }), (err) => {
        if (err) throw err;
    });
}

// 获取oauth2 code
async function getOAuth2Code() {
    const response = await fetch(BASE_URL + OAUTH2_CODE_URL, { headers: HEADERS });
    const data = await response.json();
    return data.token; // 假设响应中token字段就是code
}

// 用code换取token
async function getTokenWithCode(code) {
    const data = {
        "username": "sulele89757",
        "password": "8848@kok",
        "token": code
    };
    const response = await fetch(BASE_URL + TOKEN_URL, {
        method: 'POST',
        headers: HEADERS,
        body: new URLSearchParams(data)
    });
    const dataJson = await response.json();
    return dataJson.token;
}

// 进行签到
async function signIn(token) {
    const headers = { ...HEADERS };
    headers["Authorization"] = `Bearer ${token}`;
    headers["Cookie"] = `b2_token=${token}; order_id=E820149517740389; b2_back_url=http://www.570vip.com/vips; wordpress_test_cookie=WP%20Cookie%20check`;

    try {
        const response = await fetch(BASE_URL + SIGN_IN_URL, {
            method: 'POST',
            headers,
        });
        const data = await response.json();
        logInfo("签到响应: ", data);
        // 检查响应中的 code 字段
        if (data.code === 'user_error') {
            // 如果 code 是 user_error，重新获取token
            log("需要重新登录...");
            const code = await getOAuth2Code();
            const token = await getTokenWithCode(code);
            cacheToken(token);
            return await signIn(token);
        }
        return data;
    } catch (error) {
        logError(error.message);
        throw error;
    }
}

async function main() {
    let token = await getCachedToken();
    logInfo("cached token: ", token);
    if (!token) {
        const code = await getOAuth2Code();
        token = await getTokenWithCode(code);
        cacheToken(token);
        logInfo("new token: ", token);
    }
    const response = await signIn(token);
    logInfo("签到结果: ", response);
    log("签到结果:", response);
}

main().catch(logError);
