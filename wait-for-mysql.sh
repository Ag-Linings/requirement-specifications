#!/bin/bash
# wait-for-mysql.sh

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

until nc -z -v -w30 "$host" "$port"; do
  echo "MySQL is unavailable - waiting"
  sleep 2
done

echo "MySQL is up - executing command"
exec $cmd
