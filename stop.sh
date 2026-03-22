#!/bin/sh
set -eu
cd "$(dirname "$0")"
ROOT=$(pwd)
ROOT_CANON=$(readlink -f "$ROOT" 2>/dev/null || echo "$ROOT")

# 工作目录为本项目目录，且命令行为「某 python + bot.py」
is_our_bot() {
  _pid=$1
  case "$_pid" in ''|*[!0-9]*) return 1 ;; esac
  [ -d "/proc/$_pid" ] || return 1
  _cwd=$(readlink -f "/proc/$_pid/cwd" 2>/dev/null) || return 1
  [ "$_cwd" = "$ROOT_CANON" ] || return 1
  _cmd=$(tr '\0' ' ' < "/proc/$_pid/cmdline" 2>/dev/null) || return 1
  echo "$_cmd" | grep -q 'bot[.]py' || return 1
  echo "$_cmd" | grep -q python || return 1
  return 0
}

collect_pids() {
  _out=""
  if [ -d /proc ]; then
    for _d in /proc/[0-9]*; do
      _p=${_d#/proc/}
      case "$_p" in *[!0-9]*) continue ;; esac
      is_our_bot "$_p" || continue
      _out="$_out $_p"
    done
  fi
  echo ${_out# }
}

PIDS=$(collect_pids)

# 非 Linux 无 /proc 时，尝试使用 bot.pid（由 ./start.sh -b 写入）
if [ -z "$PIDS" ] && [ -f bot.pid ]; then
  _p=$(tr -d ' \t\r\n' < bot.pid)
  case "$_p" in *[!0-9]*) _p="" ;; esac
  if [ -n "$_p" ] && kill -0 "$_p" 2>/dev/null; then
    PIDS=$_p
  fi
fi

if [ -z "$PIDS" ]; then
  echo "未发现运行中的 vote_bot（工作目录: $ROOT）"
  rm -f bot.pid
  exit 0
fi

for pid in $PIDS; do
  echo "正在停止 PID $pid ..."
  kill -TERM "$pid" 2>/dev/null || true
done

_i=0
while [ "$_i" -lt 30 ]; do
  _alive=""
  for pid in $PIDS; do
    kill -0 "$pid" 2>/dev/null && _alive="$_alive $pid"
  done
  _alive=${_alive# }
  [ -z "$_alive" ] && break
  _i=$((_i + 1))
  sleep 1
done

for pid in $PIDS; do
  if kill -0 "$pid" 2>/dev/null; then
    echo "PID $pid 未响应 SIGTERM，发送 SIGKILL"
    kill -KILL "$pid" 2>/dev/null || true
  fi
done

rm -f bot.pid
echo "已停止。"
