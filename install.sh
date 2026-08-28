#!/bin/sh
set -eu

repo="https://raw.githubusercontent.com/sileod/albert-harness/main/bin/albert"
install_dir="${ALBERT_INSTALL_DIR:-$HOME/.local/bin}"
target="$install_dir/albert"

command -v python3 >/dev/null 2>&1 || {
  echo "albert: python3 is required" >&2
  exit 1
}

mkdir -p "$install_dir"
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT HUP INT TERM
curl -fsSL "$repo" -o "$tmp"
chmod +x "$tmp"
mv "$tmp" "$target"
trap - EXIT HUP INT TERM

echo "Installed albert to $target"
case ":${PATH:-}:" in
  *":$install_dir:"*) ;;
  *) echo "Add $install_dir to PATH" ;;
esac
