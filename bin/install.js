#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const REPO = 'https://github.com/mixgreen/llm-wiki-toolchain.git';
const SKILL_NAME = 'llm-wiki-toolchain';

const AGENTS = [
  { id: 'claude',  name: 'Claude Code',  path: `~/.claude/skills/${SKILL_NAME}`,   instr: '~/.claude/CLAUDE.md' },
  { id: 'gemini',  name: 'Gemini CLI',   path: `~/.gemini/skills/${SKILL_NAME}`,   instr: '~/.gemini/GEMINI.md' },
  { id: 'codex',   name: 'Codex CLI',    path: `~/.codex/skills/${SKILL_NAME}`,    instr: '~/.codex/AGENTS.md' },
  { id: 'openclaw',name: 'OpenClaw',     path: `~/.openclaw/skills/${SKILL_NAME}`, instr: '~/.openclaw/OPENCLAW.md' },
  { id: 'hermes',  name: 'Hermes Agent', path: `~/.hermes/skills/note-taking/${SKILL_NAME}`, instr: '' },
];

function expandTilde(p) {
  return p.replace(/^~/, process.env.HOME || '');
}

function detectAgents() {
  return AGENTS.filter(a => {
    const parent = path.dirname(expandTilde(a.path));
    return fs.existsSync(parent);
  });
}

async function askQuestion(rl, question) {
  return new Promise(resolve => rl.question(question, resolve));
}

async function selectAgents(agents) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  
  console.log('\n\x1b[1mSelect agents to install llm-wiki-toolchain into:\x1b[0m');
  console.log('  \x1b[36m(Enter number to toggle, then press Enter to confirm)\x1b[0m\n');
  
  agents.forEach((a, i) => {
    const detected = detectAgents().includes(a) ? ' \x1b[32m[detected]\x1b[0m' : '';
    console.log(`  ${i + 1}. ${a.name}${detected}`);
    console.log(`     ${a.path}`);
  });
  
  console.log(`  ${agents.length + 1}. All of the above`);
  console.log(`  0. None (exit)\n`);
  
  const answer = await askQuestion(rl, 'Enter numbers (comma-separated) or press Enter for all: ');
  rl.close();
  
  if (answer.trim() === '') return agents.map((_, i) => i);
  if (answer.trim() === '0') return [];
  if (answer.trim() === String(agents.length + 1)) return agents.map((_, i) => i);
  
  return answer.split(',').map(n => parseInt(n.trim()) - 1).filter(i => i >= 0 && i < agents.length);
}

function installToAgent(src, agent) {
  const targetPath = expandTilde(agent.path);
  const instrFile = agent.instr ? expandTilde(agent.instr) : '';
  
  // Create target directory
  fs.mkdirSync(targetPath, { recursive: true });
  
  // Copy files
  execSync(`cp -R "${src}"/* "${targetPath}/"`, { stdio: 'inherit' });
  console.log(`  \x1b[32m✓\x1b[0m Installed to ${agent.name}: ${targetPath}`);
  
  // Add loader note if instruction file exists and doesn't already mention us
  if (instrFile) {
    const loaderMarker = 'llm-wiki-toolchain/SKILL.md';
    
    if (fs.existsSync(instrFile)) {
      const content = fs.readFileSync(instrFile, 'utf8');
      if (content.includes(loaderMarker)) {
        console.log(`  \x1b[36m▸\x1b[0m   Loader note already exists in ${instrFile}, skipping`);
        return;
      }
    }
    
    fs.mkdirSync(path.dirname(instrFile), { recursive: true });
    const loaderNote = `

## Agent skills — LLM Wiki Toolchain

When working with Obsidian LLM Wiki knowledge bases, load and follow:
\`${targetPath}/SKILL.md\`.

Resolve linked files relative to that directory:
- scripts/init.py
- scripts/lint.py
- templates/
- references/
`;
    fs.appendFileSync(instrFile, loaderNote);
    console.log(`  \x1b[32m✓\x1b[0m   Added loader note to ${instrFile}`);
  }
  
  if (agent.id === 'hermes') {
    console.log('  \x1b[36m▸\x1b[0m   Hermes will auto-discover this skill on next session');
  }
}

async function main() {
  console.log('');
  console.log('\x1b[1m┌─────────────────────────────────────────┐\x1b[0m');
  console.log('\x1b[1m│   LLM Wiki Toolchain — Installer        │\x1b[0m');
  console.log('\x1b[1m└─────────────────────────────────────────┘\x1b[0m');
  console.log('');
  
  // Download
  const tmpdir = fs.mkdtempSync('/tmp/llm-wiki-');
  const src = path.join(tmpdir, 'src');
  
  try {
    console.log('\x1b[36m▸\x1b[0m Downloading llm-wiki-toolchain...');
    execSync(`git clone --depth 1 "${REPO}" "${src}"`, { stdio: 'pipe' });
    console.log('  \x1b[32m✓\x1b[0m Downloaded');
    
    // Clean non-essential files
    execSync(`rm -rf "${src}/.git" "${src}/__pycache__"`, { stdio: 'pipe' });
    execSync(`find "${src}" -name '*.pyc' -delete 2>/dev/null || true`, { stdio: 'pipe' });
    execSync(`find "${src}" -name '.DS_Store' -delete 2>/dev/null || true`, { stdio: 'pipe' });
    
    console.log('');
    
    // Detect and select agents
    const available = AGENTS;
    const selected = await selectAgents(available);
    
    if (selected.length === 0) {
      console.log('\n  \x1b[33m⚠\x1b[0m Nothing selected. Exiting.\n');
      process.exit(0);
    }
    
    console.log('');
    console.log('\x1b[1mInstalling...\x1b[0m');
    console.log('');
    
    for (const idx of selected) {
      installToAgent(src, available[idx]);
    }
    
    console.log('');
    console.log('\x1b[1m┌─────────────────────────────────────────┐\x1b[0m');
    console.log('\x1b[32m\x1b[1m  Done! llm-wiki-toolchain installed.\x1b[0m');
    console.log('\x1b[1m└─────────────────────────────────────────┘\x1b[0m');
    console.log('');
    console.log('\x1b[36m▸\x1b[0m Update later: cd <install-path> && git pull');
    console.log('');
    
  } finally {
    // Cleanup
    execSync(`rm -rf "${tmpdir}"`, { stdio: 'pipe' });
  }
}

main().catch(err => {
  console.error('\x1b[31m✗\x1b[0m', err.message);
  process.exit(1);
});
