#!/usr/bin/env bash
set -euo pipefail

# ─── Config ──────────────────────────────────────────────────────────────────
REPO="https://github.com/mixgreen/llm-wiki-toolchain.git"
SKILL_NAME="llm-wiki-toolchain"

# ─── Colors ──────────────────────────────────────────────────────────────────
BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ─── Helpers ─────────────────────────────────────────────────────────────────
info()  { echo -e "${CYAN}▸${NC} $*" >&2; }
ok()    { echo -e "${GREEN}✓${NC} $*" >&2; }
warn()  { echo -e "${YELLOW}⚠${NC} $*" >&2; }
err()   { echo -e "${RED}✗${NC} $*" >&2; }

# When piped (curl | bash), stdin is the script source, not the terminal.
# We need /dev/tty for interactive prompts.
if [ -t 0 ]; then
  TTY_STDIN=0
else
  if [ ! -e /dev/tty ]; then
    err "No terminal detected and /dev/tty unavailable. Run interactively."
    exit 1
  fi
  TTY_STDIN="/dev/tty"
fi

read_input() {
  local prompt="$1"
  local result
  if [ "$TTY_STDIN" = "0" ]; then
    read -rp "$prompt" result
  else
    echo -ne "$prompt" >&2
    read -r result < /dev/tty
  fi
  echo "$result"
}

