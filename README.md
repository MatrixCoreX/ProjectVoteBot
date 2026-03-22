# ProjectVoteBot

Telegram 项目看板与投票机器人（基于 pyTelegramBotAPI）。

在 Telegram 里如何用机器人（命令、投票、群组等），见 **[机器人使用说明.md](./机器人使用说明.md)**。

---

## 环境要求

- Python 3.10+（当前环境为 3.12 亦可）
- 网络可访问 Telegram API

## 首次配置

### 1. 创建虚拟环境并安装依赖

在项目根目录执行：

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. 配置 Bot Token

1. 在 Telegram 中向 [@BotFather](https://t.me/BotFather) 创建机器人，获取 **Token**。
2. 在项目根目录创建 `.env`（可从示例复制）：

   ```bash
   cp .env.example .env
   ```

3. 编辑 `.env`，设置：

   ```env
   BOT_TOKEN=你的机器人Token
   ```

   **注意**：不要把真实 Token 提交到 Git；`.env` 已在 `.gitignore` 中。

## 启动方式

### 推荐：使用启动脚本（后台，脚本立即退出）

```bash
./start.sh
```

脚本会：

- 切换到项目根目录（保证能加载 `.env` 与数据文件）
- 检查 `.venv`、`.env` 是否存在
- 用 `nohup` 在**后台**启动 `bot.py`，**马上结束**，不占用当前终端
- 写入 **`bot.pid`**，标准输出与错误追加到 **`bot.log`**（可用环境变量 **`VOTE_BOT_LOG`** 指定其它日志路径）

`./start.sh -b` 与无参数行为相同（兼容旧用法）。若未赋予执行权限：`chmod +x start.sh`。

脚本为 POSIX `sh` 写法，可用 `./start.sh` 或 `sh start.sh`。查看帮助：`./start.sh --help`。

### 停止

```bash
./stop.sh
```

会先发送 **SIGTERM**，最多等待约 30 秒，仍存活则 **SIGKILL**。在 Linux 上会按**工作目录 + 命令行**识别本项目下的 `bot.py` 进程（同一目录多个实例会一并停止）。结束后会删除 `bot.pid`。若未赋予执行权限：`chmod +x stop.sh`。

### 手动启动（前台，调试用）

需要在终端里看实时日志或调试时：

```bash
cd /path/to/vote_bot
source .venv/bin/activate
python bot.py
```

或直接：

```bash
/path/to/vote_bot/.venv/bin/python /path/to/vote_bot/bot.py
```

（工作目录建议在项目根目录，以便正确读取 `.env` 与 `projects_data.json`。）

## 数据文件

- `projects_data.json`：项目与投票数据，与 `bot.py` 同目录；首次运行或文件缺失时会按逻辑初始化。
- 请定期备份该文件，避免丢失数据。

## 常见问题

| 现象 | 处理 |
|------|------|
| 提示缺少 `BOT_TOKEN` | 检查 `.env` 是否在项目根目录，且含 `BOT_TOKEN=...` |
| 提示未找到 `.venv` | 按上文「首次配置」创建虚拟环境并安装依赖 |
| 提示未找到 `.env` | 执行 `cp .env.example .env` 并填入 Token |
| `409 Conflict` / `terminated by other getUpdates request` | 同一 Token 只能有一处长轮询：在项目目录执行 `./stop.sh`，关掉其它终端/机器上的实例；若用过 Webhook，需先 `deleteWebhook` 或停用另一套服务 |

## 后台长期运行（可选）

可用 `systemd`、`screen`、`tmux` 等保持进程常驻，例如：

```bash
./start.sh
# 或仍需 tmux 时也可在会话内再执行 ./start.sh
```

具体服务化配置需按你的服务器环境自行编写单元文件或进程管理配置。
