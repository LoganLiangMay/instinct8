# Guide: Repackaging Codex CLI with Your Changes

This guide walks you through repackaging the Codex CLI with your modifications into a new npm package.

## Overview

The Codex CLI consists of:
1. **Node.js wrapper** (`codex-cli/bin/codex.js`) - Launches the Rust binary
2. **Rust binary** (`codex-rs/`) - The actual CLI implementation
3. **Native binaries** - Platform-specific Rust binaries in `vendor/` directory

## Step-by-Step Process

### Step 1: Update Package Configuration

#### 1.1 Update `package.json`

Edit `codex-cli/package.json` to change the package name:

```json
{
  "name": "@your-org/your-codex-cli",  // Change this
  "version": "1.0.0",                   // Set your version
  "license": "Apache-2.0",
  "bin": {
    "your-codex": "bin/codex.js"       // Optional: change command name
  },
  // ... rest of config
}
```

**Note:** If you change the `bin` command name, you'll also need to update `bin/codex.js` to reference the correct binary path (though it should work as-is since it looks for `vendor/{target}/codex/codex`).

#### 1.2 Update README (Optional)

Update `codex-cli/README.md` to reflect your package name and any customizations.

### Step 2: Build Rust Binaries (If Modified)

If you've made changes to the Rust codebase (`codex-rs/`), you need to build the binaries:

#### Option A: Build Locally

```bash
cd codex-rs

# Install dependencies (if using just)
just install  # or cargo build --release

# Build the CLI binary
cargo build --release -p codex-cli

# The binary will be at: target/release/codex (or codex.exe on Windows)
```

#### Option B: Build for Multiple Platforms

For cross-platform distribution, you'll need to build for each target:

```bash
cd codex-rs

# Linux x64
cargo build --release --target x86_64-unknown-linux-musl -p codex-cli

# Linux ARM64
cargo build --release --target aarch64-unknown-linux-musl -p codex-cli

# macOS x64
cargo build --release --target x86_64-apple-darwin -p codex-cli

# macOS ARM64 (Apple Silicon)
cargo build --release --target aarch64-apple-darwin -p codex-cli

# Windows x64
cargo build --release --target x86_64-pc-windows-msvc -p codex-cli

# Windows ARM64
cargo build --release --target aarch64-pc-windows-msvc -p codex-cli
```

### Step 3: Prepare Vendor Directory

The npm package expects binaries in a specific structure:

```
vendor/
├── x86_64-unknown-linux-musl/
│   └── codex/
│       └── codex
├── aarch64-unknown-linux-musl/
│   └── codex/
│       └── codex
├── x86_64-apple-darwin/
│   └── codex/
│       └── codex
├── aarch64-apple-darwin/
│   └── codex/
│       └── codex
├── x86_64-pc-windows-msvc/
│   └── codex/
│       └── codex.exe
└── aarch64-pc-windows-msvc/
    └── codex/
        └── codex.exe
```

#### Option A: Use the Install Script

If you have binaries available (e.g., from a GitHub Actions workflow), use:

```bash
cd codex-cli
python3 scripts/install_native_deps.py \
  --workflow-url <WORKFLOW_URL> \
  --component codex \
  vendor
```

#### Option B: Manual Setup

Create the vendor structure manually:

```bash
cd codex-cli

# Create vendor directory structure
mkdir -p vendor/x86_64-unknown-linux-musl/codex
mkdir -p vendor/aarch64-unknown-linux-musl/codex
mkdir -p vendor/x86_64-apple-darwin/codex
mkdir -p vendor/aarch64-apple-darwin/codex
# ... etc for other platforms

# Copy your built binaries
cp ../codex-rs/target/x86_64-unknown-linux-musl/release/codex \
   vendor/x86_64-unknown-linux-musl/codex/codex

cp ../codex-rs/target/aarch64-unknown-linux-musl/release/codex \
   vendor/aarch64-unknown-linux-musl/codex/codex

# ... repeat for other platforms
```

### Step 4: Build the npm Package

#### Option A: Using the Build Script (Recommended)

