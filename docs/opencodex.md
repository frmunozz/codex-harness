# Optional OpenCodex integration

OpenCodex is a separate local proxy for routing Codex requests to multiple providers. The core harness works without it.

This guide records an optional setup path. It does not make OpenCodex a harness dependency, and it does not place credentials or provider configuration in this repository.

## Boundary

The harness manages portable Codex assets:

- `~/.codex/AGENTS.md`
- `~/.codex/agents/`
- `~/.codex/hooks/`
- `~/.agents/skills/`
- the portable config baseline

OpenCodex manages provider routing and its own runtime state:

- `~/.opencodex/config.json`
- `~/.opencodex/` service state and logs
- `~/.codex/opencodex-catalog.json`
- OpenCodex routing entries in `~/.codex/config.toml`

The harness installer must not copy, sync, or overwrite those OpenCodex-managed files. `config/config.toml.template` remains provider-neutral.

OpenCodex has changed user-level `.codex` state in this setup: it pointed Codex at the local proxy and generated a proxy model catalog. The harness itself does not manage those changes. Running `ocx stop` restores the native Codex routing recorded by OpenCodex.

## Install and start

Install OpenCodex separately:

```powershell
npm install -g @bitkyc08/opencodex
ocx start
```

OpenCodex listens on `http://127.0.0.1:10100` by default. Configure providers through the local dashboard or the `ocx provider` commands.

For background operation on Windows:

```powershell
ocx service install
ocx service start
ocx status
ocx health
```

The exact service command can vary by OpenCodex release; check `ocx --help` if the installed version reports a different lifecycle command.

## Preserve ChatGPT Plus

Keep the canonical OpenAI/ChatGPT provider as the default provider. Complete the normal Codex login before testing external providers.

OpenCodex can route external models through the proxy while forwarding the native ChatGPT provider. Provider selection is model-specific; external providers do not replace the ChatGPT subscription credentials.

The OpenCodex proxy must be running before using routed models in Codex. To return to native Codex routing:

```powershell
ocx stop
```

## Optional DeepSeek provider

Required values:

- API base URL: `https://api.deepseek.com`
- API key: stored in the user environment as `DEEPSEEK_API_KEY`
- model: `deepseek-flash`

Configure the key through a secure environment-variable workflow or the OpenCodex dashboard. Never put the key in this repository, a TOML file committed to Git, shell history, or a command argument.

After adding the provider:

```powershell
ocx provider test deepseek
ocx models list
```

Use the provider-qualified model when needed:

```text
deepseek/deepseek-flash
```

The local setup caps DeepSeek's advertised context at 272k to match the other Codex harness models. Recheck this setting after OpenCodex upgrades because model discovery may refresh provider metadata.

## Optional AWS Bedrock provider

Required values for the planned `us-east-1` setup:

- Bedrock Mantle base URL: `https://bedrock-mantle.us-east-1.api.aws/openai/v1`
- API key: stored in the user environment as `BEDROCK_API_KEY`
- model: `openai.gpt-5.6-luna`

The API key itself does not contain a region. The region is selected by the Bedrock endpoint and provider configuration.

AWS account prerequisites are outside this repository. The AWS account may require:

- a valid payment instrument for the model agreement or Marketplace entitlement;
- model access/agreement approval in `us-east-1`;
- IAM permissions for model access and, where required, AWS Marketplace subscription actions.

If the request returns `INVALID_PAYMENT_INSTRUMENT`, the proxy configuration is being reached but AWS has not established the account entitlement. An account owner or IAM principal with billing/Marketplace authority may need to complete that step.

Validate only after the AWS account is enabled:

```powershell
ocx provider test bedrock
ocx models list
```

Use:

```text
bedrock/openai.gpt-5.6-luna
```

Do not commit AWS account IDs, API keys, payment details, agreement tokens, or account-specific config.

## Sub-agent fallback

OpenCodex supports a separate fallback chain for spawned sub-agents. Native Codex config does not provide automatic provider failover when ChatGPT Plus quota is exhausted.

Inspect the current routing:

```powershell
ocx agent status
```

Configure fallback only after the target provider has passed its provider test. Example shape:

```powershell
ocx agent fallback set deepseek/deepseek-flash
```

The fallback chain is OpenCodex state. It does not belong in `agents/*.toml`, and it does not alter the primary model declared by a harness agent role.

Keep the heterogeneous-provider collaboration surface on OpenCodex v1 unless the installed OpenCodex version documents a compatible v2 setup. Native-to-routed v2 tasks can contain encrypted task content that external providers cannot read.

## Sync Codex App

After adding or changing providers, refresh the model catalog:

```powershell
ocx sync
```

If the Codex App still shows the old catalog, restart only its app-server processes:

```powershell
ocx sync --restart-app-server-only
```

This can interrupt active turns. Start a fresh Codex session after model-surface changes.

## Checks and recovery

Useful checks:

```powershell
ocx status
ocx health
ocx ready --wait
ocx provider list
ocx agent status
```

If OpenCodex is unavailable, native Codex requests pointed at the proxy will fail until it is started or routing is restored with `ocx stop`.

If a provider fails:

1. Check the provider key without printing it.
2. Run `ocx provider test <provider>`.
3. Check the provider's account, billing, region, and model entitlement.
4. Run `ocx sync` after provider or model changes.

Stop the background service before removing OpenCodex:

```powershell
ocx service stop
ocx stop
```

Keep the OpenCodex runtime and state outside the harness repository. The harness backup and rollback commands do not restore OpenCodex state.

## Sources

- [OpenCodex repository](https://github.com/lidge-jun/opencodex)
- [OpenCodex sub-agent surface and fallback chains](https://opencodex.me/guides/sub-agent-surface/)
- [Codex configuration reference](https://developers.openai.com/docs/config-file/config-reference)
- [Amazon Bedrock model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)
