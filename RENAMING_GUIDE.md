# Complete Guide: Renaming Codex CLI to Your Own Brand

This guide shows you **every place** you need to change to fully rebrand the Codex CLI as your own.

## Overview

To rename the CLI, you'll need to change references in:
1. **npm package** (package.json, bin files)
2. **Rust binary** (Cargo.toml, source code)
3. **Build scripts** (Python build scripts)
4. **Configuration paths** (~/.codex → ~/.yourname)
5. **Environment variables** (CODEX_* → YOURNAME_*)
6. **Documentation** (README, comments)

## Step 1: Choose Your Name

Decide on:
- **CLI command name**: e.g., `instinct`, `mycli`, `agent`
- **Package name**: e.g., `@yourorg/instinct-cli`
- **Binary name**: e.g., `instinct` (usually same as CLI command)
- **Config directory**: e.g., `~/.instinct`
- **Env var prefix**: e.g., `INSTINCT_` (uppercase)

**Example:** Let's say you want to rename it to `instinct`:
- CLI command: `instinct`
- Package: `@instinct8/instinct-cli`
- Binary: `instinct`
- Config: `~/.instinct`
- Env vars: `INSTINCT_*`

## Step 2: Update npm Package Files

### 2.1 Update `codex-cli/package.json`

```json
{
  "name": "@instinct8/instinct-cli",  // Change this
  "version": "1.0.0",
  "license": "Apache-2.0",
  "bin": {
    "instinct": "bin/instinct.js"  // Change command name and file
  },
  "type": "module",
  "engines": {
    "node": ">=16"
  },
  "files": [
    "bin",
    "vendor"
  ],
  "repository": {
    "type": "git",
    "url": "git+https://github.com/yourorg/yourrepo.git",
    "directory": "codex-cli"
  }
}
```

### 2.2 Rename `codex-cli/bin/codex.js` → `codex-cli/bin/instinct.js`

Then update the file contents:

```javascript
#!/usr/bin/env node
// Unified entry point for the Instinct CLI.  // Update comment

// ... existing code ...

const instinctBinaryName = process.platform === "win32" ? "instinct.exe" : "instinct";  // Change codex → instinct
const binaryPath = path.join(archRoot, "instinct", instinctBinaryName);  // Change "codex" → "instinct"

// ... existing code ...

/**
 * Use heuristics to detect the package manager that was used to install Instinct  // Update comment
 * in order to give the user a hint about how to update it.
 */
function detectPackageManager() {
  // ... existing code ...
}

// ... existing code ...

const env = { ...process.env, PATH: updatedPath };
const packageManagerEnvVar =
  detectPackageManager() === "bun"
    ? "INSTINCT_MANAGED_BY_BUN"  // Change CODEX_ → INSTINCT_
    : "INSTINCT_MANAGED_BY_NPM";  // Change CODEX_ → INSTINCT_
env[packageManagerEnvVar] = "1";

// ... rest stays the same ...
```

### 2.3 Update `codex-cli/README.md`

Update all references:
- `@openai/codex` → `@instinct8/instinct-cli`
- `codex` command → `instinct` command
- `Codex CLI` → `Instinct CLI`
- `~/.codex` → `~/.instinct`
- `CODEX_*` env vars → `INSTINCT_*`

## Step 3: Update Rust Binary

### 3.1 Update `codex-rs/cli/Cargo.toml`

```toml
[package]
name = "instinct-cli"  # Change from "codex-cli"
version.workspace = true
edition.workspace = true
license.workspace = true

[[bin]]
name = "instinct"  # Change from "codex"
path = "src/main.rs"

[lib]
name = "instinct_cli"  # Change from "codex_cli"
path = "src/lib.rs"

# ... rest stays the same ...
```

### 3.2 Update `codex-rs/cli/src/main.rs`

Find and replace:
- `bin_name = "codex"` → `bin_name = "instinct"`
- `override_usage = "codex [OPTIONS]..."` → `override_usage = "instinct [OPTIONS]..."`
- Any hardcoded `"codex"` strings in help text

Look for around line 60:
```rust
#[clap(
    // ... other attributes ...
    bin_name = "instinct",  // Change this
    override_usage = "instinct [OPTIONS] [PROMPT]\n       instinct [OPTIONS] <COMMAND> [ARGS]"  // Change this
)]
```

And around line 767:
```rust
let name = "instinct";  // Change from "codex"
```

### 3.3 Update Config Directory References

#### Update `codex-rs/core/src/config/mod.rs`

Find `find_codex_home()` function (around line 1349):

