# Brave Frontier Offline v0.13.1 — GitHub cloud-build setup

This project contains a working GitHub Actions **build configuration**, not a verified APK.

## First-time setup

1. Create a private repository at https://github.com/new, e.g. `brave-frontier-offline`. Set the default branch to `main`.
2. Extract this ZIP onto a PC.
3. In the new repo on GitHub, choose **Add file > Upload files**. Drag all of the extracted project contents (including the hidden `.github` directory) into the uploader. Do not place the entire containing folder inside the repo — `app/`, `build.gradle` and `.github/` must be at the repository root.
4. Commit the upload to `main`.
5. Open your repo's **Actions** tab and select **Build Offline Android APK**. It should start on push; you can also choose **Run workflow**.
6. Once a run is successful, open the run, find **Artifacts**, and download `BraveFrontierOffline-demo-debug-apk`. Extract the downloaded artifact ZIP to obtain `app-debug.apk`.
7. Install on your own Android device after reviewing it. The APK is a debug/sideload build, not a Play Store release.

Share the private repository's `owner/repo` URL in ChatGPT, and ensure the GitHub connection has access. ChatGPT can then review the code and GitHub Actions logs, update source with your direction, and troubleshoot builds.

## Keep safe

Never commit passwords, service account keys, signed release keystores, or real production API credentials. Leave the repository private while using archived proprietary game assets. Export a save JSON before reinstalling a debug APK signed with a different key.

If GitHub Actions says it cannot find the workflow, check that `.github/workflows/build-debug-apk.yml` is at the repo root and GitHub Actions is enabled under repository settings.
