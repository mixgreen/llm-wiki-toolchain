#!/usr/bin/env bash
set -euo pipefail

# ─── Config ──────────────────────────────────────────────────────────────────
REPO="https://github.com/mixgreen/llm-wiki-toolchain.git"
SKILL_NAME="llm-wiki-toolchain"

# Agent definitions: id|display_name|install_path|instruction_file
AGENTS=(
  "claude|Claude Code|~/.claude/skills/${SKILL_NAME}|~/.claude/CLAUDE.md"
  "gemini|Gemini CLI|~/.gemini/skills/${SKILL_NAME}|~/.gemini/GEMINI.md"
  "codex|Codex CLI|~/.codex/skills/${SKILL_NAME}|~/.codex/AGENTS.md"
  "openclaw|OpenClaw|~/.openclaw/skills/${SKILL_NAME}|~/.openclaw/OPENCLAW.md"
  "hermes|Hermes Agent|~/.hermes/skills/note-taking/${SKILL_NAME}|"
)

# ─── Colors ──────────────────────────────────────────────────────────────────
BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ─── Helpers ─────────────────────────────────────────────────────────────────
info()  { echo -e "${CYAN}▸${NC} $*"; }
ok()    { echo -e "${GREEN}✓${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠${NC} $*"; }
err()   { echo -e "${RED}✗${NC} $*"; }

expand_tilde() {
  local p="$1"
  echo "${p/#\~/$HOME}"
}

