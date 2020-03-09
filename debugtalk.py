# encoding: utf-8

import os
import time
from common import read_config
from common.util import *
from common.op_mysql import OpMysql
from common.op_redis import OpRedis

# 读取 .env 配置
TEST_ENV = os.environ['environment']
# 获取测试域名hosts
INTERNAL_ACCOUNT_API_HOST = os.environ['internal_account_api_host']
INTERNAL_ACCOUNT_SERVICE_HOST = os.environ['internal_account_service_host']
AUHTORITY_API_HOST = os.environ['authority_api_host']

# 获取内部账号配置数据
internal_source_user = read_config.internal_source_user(TEST_ENV)

def internal_source_user_email():
    return internal_source_user.get('email')

def internal_source_user_password():
    return internal_source_user.get('password')

def internal_source_user_id():
    return internal_source_user.get('id')

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

# 读取内部账号 mysql 配置
def get_mysql_config_internal_account():
    if TEST_ENV != 'production':
        mysql_config_internal_account = read_config.read_config_mysql(TEST_ENV, 'internal_account')
        global opmysql_internal_account
        opmysql_internal_account = OpMysql(host=mysql_config_internal_account['host'], user=mysql_config_internal_account['user'], password=mysql_config_internal_account['password'], database=mysql_config_internal_account['database'])

def internal_account_delete_two_step_verification(user_id):
    opmysql_internal_account.internal_account_delete_two_step_verification(user_id)

# 初始化mysql配置并且跳过正式环境
get_mysql_config_internal_account()

# 读取内部账号 redis 配置
def get_redis_config():
    if TEST_ENV != 'production':
        redis_config = read_config.read_config_redis(TEST_ENV)
        global op_redis_internal_account
        op_redis_internal_account = OpRedis(host=redis_config['host'], port=redis_config['port'], password=redis_config['password'], db=2)

# 初始化redis配置并跳过正式环境
get_redis_config()

# 获取内部账号手机号验证码
def get_phone_number_captcha_internal_account(phone_number):
    return op_redis_internal_account.get_phone_number_captcha_internal_account(phone_number)

# 设置内部账号邮件发送验证码的总次数
def set_send_email_captcha_limit(email, value):
    return op_redis_internal_account.set_send_email_captcha_limit(email, value)

# 判断是否是dev或者test环境
def is_dev_or_test():
    return True if TEST_ENV not in ('staging', 'production') else False

# 判断是否是正式环境
def is_production():
    return True if TEST_ENV == 'production' else False

# 因为test中None会被解析为字符串，所以这里增加此函数
def is_none(source):
    return True if source == None else False


