#!/bin/sh
# 부하 테스트(TST-03): 동시 연결 100 → 1,000 → 10,000 단계, 단계마다 30초씩 3회.
# 성능 수치는 ASan을 끈 일반 빌드로 잰다 (TST-06). 원본 출력은 tests/results/에 저장한다.
# 사용법: tests/bench.sh [서버 바이너리]
set -e
cd "$(dirname "$0")/.."
BINARY=${1:-build/webserver}
PORT=${PORT:-18700}
DURATION=${DURATION:-30}
RUNS=${RUNS:-3}
LEVELS=${LEVELS:-"100 1000 10000"}
RESULTS=${RESULTS:-tests/results}

# wrk도 연결마다 fd를 쓰므로 이 터미널의 fd 한도도 올린다
ulimit -n 65000 2>/dev/null || ulimit -n "$(ulimit -Hn)"
mkdir -p "$RESULTS"
ROOT=$(mktemp -d)
python3 -c "print('<html><body>' + 'hello ' * 300 + '</body></html>')" > "$ROOT/index.html"

"$BINARY" --root "$ROOT" --port "$PORT" --log-level error &
SERVER_PID=$!
trap 'kill -INT $SERVER_PID 2>/dev/null; rm -rf "$ROOT"' EXIT
sleep 1

for level in $LEVELS; do
    for run in $(seq 1 "$RUNS"); do
        echo "연결 $level, ${run}회차"
        wrk -t4 -c"$level" -d"${DURATION}s" --latency \
            "http://127.0.0.1:$PORT/index.html" > "$RESULTS/wrk_c${level}_run${run}.txt"
    done
done
python3 tests/summarize_wrk.py "$RESULTS" | tee "$RESULTS/wrk_summary.md"
