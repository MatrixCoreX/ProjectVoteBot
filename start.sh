#!/bin/sh
set -eu
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "未找到 .venv，请先执行: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

if [ ! -f .env ]; then
  echo "未找到 .env，可从 .env.example 复制: cp .env.example .env" >&2
  exit 1
fi

case "${1:-}" in
  -h|--help)
    echo "用法: $0 [-b|--background|-h|--help]"
    echo "  在后台启动 bot.py，脚本立即退出；日志追加写入 bot.log"
    echo "  环境变量 VOTE_BOT_LOG 可指定日志文件路径"
    echo "  -b / --background 与无参数相同（兼容旧用法）"
    echo "  停止: ./stop.sh"
    ;;
  -b|--background|"")
    LOG="${VOTE_BOT_LOG:-$(pwd)/bot.log}"
    nohup .venv/bin/python -u bot.py >>"$LOG" 2>&1 &
    echo "$!" > bot.pid
    echo "已在后台启动，PID $!，日志: $LOG（停止: ./stop.sh）"
    ;;
  *)
    echo "未知参数: $1  使用 $0 --help 查看说明" >&2
    exit 1
    ;;
esac
