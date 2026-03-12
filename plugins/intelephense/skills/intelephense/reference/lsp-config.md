# Intelephense LSP Configuration

## .lsp.json Setup

Place `.lsp.json` in your project root or configure globally.

### Minimal Configuration

```json
{
  "intelephense": {
    "command": "intelephense",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".php": "php",
      ".phtml": "php"
    }
  }
}
```

### Configuration with Settings

```json
{
  "intelephense": {
    "command": "intelephense",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".php": "php",
      ".phtml": "php",
      ".inc": "php"
    },
    "settings": {
      "intelephense": {
        "environment": {
          "phpVersion": "8.2.0",
          "includePaths": []
        },
        "files": {
          "maxSize": 5000000,
          "associations": ["*.php", "*.phtml", "*.inc"],
          "exclude": [
            "**/.git/**",
            "**/node_modules/**"
          ]
        },
        "diagnostics": {
          "enable": true,
          "run": "onType"
        }
      }
    }
  }
}
```

## Available .lsp.json Fields

| Field | Description |
|-------|-------------|
| `command` | Path to the LSP binary |
| `args` | Command arguments (use `["--stdio"]`) |
| `extensionToLanguage` | Map file extensions to language IDs |
| `transport` | `stdio` (default) or `socket` |
| `env` | Environment variables for the process |
| `initializationOptions` | Passed during LSP init (e.g., `licenceKey`, `storagePath`, `clearCache`) |
| `settings` | Passed via `workspace/didChangeConfiguration` |
| `workspaceFolder` | Workspace root override |
| `startupTimeout` | Milliseconds to wait for startup |
| `shutdownTimeout` | Milliseconds to wait for shutdown |
| `restartOnCrash` | Auto-restart on crash (boolean) |
| `maxRestarts` | Max restart attempts |

## License Key

Activate your license by creating `$HOME/intelephense/licence.txt` with the key, or pass via `.lsp.json`:
```json
{
  "initializationOptions": {
    "licenceKey": "YOUR-KEY-HERE"
  }
}
```

## Intelephense Settings Reference

### Stubs

The `stubs` array controls which PHP extension type information is available. Additional stubs (e.g., `wordpress`) can be added for framework support.

Default stubs (63 total): apache, bcmath, bz2, calendar, com_dotnet, Core, ctype, curl, date, dba, dom, enchant, exif, FFI, fileinfo, filter, fpm, ftp, gd, gettext, gmp, hash, iconv, imap, intl, json, ldap, libxml, mbstring, meta, mysqli, oci8, odbc, openssl, pcntl, pcre, PDO, pdo_ibm, pdo_mysql, pdo_pgsql, pdo_sqlite, pgsql, Phar, posix, pspell, readline, Reflection, session, shmop, SimpleXML, snmp, soap, sockets, sodium, SPL, sqlite3, standard, superglobals, sysvmsg, sysvsem, sysvshm, tidy, tokenizer, xml, xmlreader, xmlrpc, xmlwriter, xsl, Zend OPcache, zip, zlib

**Important:** When you set `stubs`, you REPLACE the defaults — you don't append. Always include the default stubs you need plus any framework-specific stubs.

### Diagnostics Settings

All default to `true`:

| Setting | What It Catches |
|---------|----------------|
| `enable` | Master toggle |
| `run` | `"onType"` (default) or `"onSave"` |
| `undefinedVariables` | Variables used but never assigned |
| `undefinedTypes` | Classes/interfaces/traits that don't exist (P1009) |
| `undefinedFunctions` | Functions that don't exist (P1010) |
| `undefinedConstants` | Constants that don't exist |
| `undefinedClassConstants` | Class constants that don't exist |
| `undefinedMethods` | Methods that don't exist (P1013) |
| `undefinedProperties` | Properties that don't exist |
| `unusedSymbols` | Unused variables, imports, private members |
| `unexpectedTokens` | Syntax errors |
| `duplicateSymbols` | Duplicate definitions |
| `argumentCount` | Wrong number of arguments |
| `typeErrors` | Type incompatibilities |
| `deprecated` | Usage of `@deprecated` symbols |
| `memberAccess` | Invalid member access (private/protected) |
| `implementationErrors` | Missing interface methods |
| `languageConstraints` | PHP language violations |

### Selectively Disabling Diagnostics

For frameworks with heavy dynamic features (magic methods, runtime resolution), selectively disable specific checks:

```json
{
  "diagnostics": {
    "undefinedMethods": false,
    "undefinedProperties": false
  }
}
```

This is a tradeoff — you lose real error detection. Prefer adding stubs/includePaths first.

### Environment Settings

```json
{
  "environment": {
    "phpVersion": "8.2.0",
    "shortOpenTag": true,
    "includePaths": []
  }
}
```

### Files Settings

```json
{
  "files": {
    "maxSize": 5000000,
    "associations": ["*.php", "*.phtml"],
    "exclude": [
      "**/.git/**",
      "**/node_modules/**",
      "**/vendor/{[^b],?[^a]}*/**"
    ]
  }
}
```

The `exclude` pattern `**/vendor/{[^b],?[^a]}*/**` excludes everything in vendor except directories starting with `ba` (preserving `barryvdh` and similar commonly-needed packages). Adjust as needed.

### Compatibility

```json
{
  "compatibility": {
    "preferPsalmPhpstanPrefixedAnnotations": false
  }
}
```

Set to `true` if your codebase uses `@psalm-param` or `@phpstan-return` style annotations.

## Troubleshooting

### "Undefined function" for framework functions
Add the appropriate stub to `stubs` (e.g., `"wordpress"`). For third-party libraries, install composer stubs or add paths to `includePaths`.

### Indexing is slow / memory issues
- Increase `files.maxSize` if large files are skipped
- Use `files.exclude` to skip directories you don't develop
- Maximum 262,143 PHP files per workspace

### Short open tags `<?` not recognized
Set `environment.shortOpenTag` to `true`.

### Stale index after major changes
Pass `"clearCache": true` in `initializationOptions` to force re-index, then remove it.
