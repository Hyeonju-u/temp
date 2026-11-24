#!/usr/bin/env python3
"""wrk 원본 출력(tests/results/wrk_c*_run*.txt)에서 단계별 중앙값을 뽑아 표로 만든다."""
import glob
import os
import re
import statistics
import sys


def to_milliseconds(text):
    number = float(re.match(r"[\d.]+", text).group(0))
    for suffix, scale in (("us", 0.001), ("ms", 1.0), ("s", 1000.0)):
        if text.endswith(suffix):
            return number * scale
    return number


def parse(path):
    text = open(path).read()
    rps = float(re.search(r"Requests/sec:\s+([\d.]+)", text).group(1))
    p50 = to_milliseconds(re.search(r"\s50%\s+([\d.]+\w+)", text).group(1))
    p99 = to_milliseconds(re.search(r"\s99%\s+([\d.]+\w+)", text).group(1))
    errors = re.search(r"Socket errors: connect (\d+), read (\d+), write (\d+), timeout (\d+)", text)
    error_count = sum(int(v) for v in errors.groups()) if errors else 0
    non_ok = re.search(r"Non-2xx or 3xx responses: (\d+)", text)
    error_count += int(non_ok.group(1)) if non_ok else 0
    return rps, p50, p99, error_count


def main(directory):
    levels = sorted({int(re.search(r"wrk_c(\d+)_", p).group(1)) for p in glob.glob(os.path.join(directory, "wrk_c*_run*.txt"))})
    print("| 동시 연결 | 측정 횟수 | 처리량 중앙값(req/s) | p50 중앙값(ms) | p99 중앙값(ms) | 에러 합계 |")
    print("|---|---|---|---|---|---|")
    for level in levels:
        rows = [parse(p) for p in sorted(glob.glob(os.path.join(directory, "wrk_c%d_run*.txt" % level)))]
        print("| %d | %d | %.0f | %.2f | %.2f | %d |" % (
            level, len(rows), statistics.median(r[0] for r in rows), statistics.median(r[1] for r in rows),
            statistics.median(r[2] for r in rows), sum(r[3] for r in rows)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tests/results")
