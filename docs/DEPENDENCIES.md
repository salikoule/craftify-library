# Add dependencies in the Anvil IDE (required for LibraryDemo)

`anvil.yaml` **does not** list Tabulator / Anvil Extras anymore. Unresolved dependency app IDs caused **“An internal error occurred”** on Run for some accounts.

In the **craftify-library** app:

1. **Settings → Dependencies → Add**
2. Add **Anvil Extras** — version **v3.6.3** (package `anvil_extras`)
3. Add **Tabulator** — version **v3.3.2** (package `tabulator`)

Use the Anvil dependency search if the app IDs from other projects are not visible.

After both show as linked, open **LibraryDemo** (or set it as startup form). **Form1** should run without them.

Optional: once linking works, you can copy dependency stanzas back into `anvil.yaml` from git history for git-native clones.