```rust
/// Returns the path to the Instinct configuration directory, which can be
/// specified by the `INSTINCT_HOME` environment variable. If not set, defaults to
/// `~/.instinct`.
///
/// - If `INSTINCT_HOME` is set, the value will be canonicalized and this
///   function will Err if the path does not exist.
/// - If `INSTINCT_HOME` is not set, this function does not verify that the
///   directory exists.
pub fn find_codex_home() -> std::io::Result<PathBuf> {  // Consider renaming to find_instinct_home()
    // Honor the `INSTINCT_HOME` environment variable when it is set to allow users
    // (and tests) to override the default location.
    if let Ok(val) = std::env::var("INSTINCT_HOME")  // Change CODEX_HOME → INSTINCT_HOME
        && !val.is_empty()
    {
        return PathBuf::from(val).canonicalize();
    }

    let mut p = home_dir().ok_or_else(|| {
        std::io::Error::new(
            std::io::ErrorKind::NotFound,
            "Could not find home directory",
        )
    })?;
    p.push(".instinct");  // Change ".codex" → ".instinct"
    Ok(p)
}
```

**Note:** You may also want to rename the function from `find_codex_home()` to `find_instinct_home()`, but that requires updating all call sites.

#### Update `codex-rs/rmcp-client/src/find_codex_home.rs`

Same changes as above - update env var and directory name.

### 3.4 Update Other Rust References

Search for and update:
- `CODEX_HOME` → `INSTINCT_HOME` (environment variable)
- `CODEX_*` → `INSTINCT_*` (all environment variables)
- `.codex` → `.instinct` (config directory)
- Comments mentioning "Codex" → "Instinct"

**Quick search command:**
```bash
cd codex-rs
grep -r "CODEX_" --include="*.rs" | grep -v "codex-" | grep -v "codex_"
grep -r "\.codex" --include="*.rs"
grep -r "codex" --include="*.rs" | grep -i "home\|config\|directory"
```

## Step 4: Update Build Scripts

### 4.1 Update `codex-cli/scripts/build_npm_package.py`

```python
#!/usr/bin/env python3
"""Stage and optionally package the @instinct8/instinct-cli npm module."""  # Update docstring

# ... existing imports ...

PACKAGE_NATIVE_COMPONENTS: dict[str, list[str]] = {
    "instinct": ["instinct", "rg"],  # Change "codex" → "instinct"
    "codex-responses-api-proxy": ["codex-responses-api-proxy"],  # Leave if not changing
    "codex-sdk": ["codex"],  # Leave if not changing
}
COMPONENT_DEST_DIR: dict[str, str] = {
    "instinct": "instinct",  # Change "codex" → "instinct"
    "codex-responses-api-proxy": "codex-responses-api-proxy",
    "rg": "path",
}

# ... in parse_args() ...

parser.add_argument(
    "--package",
    choices=("instinct", "codex-responses-api-proxy", "codex-sdk"),  # Add "instinct"
    default="instinct",  # Change default
    help="Which npm package to stage (default: instinct).",
)

# ... in stage_sources() ...

if package == "instinct":  # Change from "codex"
    bin_dir = staging_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CODEX_CLI_ROOT / "bin" / "instinct.js", bin_dir / "instinct.js")  # Change filename
    rg_manifest = CODEX_CLI_ROOT / "bin" / "rg"
    if rg_manifest.exists():
        shutil.copy2(rg_manifest, bin_dir / "rg")

    # ... rest stays the same ...

# ... in print statements ...

if package == "instinct":  # Change from "codex"
    print(
        f"Staged version {version} for release in {staging_dir_str}\n\n"
        "Verify the CLI:\n"
        f"    node {staging_dir_str}/bin/instinct.js --version\n"  # Change filename
        f"    node {staging_dir_str}/bin/instinct.js --help\n\n"
    )
```

### 4.2 Update `codex-cli/scripts/install_native_deps.py`

Find references to component names and update:

```python
Component(
    dest_dir="instinct",  # Change from "codex"
    binary_basename="instinct",  # Change from "codex"
),
```

## Step 5: Update Documentation

### 5.1 Update `codex-cli/README.md`

Replace throughout:
- `@openai/codex` → `@instinct8/instinct-cli`
- `npm install -g @openai/codex` → `npm install -g @instinct8/instinct-cli`
- `codex` command → `instinct` command
- `Codex CLI` → `Instinct CLI`
- `~/.codex` → `~/.instinct`
- `CODEX_*` → `INSTINCT_*`
- `AGENTS.md` references (if you want to rename this too)

### 5.2 Update Root `README.md`

Update any references to the CLI installation/usage.

## Step 6: Update Environment Variables

Search for all `CODEX_*` environment variables and update:

```bash
# Find all CODEX_ env var references
cd codex-rs
grep -r "CODEX_" --include="*.rs" --include="*.md" --include="*.toml" | \
  grep -v "codex-" | grep -v "codex_" | grep -v "codex/"
```

Common ones to update:
- `CODEX_HOME` → `INSTINCT_HOME`
- `CODEX_MANAGED_BY_NPM` → `INSTINCT_MANAGED_BY_NPM`
- `CODEX_MANAGED_BY_BUN` → `INSTINCT_MANAGED_BY_BUN`
- `CODEX_SANDBOX_*` → `INSTINCT_SANDBOX_*` (if you want)
- `CODEX_QUIET_MODE` → `INSTINCT_QUIET_MODE`
- `CODEX_DISABLE_PROJECT_DOC` → `INSTINCT_DISABLE_PROJECT_DOC`

## Step 7: Update Config File References

