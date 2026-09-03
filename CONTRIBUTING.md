# Contributing to PROJECT AURA

Thank you for your interest in contributing to **PROJECT AURA**! AURA is a Linux-native personal computing platform combining an upstream Linux foundation (via NixOS), a custom Wayland desktop shell, an OS-native AI runtime (**JARVIS**), and empirical Windows compatibility.

Repository: [https://github.com/davistolu/project-aura-os.git](https://github.com/davistolu/project-aura-os.git)

---

## 1. Branching Strategy

The repository maintains two primary branches:

```
                  +-----------------------------------+
                  |  main (Stable Production Releases)|
                  +-----------------------------------+
                                    ^
                                    | (Release PRs & Tagged Versions)
                  +-----------------------------------+
                  |   dev (Active Integration Branch) |
                  +-----------------------------------+
                       ^            ^            ^
                       |            |            |
             +-------------+  +------------+  +-------------+
             | feat/jarvis |  | fix/policy |  | adr/memory  |
             +-------------+  +------------+  +-------------+
```

1. **`main`**:
   - The production branch representing stable, tagged releases.
   - All commits on `main` must pass all release gates and ISO verification.
   - Direct pushes to `main` are restricted.
2. **`dev`**:
   - The primary integration branch where new features, fixes, and subsystem enhancements land.
   - All pull requests from contributors should target `dev`.
3. **Topic / Feature Branches**:
   - Branch off `dev` using conventional prefixes:
     - `feat/<feature-name>` (e.g., `feat/gpu-passthrough`)
     - `fix/<bug-name>` (e.g., `fix/secret-broker-mask`)
     - `adr/<decision-title>` (e.g., `adr/pipewire-low-latency`)
     - `docs/<doc-update>` (e.g., `docs/sdk-guide`)

---

## 2. Non-Negotiable Engineering Principles

Every contribution must align with the core engineering axioms of PROJECT AURA:

1. **Zero Ambient Authority**:
   - AI models and tools are **never** given unrestricted root or sudo access.
   - New tools must declare explicit required capabilities (e.g., `filesystem.read`, `system.process.kill`) and belong to a defined permission tier (`OBSERVE`, `SUGGEST`, `EXECUTE_SAFE`, `EXECUTE_PRIVILEGED`, `AUTONOMOUS`).
2. **Secret Isolation**:
   - Credentials, SSH keys, passwords, and tokens must never enter LLM prompt contexts.
   - All secrets must be brokered through the `SecretBroker`.
3. **Deterministic Fast-Paths**:
   - System verbs (e.g., `workspace switch`, `open app`, `doctor`) must execute deterministically without invoking LLM inference.
4. **Architecture Decision Records (ADRs)**:
   - Any architectural modification, new IPC protocol, or major dependency introduction requires an ADR in `docs/adr/`.

---

## 3. Development Workflow

### Step 1: Clone and Set Up
```bash
git clone https://github.com/davistolu/project-aura-os.git
cd project-aura-os
git checkout dev
git checkout -b feat/your-feature-name
```

### Step 2: Implement Changes
Follow the repository conventions:
- **Rust Systems Crates**: In `crates/` using Rust 2021 edition.
- **SDK**: In `crates/aura-sdk` (Rust) or `sdk/typescript` (TypeScript).
- **OS Configurations**: In `nix/` using Nix Flakes.

### Step 3: Run the Verification Test Suite
Before committing, verify all release gates and capability invariants pass:
```bash
# Run security, capability, and red-team tests
python tests/run_all_tests.py

# Test Rust workspace formatting and checks
cargo check --workspace
cargo test --workspace
```

### Step 4: Commit Conventions
Use Conventional Commits:
- `feat(jarvis): add dynamic SLM context pruning`
- `fix(policy): enforce strict canonical path checking in sandbox`
- `security(broker): redact credential handles from JSON logs`
- `docs(adr): add ADR-0006 for PipeWire audio routing`

### Step 5: Open a Pull Request
- Target the **`dev`** branch.
- Complete the Pull Request template checklist.
- Ensure all CI workflow checks pass.

---

## 4. Code of Conduct

All contributors and maintainers are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).
