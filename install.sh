#!/bin/sh
set -eu

repo="${HARNESS_LINK_RAW_BASE:-https://raw.githubusercontent.com/sileod/albert-harness/main/bin}"
install_dir="${HARNESS_LINK_INSTALL_DIR:-${HARNESS_INSTALL_DIR:-${ALBERT_INSTALL_DIR:-$HOME/.local/bin}}}"

command -v python3 >/dev/null 2>&1 || {
  echo "harness-link: python3 is required" >&2
  exit 1
}

mkdir -p "$install_dir"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT HUP INT TERM

for name in harness-link harness-link-spawn albert albert-spawn nim nim-spawn; do
  curl -fsSL "$repo/$name" -o "$tmp_dir/$name"
  chmod +x "$tmp_dir/$name"
  mv "$tmp_dir/$name" "$install_dir/$name"
done

trap - EXIT HUP INT TERM

echo "Installed Harness Link providers (albert, nim) to $install_dir"
case ":${PATH:-}:" in
  *":$install_dir:"*) ;;
  *) echo "Add $install_dir to PATH" ;;
esac
