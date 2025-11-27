import time
import execjs
import requests
import re
import json
import os

def get_session():
    login_response = requests.get('https://sso1.tyust.edu.cn/login')
    match = re.search(r'<p id="login-page-flowkey">(.*?)</p>', login_response.text, re.DOTALL)
    if match:
        execution_code = match.group(1)
    session = login_response.headers['Set-Cookie'].split(';')[0].split('=')[1]
    return session, execution_code


def get_ronghemenhu_jsessionid(_code):
    _url = 'https://ronghemenhu.tyust.edu.cn/portal/publish/web/login/loginByOauth'
    # _headers = {
    #     'Accept': 'application/json, text/plain, */*',
    #     'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    #     'Connection': 'keep-alive',
    #     'Content-Type': 'application/json;charset=UTF-8',
    #     'Origin': 'https://ronghemenhu.tyust.edu.cn',
    #     'Referer': f'https://ronghemenhu.tyust.edu.cn/sso/login?code={_code}',
    #     'Sec-Fetch-Dest': 'empty',
    #     'Sec-Fetch-Mode': 'cors',
    #     'Sec-Fetch-Site': 'same-origin',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
    #     'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    # }

    json_data = {
        'code': code,
        'username': '',
        'password': '',
    }

    response = requests.post(
        _url,
        # headers=_headers,
        json=json_data,
    )
    original_jsessionid = response.headers.get('Set-Cookie')
    jsessionid = original_jsessionid.split(';')[0].split('=')[1]
    return jsessionid


def handle_login_information(headers):
    ticket = headers['Location'].split('=')[1]
    sourceid_tgc = headers['Set-Cookie'].split('=')[1].split(';')[0]
    match = re.search(r"rg_objectid=([a-zA-Z0-9]+)", headers['Set-Cookie'])
    if match:
        rg_objectid = match.group(1)
    return ticket, sourceid_tgc, rg_objectid

def get_login_code(username, _cookie, _execution_code):
    # headers = {
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #     'Accept-Language': 'en-US,en;q=0.9',
    #     'Cache-Control': 'max-age=0',
    #     'Connection': 'keep-alive',
    #     'Content-Type': 'application/x-www-form-urlencoded',
    #     'Origin': 'https://sso1.tyust.edu.cn',
    #     'Referer': 'https://sso1.tyust.edu.cn/login',
    #     'Sec-Fetch-Dest': 'document',
    #     'Sec-Fetch-Mode': 'navigate',
    #     'Sec-Fetch-Site': 'same-origin',
    #     'Upgrade-Insecure-Requests': '1',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
    #     'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    # }
    login_page_data = {
        'username': username,
        'type': 'UsernamePassword',
        '_eventId': 'submit',
        'geolocation': '',
        'execution': _execution_code,
        'captcha_code': '',
        'croypto': ret['crypto'],
        'password': ret['password_str'],
    }
    cookies = {'SESSION': _cookie}
    response = requests.post('https://sso1.tyust.edu.cn/login', cookies=cookies,
                             # headers=headers,
                             data=login_page_data)
    ticket, sourceid_tgc, rg_objectid = handle_login_information(response.history[0].headers)
    code = response.request.url.split('=')[1]
    return code, ticket, sourceid_tgc, rg_objectid


def get_user_info(code):
    # headers = {
    #     'Accept': 'application/json, text/plain, */*',
    #     'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    #     'Connection': 'keep-alive',
    #     'Content-Type': 'application/json;charset=UTF-8',
    #     'Origin': 'https://ronghemenhu.tyust.edu.cn',
    #     'Referer': f'https://ronghemenhu.tyust.edu.cn/sso/login?code={code}',
    #     'Sec-Fetch-Dest': 'empty',
    #     'Sec-Fetch-Mode': 'cors',
    #     'Sec-Fetch-Site': 'same-origin',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
    #     'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    # }
    jsessionid = get_ronghemenhu_jsessionid(code)
    cookies = {'JSESSIONID': jsessionid}
    response = requests.get('https://ronghemenhu.tyust.edu.cn/portal/publish/web/login/user', cookies=cookies,
                            # headers=headers
                            )
    return response.json()


def generate_device_id():
    return os.urandom(16).hex()


