# python连接redis
import redis
import sys

class OpRedis(object):
    # 连接阿里云redis实例下的某个库
    def __init__(self, host, port, password, db):
        try:
            # decode_responses=True，写入键值对中的value为str类型，不加这个参数写入的则为字节类型
            pool = redis.ConnectionPool(host=host, port=port, password=password, db=db, decode_responses=True)
            self.r = redis.Redis(connection_pool=pool)
        except:
            print('连接redis失败，退出！')
            sys.exit(0)

    # 获取内部账号手机号验证码
    def get_phone_number_captcha_internal_account(self, phone_number):
        key_name = 'internal_account:captcha:auth:{}'.format(phone_number)
        captcha_value = self.r.get(key_name)
        return captcha_value

    # 获取内部账号邮件验证码
    def get_email_captcha_internal_account(self, email):
        key_name = 'internal_account:forgot_password:email:{}'.format(email)
        email_captcha_value = self.r.hget(key_name, 'captcha')
        return email_captcha_value

    # 在Redis中设置值，默认不存在则创建，存在则修改
    # return True/False
    def set_send_email_captcha_limit(self, email, value):
        key_name = 'internal_account:forgot_password:limit:{}'.format(email)
        return self.r.set(key_name, value)


if __name__ == '__main__':
    op_redis = OpRedis(host='r-bp19c78721368bd4371.redis.rds.aliyuncs.com', password='liuWcl8hj3InVQONzonkIeNa', port=6379, db=2)
    #print(op_redis.get_captcha_internal_account('15889741219'))
    print(op_redis.set_send_email_captcha_limit('maxiaoqian@codemao.cn', -1))