# ─── Download ────────────────────────────────────────────────────────────────
download_skill() {
  local tmpdir
  tmpdir="$(mktemp -d)"
  trap 'rm -rf "$tmpdir"' EXIT

  info "Downloading ${SKILL_NAME}..."
  if command -v git &>/dev/null; then
    git clone --depth 1 "$REPO" "$tmpdir/src" 2>/dev/null
  else
    warn "git not found, falling back to curl..."
    curl -fsSL "${REPO%.git}/archive/refs/heads/main.tar.gz" | tar xz -C "$tmpdir"
    mv "$tmpdir"/*/  "$tmpdir/src"
  fi

  # Clean non-essential files
  rm -rf "$tmpdir/src/.git" "$tmpdir/src/__pycache__"
  find "$tmpdir/src" -name '*.pyc' -delete 2>/dev/null || true
  find "$tmpdir/src" -name '.DS_Store' -delete 2>/dev/null || true

  echo "$tmpdir/src"
}

# ─── Detect installed agents ────────────────────────────────────────────────
detect_agents() {
  local detected=()
  for entry in "${AGENTS[@]}"; do
    IFS='|' read -r id name path _ <<< "$entry"
    path="$(expand_tilde "$path")"
    # Check if the parent dir exists (e.g., ~/.claude exists → Claude Code likely installed)
    local parent
    parent="$(dirname "$path")"
    if [ -d "$parent" ]; then
      detected+=("$entry")
    fi
  done
  printf '%s\n' "${detected[@]}"
}

# ─── Interactive checkbox selection ─────────────────────────────────────────
# Pure bash multi-select with arrow keys + space to toggle
select_agents() {
  local -a entries=("$@")
  local count=${#entries[@]}
  local -a selected=()
  local cursor=0

  # Initialize: auto-select all detected agents
  for i in $(seq 0 $((count - 1))); do
    selected+=("true")
  done

  # Hide cursor
  tput civis 2>/dev/null || true
  trap 'tput cnorm 2>/dev/null || true' RETURN

  draw_menu() {
    # Move cursor to start of menu
    for i in $(seq 1 $((count + 2))); do
      echo -ne "\033[1A\033[2K"
    done
    print_menu
  }

  print_menu() {
    echo -e "${BOLD}Select agents to install ${SKILL_NAME} into:${NC}"
    echo -e "  ${CYAN}(↑↓ navigate, Space toggle, Enter confirm)${NC}"
    for i in $(seq 0 $((count - 1))); do
      IFS='|' read -r id name path _ <<< "${entries[$i]}"
      local marker=" "
      [ "${selected[$i]}" = "true" ] && marker="●"
      local cursor_mark="  "
      [ "$i" -eq "$cursor" ] && cursor_mark="▸ "
      local check
      if [ "${selected[$i]}" = "true" ]; then
        check="${GREEN}[${marker}]${NC}"
      else
        check="[${marker}]"
      fi
      echo -e "  ${cursor_mark}${check} ${BOLD}${name}${NC}  ${CYAN}${path}${NC}"
    done
  }

  print_menu

  while true; do
    read -rsn1 key
    case "$key" in
      $'\x1b')  # Escape sequence (arrow keys)
        read -rsn2 rest
        case "$rest" in
          '[A')  # Up
            cursor=$(( (cursor - 1 + count) % count ))
            ;;
          '[B')  # Down
            cursor=$(( (cursor + 1) % count ))
            ;;
        esac
        ;;
      ' ')  # Space: toggle
        if [ "${selected[$cursor]}" = "true" ]; then
          selected[$cursor]="false"
        else
          selected[$cursor]="true"
        fi
        ;;
      '')  # Enter: confirm
        break
        ;;
    esac
    draw_menu
  done

  # Return selected indices
  local result=()
  for i in $(seq 0 $((count - 1))); do
    if [ "${selected[$i]}" = "true" ]; then
      result+=("$i")
    fi
  done
  echo "${result[@]}"
}

# ─── Install to one agent ───────────────────────────────────────────────────
install_to_agent() {
  local src="$1"
  local id="$2"
  local name="$3"
  local target_path="$4"
  local instr_file="$5"

  target_path="$(expand_tilde "$target_path")"
  instr_file="$(expand_tilde "$instr_file")"

  # Create target directory
  mkdir -p "$target_path"

  # Copy files
  cp -R "$src"/* "$target_path"/
  ok "Installed to ${name}: ${target_path}"

  # Add loader note if instruction file is specified and doesn't already mention us
  if [ -n "$instr_file" ] && [ -f "$instr_file" ] 2>/dev/null || [ -n "$instr_file" ]; then
    local loader_marker="llm-wiki-toolchain/SKILL.md"
    if [ -n "$instr_file" ] && [ -f "$instr_file" ]; then
      if grep -q "$loader_marker" "$instr_file" 2>/dev/null; then
        info "  Loader note already exists in ${instr_file}, skipping"
        return
      fi
    fi

    if [ -n "$instr_file" ]; then
      mkdir -p "$(dirname "$instr_file")"
      cat >> "$instr_file" <<EOF

## Agent skills — LLM Wiki Toolchain

When working with Obsidian LLM Wiki knowledge bases, load and follow:
\`${target_path}/SKILL.md\`.

Resolve linked files relative to that directory:
- scripts/init.py
- scripts/lint.py
- templates/
- references/
EOF
      ok "  Added loader note to ${instr_file}"
    fi
  fi

  # Hermes: auto-discovered, no instruction file needed
  if [ "$id" = "hermes" ]; then
    info "  Hermes will auto-discover this skill on next session"
  fi
}

# ─── Main ────────────────────────────────────────────────────────────────────
main() {
  echo ""
  echo -e "${BOLD}┌─────────────────────────────────────────┐${NC}"
  echo -e "${BOLD}│   LLM Wiki Toolchain — Installer        │${NC}"
  echo -e "${BOLD}└─────────────────────────────────────────┘${NC}"
  echo ""

  # Check prerequisites
  if ! command -v git &>/dev/null && ! command -v curl &>/dev/null; then
    err "Need git or curl to download. Install one first."
    exit 1
  fi

  # Download
  local src
  src="$(download_skill)"
  ok "Downloaded to ${src}"
  echo ""

  # Detect installed agents
  local -a detected=()
  while IFS= read -r line; do
    [ -n "$line" ] && detected+=("$line")
  done < <(detect_agents)

  if [ ${#detected[@]} -eq 0 ]; then
    # No agents detected, offer all
    warn "No agent directories detected. Showing all options."
    detected=("${AGENTS[@]}")
  fi

  # Interactive selection
  local -a selected_indices
  read -ra selected_indices < <(select_agents "${detected[@]}")

  if [ ${#selected_indices[@]} -eq 0 ]; then
    warn "Nothing selected. Exiting."
    exit 0
  fi

  echo ""
  echo -e "${BOLD}Installing...${NC}"
  echo ""

  for idx in "${selected_indices[@]}"; do
    IFS='|' read -r id name path instr <<< "${detected[$idx]}"
    install_to_agent "$src" "$id" "$name" "$path" "$instr"
  done

  echo ""
  echo -e "${BOLD}┌─────────────────────────────────────────┐${NC}"
  echo -e "${GREEN}${BOLD}  Done! ${SKILL_NAME} installed.${NC}"
  echo -e "${BOLD}└─────────────────────────────────────────┘${NC}"
  echo ""
  info "Update later: cd <install-path> && git pull"
  echo ""
}

main "$@"