def get__access_token(session, sourceid_tgc, rg_objectid):
    cookies = {
        'SESSION': session,
        'SOURCEID_TGC': sourceid_tgc,
        'rg_objectid': rg_objectid,
    }

    # headers = {
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #     'Accept-Language': 'en-US,en;q=0.9',
    #     'Connection': 'keep-alive',
    #     'Sec-Fetch-Dest': 'document',
    #     'Sec-Fetch-Mode': 'navigate',
    #     'Sec-Fetch-Site': 'cross-site',
    #     'Upgrade-Insecure-Requests': '1',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
    #     'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    # }

    response = requests.get(
        'https://sso1.tyust.edu.cn/login?service=https://zero.tyust.edu.cn/login/casCallback/r3IveGXj/',
        cookies=cookies,
        # headers=headers,
    )
    ticket = response.history[0].headers['Location'].split('=')[1]

    # headers = {
    #     'accept': 'application/json, text/plain, */*',
    #     'accept-language': 'en-US,en;q=0.9',
    #     'cache-control': 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0',
    #     'content-type': 'application/json;charset=UTF-8',
    #     'origin': 'https://zero.tyust.edu.cn',
    #     'priority': 'u=1, i',
    #     'referer': f'https://zero.tyust.edu.cn/login/casCallback/r3IveGXj/?ticket={ticket}',
    #     'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    #     'sec-fetch-dest': 'empty',
    #     'sec-fetch-mode': 'cors',
    #     'sec-fetch-site': 'same-origin',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
    #     'x-requested-with': 'XMLHttpRequest',
    # }
    json_data = {
        'externalId': 'r3IveGXj',
        "data": json.dumps({
            "callbackUrl": "https://zero.tyust.edu.cn/login/casCallback/r3IveGXj/",
            "ticket": ticket,
            "deviceId": generate_device_id()
        })
    }

    response = requests.post('https://zero.tyust.edu.cn/api/access/auth/finish',
                             # headers=headers,
                             json=json_data)
    # also get the access_token with response's json
    _access_token = response.json()['data']['token']
    # following code also get access_token
    # match = re.search(r"__access_token=([^;]+)", response.headers['Set-Cookie'])
    # if match:
    #     _access_token = match.group(1)

    return _access_token
    # Note: json_data will not be serialized by requests
    # exactly as it was in the original request.
    # data = '{"externalId":"r3IveGXj","data":"{\\"callbackUrl\\":\\"https://zero.tyust.edu.cn/login/casCallback/r3IveGXj/\\",\\"ticket\\":\\"ST-500547-6sl84wA9ttvQtGrq-l2NUcn1ZAUrg-sso-7c69df9fff-2crrm\\",\\"deviceId\\":\\"bf087053f5a01aec3a879802c93f438a\\"}"}'
    # response = requests.post('https://zero.tyust.edu.cn/api/access/auth/finish', headers=headers, data=data)


def get_route(access_token):
    cookies = {
        '__access_token': access_token
    }

    # headers = {
    #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #     'accept-language': 'en-US,en;q=0.9',
    #     'priority': 'u=0, i',
    #     'referer': 'https://zero.tyust.edu.cn/',
    #     'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    #     'sec-fetch-dest': 'document',
    #     'sec-fetch-mode': 'navigate',
    #     'sec-fetch-site': 'same-site',
    #     'upgrade-insecure-requests': '1',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
    #     # 'cookie': '__access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxMTk5MzYxMTkyMjI1NjY5MTMiLCJhdXRoVHlwZSI6NSwiZXh0ZXJuYWxJZCI6InIzSXZlR1hqIiwic2FsdCI6IjExOTkzNjExOTI4OTY3NTc3NyIsImV4cCI6MTc1NjI2NTQwOCwiaXNzIjoiZXhwIn0.yrBByfydJ3BpU-OWPhdTVKrDysfrHU9kGacXJJYWLYk',
    # }

    response = requests.get('https://newjwc.tyust.edu.cn/sso/jasiglogin/jwglxt',
                            cookies=cookies,
                            # headers=headers
                            )

    match = re.search(r"route=([^;]+)", response.history[0].headers['Set-Cookie'])
    if match:
        route = match.group(1)
    return route


