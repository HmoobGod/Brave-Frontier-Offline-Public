"""Synthetic, memory-only progress/storage guard for source screenshot runners.

This module is test infrastructure, never packaged into the Android app.
"""

INSTALL_STORAGE = r"""(() => {
  const entries = new Map();
  let writes = 0;
  const storage = Object.freeze({
    getItem: key => entries.get(String(key)) ?? null,
    setItem: (key, value) => { writes++; entries.set(String(key), String(value)); },
    removeItem: key => { writes++; entries.delete(String(key)); },
    clear: () => { writes++; entries.clear(); },
    key: index => Array.from(entries.keys())[index] ?? null,
    get length() { return entries.size; }
  });
  Object.defineProperty(window, 'localStorage', {value: storage});
  Object.defineProperty(window, 'BF_captureStorageAudit', {value: () => ({
    entries: Array.from(entries.entries()).sort((a,b) => a[0].localeCompare(b[0])),
    writes
  })});
})();"""

SNAPSHOT = """() => ({
  player: JSON.stringify(P), storage: BF_captureStorageAudit()
})"""


def assert_unchanged(page, baseline, context):
    """Reject any persistent player change or any storage call since baseline."""
    current = page.evaluate(SNAPSHOT)
    assert current['player'] == baseline['player'], (context, 'player progress changed')
    assert current['storage']['entries'] == baseline['storage']['entries'], (
        context, 'storage entries changed')
    assert current['storage']['writes'] == baseline['storage']['writes'], (
        context, 'storage write called, even if later restored')
    return dict(entirePlayerUnchanged=True, allStorageUnchanged=True,
                storageWriteCalls=0)
