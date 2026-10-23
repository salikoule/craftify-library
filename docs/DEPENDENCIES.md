# Dependencies (Tabulator + Anvil Extras)

Declared in **`anvil.yaml`** for git clones and consumer apps:

| Package | Version | `package_name` |
|---------|---------|----------------|
| Anvil Extras | v3.6.3 | `anvil_extras` |
| Tabulator | v3.3.2 | `tabulator` |

After cloning, open **Settings → Dependencies** in the Anvil IDE and confirm both are **linked** (no errors). If Run fails with an internal error, fix linking in the IDE first — the YAML IDs must match apps your account can access.

**LibraryDemo** (startup) needs these dependencies. **Form1** does not.
