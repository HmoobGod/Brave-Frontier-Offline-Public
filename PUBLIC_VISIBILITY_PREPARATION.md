# Brave Frontier public-repository migration guide — 2026-10-26

## Current status

**Code preparation complete on this branch; publishing and CI verification pending.**
This branch is based on the original **v94 development commit**, not the much older `main` gameplay snapshot.

- `chore/public-migration-prep-v94` removes the persistent development APK signing key
  from the **current working tree**. It does **NOT** erase earlier private Git history.
- The GitHub Actions build requires the repo-level `BF_DEBUG_KEYSTORE_B64` secret
  and refuses to fall back to a public source file.
- GitHub Actions token permissions are restricted to read-only; checkout does not
  persist its authentication credentials.
- New-repository CI builds use `versionCode = 100000 + github.run_number`.
  This is intentional: a new repo starts numbering runs at 1, and
  `1000 + github.run_number` would potentially downgrade an installed private-repo APK.
- The existing Android application ID `org.bravefrontier.offline`, development certificate,
  app contents, and save schema are deliberately unchanged in this preparation.
- The repository owner has confirmed adding `BF_DEBUG_KEYSTORE_B64` to the
  **existing private** repository, but the secret's contents and matching signing identity
  are **not yet verified by a successful build**.
- Recent private-repo Actions jobs, including the preparation-branch run, completed
  without executing build steps. Do not treat this as successful compilation/testing.

## Important: DO NOT make the original repository public

The private repository still contains the development signing key in *old commits and
other feature branches*, along with commit metadata and archived third-party game assets.
Deleting the key from this branch does not protect the old history if the original repository
is switched to public. Keep `HmoobGod/Brave-Frontier-Offline` private as your backup.

The goal is to publish a **fresh repository created from a ZIP snapshot**, without
carrying over its original Git history or signing key.

## Recommended beginner-friendly public publishing steps (GitHub Desktop)

1. In the **private** repository, switch the branch dropdown to
   `chore/public-migration-prep-v94`.
2. Choose **Code > Download ZIP**. This ZIP contains the current files only,
   not the old `.git` history. **Do not download a ZIP from `main` or v94 itself**.
3. On your PC, extract the ZIP. Open the extracted folder and confirm the top level has
   `.github`, `app`, and `build.gradle`, and that
   `.github/debug/bf-development-debug.keystore.b64` is **absent**.
4. In **GitHub Desktop**, choose **File > Add Local Repository**, select the extracted
   folder, and if prompted, choose **Create a Repository**. Commit the files if needed.
   The new repo's history must begin with a **fresh initial commit**.
5. Choose **Publish repository**. Uncheck **Keep this code private**.
   Name it something distinguishable, e.g. `Brave-Frontier-Offline-Public`.
   The new repository is public and the original stays private.
6. In the **new public repository**, go to
   **Settings > Secrets and variables > Actions > New repository secret**.
   Add `BF_DEBUG_KEYSTORE_B64` using the *same full Base64 contents from the
   original private repository's signing-key file*. The secret in the private repository
   is **not copied automatically**. Never paste the value in a public file, PR, or chat.
7. The new public repo's GitHub Actions build should run on pushes to `main`;
   once the secret is configured, rerun any earlier failed build using GitHub Actions.
8. Confirm a **successful** signed APK and its certificate matches the prior installed APK,
   and then test in-place installation and save persistence before designating the public
   repo as the new development source of truth.

### Safety/limitations

- This process changes source visibility and build billing, **not** GitHub write permissions.
  Only the owner and explicitly authorized collaborators can push to the new repository.
- Publishing proprietary game files may create copyright/takedown exposure.
- The migration does not imply v94 was verified through CI or tested on Android.
- Keep a verified save backup outside the application, particularly before any uninstall.
- Use public-repository branch protection/rulesets once available; they are not enabled here.
- Do not push/fork/clone the **entire private Git history** into a public repository.
