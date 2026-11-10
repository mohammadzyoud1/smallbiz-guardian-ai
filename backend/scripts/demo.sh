#!/usr/bin/env bash
set -e

API="http://127.0.0.1:8000"
FILE="${1:-data/synthetic/corner.csv}"

echo "== Health"
curl -s "$API/health"
echo

echo "== Upload $FILE"
RESPONSE=$(curl -s -F "file=@$FILE" "$API/upload")
SESSION=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['session_id'])")
echo "session: $SESSION"

echo "== Forecast"
curl -s "$API/forecast?session_id=$SESSION" | python -c "import sys, json; d = json.load(sys.stdin); print('forecast net, first 4 weeks:', d['net']['forecast'][:4])"

echo "== Flags"
curl -s "$API/flags?session_id=$SESSION" | python -c "
import sys, json
d = json.load(sys.stdin)
for name, value in d.items():
    if isinstance(value, dict):
        print(f\"{name:<28} flag={value.get('flag')}  {value.get('reason')}\")
"

echo "== Scenario: slow season"
curl -s -X POST "$API/scenario" -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION\", \"name\": \"slow_season\", \"drop\": 0.3, \"start\": 3, \"length\": 4}" \
  | python -c "import sys, json; d = json.load(sys.stdin); print('change:', d['change'])"

echo "== Scenario: cost shock"
curl -s -X POST "$API/scenario" -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION\", \"name\": \"cost_shock\", \"amount\": 3000, \"week\": 4}" \
  | python -c "import sys, json; d = json.load(sys.stdin); print('change:', d['change'])"

echo "== Scenario: decision lever"
curl -s -X POST "$API/scenario" -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION\", \"name\": \"decision_lever\", \"price_change\": 0.1, \"demand_response\": 0.5, \"extra_cost\": 200, \"week\": 3}" \
  | python -c "import sys, json; d = json.load(sys.stdin); print('change:', d['change'], '| break-even lift:', d.get('break_even_lift'))"

echo "== Done"