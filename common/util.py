import requests
import time
import hmac
import hashlib
import json

# 获取内部账号系统登录token
# 因加有极验，目前无法获取内部账号的极验ticket，因此先用服务层生成token
# def login_token_internal_account(host, identity, password):
#     data = {
#         "identity": identity,
#         "password": password
#     }
#     res = requests.post(host+'/auth/login', json=data)
#     if res.status_code == 200 and 'application/json' in res.headers['Content-Type']:
#         bearer_token = 'Bearer '+ res.json()['token']
#         return bearer_token

# 内部账号服务层生成token
def generate_internal_account_token(host, user_id):
    data = {
        "id": user_id,
        "authorities": ["ROLE_ADMIN"]
    }
    res = requests.post(host+'accounts/auth/sign', json=data)
    if res.status_code == 200:
        return 'Bearer '+res.json()['token']
    else:
        print("内部账号Service生成token失败，状态码为：{}".format(res.status_code))

#通过接口动态获取服务ip
def get_request_host_url(host,applicationName,token):
    res = requests.get(host+'/eureka/apps/'+applicationName, headers={"Authorization": token, "Accept": 'application/json'})
    if res.status_code == 200:
        return res.json()['application']['instance'][0]['homePageUrl']
    else:
        print("获取服务地址失败，状态码为：{}".format(res.status_code))


# 获取某具体时间的时间戳
def get_timeslot(time_date):
    return int(time.mktime(time.strptime(str(time_date), '%Y-%m-%d')))

if __name__ == '__main__':
    print(get_timeslot('2020-1-10'))