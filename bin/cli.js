#!/usr/bin/env node

/**
 * mobilerun-mcp npm CLI launcher
 *
 * Provides a zero-setup runner for mobilerun-mcp.
 * Automatically provisions Astral's standalone `uv` binary and manages the isolated
 * Python environment and dependencies (mobilerun-core, mobilerun CLI, FastMCP, onnxruntime, etc.)
 * in a persistent user cache directory without requiring any manual installation from the user.
 */

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const https = require('https');

const PACKAGE_ROOT = path.resolve(__dirname, '..');

function getCacheDir() {
  if (process.platform === 'win32') {
    const base = process.env.LOCALAPPDATA || path.join(os.homedir(), 'AppData', 'Local');
    return path.join(base, 'mobilerun-mcp');
  }
  return path.join(os.homedir(), '.cache', 'mobilerun-mcp');
}

function checkSystemUv() {
  try {
    const stdout = execSync(process.platform === 'win32' ? 'where uv' : 'which uv', {
      stdio: ['ignore', 'pipe', 'ignore'],
    })
      .toString()
      .trim();
    if (stdout) {
      const first = stdout.split(/\r?\n/)[0].trim();
      if (first && fs.existsSync(first)) {
        return first;
      }
    }
  } catch {
    // uv not in PATH
  }
  return null;
}

function getUvDownloadInfo() {
  const platform = process.platform;
  const arch = process.arch;

  const mapping = {
    'win32-x64': {
      filename: 'uv-x86_64-pc-windows-msvc.zip',
      type: 'zip',
      binName: 'uv.exe',
    },
    'darwin-arm64': {
      filename: 'uv-aarch64-apple-darwin.tar.gz',
      type: 'tar.gz',
      binName: 'uv',
    },
    'darwin-x64': {
      filename: 'uv-x86_64-apple-darwin.tar.gz',
      type: 'tar.gz',
      binName: 'uv',
    },
    'linux-x64': {
      filename: 'uv-x86_64-unknown-linux-gnu.tar.gz',
      type: 'tar.gz',
      binName: 'uv',
    },
    'linux-arm64': {
      filename: 'uv-aarch64-unknown-linux-gnu.tar.gz',
      type: 'tar.gz',
      binName: 'uv',
    },
  };

  const key = `${platform}-${arch}`;
  const info = mapping[key];
  if (!info) {
    throw new Error(
      `Unsupported platform/architecture for automatic uv download: ${platform} ${arch}. Please install uv manually: https://docs.astral.sh/uv/`
    );
  }

  info.url = `https://github.com/astral-sh/uv/releases/latest/download/${info.filename}`;
  return info;
}

function downloadFile(url, destPath) {
  return new Promise((resolve, reject) => {
    function get(currentUrl, redirectsLeft) {
      if (redirectsLeft <= 0) {
        return reject(new Error(`Too many redirects downloading ${url}`));
      }
      https
        .get(currentUrl, (res) => {
          if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
            return get(res.headers.location, redirectsLeft - 1);
          }
          if (res.statusCode !== 200) {
            return reject(new Error(`Failed to download ${url}: HTTP status ${res.statusCode}`));
          }
          const fileStream = fs.createWriteStream(destPath);
          res.pipe(fileStream);
          fileStream.on('finish', () => {
            fileStream.close(resolve);
          });
          fileStream.on('error', (err) => {
            fs.unlink(destPath, () => {});
            reject(err);
          });
        })
        .on('error', reject);
    }
    get(url, 5);
  });
}

async function ensureUv(cacheDir) {
  const systemUv = checkSystemUv();
  if (systemUv) {
    return systemUv;
  }

  const binDir = path.join(cacheDir, 'bin');
  fs.mkdirSync(binDir, { recursive: true });

  const isWin = process.platform === 'win32';
  const localUv = path.join(binDir, isWin ? 'uv.exe' : 'uv');

  if (fs.existsSync(localUv)) {
    return localUv;
  }

  console.error('[mobilerun-mcp] uv not found on system. Downloading standalone uv runner...');
  const info = getUvDownloadInfo();
  const archivePath = path.join(cacheDir, info.filename);

  try {
    await downloadFile(info.url, archivePath);

    console.error('[mobilerun-mcp] Extracting uv runner...');
    if (isWin) {
      try {
        // Windows 10/11 includes bsdtar in system32
        execSync(`tar -xf "${archivePath}" -C "${binDir}"`, { stdio: 'ignore' });
      } catch {
        // Fallback to PowerShell Expand-Archive
        execSync(
          `powershell -NoProfile -Command "Expand-Archive -Path '${archivePath}' -DestinationPath '${binDir}' -Force"`,
          { stdio: 'ignore' }
        );
      }
    } else {
      execSync(`tar -xzf "${archivePath}" -C "${binDir}"`, { stdio: 'ignore' });
    }

    // Some archives extract into a subfolder uv-<arch> or directly into binDir
    if (!fs.existsSync(localUv)) {
      const files = fs.readdirSync(binDir);
      for (const f of files) {
        const sub = path.join(binDir, f);
        if (fs.statSync(sub).isDirectory()) {
          const candidate = path.join(sub, info.binName);
          if (fs.existsSync(candidate)) {
            fs.copyFileSync(candidate, localUv);
            break;
          }
        }
      }
    }

    if (!isWin && fs.existsSync(localUv)) {
      fs.chmodSync(localUv, 0o755);
    }

    if (!fs.existsSync(localUv)) {
      throw new Error(`Failed to locate ${info.binName} after extraction.`);
    }

    try {
      fs.unlinkSync(archivePath);
    } catch {
      // Ignore cleanup error
    }

    console.error('[mobilerun-mcp] uv runner ready.');
    return localUv;
  } catch (err) {
    throw new Error(`Failed to automatically provision uv: ${err.message}`);
  }
}

async function main() {
  const cacheDir = getCacheDir();
  const venvDir = path.join(cacheDir, 'venv');
  fs.mkdirSync(cacheDir, { recursive: true });

  const uvBin = await ensureUv(cacheDir);

  const userArgs = process.argv.slice(2);
  const invokerName = path.basename(process.argv[1] || '', path.extname(process.argv[1] || ''));
  const isMobilerunCli =
    invokerName === 'mobilerun' ||
    userArgs[0] === 'mobilerun' ||
    userArgs[0] === 'cli';

  const command = isMobilerunCli ? 'mobilerun' : 'mobilerun-mcp';
  const commandArgs =
    (userArgs[0] === 'mobilerun' || userArgs[0] === 'cli') ? userArgs.slice(1) : userArgs;

  const args = [
    'run',
    '--project',
    PACKAGE_ROOT,
    command,
    ...commandArgs,
  ];

  const env = {
    ...process.env,
    UV_PROJECT_ENVIRONMENT: venvDir,
  };

  const child = spawn(uvBin, args, {
    stdio: 'inherit',
    env,
  });

  const forwardSignal = (sig) => {
    if (child && !child.killed) {
      child.kill(sig);
    }
  };

  process.on('SIGINT', () => forwardSignal('SIGINT'));
  process.on('SIGTERM', () => forwardSignal('SIGTERM'));

  child.on('exit', (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
    } else {
      process.exit(code ?? 0);
    }
  });

  child.on('error', (err) => {
    console.error(`[mobilerun-mcp] Failed to launch server process: ${err.message}`);
    process.exit(1);
  });
}

main().catch((err) => {
  console.error(`[mobilerun-mcp] Error: ${err.message}`);
  process.exit(1);
});
