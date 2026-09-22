#!/usr/bin/env bash
# Proves the scorer runs and that its four refusal guards fire, on fabricated data.
# Run this once at the start of a run, before spending anything:
#     bash selftest/run-selftest.sh
# Expected last line: SELFTEST PASSED
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SCORER="$HERE/../scorer/TG-score-batch.py"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fails=0

check () { # name, expected-substring, expected-exit, workdir
  local name="$1" want="$2" wantrc="$3" dir="$4"
  local out rc
  out="$(cd "$dir" && python3 "$SCORER" --config run-config.json 2>&1)"; rc=$?
  if [ "$rc" = "$wantrc" ] && printf '%s' "$out" | grep -qF -- "$want"; then
    echo "  ok    $name"
  else
    echo "  FAIL  $name (exit $rc, expected $wantrc; wanted \"$want\")"
    printf '%s\n' "$out" | sed 's/^/        /'
    fails=$((fails+1))
  fi
}

echo "self-test: scoring a six-row fabricated fixture"

cp -R "$HERE" "$TMP/clean"
check "clean fixture scores and passes its invariants" "invariants: clean" 0 "$TMP/clean"

cp -R "$HERE" "$TMP/hedged"
python3 - "$TMP/hedged/judgments.json" <<'PY'
import json,sys
p=sys.argv[1]; j=json.load(open(p))
j["competitor"]["bridgeway-staffing.test"]="Possibly a competitor - the site mentions recruiting."
json.dump(j,open(p,"w"),indent=1)
PY
check "refuses a hedged hard disqualifier" "is hedged" 1 "$TMP/hedged"

cp -R "$HERE" "$TMP/empty"
python3 - "$TMP/empty/judgments.json" <<'PY'
import json,sys
p=sys.argv[1]; j=json.load(open(p))
j["competitor"]["bridgeway-staffing.test"]="   "
json.dump(j,open(p,"w"),indent=1)
PY
check "refuses a hard disqualifier with no evidence" "has no evidence" 1 "$TMP/empty"

cp -R "$HERE" "$TMP/email"
sed -i 's/,verified,c_suite,United States/,User Managed,c_suite,United States/' \
    "$TMP/email/intermediates/verified.csv"
check "refuses an unmapped email_status" "CANNOT RUN: verified.csv" 1 "$TMP/email"

cp -R "$HERE" "$TMP/patchver"
sed -i 's/"rubric_version": "v3.1"/"rubric_version": "v3.1.1"/' "$TMP/patchver/run-config.json"
check "refuses a patch digit in rubric_version" "major.minor only" 1 "$TMP/patchver"

cp -R "$HERE" "$TMP/wrongver"
sed -i 's/"rubric_version": "v3.1"/"rubric_version": "v3.2"/' "$TMP/wrongver/run-config.json"
check "refuses a rubric version it does not implement" "This scorer implements" 1 "$TMP/wrongver"

cp -R "$HERE" "$TMP/flat"
python3 - "$TMP/flat/intermediates/matched.json" <<'PY'
import json,sys
p=sys.argv[1]
json.dump({k:{"id":v.get("id")} for k,v in json.load(open(p)).items()},open(p,"w"),indent=1)
PY
check "refuses a matched.json that cannot answer the departure test" "departure test" 1 "$TMP/flat"

if [ "$fails" = 0 ]; then echo "SELFTEST PASSED"; else echo "SELFTEST FAILED ($fails)"; exit 1; fi