def get_jwglxt_jsession(session, sourceid_tgc, rg_objectid, _access_token, route):
    cookies = {
        'SESSION': session,
        'SOURCEID_TGC': sourceid_tgc,
        'rg_objectid': rg_objectid,
        '__access_token': _access_token,
        'route': route,
    }

    # headers = {
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #     'Accept-Language': 'en-US,en;q=0.9',
    #     'Connection': 'keep-alive',
    #     'Referer': 'https://zero.tyust.edu.cn/',
    #     'Sec-Fetch-Dest': 'document',
    #     'Sec-Fetch-Mode': 'navigate',
    #     'Sec-Fetch-Site': 'same-site',
    #     'Upgrade-Insecure-Requests': '1',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
    #     'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    #     # 'Cookie': 'SESSION=d5e9d349-3225-4343-a875-d09498665202; SOURCEID_TGC=eyJhbGciOiJIUzUxMiJ9.ZXlKNmFYQWlPaUpFUlVZaUxDSmhiR2NpT2lKa2FYSWlMQ0psYm1NaU9pSkJNVEk0UTBKRExVaFRNalUySW4wLi41TElWbktoaXVUZHd2eklPMWVRdWlBLk55eHZuOVFRa19vOUx1akcweTlIUmdST0NwdHRidTR5QkxpMWRxRFpYZkFjWnZrNGdMcVRTZlk3dkhtVzZ2d1pkZ1RvSnRPTVhrME5LZXNvLUM2X2lpd2l0QTZZQkxUMjJLZ01yT2x1aExzMXNuaHVxNkJ2VGVqNXljc2RBX29SNURidFNUUjZ5ZkVDTVd0OE93eDRSNVZHVFpvMTNTS3NvS2FBREVrckNEdDgxaUNUVDJ6UXhiaXhja2VUMktXMS5OMEZCZFZDV3NvT0FTNFc5T2VRcExR.cpa8IXxY2nLfkgjoixITD8NIfjFbjaGJuqs5Zxyf1lV0N2k80j1g9VmPXmIVh3S3RCNEADu7Z-SHkORqrd4YoQ; rg_objectid=dfb239ed31bd6756e6d800c898bc563ce7b96dc8f97a1861e55a24d1a8b2973128c21dde5f5ce7c8c04903e3366ba801; __access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxMTk5MzYxMTkyMjI1NjY5MTMiLCJhdXRoVHlwZSI6NSwiZXh0ZXJuYWxJZCI6InIzSXZlR1hqIiwic2FsdCI6IjExOTkzNjExOTI4OTY3NTc3NyIsImV4cCI6MTc1NjI2NTQwOCwiaXNzIjoiZXhwIn0.yrBByfydJ3BpU-OWPhdTVKrDysfrHU9kGacXJJYWLYk',
    # }

    params = {
        'service': 'https://newjwc.tyust.edu.cn/sso/jasiglogin/jwglxt',
    }

    response = requests.get('https://sso1.tyust.edu.cn/login', params=params, cookies=cookies,
                            # headers=headers
                            )
    jwglxt_jsession = response.history[3].headers['Set-Cookie'].split('=')[1].split(';')[0]
    return jwglxt_jsession


