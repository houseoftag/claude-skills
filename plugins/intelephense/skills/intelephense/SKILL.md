---
name: intelephense
description: >
  Use when working with PHP files and needing code intelligence —
  diagnostics, type checking, go-to-definition, find references, symbol
  search, hover info, code actions, formatting, rename refactoring.
  Triggers on: PHP development, PHP LSP, Intelephense, PHP type errors,
  PHP diagnostics, undefined method, undefined variable, PHP
  autocompletion, PHP namespace resolution, phpdoc, PHP refactoring.
---

# Intelephense (PHP LSP)

Intelephense is a PHP Language Server available via Claude Code's LSP tool. It provides type-aware code intelligence that is **dramatically better than grep or file reading** for understanding PHP codebases.

## When to Use LSP vs Other Tools

| Task | Use | Why |
|------|-----|-----|
| Find all usages of a method | `findReferences` | Namespace-aware, no false positives from string matches |
| Jump to where something is defined | `goToDefinition` | Resolves through inheritance, traits, `use` imports |
| Check what a function expects/returns | `hover` | Full signature + PHPDoc without opening the file |
| List all functions/classes in a file | `documentSymbol` | Structured results, faster than scanning |
| Search for a class/function by name | `workspaceSymbol` | Finds across entire project by symbol name |
| Find implementations of an interface | `goToImplementation` | Only reliable way to find concrete classes |
| Trace who calls a function | `incomingCalls` | Follows the call graph, not just text matches |
| Trace what a function calls | `outgoingCalls` | Maps the full dependency chain |
| Check for type errors after edits | Automatic | Diagnostics push after every file edit |
| Read file content/logic | **Read tool** | LSP gives metadata, not code |
| Search for strings/comments/config | **Grep tool** | LSP only understands symbols |

**Rule of thumb:** If you're looking for a *symbol* (function, class, method, variable), use LSP. If you're looking for *text*, use Grep/Read.

## LSP Tool Operations

All operations require three parameters:
- `filePath` — absolute path to the PHP file
- `line` — 1-based line number
- `character` — 1-based character offset (position your cursor on the symbol)

### Available Operations

```
goToDefinition      — Where is this symbol defined?
findReferences      — Where is this symbol used?
hover               — What type/docs does this symbol have?
documentSymbol      — What symbols exist in this file?
workspaceSymbol     — Search for a symbol across the workspace
goToImplementation  — What classes implement this interface/abstract?
prepareCallHierarchy — Get the call hierarchy item at this position
incomingCalls       — What calls this function/method?
outgoingCalls       — What does this function/method call?
```

## Practical Workflows

### Understanding unfamiliar code

1. `documentSymbol` on the file to see its structure
2. `hover` on key functions to understand signatures
3. `goToDefinition` to trace dependencies
4. `incomingCalls` to understand who uses this code

### Refactoring safely

1. `findReferences` on the symbol you want to change — know every callsite
2. `hover` to confirm the current type contract
3. Make your changes
4. Check diagnostics (automatic) for type errors introduced

### Debugging "undefined" errors

1. `hover` on the symbol — does Intelephense see it?
2. `goToDefinition` — can it resolve the definition?
3. If not, the symbol may need stubs or `includePaths` configured (see Configuration)

### Tracing call chains

1. `prepareCallHierarchy` on the function
2. `incomingCalls` — who calls this?
3. `outgoingCalls` — what does this call?

## Automatic Diagnostics

After every file edit, Intelephense pushes diagnostics automatically. These catch:

**Undefined symbols** — variables, functions, methods, classes, constants, properties
**Type errors** — incompatible argument types, return type mismatches
**Argument count** — wrong number of arguments to function/method
**Unused symbols** — unused variables, imports, private members
**Deprecated usage** — calls to `@deprecated` symbols
**Syntax errors** — unexpected tokens
**Implementation errors** — missing interface methods, abstract violations
**Member access** — accessing private/protected from wrong scope

Common diagnostic codes:
- **P1009** — Undefined type
- **P1010** — Undefined function
- **P1013** — Undefined method
- **P1036** — Non-static method called statically

## Configuration Reference

See `reference/lsp-config.md` for `.lsp.json` setup, stubs, diagnostics settings, and troubleshooting.

For WordPress-specific Intelephense configuration (stubs, includePaths, false positives), see the **wordpress** skill's `reference/intelephense-wordpress.md`.
