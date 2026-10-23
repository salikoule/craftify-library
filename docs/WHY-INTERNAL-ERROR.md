# Why “The app could not be loaded” / internal error

That pink banner appears **before any of your forms run**. Anvil’s servers failed while **building the app bundle** (compile + link dependencies + theme). The hex id (`413a0197…`, `5eaeaccf…`) is only for Anvil support — it is not a line in your Python code.

## Most common cause (this repo)

**`anvil.yaml` lists dependency apps your Anvil account cannot link.**

This project had:

```yaml
dependencies:
- … Anvil Extras (app_id C6ZZPAPN4YYF5NVJ)
- … Tabulator (app_id TGQCF3WT6FVL2EM2)
```

Those IDs come from **another workspace** (e.g. Neways). On your Craftify account they often stay **unlinked or red** in **Settings → Dependencies**. Anvil still tries to resolve them on every Run → **internal error**, with no Python traceback in the browser.

**Important:** If you run `anvil watch`, the **cloud copy** may keep putting `dependencies` and `startup_form: null` back into `anvil.yaml` after you edit locally. You must fix the **app in the Anvil IDE**, not only on disk.

## How to confirm (2 minutes)

1. Open the app at [anvil.works](https://anvil.works) (not only git watch).
2. **Settings → Dependencies** (or **App Dependencies**).
3. If **Tabulator** or **Anvil Extras** show an error, “needs linking”, or missing — that is the failure.

Also check **Settings → Runtime**: if **Python 3.14** is selected and the app fails, try **Python 3.12** (local `anvil.yaml` now uses `python312`).

## Recovery procedure (do in this order)

### A. Stop the sync tug-of-war

1. **Stop `anvil watch`** in the terminal (Ctrl+C).
2. Only continue when you are ready to push a deliberate change.

### B. Fix the cloud app (required)

In the **Anvil IDE** for **craftify-library**:

1. **Settings → Dependencies**  
   - **Remove** Tabulator and Anvil Extras *or* use **Add dependency** and pick them from the **public catalog** (not broken git IDs).  
   - Until they link cleanly, leave **zero** dependencies.
2. **Settings → Startup form** → **Form1**.
3. **Save** / let the IDE sync.
4. Click **Run**. You should see the Form1 placeholder HTML.

### C. Push minimal git config (optional, after B works)

Local repo is intentionally reset to a **minimal boot** `anvil.yaml`:

- No `dependencies`
- No `native_deps`
- No `startup_form: null`
- Empty `theme.css` (full styles stay in `craftify-full-theme.css` for later)
- Python **3.12**

From the repo (watch **stopped**):

```bash
cd craftify-library
# commit minimal anvil.yaml if you use git push to Anvil
git add anvil.yaml theme/
git commit -m "Minimal boot: no deps in yaml, python312"
# then anvil sync / IDE git pull — one direction only
```

### D. Turn the library back on (after Form1 runs)

1. In IDE, add **Anvil Extras v3.6.3** and **Tabulator v3.3.2** from the dependency browser.
2. Run **LibraryDemo** (needs those deps).
3. Optionally copy the dependency block into `anvil.yaml` again — only after both are green in the IDE.

See [DEPENDENCIES.md](./DEPENDENCIES.md).

## If it still fails after zero dependencies

1. **New test app**: Anvil → New app → Clone from Git → same repo, branch with minimal `anvil.yaml`. Proves whether the cloud app record is corrupt.
2. **Support**: email/chat Anvil with the **exact error id** and app name **craftify-library**.
3. **Local runtime** (real traceback):

   ```bash
   cd craftify-library
   python3 -m venv .venv && . .venv/bin/activate
   pip install anvil-app-server
   anvil-app-server --app .
   # open http://localhost:3030 — errors print in the terminal
   ```

## What is *not* the cause (usually)

- Form1 Python body (it is trivial).
- LibraryDemo until you set it as startup.
- Cyclops / body-comp (different projects).

The failure is **platform app assembly**, almost always **dependencies** or **IDE/cloud config out of sync with git**.