def get_current_course(jwglxt_jsession, _access_token, route):
    cookies = {
        'JSESSIONID': jwglxt_jsession,
        '__access_token': _access_token,
        'route': route,
    }

    # headers = {
    #     'accept': '*/*',
    #     'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    #     'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
    #     'origin': 'https://newjwc.tyust.edu.cn',
    #     'priority': 'u=1, i',
    #     'referer': 'https://newjwc.tyust.edu.cn/jwglxt/kbcx/xskbcx_cxXskbcxIndex.html?gnmkdm=N253508&layout=default',
    #     'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    #     'sec-fetch-dest': 'empty',
    #     'sec-fetch-mode': 'cors',
    #     'sec-fetch-site': 'same-origin',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
    #     'x-requested-with': 'XMLHttpRequest',
    #     # 'cookie': 'JSESSIONID=1FC3362F33F457E580DC4DFA5701EC9F; __access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxMTk5MzYxMTkyMjI1NjY5MTMiLCJhdXRoVHlwZSI6NSwiZXh0ZXJuYWxJZCI6InIzSXZlR1hqIiwic2FsdCI6IjExOTkzNjExOTI4OTY3NTc3NyIsImV4cCI6MTc1NjI2MzU3MSwiaXNzIjoiZXhwIn0.Uh2ynWSBXWHGQ3sDGBqAiZZV-BWbKp9lRX9xKZ3ienI; route=aec33f5c13ed8018b3e10c7e7e2f1e6d',
    # }

    params = {
        'gnmkdm': 'N253508',
    }

    data = {
        'xnm': '2025',
        'xqm': '3',
        'kzlx': 'ck',
        'xsdm': '',
    }

    response = requests.post(
        'https://newjwc.tyust.edu.cn/jwglxt/kbcx/xskbcx_cxXsgrkb.html',
        params=params,
        cookies=cookies,
        # headers=headers,
        data=data,
    )

    data = response.json()['kbList']
    for course in data:
        course_name = course.get('kcmc')  # 课程名
        class_time = course.get('jc')  # 节次
        weekday = course.get('xqjmc')  # 星期几
        location = course.get('lh')  # 上课地点
        teachers = course.get('xm')  # 教师
        credits = course.get('xf')  # 学分
        course_type = course.get('kclb')  # 课程类别
        weeks = course.get('zcd')  # 周次范围

        print(f"课程名: {course_name}")
        print(f"节次: {class_time}, 星期: {weekday}, 地点: {location}")
        print(f"教师: {teachers}, 学分: {credits}, 类别: {course_type}, 周次: {weeks}")
        print("-" * 50)

def extract_field(html, field_name):
    """
    使用正则表达式从 HTML 内容中提取指定字段的值。

    :param html: HTML 文本内容
    :param field_name: 要提取的字段名 (如 '学号', '姓名', '证件类型', '证件号码')
    :return: 提取到的值或 "Not Found"
    """
    # 构造正则表达式模式:
    # 1. 匹配字段名 (如 '学号') 和冒号 (：)
    # 2. \s* 匹配零或多个空格或换行
    # 3. </label> 匹配标签结束
    # 4. .*? 非贪婪匹配，匹配到 <p class="form-control-static"> 之前的所有内容
    # 5. \s* 匹配 <p> 标签内的前导空格/换行
    # 6. (.*?) 捕获组，捕获实际的字段值
    # 7. \s* 匹配 <p> 标签内的尾随空格/换行
    # 8. </p> 匹配 <p> 标签结束
    pattern = rf'{field_name}：\s*</label>.*?<p class="form-control-static">\s*(.*?)\s*</p>'

    # re.DOTALL (re.S) 标志使得 '.' 能匹配包括换行符在内的所有字符，这对于跨行匹配 HTML 至关重要
    match = re.search(pattern, html, re.DOTALL)

    if match:
        # 清理捕获到的值，去除首尾空白（包括换行）
        return match.group(1).strip()
    return "Not Found"



def get_user_detail_information(jwglxt_jsession,route):
    cookies = {
        'JSESSIONID': jwglxt_jsession,
        'route': route,
    }
    response = requests.get('https://newjwc.tyust.edu.cn/jwglxt/xsxxxggl/xsgrxxwh_cxXsgrxx.html?gnmkdm=N100801&layout=default',cookies=cookies)
    html_content = response.text
    # 提取所有字段
    data = {
        "学号": extract_field(html_content, "学号"),
        "姓名": extract_field(html_content, "姓名"),
        "证件类型": extract_field(html_content, "证件类型"),
        "证件号码": extract_field(html_content, "证件号码"),
        "学院名称": extract_field(html_content, "学院名称"),
        "专业名称": extract_field(html_content, "专业名称"),
        "班级名称": extract_field(html_content, "班级名称")
    }

    # 打印结果
    for key, value in data.items():
        print(f"{key}: {value}")

