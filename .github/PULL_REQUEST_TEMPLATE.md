## Description
<!-- Provide a brief description of the changes made and the motivation. -->

## Target Branch
- [ ] Target branch is `dev` (or `main` for release promotion PRs)

## Type of Change
- [ ] `feat`: New feature / capability
- [ ] `fix`: Bug fix
- [ ] `security`: Security enhancement / trust boundary fix
- [ ] `docs`: Documentation / ADR update
- [ ] `refactor`: Code refactoring with no behavior change
- [ ] `nix`: Operating system flake / module change

## Security & Capability Checklist
- [ ] Does this change introduce new AI capabilities? If so, are they declared in `Capability` enum?
- [ ] Are all privileged actions gated behind explicit permission tiers (`EXECUTE_PRIVILEGED`)?
- [ ] Zero ambient root/sudo access maintained?
- [ ] Secrets isolated via `SecretBroker` (no credentials in LLM context)?

## Verification & Testing
- [ ] `python tests/run_all_tests.py` passes with 0 failures
- [ ] Cargo checks / formatting pass (`cargo check --workspace`)
- [ ] TypeScript SDK builds (`npm run build`)
- [ ] New unit or integration tests added for new functionality
