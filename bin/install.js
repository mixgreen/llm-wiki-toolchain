#!/usr/bin/env node

/**
 * Thin wrapper that delegates to install.sh (the single source of truth).
 * This file exists so `npx llm-wiki-toolchain` works on systems with bash.
 */

const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Non-interactive environment check
if (!process.stdin.isTTY) {
  console.error('\x1b[33m⚠\x1b[0m Non-interactive environment detected.');
  console.error('  Run interactively: npx llm-wiki-toolchain');
  console.error('  Or use: curl -fsSL https://raw.githubusercontent.com/mixgreen/llm-wiki-toolchain/main/install.sh | bash');
  process.exit(0);
}

const scriptDir = path.resolve(__dirname, '..');
const installSh = path.join(scriptDir, 'install.sh');

if (!fs.existsSync(installSh)) {
  console.error('\x1b[31m✗\x1b[0m install.sh not found at', installSh);
  console.error('  Package may be corrupted. Re-install with: npm install -g llm-wiki-toolchain');
  process.exit(1);
}

try {
  execFileSync('bash', [installSh], { stdio: 'inherit' });
} catch (err) {
  process.exit(err.status || 1);
}
