# Validation method

The first implementation, if justified, must be tested without network access
or credentials.

1. Define a JSON snapshot containing only tool names, schemas, protocol era,
   and explicitly allowed metadata.
2. Canonicalize using an explicit stable-key and normalization policy. Never
   silently drop fields that could alter a contract.
3. Compare unchanged, description-only, input-schema, output-schema, tool
   add/remove, protocol-era, malformed, and incomplete fixtures.
4. Emit a typed result with the changed dimensions and an `unknown` or
   `incompatible` state when the input cannot support a conclusion.
5. Run the fixture command twice and compare serialized output byte-for-byte.
6. Run compilation/tests and `git diff --check`; confirm no network or secret
   access is present in the implementation.

Success is a deterministic, reviewable witness—not a claim that two schemas
are semantically equivalent or that a changed contract is safe to execute.

