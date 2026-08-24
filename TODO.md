# 项目交接说明

## 项目简介

跨校区文件交接管理系统 — 佛山南海校区 ↔ 广州石牌校区 文件转交追踪与确认平台。

两校区负责人通过本系统登记校车转交的文件，系统自动发微信通知对方，对方收到实物后在线确认，全程留痕。

## 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 后端 | FastAPI + SQLAlchemy + SQLite | ✅ 已完成 |
| 通知 | 企业微信群机器人 Webhook | ✅ 已完成 |
| 定时任务 | APScheduler | ✅ 已完成 |
| 前端 | **Vue 3 + Element Plus + Pinia + Axios** | ❌ 待开发 |

## 后端已完成（100%）

后端接口共 **26 个**，全部已开发并测试通过。

### 接口清单

| 模块 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 鉴权 | /api/auth/login | POST | 登录 |
| | /api/auth/me | GET | 获取当前用户 |
| | /api/auth/change-password | POST | 修改密码 |
| 文件 | /api/files/upload | POST | 上传文件（多文件） |
| | /api/files/{id}/download | GET | 下载文件 |
| | /api/files/{id} | DELETE | 删除文件 |
| 转交单 | /api/transfers | POST | 发起转交单 |
| | /api/transfers | GET | 列表（分页+筛选+搜索） |
| | /api/transfers/{id} | GET | 详情 |
| | /api/transfers/{id} | PUT | 编辑 |
| | /api/transfers/{id}/cancel | POST | 撤回 |
| | /api/transfers/{id}/confirm | POST | 确认收到 |
| | /api/transfers/{id}/exception | POST | 上报异常 |
| 校车班次 | /api/buses | GET | 班次列表（可按校区过滤） |
| | /api/buses/{id} | GET | 班次详情 |
| | /api/buses | POST | 新增班次（管理员） |
| | /api/buses/{id} | PUT | 编辑班次（管理员） |
| | /api/buses/{id} | DELETE | 删除班次（管理员） |
| 统计 | /api/stats/dashboard | GET | 首页仪表盘数据 |
| | /api/stats/trend | GET | 近 N 天趋势（折线图用） |
| | /api/stats/export | GET | 导出 Excel |
| 通知测试 | /api/notification/test | POST | 发送测试消息 |

### 数据库（5 张表）

1. **users** — 用户表（南海/石牌负责人）
2. **transfers** — 转交单表（核心）
3. **transfer_files** — 转交附件表
4. **bus_schedules** — 校车班次表
5. **operation_logs** — 操作日志表

### 枚举类型

- `Campus`：nanhai（南海）/ shipai（石牌）
- `TransferStatus`：pending（待接收）/ confirmed（已确认）/ overdue（已逾期）/ exception（异常）/ cancelled（已撤回）
- `FileType`：admin（行政）/ teaching（教学）/ student（学生）/ finance（财务）/ other（其他）
- `Urgency`：normal（普通）/ urgent（加急）/ critical（特急）

### 初始账号

| 校区 | 用户名 | 密码 |
|------|--------|------|
| 南海校区 | nanhai | admin123 |
| 石牌校区 | shipai | admin123 |

### 自动编号规则

`NH-SP-20260824-001` — 出发地-目的地-日期-当日序号

### 微信通知场景

1. **新建转交单** → 通知对方校区查收
2. **确认签收** → 通知发起人已收到
3. **上报异常** → 通知发起人核实
4. **逾期提醒** → 定时任务自动检测，通知接收方

### 定时任务

- 每 30 分钟扫描一次
- 预计到达时间 + OVERDUE_HOURS（默认3小时）后仍未确认 → 标记为逾期 + 发微信提醒

### 接口文档

启动后端后访问：`http://localhost:8000/docs` （交互式 Swagger 文档，可直接调试）

---

## 未完成部分（前端开发）

### 需要做的页面

