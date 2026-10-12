#!/usr/bin/env bash
# Start a disposable, socket-only MySQL server and the local Project 60 app.
# This never opens or changes the Mac's existing MySQL installation/data.
set -euo pipefail
cd "$(dirname "$0")/.."

for command in mysqld mysql mysqladmin; do
  command -v "$command" >/dev/null || { echo "Missing $command. Install MySQL first."; exit 1; }
done
[[ -x .venv/bin/python ]] || { echo "Create .venv using docs/review-3/README.md first."; exit 1; }

demo_dir=$(mktemp -d /tmp/dbms-pbl-video.XXXXXX)
socket="$demo_dir/mysql.sock"
mkdir "$demo_dir/data"

cleanup() {
  if [[ -S "$socket" ]]; then
    mysqladmin --no-defaults --protocol=SOCKET --socket="$socket" \
      --user=root shutdown >/dev/null 2>&1 || true
  fi
  echo "Stopped the isolated demo server. Its temporary files are in $demo_dir."
}
trap cleanup EXIT

echo "Preparing a fresh, isolated MySQL demo..."
mysqld --no-defaults --initialize-insecure --datadir="$demo_dir/data" \
  --log-error="$demo_dir/init.log"
if ! mysqld --no-defaults --datadir="$demo_dir/data" --socket="$socket" \
    --pid-file="$demo_dir/mysql.pid" --log-error="$demo_dir/server.log" \
    --skip-networking --daemonize; then
  cat "$demo_dir/server.log"
  exit 1
fi

mysql --no-defaults --protocol=SOCKET --socket="$socket" --user=root \
  -e 'CREATE DATABASE disaster_relief CHARACTER SET utf8mb4'
mysql --no-defaults --protocol=SOCKET --socket="$socket" --user=root \
  disaster_relief < database/schema.sql
mysql --no-defaults --protocol=SOCKET --socket="$socket" --user=root \
  disaster_relief < database/seed.sql

export DB_SOCKET="$socket" DB_USER=root DB_PASSWORD= DB_NAME=disaster_relief APP_PORT=5055
echo "Demo ready: http://127.0.0.1:5055"
echo "Keep this Terminal open. Press Ctrl+C after recording to stop the demo."
.venv/bin/python -m app.web
