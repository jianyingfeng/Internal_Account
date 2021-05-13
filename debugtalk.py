# encoding: utf-8

import os
import time
from common import read_config
from common.util import *
from common.op_mysql import OpMysql
from common.op_redis import OpRedis
import requests
import json

# 读取 .env 配置
TEST_ENV = os.environ['environment']
# 获取测试域名hosts
INTERNAL_ACCOUNT_API_HOST = os.environ['internal_account_api_host']
INTERNAL_ACCOUNT_SERVICE_HOST = os.environ['internal_account_service_host']
AUHTORITY_API_HOST = os.environ['authority_api_host']
TRANSACTION_API_HOST = os.environ['transaction_admin_api_host']
REAG_DISCOVERY_CENTER_HOST = os.environ['read_discovery_center_host']
REAG_DISCOVERY_CENTER_TOKEN = os.environ['read_discovery_center_token']
OPEN_SERVICE_HOST = os.environ['open_service_host']
#获取内部账号服务ip地址
def get_internal_account_service_host():
    return get_request_host_url(REAG_DISCOVERY_CENTER_HOST,INTERNAL_ACCOUNT_SERVICE_HOST,REAG_DISCOVERY_CENTER_TOKEN)

# 获取内部账号配置数据
internal_source_user = read_config.internal_source_user(TEST_ENV)

def internal_source_user_email():
    return internal_source_user.get('email')

def internal_source_reset_email():
    return internal_source_user.get('reset_email')

def internal_source_user_password():
    return internal_source_user.get('password')

def internal_source_reset_password():
    return internal_source_user.get('reset_password')

def internal_source_user_id():
    return internal_source_user.get('id')

def internal_source_identity():
    return internal_source_user.get('identity')

def internal_source_reset_id():
    return internal_source_user.get('reset_id')

def internal_source_user_phone_number():
    return internal_source_user.get('phone_number')

def internal_source_user_department_id():
    return internal_source_user.get('department_id')

def internal_source_user_fish_id():
    return internal_source_user.get('relation_fish_id')


# 获取内部账号系统token
def internal_source_user_login_token():
    #login_token= login_token_internal_account(INTERNAL_ACCOUNT_API_HOST, internal_source_user_email(), internal_source_user_password())
    login_token = generate_internal_account_token(INTERNAL_ACCOUNT_SERVICE_HOST, internal_source_user_id())
    return login_token

# 获取Fish账号配置信息
fish_account_beisen = read_config.read_config_fish_account(TEST_ENV)['fish_account_beisen']

def fish_account_beisen_username():
    return fish_account_beisen.get('username')

def fish_account_beisen_password():
    return fish_account_beisen.get('password')

def fish_account_beisen_encypted_password():
    return fish_account_beisen.get('encrypted_password')

def fish_account_beisen_email():
    return fish_account_beisen.get('email')

def fish_account_beisen_fishId():
    return fish_account_beisen.get('fish_id')

# 读取内部账号 mysql 配置，并且跳过正式环境
def get_mysql_config_internal_account():
    if TEST_ENV != 'production':
        mysql_config_internal_account = read_config.read_config_mysql(TEST_ENV, 'internal_account')
        global opmysql_internal_account
        opmysql_internal_account = OpMysql(host=mysql_config_internal_account['host'], user=mysql_config_internal_account['user'], password=mysql_config_internal_account['password'], database=mysql_config_internal_account['database'])

# 初始化mysql配置
get_mysql_config_internal_account()

def internal_account_delete_two_step_verification(user_id):
    opmysql_internal_account.internal_account_delete_two_step_verification(user_id)

def delete_relation_internal_fish(fish_id):
    opmysql_internal_account.delete_relation_internal_fish(fish_id)

# 读取内部账号 redis 配置并跳过正式环境
def get_redis_config():
    if TEST_ENV != 'production':
        redis_config = read_config.read_config_redis(TEST_ENV)
        global op_redis_internal_account
        op_redis_internal_account = OpRedis(host=redis_config['host'], port=redis_config['port'], password=redis_config['password'], db=2)

# 初始化redis配置
get_redis_config()

# 获取内部账号手机号验证码
def get_phone_number_captcha_internal_account(phone_number):
    return op_redis_internal_account.get_phone_number_captcha_internal_account(phone_number)

# 设置内部账号邮件发送验证码的总次数
def set_send_email_captcha_limit(email, value):
    return op_redis_internal_account.set_send_email_captcha_limit(email, value)

# 获取内部账号忘记密码的邮箱验证码
def get_email_captcha(email):
    captcha_value = op_redis_internal_account.get_email_captcha_internal_account(email)
    if captcha_value == None:
        host = get_internal_account_service_host()
        url = host+'/accounts/forgot-password/email'
        header = {"Content-Type": "application/json"}
        data = {"email": email}
        r = requests.post(url, headers=header, json=data)
        if r.status_code == 200:
            return op_redis_internal_account.get_email_captcha_internal_account(email)
        elif r.status_code == 422 and r.json()['error_code'] == '10007011':
            op_redis_internal_account.clear_email_limit_internal_account(email)
            requests.post(url, headers=header, json=data)
            time.sleep(3)
            return op_redis_internal_account.get_email_captcha_internal_account(email)
        elif r.status_code == 422 and r.json()['error_code'] == '10007007':
            print("发送邮件频繁")
            time.sleep(60)
            requests.post(url, headers=header, json=data)
            time.sleep(3)
            return op_redis_internal_account.get_email_captcha_internal_account(email)
    else:
        return captcha_value
    #print(op_redis_internal_account.get_email_captcha_internal_account(email))


# 判断两个值是否相等
def eval_equal(source, target):
    return source == target

# 判断是否是dev或者test环境
def is_dev_or_test():
    return True if TEST_ENV not in ('staging', 'production') else False

# 判断是否是正式环境
def is_production():
    return True if TEST_ENV == 'production' else False

# 因为test中None会被解析为字符串，所以这里增加此函数
def is_none(source):
    return True if source == None else False

def setup_hook_sleep_N_secs(n_secs):
    return time.sleep(n_secs)

#获取极验ticket验证码
def get_jiyan_ticket():
    url = OPEN_SERVICE_HOST + '/captcha/rule'
    data = {"pid": "hp_y9Wiw",
            "identity": "18018790522",
            "timestamp": 1587546656,
            "deviceId": ""
            }
    r = requests.post(url,json=data)
    ticket = r.json()['ticket']
    return ticket