If users have config files, update references:
- `~/.codex/config.toml` → `~/.instinct/config.toml`
- `~/.codex/AGENTS.md` → `~/.instinct/AGENTS.md`

Search for `.codex` in the codebase:
```bash
grep -r "\.codex" --include="*.rs" --include="*.md" --include="*.toml"
```

## Step 8: Automated Renaming Script

Here's a helper script to do bulk replacements (use carefully!):

```bash
#!/bin/bash
# rename-codex.sh - Bulk rename script (USE WITH CAUTION)

OLD_NAME="codex"
NEW_NAME="instinct"
OLD_PKG="@openai/codex"
NEW_PKG="@instinct8/instinct-cli"
OLD_ENV_PREFIX="CODEX_"
NEW_ENV_PREFIX="INSTINCT_"
OLD_CONFIG_DIR=".codex"
NEW_CONFIG_DIR=".instinct"

# Update package.json
sed -i '' "s/$OLD_PKG/$NEW_PKG/g" codex-cli/package.json
sed -i '' "s/\"$OLD_NAME\"/\"$NEW_NAME\"/g" codex-cli/package.json

# Update Rust Cargo.toml
sed -i '' "s/name = \"codex-cli\"/name = \"$NEW_NAME-cli\"/g" codex-rs/cli/Cargo.toml
sed -i '' "s/name = \"codex\"/name = \"$NEW_NAME\"/g" codex-rs/cli/Cargo.toml
sed -i '' "s/name = \"codex_cli\"/name = \"${NEW_NAME}_cli\"/g" codex-rs/cli/Cargo.toml

# Update Rust source (be careful with this!)
find codex-rs -name "*.rs" -type f -exec sed -i '' "s/CODEX_HOME/INSTINCT_HOME/g" {} \;
find codex-rs -name "*.rs" -type f -exec sed -i '' "s/\.codex/.instinct/g" {} \;

# Update bin file
mv codex-cli/bin/codex.js codex-cli/bin/$NEW_NAME.js
sed -i '' "s/codex/$NEW_NAME/g" codex-cli/bin/$NEW_NAME.js
sed -i '' "s/CODEX_/$NEW_ENV_PREFIX/g" codex-cli/bin/$NEW_NAME.js

# Update build scripts
sed -i '' "s/\"codex\"/\"$NEW_NAME\"/g" codex-cli/scripts/build_npm_package.py
sed -i '' "s/codex\.js/$NEW_NAME.js/g" codex-cli/scripts/build_npm_package.py

echo "Done! Review changes carefully before committing."
```

**⚠️ WARNING:** This script does bulk replacements. Review all changes carefully!

## Step 9: Test Your Renamed CLI

After making changes:

```bash
# 1. Build Rust binary
cd codex-rs
cargo build --release -p instinct-cli  # Use new name

# 2. Set up vendor directory
cd ../codex-cli
TARGET=$(rustc -vV | sed -n 's|host: ||p')
mkdir -p vendor/$TARGET/instinct  # Use new name
cp ../codex-rs/target/release/instinct vendor/$TARGET/instinct/instinct  # Use new name

# 3. Test the Node wrapper
node bin/instinct.js --version  # Use new name
node bin/instinct.js --help

# 4. Build npm package
python3 scripts/build_npm_package.py \
  --package instinct \
  --release-version 1.0.0 \
  --vendor-src ./vendor \
  --pack-output ./dist/instinct-cli-1.0.0.tgz

# 5. Install and test
npm install -g ./dist/instinct-cli-1.0.0.tgz
instinct --version
instinct --help
```

## Step 10: Checklist

Before publishing, verify:

- [ ] Package name updated in `package.json`
- [ ] Binary name updated in `Cargo.toml`
- [ ] Node wrapper renamed and updated (`bin/instinct.js`)
- [ ] Rust source updated (`main.rs`, config files)
- [ ] Build scripts updated (`build_npm_package.py`)
- [ ] Environment variables updated (`CODEX_*` → `INSTINCT_*`)
- [ ] Config directory updated (`~/.codex` → `~/.instinct`)
- [ ] Documentation updated (README, comments)
- [ ] CLI builds successfully
- [ ] CLI runs and shows correct name in help/version
- [ ] Config directory uses new name
- [ ] Environment variables use new prefix

## Common Issues

### Issue: Binary not found

**Solution:** Make sure vendor directory structure matches:
```
vendor/{target-triple}/instinct/instinct
```

### Issue: Config directory still uses old name

**Solution:** Search for all `.codex` references and update to `.instinct`

### Issue: Environment variables not working

**Solution:** Update all `CODEX_*` references to `INSTINCT_*` in Rust source

## Optional: Keep Backward Compatibility

If you want to support both names temporarily:

1. Keep both binary names in vendor directory
2. Check for both env vars (`CODEX_HOME` and `INSTINCT_HOME`)
3. Support both config directories (`~/.codex` and `~/.instinct`)

This is more complex but helps with migration.

## Next Steps

After renaming:
1. Update CI/CD workflows
2. Update any automation scripts
3. Update documentation sites
4. Announce the rename to users
5. Consider deprecation period for old name

