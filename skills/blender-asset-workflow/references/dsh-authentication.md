# DSH credentials and model selection

Read this when running the Blender skill through DSH, especially when Web works but headless fails. This is host setup, not a Blender dependency. The behavior below was checked against installed `@deepseek-ai/dsh@0.2.1-rc.5` and the linked upstream documentation on 2026-11-01. Recheck the installed release before applying it to another version.

## Contents

- [Choose the credential and its scope](#choose-the-credential-and-its-scope)
- [API key for CLI or CI](#option-a-an-api-key-for-a-cli-only-or-ci-run)
- [Reuse saved DSH credentials](#option-b-reuse-credentials-already-saved-by-dsh)
- [Match model route and authentication](#match-the-model-route-to-the-authentication)
- [Troubleshooting](#troubleshoot-before-starting-blender)
- [Sources and validation limits](#references-and-documentation-patterns)

## Choose the credential and its scope

Do not assume that the user has a key, that a browser login created one, or that another application's login is available to DSH. Identify the intended provider, authentication method, active profile, and `DSH_HOME` before a model call. Ask for missing choices, never for secret values in chat.

| What the user has | Default behavior | Next step |
|---|---|---|
| A DeepSeek API key in the launch environment | Headless can use `DEEPSEEK_API_KEY` for the API-key route | Select that route and run the small CLI probe below |
| An API key saved in DSH Web | Stock headless ignores the managed credential store | Use the saved-store overlay below, or independently inject a key through the launch environment |
| A supported account sign-in saved by DSH | Stock headless also disables the authorization/account consumers | Restore all three upstream entries and select the matching account route; reauthenticate in DSH if the grant is absent or rejected |
| A `dsh web` URL containing `?token=...` | This grants access to the local Web UI | Open it locally; it is not a model API key or a portable account login |
| A login in an ordinary provider website, Codex, or Nanocoder | It is not evidence that DSH has a supported stored grant | Complete DSH's own supported sign-in, or configure an API key for the intended route |
| A different `DSH_HOME`, Windows user, WSL installation, container, or remote machine | The original local store is not automatically present at the new default path | Sign in/configure credentials there, inject an API key, or explicitly reference a supported local DSH store where appropriate |

Web, SDK and ACP retain managed-store precedence in this DSH release. Headless is the specific exception; do not generalize this to all CLI tools. Separate homes isolate application state, not filesystem permissions. Sharing a store deliberately also shares its credential lifecycle; account refresh/sign-out can affect other consumers.

## Option A: an API key for a CLI-only or CI run

No Web server is required. Configure the provider's API key through the launch environment or the CI secret mechanism. For a person using Windows PowerShell, masked input avoids typing the literal key into command history:

```powershell
$PreviousKey = [Environment]::GetEnvironmentVariable('DEEPSEEK_API_KEY', 'Process')
$SecureKey = Read-Host 'DeepSeek API key (local input only)' -AsSecureString
try {
    $env:DEEPSEEK_API_KEY = [System.Net.NetworkCredential]::new('', $SecureKey).Password
    dsh.cmd --profile headless 'Reply exactly DSH_AUTH_OK. Do not use tools.'
    if ($LASTEXITCODE -ne 0) { throw "DSH probe failed: $LASTEXITCODE" }
} finally {
    [Environment]::SetEnvironmentVariable('DEEPSEEK_API_KEY', $PreviousKey, 'Process')
    $SecureKey.Dispose()
}
```

This assumes the shipped API-key route is selected. If a custom profile has selected another provider, apply the route override described below. A response must actually contain `DSH_AUTH_OK`; exit 0 alone does not verify its content. The key is available to the launched process as an environment value; masked input does not make it inaccessible to that process.

Stock headless resolution is launch environment, then `<invocation cwd>/.env`, then `$DSH_HOME/.env`. An exported empty variable shadows `.env`: remove the empty process variable when intending to use the fallback. If using `.env`, keep it out of version control and task attachments. Never embed credentials in prompts, task files, committed YAML, screenshots, or diagnostic dumps.

## Option B: reuse credentials already saved by DSH

For the usual same-home case, save the following **non-secret** overlay as a new `dsh-auth.patch.yml` in the test directory, using UTF-8. Do not overwrite an existing profile or credential file:

```yaml
- id: credentials
  disabled: false
- id: authorization
  disabled: false
- id: deepseek-account
  disabled: false
```

These are the three entries recommended by upstream for restoring stored authentication. Re-enabling `credentials` alone was sufficient in our API-key test; that narrower result does not validate account sign-in. Use the complete overlay when the requested route depends on saved login state.

Launch from the intended project using the same `DSH_HOME` as the Web setup:

```powershell
$AuthPatch = (Resolve-Path -LiteralPath '.\dsh-auth.patch.yml').Path
dsh.cmd --profile headless --patch $AuthPatch 'Reply exactly DSH_AUTH_OK. Do not use tools.'
if ($LASTEXITCODE -ne 0) { throw "DSH probe failed: $LASTEXITCODE" }
```

Use the explicit `--profile headless --patch ...` form. In the tested release, putting an overlay before a positional profile caused `--profile <name> is required`.

When restored, precedence becomes **saved store > launch environment > project `.env` > home `.env`**. Setting an environment key does not replace an existing saved key. To intentionally use an injected key, use stock headless without restoring the store; to update a stored key, use DSH's credential UI. Do not delete the entire store to fix one route.

For a separate test home, the `credentials` entry can reference the existing DSH store without copying its contents:

```yaml
- id: credentials
  disabled: false
  config:
    path: 'C:/absolute/path/to/original-dsh-home/.credentials.yaml'
    watch: false
```

Replace the placeholder with the actual path; the default original home is `$env:USERPROFILE\.dsh` unless `DSH_HOME` was set. Use this entry instead of duplicating `id: credentials`. Keep the authorization/account entries if using saved login. The reference is not a read-only mount; a credential operation can still update the original file. For independent credentials, configure/login within the new home instead. Do not copy all of `.dsh` merely to make a test work.

## Match the model route to the authentication

In the tested DSH release, `deepseek-official` is the API-key route. Its `apiKeyEnv` defaults to `DEEPSEEK_API_KEY`; a DeepSeek account login cannot substitute for that key. The `deepseek-account` route uses the supported DSH account grant and never falls back to an API key. Select the provider/model shown by the installed version, with a model the account or API key can actually use.

Web model choices are profile-specific configuration; changing `DSH_HOME` or profile can change the effective selection. For a reproducible API-key test, add this entry to the same overlay, replacing the example model with one available to your provider if necessary:

```yaml
- id: agent-default-model
  config:
    provider: deepseek-official
    model: deepseek-flash
```

For an account-login test in this release, use `provider: deepseek-account` instead and a model available to that account; verify both identifiers against the installed version. If a saved account is absent or rejected, return to DSH's supported sign-in UI using the intended home, complete login, then retry headless with the restore overlay. Do not paste cookies, OAuth grants, or the Web access token into an API-key field. If that release/provider offers no usable login flow in the target environment, use a supported API-key route or report account authentication as blocked; do not invent a DSH device-login command.

## Troubleshoot before starting Blender

| Symptom | Check and recovery |
|---|---|
| `MISSING_CREDENTIAL` after Web setup | Confirm headless profile, home, matching route, and whether the store is enabled. Apply Option B or inject the route's API key with Option A |
| `INVALID_CREDENTIAL`, HTTP 401, or account sign-in required | Distinguish malformed/rejected key from missing account grant. Correct the selected route's credential or complete its sign-in again; do not print the rejected value |
| Old key still used after setting an environment variable | Restored saved-store precedence wins. Update that saved entry or use stock headless for the injected-key run |
| Key works but wrong model/account is selected | Inspect the profile's provider/model selection; model listing success is not inference success |
| Quota, unsupported model, upgrade required, or network failure | Retain the actual error and handle that cause; do not relabel every failed request as a login problem |

For support, record DSH version, surface/profile, provider/model, credential **source category**, home/overlay location, exit code and a redacted error. Do not print credential files or raw configuration dumps. A local Web HTTP 200, a model-list response, or a successful `--version` is not proof of a working headless request.

## References and documentation patterns

- [DSH headless credentials](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/bundle/headless/README.md#credentials) and [local credential precedence](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/credentials/credentials-local/README.md): source of the DSH behavior and restore entries above.
- [DSH API-key provider](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/llm/llm-deepseek-api-key/README.md), [account provider](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/llm/llm-deepseek-account/README.md), and [account service](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/credentials/deepseek-account/README.md): distinct authentication owners, model admission and account recovery.
- [Nanocoder provider setup](https://github.com/Nano-Collective/nanocoder/blob/main/docs/configuration/providers/index.md) separates guided setup, environment configuration and provider selection. Its [ChatGPT/Codex provider](https://github.com/Nano-Collective/nanocoder/blob/main/docs/configuration/providers/chatgpt-codex.md) documents its own login commands and exact provider-name matching. Follow that explicit setup pattern; its credentials and commands are not DSH configuration.
- [Codex authentication](https://developers.openai.com/codex/auth/) distinguishes API keys from account login, documents cached-credential scope and headless recovery, and provides a login-status check. Codex CLI and IDE extension can share their own login cache; this does not imply DSH can import it. Follow the scope-and-verification pattern, not a blanket rule that all applications either share or isolate credentials.

The saved API-key path was exercised end to end on Windows. DSH account login, refresh/rejection recovery, and cross-machine credential reuse were **not** live-tested in this workflow; those instructions are source-checked, not a claimed OAuth test result. See the [Windows DSH guide](windows-dsh.md) for the remaining setup and modeling checks.
