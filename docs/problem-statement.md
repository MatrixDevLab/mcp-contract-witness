# Problem statement

## Observed external failures

- GitHub's Copilot app issue [#2139](https://github.com/github/app/issues/2139)
  reports an MCP server that reconnects successfully while an active chat keeps
  a stale client binding. Tool schemas remain visible, but calls fail with a
  missing-client error until a fresh chat is opened.
- The MCP Go SDK issue [#1188](https://github.com/modelcontextprotocol/go-sdk/issues/1188)
  reports one static schema being returned across protocol eras even when a
  modern schema is outside the legacy envelope.
- The MCP TypeScript SDK issue [#2614](https://github.com/modelcontextprotocol/typescript-sdk/issues/2614)
  reports a failed catalog refresh clearing previously valid validator metadata
  before the replacement catalog has compiled successfully.
- The MCP Inspector issue [#1292](https://github.com/modelcontextprotocol/inspector/issues/1292)
  documents a stale tools panel after `tools/list_changed`, with disconnect and
  reconnect as the workaround.
- The MCP discussion [#2744](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/2744)
  proposes stable fingerprints because clients and gateways otherwise invent
  incompatible hashing and normalization rules.

## Narrow product hypothesis

An offline tool that canonicalizes a recorded catalog, computes explicit
identity/input/output/catalog digests, and compares two snapshots could give
client and gateway maintainers a cheap witness before replay or execution.
The witness should distinguish `current`, `changed`, `unknown`, and
`incompatible` without claiming that a changed schema is semantically safe or
unsafe in every provider.

## Non-goals

- connecting to MCP servers or replaying calls;
- OAuth, API keys, secrets, or transport handling;
- rewriting schemas to fit a provider or protocol era;
- semantic equivalence claims;
- automatic refresh, retry, or recovery policy;
- modifying an SDK or inspector in place.

## Falsifier

Reject this hypothesis if a maintainer's smallest useful integration requires
transport-specific refresh, provider-specific schema conversion, or semantic
compatibility rather than a deterministic snapshot witness. Also reject it if
an existing MCP tool already provides the same result with less setup.