```bash
cd codex-cli

# Stage the package
python3 scripts/build_npm_package.py \
  --package codex \
  --release-version 1.0.0 \
  --vendor-src ./vendor \
  --staging-dir ./dist/staged

# This creates a staged package in ./dist/staged
# Verify it works:
node ./dist/staged/bin/codex.js --version
node ./dist/staged/bin/codex.js --help

# Create npm tarball
python3 scripts/build_npm_package.py \
  --package codex \
  --release-version 1.0.0 \
  --vendor-src ./vendor \
  --pack-output ./dist/your-codex-cli-1.0.0.tgz
```

#### Option B: Manual npm pack

If you've manually set up the vendor directory:

```bash
cd codex-cli

# Ensure package.json is updated
# Copy vendor directory to staging location
mkdir -p dist/staged
cp -r bin dist/staged/
cp -r vendor dist/staged/  # if vendor exists in codex-cli/
cp package.json dist/staged/
cp README.md dist/staged/  # optional

cd dist/staged
npm pack
# This creates: your-codex-cli-1.0.0.tgz
```

### Step 5: Test the Package

Before publishing, test the package locally:

```bash
# Install from tarball
npm install -g ./dist/your-codex-cli-1.0.0.tgz

# Test it works
your-codex --version
your-codex --help
your-codex "test command"
```

### Step 6: Publish to npm (Optional)

If you want to publish to npm:

```bash
# Make sure you're logged in
npm login

# Publish
npm publish ./dist/your-codex-cli-1.0.0.tgz

# Or publish from the staged directory
cd dist/staged
npm publish
```

## Quick Reference: Complete Workflow

Here's a complete workflow assuming you've modified the Rust code:

```bash
# 1. Build Rust binaries (for your platform)
cd codex-rs
cargo build --release -p codex-cli

# 2. Set up vendor directory
cd ../codex-cli
mkdir -p vendor/$(rustc -vV | sed -n 's|host: ||p')/codex
cp ../codex-rs/target/release/codex vendor/$(rustc -vV | sed -n 's|host: ||p')/codex/codex

# 3. Update package.json with your name/version
# (Edit codex-cli/package.json)

# 4. Build npm package
python3 scripts/build_npm_package.py \
  --package codex \
  --release-version 1.0.0 \
  --vendor-src ./vendor \
  --pack-output ./dist/your-codex-cli-1.0.0.tgz

# 5. Test locally
npm install -g ./dist/your-codex-cli-1.0.0.tgz
your-codex --version
```

## Customizing the Binary Name

If you want to change the binary name (not just the npm command), you'll need to:

1. **Update Rust build configuration** - Change the binary name in `codex-rs/cli/Cargo.toml`:
   ```toml
   [[bin]]
   name = "your-codex"  # Change from "codex"
   ```

2. **Update `bin/codex.js`** - Modify the binary path:
   ```javascript
   const codexBinaryName = process.platform === "win32" ? "your-codex.exe" : "your-codex";
   const binaryPath = path.join(archRoot, "your-codex", codexBinaryName);
   ```

3. **Update build script** - Modify `build_npm_package.py`:
   ```python
   PACKAGE_NATIVE_COMPONENTS: dict[str, list[str]] = {
       "codex": ["your-codex", "rg"],  # Change "codex" to "your-codex"
   }
   COMPONENT_DEST_DIR: dict[str, str] = {
       "your-codex": "your-codex",  # Add this mapping
   }
   ```

## Troubleshooting

### Issue: "Missing native component" error

**Solution:** Ensure your vendor directory structure matches exactly:
```
vendor/{target-triple}/codex/codex
```

### Issue: Binary not executable

**Solution:** Make sure binaries are executable:
```bash
chmod +x vendor/*/codex/codex
```

### Issue: Wrong binary path in codex.js

**Solution:** Verify the `targetTriple` detection in `bin/codex.js` matches your platform. You can debug by adding:
```javascript
console.log('Target triple:', targetTriple);
console.log('Binary path:', binaryPath);
```

## Alternative: Fork-Based Approach

If you want to maintain a fork that's easier to update:

1. Fork the repository
2. Make your changes
3. Set up CI/CD to automatically build and publish when you push tags
4. Use the existing build scripts with minimal modifications

## Next Steps

- Set up automated builds via GitHub Actions
- Configure npm registry (public or private)
- Add versioning strategy
- Set up automated testing before publishing

