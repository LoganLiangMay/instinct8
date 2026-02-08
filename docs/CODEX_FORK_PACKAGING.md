# Codex Fork Packaging Guide

Guide to repackaging and rebranding the Codex CLI as your own product.

## Overview

The Codex CLI consists of:
1. **Node.js wrapper** (`codex-cli/bin/codex.js`) - Launches the Rust binary
2. **Rust binary** (`codex-rs/`) - The actual CLI implementation
3. **Native binaries** - Platform-specific Rust binaries in `vendor/` directory

To rename and repackage, you need to update references in: npm package, Rust binary, build scripts, configuration paths, environment variables, and documentation.

## Step 1: Choose Your Name

Decide on:
- **CLI command name**: e.g., `instinct`
- **Package name**: e.g., `@instinct8/instinct-cli`
- **Config directory**: e.g., `~/.instinct`
- **Env var prefix**: e.g., `INSTINCT_`

## Step 2: Update npm Package

### package.json

```json
{
  "name": "@instinct8/instinct-cli",
  "version": "1.0.0",
  "license": "Apache-2.0",
  "bin": {
    "instinct": "bin/instinct.js"
  }
}
```

### Rename bin/codex.js to bin/instinct.js

Update binary paths and environment variable references inside the file.

## Step 3: Update Rust Binary

### Cargo.toml

```toml
[package]
name = "instinct-cli"

[[bin]]
name = "instinct"
path = "src/main.rs"

[lib]
name = "instinct_cli"
path = "src/lib.rs"
```

### main.rs

Update `bin_name`, `override_usage`, and help text strings.

### Config Directory (config/mod.rs)

Update `find_codex_home()`:
- Change `CODEX_HOME` env var to `INSTINCT_HOME`
- Change `.codex` directory to `.instinct`

## Step 4: Update Build Scripts

### build_npm_package.py

Update component names and file references from `codex` to your new name.

### install_native_deps.py

Update component dest directory and binary basename.

## Step 5: Update Environment Variables

Search and replace all `CODEX_*` environment variables:
- `CODEX_HOME` -> `INSTINCT_HOME`
- `CODEX_MANAGED_BY_NPM` -> `INSTINCT_MANAGED_BY_NPM`
- `CODEX_MANAGED_BY_BUN` -> `INSTINCT_MANAGED_BY_BUN`
- `CODEX_SANDBOX_*` -> `INSTINCT_SANDBOX_*`
- `CODEX_QUIET_MODE` -> `INSTINCT_QUIET_MODE`

## Step 6: Build and Test

### Build Rust Binaries

```bash
cd codex-rs
cargo build --release -p instinct-cli
```

For cross-platform distribution:
```bash
cargo build --release --target x86_64-unknown-linux-musl -p instinct-cli
cargo build --release --target aarch64-apple-darwin -p instinct-cli
# ... etc for other platforms
```

### Set Up Vendor Directory

```bash
cd codex-cli
TARGET=$(rustc -vV | sed -n 's|host: ||p')
mkdir -p vendor/$TARGET/instinct
cp ../codex-rs/target/release/instinct vendor/$TARGET/instinct/instinct
```

### Build npm Package

```bash
python3 scripts/build_npm_package.py \
  --package instinct \
  --release-version 1.0.0 \
  --vendor-src ./vendor \
  --pack-output ./dist/instinct-cli-1.0.0.tgz
```

### Test

```bash
npm install -g ./dist/instinct-cli-1.0.0.tgz
instinct --version
instinct --help
```

## Vendor Directory Structure

The npm package expects binaries in this structure:

```
vendor/
├── x86_64-unknown-linux-musl/instinct/instinct
├── aarch64-unknown-linux-musl/instinct/instinct
├── x86_64-apple-darwin/instinct/instinct
├── aarch64-apple-darwin/instinct/instinct
├── x86_64-pc-windows-msvc/instinct/instinct.exe
└── aarch64-pc-windows-msvc/instinct/instinct.exe
```

## Checklist

- [ ] Package name updated in `package.json`
- [ ] Binary name updated in `Cargo.toml`
- [ ] Node wrapper renamed and updated
- [ ] Rust source updated (`main.rs`, config files)
- [ ] Build scripts updated
- [ ] Environment variables updated (`CODEX_*` -> `INSTINCT_*`)
- [ ] Config directory updated (`.codex` -> `.instinct`)
- [ ] Documentation updated
- [ ] CLI builds and runs successfully
- [ ] Config directory uses new name
- [ ] Environment variables use new prefix

## Troubleshooting

**Binary not found**: Ensure vendor directory structure matches `vendor/{target-triple}/instinct/instinct`

**Binary not executable**: Run `chmod +x vendor/*/instinct/instinct`

**Config directory still uses old name**: Search for all `.codex` references and update

**Environment variables not working**: Update all `CODEX_*` references in Rust source
