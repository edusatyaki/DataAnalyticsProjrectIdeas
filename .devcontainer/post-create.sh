#!/usr/bin/env bash
# Runs once when the Codespace is created.
set -e

# Wait for Postgres so the first psql works straight away
for i in $(seq 1 30); do
  pg_isready -q && break
  sleep 1
done

python -m ipykernel install --user --name analytics --display-name "Python (analytics)" >/dev/null

echo
echo "Ready."
echo "  Postgres : psql            (db=analytics user=analyst pw=analyst host=db)"
echo "  Jupyter  : jupyter lab --ip 0.0.0.0 --port 8888 --no-browser"
echo "  Streamlit: streamlit run app.py"
