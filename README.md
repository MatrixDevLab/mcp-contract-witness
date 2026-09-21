# mcp-contract-witness

`mcp-contract-witness` is a small, dependency-free verifier for a narrow MCP
failure boundary: a client may hold a tool contract that is no longer the
contract served by the MCP endpoint.

## Problem

Public MCP issues describe stale client bindings after reconnect, tool catalogs
that do not refresh after `tools/list_changed`, non-atomic metadata replacement
after a schema compilation failure, and protocol-era schemas that are not
valid for the negotiated client. These failures can make a healthy server look
unavailable or let a caller act on a contract different from the one it
intended to use.

The first release will stay offline and provider-neutral. Given two secret-free
tool-catalog snapshots and a declared protocol era, it will produce a typed
freshness result and a deterministic explanation of changed tool identity,
input schema, output schema, or catalog membership. It will not connect to an
MCP server, call a tool, handle credentials, or infer semantic compatibility.

## Candidate audience

MCP client, gateway, inspector, and replay-tool maintainers who need a stable
pre-call or CI witness that a cached catalog is still the catalog they measured.
This audience is a hypothesis, not a claim of adoption.

## Roadmap

- [x] Create a dedicated repository and document the boundary.
- [x] Record primary external evidence and a falsifier.
- [ ] Define a canonical, secret-free snapshot and typed diff schema.
- [ ] Add deterministic fixtures for unchanged, additive, breaking, protocol-era,
      and malformed catalogs.
- [ ] Ship one reviewable CLI or library entry point.
- [ ] Stop unless an external consumer demonstrates that this offline witness is
      useful without transport or provider-specific adapters.

## Validation method

See [docs/validation.md](docs/validation.md). The intended check is two
identical runs over a fixed fixture corpus, byte-identical output, explicit
unknown states for malformed or incomplete snapshots, and no network access.

## Stopping point and falsifier

Pause or reject this product if existing MCP inspectors, SDKs, or gateway
health checks already provide the same snapshot-to-snapshot freshness boundary
with lower friction, or if maintainers need live transport recovery rather
than a pure witness. No network client, authentication, automatic refresh,
schema rewriting, or LLM-based semantic comparison belongs in v1.

## Status

Scaffold only. No implementation or external MCP connection exists yet.

