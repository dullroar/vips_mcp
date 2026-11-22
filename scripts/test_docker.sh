#!/usr/bin/env bash
# Run me when: I want to verify the Docker build, context checks and MCP stdio tools.
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
snapshot=$(mktemp -d "${TMPDIR:-/tmp}/vips-mcp-test.XXXXXXXX")
run_name="vips-mcp-test-${snapshot##*.}"
image="vips-mcp-test:${snapshot##*.}"
built=false

cleanup() {
    local status=$?
    if "$built"; then
        docker image rm "$image" >/dev/null || true
    fi
    rm -rf -- "$snapshot"
    return "$status"
}
trap cleanup EXIT

# Copy indexed files from this worktree, including unstaged edits. The context
# checks can scan the snapshot without the linked worktree's Git metadata.
git ls-files --cached --deduplicate -z \
    | tar --create --file=- --null --no-recursion --files-from=- \
    | tar --extract --file=- --directory="$snapshot"

docker build --tag "$image" "$snapshot"
built=true
docker run --rm --name "$run_name" --network none --read-only \
    --tmpfs /tmp:rw,nosuid,nodev,mode=1777 "$image" \
    bash -ec 'python scripts/check_context.py && python -m unittest discover -s tests -v'
