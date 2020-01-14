# encoding: utf-8

import yaml
import os

conf_dir = os.path.join(os.path.dirname(__file__), '..', 'config')

# 读取内部账号配置
def read_internal_user(env, file_dir=conf_dir):
    file_name = str(env)+'_user.yml'
    file_path = os.path.join(file_dir, 'internal_user', file_name)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.load(f)
        return data

def internal_source_user(env):
    source_user_data = read_internal_user(env)['source_user']
    return source_user_data

# 读取数据库、redis 配置
def read_db(env, file_dir=conf_dir):
    file_name = str(env) + '_db.yml'
    file_path = os.path.join(file_dir, 'db', file_name)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.load(f)
        return data

def read_config_mysql(env, database_name):
    mysql_data = read_db(env)['mysql'][database_name]
    return mysql_data

def read_config_redis(env):
    redis_data = read_db(env)['redis']
    return redis_data

# 读取fish账号配置
def read_config_fish_account(env, file_dir=conf_dir):
    file_name = str(env) + '_user.yml'
    file_path = os.path.join(file_dir, 'fish_account', file_name)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.load(f)
        return data


if __name__ == '__main__':
    env = 'dev'
    internal_user = read_internal_user(env)
    print(internal_user['source_user'])