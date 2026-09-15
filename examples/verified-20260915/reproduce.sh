#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
WORK_ROOT="${1:-$REPO/../portrait-forge-verification}"
mkdir -p "$WORK_ROOT"
WORK_ROOT="$(cd "$WORK_ROOT" && pwd)"
case "$WORK_ROOT/" in "$REPO/"*) echo "Choose an output directory outside the repository." >&2; exit 2 ;; esac
RUN="$(mktemp -d "$WORK_ROOT/portrait-run.XXXXXX")"
mkdir "$RUN/tmp"
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$RUN/tmp"
cd "$REPO"
CLI="$REPO/skill/portrait-forge/scripts/portrait.py"
BASE="$SCRIPT_DIR/baseline-plan.json"

"$PYTHON_BIN" -m unittest discover -s tests -v > "$RUN/unittest.txt" 2>&1
"$PYTHON_BIN" "$CLI" validate "$BASE" > "$RUN/validate-baseline.json"
"$PYTHON_BIN" "$CLI" compile "$BASE" > "$RUN/compile-baseline.json"
"$PYTHON_BIN" "$CLI" revise "$BASE" "$SCRIPT_DIR/lip-patch.json" --allow makeup.lip_color --request "只改唇色为低饱和酒红，所有其他已登记字段保持不变。" > "$RUN/edited-plan.json"
"$PYTHON_BIN" "$CLI" validate "$RUN/edited-plan.json" --baseline "$BASE" > "$RUN/validate-edited.json"
"$PYTHON_BIN" "$CLI" compile "$RUN/edited-plan.json" --baseline "$BASE" > "$RUN/compile-edited.json"
"$PYTHON_BIN" "$CLI" compare "$BASE" "$RUN/edited-plan.json" > "$RUN/compare.json"
"$PYTHON_BIN" "$CLI" validate examples/03-roster.json > "$RUN/validate-roster.json"
"$PYTHON_BIN" "$CLI" compile examples/03-roster.json > "$RUN/compile-roster.json"
"$PYTHON_BIN" "$CLI" compile examples/04-reference.json > "$RUN/compile-reference.json"
"$PYTHON_BIN" "$CLI" compile examples/06-partial-edited.json --baseline examples/05-partial-baseline.json > "$RUN/compile-unknown.json"
"$PYTHON_BIN" tools/install.py --dest "$RUN/skills" > "$RUN/install.txt"
(
  cd "$RUN"
  "$PYTHON_BIN" "$RUN/skills/portrait-forge/scripts/portrait.py" compile "$BASE" > "$RUN/installed-compile.json"
)
cmp "$RUN/compile-baseline.json" "$RUN/installed-compile.json"
set +e
"$PYTHON_BIN" "$CLI" compile "$RUN/edited-plan.json" > "$RUN/missing-baseline.json"
BASELINE_EXIT=$?
"$PYTHON_BIN" tools/install.py --dest "$RUN/skills" > "$RUN/overwrite.txt" 2>&1
OVERWRITE_EXIT=$?
set -e
test "$BASELINE_EXIT" -eq 1
test "$OVERWRITE_EXIT" -eq 1
printf 'Program checks passed. Evidence: %s\n' "$RUN"