# ─── Download ────────────────────────────────────────────────────────────────
download_skill() {
  local tmpdir
  tmpdir="$(mktemp -d)"

  info "Downloading ${SKILL_NAME}..."
  if command -v git &>/dev/null; then
    git clone --depth 1 "$REPO" "$tmpdir/src" 2>/dev/null || {
      rm -rf "$tmpdir"
      err "git clone failed"
      exit 1
    }
  else
    warn "git not found, falling back to curl..."
    curl -fsSL "${REPO%.git}/archive/refs/heads/main.tar.gz" | tar xz -C "$tmpdir"
    mv "$tmpdir"/*/  "$tmpdir/src" 2>/dev/null || true
  fi

  # Clean non-essential files
  rm -rf "$tmpdir/src/.git" "$tmpdir/src/__pycache__"
  find "$tmpdir/src" -name '*.pyc' -delete 2>/dev/null || true
  find "$tmpdir/src" -name '.DS_Store' -delete 2>/dev/null || true

  ok "Download complete"
  echo "$tmpdir/src"
}

# ─── Agent definitions ──────────────────────────────────────────────────────
# id | name | install_path | instruction_file
AGENTS=(
  "claude|Claude Code|~/.claude/skills/${SKILL_NAME}|~/.claude/CLAUDE.md"
  "gemini|Gemini CLI|~/.gemini/skills/${SKILL_NAME}|~/.gemini/GEMINI.md"
  "codex|Codex CLI|~/.codex/skills/${SKILL_NAME}|~/.codex/AGENTS.md"
  "openclaw|OpenClaw|~/.openclaw/skills/${SKILL_NAME}|~/.openclaw/OPENCLAW.md"
  "hermes|Hermes Agent|~/.hermes/skills/note-taking/${SKILL_NAME}|"
)

expand_tilde() {
  local p="$1"
  echo "${p/#\~/$HOME}"
}

# ─── Interactive selection (number-based, works with piped stdin) ────────────
select_agents() {
  local count=${#AGENTS[@]}
  local -a detected_parent=()

  # Detect which agents have their parent dir
  for i in $(seq 0 $((count - 1))); do
    IFS='|' read -r _id _name _path _instr <<< "${AGENTS[$i]}"
    _path="$(expand_tilde "$_path")"
    local parent
    parent="$(dirname "$_path")"
    if [ -d "$parent" ]; then
      detected_parent+=("true")
    else
      detected_parent+=("false")
    fi
  done

  # Display menu
  echo "" >&2
  echo -e "${BOLD}Select agents to install ${SKILL_NAME} into:${NC}" >&2
  echo -e "  ${CYAN}Enter numbers separated by commas, then press Enter${NC}" >&2
  echo -e "  ${CYAN}(default: all detected agents)${NC}" >&2
  echo "" >&2

  for i in $(seq 0 $((count - 1))); do
    IFS='|' read -r _id _name _path _instr <<< "${AGENTS[$i]}"
    local num=$((i + 1))
    local tag=""
    if [ "${detected_parent[$i]}" = "true" ]; then
      tag=" ${GREEN}[detected]${NC}"
    fi
    echo -e "  ${BOLD}${num})${NC} ${_name}${tag}" >&2
    echo -e "     ${CYAN}${_path}${NC}" >&2
  done

  echo -e "  ${BOLD}$((count + 1)))${NC} All of the above" >&2
  echo -e "  ${BOLD}0)${NC} None (exit)" >&2
  echo "" >&2

  local answer
  answer="$(read_input "  Your choice: ")"

  # Parse answer
  SELECTED_INDICES=()
  if [ -z "$answer" ]; then
    # Default: select all detected
    for i in $(seq 0 $((count - 1))); do
      if [ "${detected_parent[$i]}" = "true" ]; then
        SELECTED_INDICES+=("$i")
      fi
    done
    # If none detected, select all
    if [ ${#SELECTED_INDICES[@]} -eq 0 ]; then
      for i in $(seq 0 $((count - 1))); do
        SELECTED_INDICES+=("$i")
      done
    fi
  elif [ "$answer" = "0" ]; then
    SELECTED_INDICES=()
  elif [ "$answer" = "$((count + 1))" ]; then
    for i in $(seq 0 $((count - 1))); do
      SELECTED_INDICES+=("$i")
    done
  else
    IFS=',' read -ra nums <<< "$answer"
    for n in "${nums[@]}"; do
      n="$(echo "$n" | tr -d ' ')"
      if [[ "$n" =~ ^[0-9]+$ ]] && [ "$n" -ge 1 ] && [ "$n" -le "$count" ]; then
        SELECTED_INDICES+=("$((n - 1))")
      fi
    done
  fi
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

  mkdir -p "$target_path"
  cp -R "$src"/* "$target_path"/
  ok "Installed to ${name}: ${target_path}"

  # Add loader note if instruction file is specified
  if [ -n "$instr_file" ]; then
    local loader_marker="llm-wiki-toolchain/SKILL.md"
    if [ -f "$instr_file" ] && grep -q "$loader_marker" "$instr_file" 2>/dev/null; then
      info "  Loader note already exists in ${instr_file}, skipping"
    else
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

  if [ "$id" = "hermes" ]; then
    info "  Hermes will auto-discover this skill on next session"
  fi
}

# ─── Main ────────────────────────────────────────────────────────────────────
main() {
  echo "" >&2
  echo -e "${BOLD}┌─────────────────────────────────────────┐${NC}" >&2
  echo -e "${BOLD}│   LLM Wiki Toolchain — Installer        │${NC}" >&2
  echo -e "${BOLD}└─────────────────────────────────────────┘${NC}" >&2
  echo "" >&2

  # Check prerequisites
  if ! command -v git &>/dev/null && ! command -v curl &>/dev/null; then
    err "Need git or curl to download. Install one first."
    exit 1
  fi

  # 下载
  local src
  src=$(download_skill)
  
  # 设置清理目录（用于 trap）
  CLEANUP_DIR="$(dirname "$src")"
  trap 'rm -rf "$CLEANUP_DIR"' EXIT

  echo "" >&2

  # Interactive selection
  SELECTED_INDICES=()
  select_agents AGENTS

  if [ ${#SELECTED_INDICES[@]} -eq 0 ]; then
    warn "Nothing selected. Exiting."
    exit 0
  fi

  echo "" >&2
  echo -e "${BOLD}Installing...${NC}" >&2
  echo "" >&2

  for idx in "${SELECTED_INDICES[@]}"; do
    IFS='|' read -r id name path instr <<< "${AGENTS[$idx]}"
    install_to_agent "$src" "$id" "$name" "$path" "$instr"
  done

  echo "" >&2
  echo -e "${BOLD}┌─────────────────────────────────────────┐${NC}" >&2
  echo -e "${GREEN}${BOLD}  Done! ${SKILL_NAME} installed.${NC}" >&2
  echo -e "${BOLD}└─────────────────────────────────────────┘${NC}" >&2
  echo "" >&2
  info "Update later: cd <install-path> && git pull"
  echo "" >&2
}

main "$@"
