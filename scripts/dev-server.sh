#!/usr/bin/env bash
# Local Anvil app server for craftify-library (agent / dev loop).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="$(cd "$ROOT/.." && pwd)"
VENV="$ROOT/.venv"
SERVER="$VENV/bin/anvil-app-server"
JAR="$HOME/.anvil/anvil-app-server.20260924-175441.jar"
DB_NAME="${ANVIL_PG_DB:-craftify_library_anvil}"
PORT="${ANVIL_PORT:-3030}"

if [[ ! -x "$SERVER" ]]; then
  echo "Missing venv. From craftify-library:"
  echo "  python3 -m venv .venv && . .venv/bin/activate && pip install anvil-app-server"
  exit 1
fi

# Java 21+ (bundled JAR targets modern class libraries).
if [[ -d /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home ]]; then
  export JAVA_HOME="/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
elif [[ -d /opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home ]]; then
  export JAVA_HOME="/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home"
else
  echo "Install Java 21: brew install openjdk@21"
  exit 1
fi
export PATH="$JAVA_HOME/bin:$PATH"

# pip wheel may ship a truncated JAR; full runtime belongs in ~/.anvil (~378MB).
if [[ ! -f "$JAR" ]] || [[ $(stat -f%z "$JAR" 2>/dev/null || stat -c%s "$JAR") -lt 300000000 ]]; then
  echo "Downloading Anvil App Server JAR to ~/.anvil (one-time, ~378MB)..."
  mkdir -p "$HOME/.anvil"
  curl -L -o "$JAR" \
    "https://anvil-public-assets.s3.eu-west-2.amazonaws.com/app-server/anvil-app-server.20260924-175441.jar"
fi
# Prefer ~/.anvil over a broken copy inside site-packages.
PKG_JAR="$(find "$VENV/lib" -name 'anvil-app-server.20260924-175441.jar' -print -quit 2>/dev/null || true)"
if [[ -n "$PKG_JAR" ]] && [[ $(stat -f%z "$PKG_JAR" 2>/dev/null || stat -c%s "$PKG_JAR") -lt 300000000 ]]; then
  rm -f "$PKG_JAR"
fi

# App directory must be a valid Python package name (underscore, not hyphen).
ln -sfn "$(basename "$ROOT")" "$WORKSPACE/craftify_library"

# Sibling dependency checkouts (GitHub mirrors match Anvil dependency apps).
ensure_dep() {
  local dir="$1" repo="$2" tag="$3"
  local path="$WORKSPACE/$dir"
  if [[ ! -d "$path/client_code" ]]; then
    echo "Cloning $dir from GitHub ($tag)..."
    git clone --depth 1 --branch "$tag" "$repo" "$path"
  fi
  ln -sfn "$dir" "$WORKSPACE/$dir"
}

ensure_dep tabulator_github https://github.com/anvilistas/tabulator.git v3.3.1
ln -sfn tabulator_github "$WORKSPACE/tabulator"
ensure_dep anvil_extras_github https://github.com/anvilistas/anvil-extras.git v3.6.3
ln -sfn anvil_extras_github "$WORKSPACE/anvil_extras"
ensure_dep routing https://github.com/anvil-works/routing.git master

if ! pg_isready -q 2>/dev/null; then
  echo "Starting PostgreSQL (Homebrew)..."
  brew services start postgresql@14 2>/dev/null || brew services start postgresql
  sleep 2
fi
psql -d postgres -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 \
  || psql -d postgres -c "CREATE DATABASE \"$DB_NAME\";"

cd "$WORKSPACE"
exec "$SERVER" \
  --app craftify_library \
  --port "$PORT" \
  --auto-migrate \
  --origin "http://localhost:$PORT" \
  --database "jdbc:postgresql://localhost/$DB_NAME?user=$(whoami)" \
  --dep-id TGQCF3WT6FVL2EM2=tabulator \
  --dep-id C6ZZPAPN4YYF5NVJ=anvil_extras \
  --dep-id dep_d6bjyrizg8vut=tabulator \
  --dep-id dep_kfkrna97mklbm=anvil_extras \
  --dep-id 3PIDO5P3H4VPEMPL=routing \
  --dep-id dep_routing=routing \
  --dep-id dep_3cbnzlajrrq4tg=routing \
  --dep-id dep_2lwdiwk1dh75u=routing