# xnm 学年
# xqm 学期 3或者12
def get_user_scores(jwglxt_jsession,route,xnm = '',xqm = ''):
    cookies = {
        'JSESSIONID': jwglxt_jsession,
        'route': route,
    }

    # headers = {
    #     'accept': 'application/json, text/javascript, */*; q=0.01',
    #     'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    #     'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
    #     'origin': 'https://newjwc.tyust.edu.cn',
    #     'priority': 'u=1, i',
    #     'referer': 'https://newjwc.tyust.edu.cn/jwglxt/xsxxxggl/xsgrxxwh_cxXsgrxx.html?gnmkdm=N100801&layout=default',
    #     'sec-ch-ua': '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    #     'sec-fetch-dest': 'empty',
    #     'sec-fetch-mode': 'cors',
    #     'sec-fetch-site': 'same-origin',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
    #     'x-requested-with': 'XMLHttpRequest',
    #     # 'cookie': 'JSESSIONID=E4451FBA673CA67B92FE5F0466B8D2AE; route=aec33f5c13ed8018b3e10c7e7e2f1e6d',
    # }

    params = {
        'gnmkdm': 'N305005',
        'doType': 'query',
    }
    timestamp_seconds = time.time()
    timestamp_milliseconds = int(timestamp_seconds * 1000)
    data = {
        'xh_id': '学号',
        'xnm': xnm,
        'xqm': xqm,
        '_search': 'false',
        'nd': f'{timestamp_milliseconds}',
        'queryModel.showCount': '5000',
        'queryModel.currentPage': '1',
        'queryModel.sortName': ' ',
        'queryModel.sortOrder': 'asc',
        'time': '0',
    }

    response = requests.post(
        'https://newjwc.tyust.edu.cn/jwglxt/cjcx/cjcx_cxDgXscj.html',
        params=params,
        cookies=cookies,
        # headers=headers,
        data=data,
    )
    response_json = response.json()
    parse_scores_json(response_json)

def parse_scores_json(json_data):
    try:
        # 1. 直接从字典中获取科目列表
        subjects = json_data.get('items', [])

        if not subjects:
            print("字典数据中未找到科目信息。")
        else:
            # 提取学生和学期信息（假设所有科目都属于同一学生和学期）
            student_name = subjects[0].get('xm', 'N/A')
            academic_year = subjects[0].get('xnmmc', 'N/A')
            semester = subjects[0].get('xqmmc', 'N/A')

            print(f"--- 学生: {student_name} ({academic_year}学年 第{semester}学期) 成绩详情 ---")

            # 2. 遍历并打印每个科目
            for i, subject in enumerate(subjects, 1):
                kcmc = subject.get('kcmc', 'N/A')  # 课程名称
                kclbmc = subject.get('kclbmc', 'N/A')  # 课程类别 (必修/选修等)
                cj = subject.get('cj', 'N/A')  # 成绩 (等级或数字)
                bfzcj = subject.get('bfzcj', 'N/A')  # 百分制成绩
                jd = subject.get('jd', 'N/A')  # 绩点
                xf = subject.get('xf', 'N/A')  # 学分
                jsxm = subject.get('jsxm', 'N/A')  # 任课教师
                kkbmmc = subject.get('kkbmmc', 'N/A')  # 开课部门

                # 统一成绩显示格式 (如果成绩是数字，则只显示成绩；如果是等级，则显示等级)
                # 这里的判断逻辑比上次更简洁：如果 cj 是数字，直接显示；如果是等级，则显示等级
                if cj.isdigit() or (cj in ["优", "良", "合格", "优秀", "及格", "不及格"]):
                    display_score = cj
                else:
                    # 对于那些 cj 是等级，bfzcj 是数字的情况
                    display_score = f"{cj} (百分制: {bfzcj})" if cj != bfzcj else cj

                print(f"\n--- 科目 {i} ---")
                print(f"  课程名称: {kcmc}")
                print(f"  课程类别: {kclbmc}")
                print(f"  成绩: {display_score}")
                print(f"  绩点 (JD): {jd}")
                print(f"  学分 (XF): {xf}")
                print(f"  任课教师: {jsxm}")
                print(f"  开课部门: {kkbmmc}")

    except Exception as e:
        # 如果在处理字典数据的过程中出现其他错误
        print(f"数据处理过程中发生错误: {e}")

if __name__ == '__main__':
    ret = execjs.compile(open('tyust_login.js', 'r', encoding='utf-8').read()).call('get_crypto_and_password',
                                                                                    '教务系统密码')
    session, execution_code = get_session()
    code, _, sourceid_tgc, rg_objectid = get_login_code('学号', session, execution_code)
    _access_token = get__access_token(session, sourceid_tgc, rg_objectid)
    route = get_route(_access_token)
    jwglxt_jsession = get_jwglxt_jsession(session, sourceid_tgc, rg_objectid, _access_token, route)
    get_user_detail_information(jwglxt_jsession,route)
    get_user_scores(jwglxt_jsession,route,'2024','3')