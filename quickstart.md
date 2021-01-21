#### 框架说明

- 脚手架： hrun --startproject demo
- api： 接口的定义，避免重复定义
- testcases： 测试用例/测试场景文件
- testsuites: 测试套件
- debugtalk.py: 函数定义
- Available response attributes: status_code, cookies, elapsed, headers, content, text, json, encoding, ok, reason, url.
- skip，skipIf, skipUnless
- setup_hooks, teardown_hooks
- output：可以用于调试时打印变量的值，也可以用于在不同测试用例之间传递output指定的变量(通过testcase关键字引用其他用例时)。
```
output:
  - login_token_old_auth
```
- testcase中的yaml文件格式，根目录是数组格式。使用：`- config`,  `- test`
- testsuite中的yaml文件格式，根目录是dict类型。使用：`config`，`testcases`

#### 环境变量的引用
- debugtalk.py中引用 .env 中的变量： tiger_api_host = os.environ['tiger_api_host']
- testcases中引用 .env 中的变量：${ENV(tiger_api_host)}

#### skipIf
- 目前skipIf等过滤函数，只支持过滤单个teststep，不支持过滤整合testcase...

##### extract

- 一个testcase中，会先执行extract再执行validate，与定义的先后顺序无关。
- extract关键字，其结构为数组，数组中的元素，可以是dict类型，也可以是字符串。
```
# 用于提取response
extract:
    - login_token: content.auth.token

# 提取另一个testcase中export的变量
extract:
    - output_login_token
```

#### 框架源码学习

- html报告生成：report.py中的render_html_report函数，使用的是jinja2的模板文件templates/report_template.html

#### 经验总结

##### variables优先级问题

> variables priority: testcase config > testcase test > testcase_def config > testcase_def test > api，output（export）的变量高于 teststep，这样更符合常理。

- 例如：下面的test中，最终传递到API层的identity和password都是正确的，而不是期望的错误的。因为优先级`testcase config > testcase test > api`

```
- config:
    name: 账号登录-正常场景
    base_url: ${ENV(tiger_api_host)}
    variables:
        - identity: mxq100
        - password: m1234567

- test:
    name: 用户名正确-密码错误
    api: api/login.yaml
    variables:
        - identity: "rrrrrrrr"
        - password: "000"
    validate:
        - eq: [status_code, 403]
        - eq: [content.error_code, AC3_2]
```

##### testcase中引用需要传参的函数

- 例如：引用debugtalk.py中的函数source_user_value(key)时，test中传递的函数的参数值，需要先定义再引用。不能直接传递字符串。下图中identity传递的是"${source_user_value('username')}"，password传递的是${source_user_value("password")}
```
- test:
    name: 用户名正确-密码正确
    api: api/login.yaml
    variables:
        - key_username: username
        - key_password: password
        - identity: ${source_user_value('username')}
        - password: ${source_user_value($key_password)}
    validate:
        - eq: [status_code, 200]
        - contains: [content.auth, token]
```

##### 响应的cookies

- 问题1： cookies传递问题
cookies提取的值是dict类型，相当于dict(res.cookies)，
{'dev-authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMDAwNzM3NjI5LCJ1c2VyX3R5cGUiOiJzdHVkZW50IiwianRpIjoiNDM3OTBlMTUtODgwNC00NjA4LWE2NGItYjkzYzdmYjBkYzNmIiwiaWF0IjoxNTYzMjU5MjIzfQ.FfzXNKB3Expxngsbvh6yHe-Lyg56gNkg_zp8jMwzImw', 'master-v1-codemao-dev': 's%3A5vh94DSJjlMQflKxNTnsFAI2tzqQBR_R.nnCgQ7VBGn37qs%2FwDDKTzJjDwPyEdO6zPPC6wWOVhBA'}
正确的请求：
```
headers: 
    Cookie: headers.Set-Cookie
```
- 问题2：cookie seesion共享问题。同一个testcase文件下的testcase共享相同的session。(each teststeps in one testcase share the same session)
- 如下：teststep2中并没有设置Cookie，但仍然可以正常获取用户信息，是因为teststep1中登录成功后，返回的Set-Cookie直接在teststep2中引用了
```
- test:
    name: 准备工作：登录账号
    api: api/account/v3_for_web/login.yaml
    variables:
        - identity: ${source_user_username()}
        - password: ${source_user_password()}
    validate:
        - eq: [status_code, 200]

# teststep会共享之前的teststep返回的Set-Cookie作为请求头Cookie
- test:
    name: 获取用户信息
    request:
        method: GET
        url: /tiger/v3/web/accounts/profile
    validate:
        - eq: [status_code, 200]

```

##### setup_hooks和teardown_hooks

- 在同一个test中，teardown_hooks无法直接引用当前test中extract的变量。
- 在同一个test中，setup_hooks、teardown_hooks可以直接引用当前test中定义的variables。

##### testcase关键字

