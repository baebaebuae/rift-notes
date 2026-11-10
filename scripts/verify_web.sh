#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
export RIFT_JSDOM="${RIFT_JSDOM:-$PWD/.github/ci/node_modules/jsdom}"
node --check dist/app.js
node --check dist/forms.js
node scripts/verify.cjs
node scripts/verify_localization.cjs
node scripts/verify_latest_patch.cjs
node scripts/verify_forms.cjs
