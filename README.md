## 项目简介

本项目是一个基于 Telegram 的异步机器人，用于链上充值与 TRON 能量租赁，支持：
- 用户绑定 TRC 钱包地址（校验是否已在链上激活）
- TRX / USDT 充值并自动监听链上转账入账
- 余额管理与能量租赁（自动调用第三方能量租赁 API）
- 邀请返佣机制
- 管理员群发消息
- 多语言支持（中文 / 英文）

## 技术栈

- 语言：Python 3.10+
- Telegram Bot：`pyTelegramBotAPI`（异步 `AsyncTeleBot`）
- ORM / 数据库：Tortoise ORM + PostgreSQL (`asyncpg`)
- HTTP 客户端：`aiohttp`（异步） + 少量 `requests`
- 区块链与外部服务：
  - TronScan API（地址校验、转账查询）
  - CryptoCompare API（TRX 汇率）
  - 自有能量租赁服务 API
- 日志：Python 标准库 `logging`（彩色控制台输出）
- 国际化：`gettext`

## 目录结构

- `main.py`：程序入口，统一启动数据库、Bot 和后台监听任务
- `config.py`：全局配置（路径、Token、管理员 ID、数据库连接、价格配置、外部 API 配置等）
- `tb/`
  - `bot.py`：初始化 `AsyncTeleBot`，注册所有 handlers 和 filters，启动轮询
  - `handlers/`
    - `user.py`：用户侧业务逻辑（/start、充值流程、能量租赁、语言切换、邀请返佣等）
    - `admin.py`：管理员功能（群发消息）
    - `group.py`：群内欢迎新成员
  - `filters/`
    - `admin.py`：管理员过滤器（基于 `settings.ADMIN_ID`）
  - `states/`
    - `__init__.py`：用户与管理员的状态定义（用于多步对话）
- `database/`
  - `mdb.py`：Tortoise ORM 初始化与连接管理
  - `models/`
    - `__init__.py`：时间戳抽象基类 `TimestampMixin`
    - `user.py`：用户模型（uid、昵称、余额、钱包地址、语言、邀请人）
    - `order.py`：订单模型（充值 / 能量订单，金额、状态、类型等）
    - `wallet.py`：收款钱包模型（TRX / USDT 钱包与启用状态）
  - `crud/`
    - `order.py`：订单相关的 CRUD 操作（如创建充值订单）
- `utils/`
  - `core/`
    - `functions.py`：汇率获取、钱包地址校验、能量租赁 API 调用等核心工具函数
    - `task.py`：后台监听器 `Listens`（监听链上转账、订单过期处理等）
  - `log/`
    - `logger.py`：全局日志配置
    - `__init__.py`：导出 `logger`
- 其他：
  - `locale/`：多语言翻译文件目录（`gettext` 使用）
  - `output/`：生成收款二维码图片的输出目录（运行时创建）

## 核心功能说明

- **用户注册与首页**
  - 通过 `/start` 命令自动创建或更新用户信息（包含邀请人 ID）
  - 展示余额、动态电价（根据时间段）、钱包地址等信息
  - 提供“能量租赁/充值/推广返现/切换语言/群与客服链接”等快捷按钮

- **钱包绑定与地址校验**
  - 用户向 Bot 发送 TRC 钱包地址
  - 通过 TronScan API 检查地址是否已激活，激活后才允许绑定

- **充值流程（TRX / USDT）**
  - 用户选择充值类型并输入金额
  - 系统创建待支付订单，分配收款钱包并生成二维码
  - 后台定时轮询 TronScan 转账记录，匹配成功后自动：
    - 更新订单状态为成功
    - 给用户增加余额
    - 按配置比例给邀请人发放返佣

- **能量租赁**
  - 用户输入能量数量，系统按当前电价计算费用
  - 余额充足时，调用自有能量租赁 API 完成租赁
  - 扣减余额并提示能量到帐和有效期

- **订单过期管理**
  - 所有待支付订单有 60 分钟有效期
  - 后台任务定期扫描，超时未支付的订单标记为过期（当前实现是直接删除，可按需改为状态更新）

- **管理员功能**
  - 只有配置的 `ADMIN_ID` 可以使用管理员命令
  - 当前支持一键对所有用户群发消息

## 部署与运行

### 1. 环境准备

- 安装 Python 3.10+
- 安装 PostgreSQL，并创建数据库（默认库名 `bot`，可在 `config.py` 中调整）
- 创建虚拟环境并安装依赖（请根据实际依赖文件调整）：
```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

