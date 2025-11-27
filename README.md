## 🌟 TYUST 统一身份认证与教务系统爬虫

[![Python 3.x](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-16%2B-green?style=for-the-badge&logo=node.js)](https://nodejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

本项目是一个功能强大的 Python 脚本，旨在模拟登录太原科技大学（TYUST）的统一身份认证系统（SSO），并自动化地从教务系统（JWGLXT）获取学生的**个人信息**、**课程表**和**成绩**。

---

## 💡 主要功能

本项目能够安全地处理登录加密和多系统间的会话跳转，实现以下核心功能：

* **🔑 SSO 模拟登录**：处理登录页面的动态参数和密码的 **DES 加密**。
* **🔗 多系统会话保持**：管理和传递 SSO、门户和 JWGLXT 之间复杂的 `Cookie` 集合（包括 `SESSION`, `__access_token`, `route` 等）。
* **👤 学生个人信息查询**：从教务系统抓取用户的详细档案信息（如学号、姓名、学院、专业、班级）。
* **📅 课程表获取**：查询指定学年的学生个人课表。
* **💯 成绩查询**：查询指定学年学期的所有科目成绩，并解析出百分制成绩、绩点和学分。

---

## 🛠️ 环境准备

本项目需要 **Python** 环境来运行主爬虫脚本，并依赖 **Node.js** 环境来执行 JavaScript 文件中的加密函数。

### 1. 安装依赖

您需要安装 Python 和 Node.js 的相关依赖库。

| 环境 | 依赖库 | 安装命令 |
| :--- | :--- | :--- |
| **Python** | `requests`, `pyexecjs` | `pip install requests pyexecjs` |
| **Node.js** | `crypto-js` | `npm install crypto-js` |

### 2. 文件结构

请确保您的项目文件夹中包含以下两个文件：

.
├── tyust.py        \# 核心爬虫和请求逻辑 (Python)
└── tyust\_login.js  \# 密码加密逻辑 (JavaScript)

````

---

## 🚀 使用指南

### 1. 修改登录凭证

在运行 `tyust.py` 之前，您必须在文件底部的 `if __name__ == '__main__':` 块中修改您的 **学号** 和 **密码**。

```python
# tyust.py (部分代码)

if __name__ == '__main__':
    # ⚠️ 1. 替换为您的真实密码
    ret = execjs.compile(open('tyust_login.js', 'r', encoding='utf-8').read()).call('get_crypto_and_password',
                                                                                    '您的真实密码') 
    
    session, execution_code = get_session()
    
    # ⚠️ 2. 替换为您的真实学号
    code, _, sourceid_tgc, rg_objectid = get_login_code('您的真实学号', session, execution_code)
    
    # ... 其他步骤 ...
    
    # ⚠️ 3. 可选：修改查询的学年和学期
    # '2024' 为学年；'3' 为学期 (3=上学期/秋季, 12=下学期/春季)
    get_user_scores(jwglxt_jsession,route,'2024','3') 
````

### 2\. 执行脚本

在终端中运行 Python 脚本：

```bash
python tyust.py
```

执行结果（个人信息、课表和成绩）将直接打印到控制台中。

-----

## ⚙️ 加密机制解析

登录过程涉及到的密码加密由 `tyust_login.js` 处理，并通过 `execjs` 库在 Python 中调用。

| 参数 | 来源 | 作用 |
| :--- | :--- | :--- |
| `crypto` | `generateDesKey()` | 随机生成并 Base64 编码的 8 字节 DES 密钥。|
| `password` | `get_crypto_and_password()` | 使用 `crypto` 作为密钥，对原始密码进行 **DES ECB/PKCS7** 加密后 Base64 编码的密文。|

### DES 加密流程

1.  随机生成一个 8 字节的 DES 密钥 (`generateDesKey`)。
2.  将此密钥 Base64 编码后作为请求参数 `crypto` 提交。
3.  使用该密钥以 **ECB** 模式和 **Pkcs7** 填充对用户密码进行加密 (`CryptoJS.DES.encrypt`)。
4.  将加密后的密文 Base64 编码后作为请求参数 `password` 提交。

-----

## 📝 输出结果示例

运行脚本后，您将在控制台看到如下格式化输出：

### 个人信息

```
学号: 202112181110
姓名: XXX
证件类型: 居民身份证
学院名称: 计算机科学与技术学院
专业名称: 软件工程
班级名称: 软件2101
```

### 课程表

```
课程名: 编译原理
节次: 3-4节, 星期: 星期一, 地点: 计科楼B204
教师: XXX, 学分: 3.5, 类别: 必修, 周次: 1-16周
--------------------------------------------------
课程名: 创新创业基础
节次: 5-6节, 星期: 星期一, 地点: 主校区B04
教师: XXX, 学分: 1.0, 类别: 必修, 周次: 1-16周
...
```

### 成绩详情

```
--- 学生: XXX (2024学年 第上学期) 成绩详情 ---

--- 科目 1 ---
  课程名称: 大数据导论
  课程类别: 必修
  成绩: 85
  绩点 (JD): 3.5
  学分 (XF): 2.0
  任课教师: XXX
  开课部门: 计算机科学与技术学院

--- 科目 2 ---
  课程名称: 计算机网络
  课程类别: 必修
  成绩: 92
  绩点 (JD): 4.2
  学分 (XF): 3.5
  任课教师: XXX
  开课部门: 计算机科学与技术学院
...
```

```
```
