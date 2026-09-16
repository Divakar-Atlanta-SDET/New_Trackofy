#!/bin/bash
# Runs the full prod regression suite in small, serial (no xdist) batches so
# only one browser process is ever alive at a time -- avoids the resource
# exhaustion that was freezing the machine under -n 4 parallel execution.
# Each batch gets its own log file so progress survives any single crash/
# interruption: on resume, just skip batches whose log already has EXIT_CODE=.
cd "/c/Users/Vaibhav/OneDrive/Desktop/asset managmeent testing"
PY="./venv1/Scripts/python.exe"
shopt -s nullglob

declare -a BATCHES=(
  "smoke|Tests/Smoke"
  "func_admin|Tests/functional/test_admin_*.py"
  "func_reports|Tests/functional/test_reports_*.py"
  "func_misc|Tests/functional/test_misc_*.py"
  "func_vt|Tests/functional/test_vt_*.py"
  "func_settings|Tests/functional/test_settings_*.py"
  "func_home|Tests/functional/test_home_*.py"
  "func_login|Tests/functional/test_login_*.py"
  "func_unit|Tests/functional/test_unit_*.py"
  "func_tracking|Tests/functional/test_tracking_*.py"
  "func_dashboard|Tests/functional/test_dashboard_*.py"
  "func_main|Tests/functional/test_main_*.py"
  "func_can|Tests/functional/test_can_*.py"
  "positive|Tests/positive"
  "negative|Tests/negative"
  "edgecase|Tests/edgecase"
  "security|Tests/security"
  "crud|Tests/CRUD"
  "admin_panel_func|Tests/Admin Panel/functional"
  "admin_panel_sec|Tests/Admin Panel/security"
  "asset_management|Tests/asset_management"
)

for entry in "${BATCHES[@]}"; do
  name="${entry%%|*}"
  path_pattern="${entry#*|}"
  log="batch_logs/${name}.log"

  if grep -q "^EXIT_CODE=" "$log" 2>/dev/null; then
    echo "=== SKIP $name (already completed, see $log) ==="
    continue
  fi

  # Only glob-expand patterns that actually contain wildcard characters --
  # unquoted expansion word-splits on spaces too, which would break the
  # literal "Tests/Admin Panel/functional" path (no glob chars, but a space).
  case "$path_pattern" in
    *[*?]*)
      args=($path_pattern)
      ;;
    *)
      args=("$path_pattern")
      ;;
  esac

  echo "=== RUNNING $name (${#args[@]} path(s)) ==="
  "$PY" -m pytest --env=prod -v "${args[@]}" > "$log" 2>&1
  echo "EXIT_CODE=$?" >> "$log"
  echo "=== DONE $name, $(grep EXIT_CODE "$log" | tail -1) ==="
done

echo "ALL BATCHES COMPLETE"