- testcase关键字：用于引用其他测试用例。注意通过testcase定义的test中，extract的变量无效
```
- test:
    name: 登录
    testcase: testcases/login.yaml
    extract:
        - login_token: content.token   # 导出的login_token无效，不能被后面的test引用
```
- `- eq: [content.id, ${str(${source_user_id()})}]`会报错，解决：`- eq: [content.id, '${str(${source_user_id()})}']`
- variables定义多个变量时，前一个定义的变量并不能被同级后一个变量立马引用到，例如下面的写法会报错
```
variables:
    - content: aaa
    - work_content: print($content)
```
- python语法报错或者TypeError(例如读取配置文件的字段不存在)或者测试文件的KeyError(例如引用不存在的变量)导致生成html报告失败时，错误提示无法定位出错的地方，例如：`from builtins import *`报错，改成 `from builtins import str,eval`
- 对于逻辑关系比较紧密的用例，可以写在一个文件中，例如：创建作品和删除作品（避免测试过后用户作品数过多）
- `less_than: [content.0.id, content.1.id]`，目标对象content.1.id会被识别为字符串，所以要先extract再比较
- api接口定义中最好填写完整的url，避免测试文件中的base_url和api接口中的域名不一致（例如批量创建用户后，验证用户登录）
- `&timestamp`，url: /api?a=aa&timestamp=21902910，&timestamp会被解析错误，改成：/api?timestamp=21902910&a=aa，可以正常解析到
- 修改数据后判断数据是否更新成功，目前是通过请求某api的返回值确认，而不是数据库操作
- 设置用户名的操作者，设置一次之后用户就无法设置了，怎么设置username为null，使测试账号可以重复使用？？？dev、test可以代码连接数据库吗？
- 直接运行整个文件夹路径，文件执行顺序是随机的
- api定义中不支持默认参数，不支持可选参数
- api定义，request中指定 base_url 不会被识别到，所以要直接在 url 中指定完整路径
- api文件中的yaml文件内容为空会报错
- api文件中的name会覆盖testcases文件test用例中的name
- testcases中yaml文件内容为空，会导致生成报告失败
- 加载顺序：.env文件---》加载testcase中定义的变量(执行其中可执行部分)---》运行testcase
- 读取可能有延迟的接口（例如MQ同步数据），需要添加sleep数据（ ${sleep_N_secs(1)} ）
- 同一个testcase的不同test之间，Cookies是继承的。（例如：第一个test用户登录成功，第二个test中如果不指定headers那么会使用默认的headers即带上Cookie）

#### 错误写法总结

##### 错误写法1

- 预期效果：先执行发送登录验证码接口，再获取验证码，执行验证码登录接口。

```
- test:
    name: 发送登录验证码-手机号未注册
    skipUnless: ${is_dev_or_test()}
    setup_hooks:
        - ${clear_phone_number($unregister_phone_number)}
    api: api/account/v3_for_web/send_login_silence_captcha.yaml
    variables:
        - phone_number: $unregister_phone_number
    validate:
        - eq: [status_code, 204]

- test:
    name: 验证码登录：手机号未注册-验证码正确
    skipUnless: ${is_dev_or_test()}
    api: api/account/v3_for_web/login_silence_by_captcha.yaml
    variables:
        - phone_number: $unregister_phone_number
        - captcha: ${get_captcha_account_v3(login_with_register, $unregister_phone_number)}  # 在执行所有testcase(包括setup_hooks)之前，variables中调用debugtalk.py中的函数会被先执行，调用几次就执行几次
    validate:
        - eq: [status_code, 200]
        - eq: [content.is_first_login, true]
```
- 实际效果：先执行了获取验证码，然后再执行发送验证码，导致获取的验证码为空（原因：test的variables中调用debugtalk.py的函数会在所有用例执行之前先执行）
- 解决方法：执行获取验证码的方法放在request中，而不是variables中，因此只要不复用api即可。


#### Hook

- 测试用例的准备和清理工作没有使用setup_hooks/teardown_hoos，而是直接调用DB层的接口（因为DB层涉及的CRUD操作的接口已经有了）
- 缺点：用例之间耦合性大，依赖于底层的DB操作接口的正确性
- 优点：减少直接操作数据库（并且正式库还没法直接修改表）
- 涉及到手机号注册相关，不会通过解绑接口清空手机号，因为业务限制太多，所以直接操作数据库

#### 注意点

- 退出登录后会导致其他用例中的source_user_login_token失效，所以退出登录用例中的已登录token需要单独获取
- 账号3.0修改密码，导致source_user_login_token失效，所以使用测试账号2（target_user）测试

#### 用例编写注意事项

1. api定义中不支持可选参数
2. testcase中不支持函数嵌套调用
3. variables变量优先级问题：testcase config > testcase test > testcase_def config > testcase_def test > api，output（export）的变量高于 teststep
4. base_url优先级: testcase test > testcase config > testsuite test > testsuite config > api
5. verify 优先级: testcase teststep (api) > testcase config > testsuite config
6. 同一个testc one testcase share the same session)ase文件下的testcase共享相同的session。(each teststeps in