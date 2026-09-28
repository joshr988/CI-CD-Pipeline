#!/usr/bin/env bash
set -euo pipefail
image="${1:?Provide an image reference}"
container=$(docker run -d --read-only --cap-drop ALL --security-opt no-new-privileges --tmpfs /tmp -p 127.0.0.1::8080 "$image")
trap 'docker logs "$container"; docker rm -f "$container" >/dev/null' EXIT
port=$(docker port "$container" 8080/tcp | head -n 1)
ready=false
for attempt in {1..30}; do
  if curl --fail --silent "http://${port}/health" | python3 -c 'import json,sys; assert json.load(sys.stdin)=={"status":"ok"}' 2>/dev/null; then
    ready=true
    break
  fi
  sleep 1
done
test "$ready" = true
curl --fail --silent "http://${port}/version" | python3 -c 'import json,sys; assert json.load(sys.stdin)["revision"]'
