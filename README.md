#### 项目说明

- internal_account分支维护：内部账号、统一用户中心权限相关的自动化

#### 测试数据准备

- config目录用于配置测试数据
- internal_user：内部账号配置
- fish_account：fish账号配置
- db：数据库配置

#### .env配置文件

- environment表示测试环境：dev、test、staging、production

#### 依赖包

- python版本：3.0+
- 安装所有依赖包: `pip install -r requirements.txt`

#### 运行脚本

1. `.env`文件中指定测试环境和配置测试手机号
2. 运行如下命令

```sh
# 运行某目录下的所有测试用例
hrun testcases/account-api --dot-env-path=dev.env

# 运行某个测试用例文件
hrun testcases/account-api/v1/login.yaml --dot-env-path=dev.env

# 指定html报告的路径和名称
hrun testcases/account-api --html-report-name reports/result.html --dot-env-path=dev.env

# 自定义报告模板。默认使用：~\httprunner\templates\report_template.html
hrun testcases/account-api/v1/login.yaml --report-template=templates/report_fail_only.html --dot-env-path=dev.env
hrun testcases/account-api/v1/login.yaml --report-template=templates/extent_reports.html --dot-env-path=dev.env # 引入extent reports
```