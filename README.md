教务系统自动化登录与数据获取工具

这是一个用于自动化登录教务系统并获取课程表、成绩和个人信息的Python脚本工具。

功能特性

• 🔐 自动化登录：通过模拟登录流程获取访问令牌

• 📊 课程表查询：获取当前学期的课程安排信息

• 📈 成绩查询：查询指定学年的成绩详情

• 👤 个人信息：提取学生基本信息（学号、姓名、学院等）

• 🔒 加密处理：使用DES加密处理密码传输

项目结构


├── main.py                 # 主程序文件
├── tyust_login.js         # 加密处理模块
└── README.md              # 项目说明文档


依赖环境

Python依赖

pip install requests execjs pycryptodome


JavaScript依赖

npm install crypto-js


使用方法

1. 基本配置

在main.py文件末尾修改以下参数：
if __name__ == '__main__':
    # 修改为你的学号和密码
    ret = execjs.compile(open('tyust_login.js', 'r', encoding='utf-8').read()).call(
        'get_crypto_and_password', '你的密码'
    )
    session, execution_code = get_session()
    code, _, sourceid_tgc, rg_objectid = get_login_code('你的学号', session, execution_code)
    # ... 其余代码


2. 功能调用

获取个人信息

get_user_detail_information(jwglxt_jsession, route)


获取课程表

get_current_course(jwglxt_jsession, _access_token, route)


获取成绩信息

# 参数说明：xnm-学年，xqm-学期（3或12）
get_user_scores(jwglxt_jsession, route, '2024', '3')


输出示例

课程表输出格式


课程名: 高等数学
节次: 1-2, 星期: 星期一, 地点: 教学楼A101
教师: 张老师, 学分: 4.0, 类别: 必修, 周次: 1-16周


个人信息输出格式


学号: 2024123456
姓名: 张三
学院名称: 计算机学院
专业名称: 计算机科学与技术
班级名称: 计算机2101班


成绩信息输出格式


--- 学生: 张三 (2024学年 第3学期) 成绩详情 ---

--- 科目 1 ---
  课程名称: 高等数学
  课程类别: 必修
  成绩: 85
  绩点 (JD): 3.5
  学分 (XF): 4.0
  任课教师: 李老师
  开课部门: 数学学院


技术实现

登录流程

1. 获取初始会话和验证码
2. 使用DES加密密码
3. 通过CAS单点登录认证
4. 获取访问令牌和路由信息
5. 建立教务系统会话

数据加密

• 使用DES算法加密密码传输

• 生成随机的CSRF令牌

• 基于时间戳的设备ID生成

注意事项

1. 合规使用：请确保遵守学校网络使用规定
2. 频率限制：避免频繁请求，防止被系统封禁
3. 数据安全：妥善保管个人账号信息
4. 系统更新：教务系统更新可能导致脚本失效

故障排除

常见问题

1. 登录失败：检查学号密码是否正确，网络连接是否正常
2. 数据获取失败：可能是系统维护或接口变更
3. 依赖安装失败：确保Node.js和Python环境配置正确

调试模式

取消注释代码中的headers部分可以启用详细调试信息。

许可证

本项目仅供学习和研究使用，请遵守相关法律法规和学校规定。

更新日志

• v1.0：初始版本，支持基本登录和数据获取功能

• 支持课程表、成绩、个人信息查询

• 实现完整的登录认证流程

免责声明：本工具仅用于技术学习，使用者应承担因不当使用而产生的一切后果。