| 页面 | 路径 | 优先级 | 说明 |
|------|------|--------|------|
| 登录页 | /login | P0 | 用户名密码登录 |
| 布局框架 | / | P0 | 侧边栏 + 顶栏 + 内容区 |
| 首页仪表盘 | /dashboard | P0 | 统计卡片 + 趋势图 + 待办列表 |
| 发起转交单 | /transfers/create | P0 | 表单 + 文件上传 + 班次选择 |
| 转交单列表 | /transfers | P0 | 表格 + 筛选 + 搜索 + 分页 + 导出 |
| 转交单详情 | /transfers/:id | P0 | 详情展示 + 确认/撤回/异常操作按钮 |
| 校车班次管理 | /buses | P1 | 班次增删改查（管理员可见） |
| 个人中心 | /profile | P1 | 修改密码、个人信息 |

### 技术选型建议

```
Vue 3          ← 框架（Composition API + <script setup>）
Vite           ← 构建工具（比 webpack 快很多）
Element Plus   ← UI 组件库（表格、表单、弹窗等现成组件）
Pinia          ← 状态管理（存用户信息、Token 等）
Vue Router     ← 路由管理
Axios          ← HTTP 请求封装（统一加 Token、统一错误处理）
ECharts        ← 图表库（仪表盘趋势图用，可选，用 Element Plus 简单图也行）
```

### 前端目录结构建议

```
frontend/
├── public/
├── src/
│   ├── api/              # 接口封装（按模块分文件）
│   │   ├── auth.js
│   │   ├── transfer.js
│   │   ├── file.js
│   │   ├── bus.js
│   │   └── stats.js
│   ├── assets/           # 静态资源
│   ├── components/       # 公共组件
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── stores/           # Pinia 状态
│   │   └── user.js
│   ├── utils/            # 工具函数
│   │   ├── request.js    # Axios 封装
│   │   └── format.js     # 时间/枚举格式化
│   ├── views/            # 页面
│   │   ├── login/
│   │   ├── layout/
│   │   ├── dashboard/
│   │   ├── transfer/
│   │   ├── bus/
│   │   └── profile/
│   ├── App.vue
│   └── main.js
├── index.html
├── package.json
└── vite.config.js
```

### 关键功能点说明

1. **登录鉴权**
   - 登录成功后 Token 存 localStorage
   - Axios 请求拦截器自动加 `Authorization: Bearer <token>`
   - 响应拦截器捕获 401 → 跳回登录页
   - 路由守卫：未登录不能进内部页面

2. **文件上传**
   - 用 Element Plus 的 `el-upload` 组件
   - 上传后拿到文件 ID 列表，提交转交单时带上 `file_ids`

3. **转交单状态展示**
   - 用 `el-tag` 不同颜色区分状态
   - 操作按钮按状态和校区显示（比如只有接收校区的人能看到"确认收到"按钮）

4. **筛选查询**
   - 列表页顶部放筛选表单（状态、类型、紧急程度、关键词、日期范围）
   - 用 `el-table` + `el-pagination` 做表格分页

5. **移动端适配**
   - Element Plus 自带响应式
   - 负责人可能手机上查收通知，至少列表和详情页要在手机上能用

---

## 本地开发环境搭建

### 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（首次运行）
python -m app.init_db

# 启动开发服务（带热重载）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- 后端地址：http://localhost:8000
- 接口文档：http://localhost:8000/docs

### 前端启动（待开发）

```bash
cd frontend
npm install
npm run dev
```

- 前端地址：http://localhost:5173
- Vite 配置代理：`/api` 转发到 `http://localhost:8000`，避免跨域

---

## 配置说明

在 `backend/.env` 中配置（复制 `.env.example` 为 `.env`）：

```env
DATABASE_URL=sqlite:///./campus_file.db
SECRET_KEY=你的密钥（生产环境务必修改）
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=52428800
WECHAT_WEBHOOK_URL=企业微信群机器人Webhook地址
OVERDUE_HOURS=3
```

---

## 代码仓库

https://github.com/Radiant927/All-in-one-Student-Service---File-Management

当前只有 `backend/` 目录，`frontend/` 目录待创建。
