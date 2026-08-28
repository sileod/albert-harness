#!/bin/sh
set -eu

repo="https://raw.githubusercontent.com/sileod/albert-harness/main/bin"
install_dir="${ALBERT_INSTALL_DIR:-$HOME/.local/bin}"
target="$install_dir/albert"
spawn_target="$install_dir/albert-spawn"

command -v python3 >/dev/null 2>&1 || {
  echo "albert: python3 is required" >&2
  exit 1
}

mkdir -p "$install_dir"
tmp="$(mktemp)"
spawn_tmp="$(mktemp)"
trap 'rm -f "$tmp" "$spawn_tmp"' EXIT HUP INT TERM
curl -fsSL "$repo/albert" -o "$tmp"
curl -fsSL "$repo/albert-spawn" -o "$spawn_tmp"
chmod +x "$tmp" "$spawn_tmp"
mv "$tmp" "$target"
mv "$spawn_tmp" "$spawn_target"
trap - EXIT HUP INT TERM

echo "Installed albert to $target"
case ":${PATH:-}:" in
  *":$install_dir:"*) ;;
  *) echo "Add $install_dir to PATH" ;;
esac
