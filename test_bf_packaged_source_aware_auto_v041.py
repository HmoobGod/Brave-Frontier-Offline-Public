"""v0.41 APK: smart-support QoL present, v0.40 and saves preserved."""
from pathlib import Path
from zipfile import ZipFile
p=Path(__file__).resolve().parent/'app/build/outputs/apk/debug/app-debug.apk'
assert p.is_file(),p
with ZipFile(p) as z:
    html=z.read('assets/index.html').decode('utf-8')
    for m in ('/* BF_SOURCE_AWARE_AUTO_V041 */','/* BF_BATTLE_BB_GUIDE_V040 */',
              '/* BF_EVOLUTION_ROADMAP_V039 */','/* BF_GLOBAL_OTHER_SIX_STAR_V038 */'):
        assert html.count(m)==1,m
    assert html.count('id="bf041-smart-auto-style"')==1
    assert 'window.BF041SmartAuto?.kindFor(p)' in html
    assert html.count('window.BF041SmartAuto?.reconsider?.(p);')==1
    dispatch = ('break;window.BFGlobalCurseBBLockV5900?.blockBurst?.(p.id);'
                'window.BF041SmartAuto?.reconsider?.(p);await performUnit(p,token);')
    assert html.count(dispatch) == 1
    assert 'Object.freeze({kindFor,enabled,reconsider})' in html
    assert html.count('function scheduleAuto(){if(document.hidden||!S.auto||S.busy||S.over)return;') == 1
    assert html.count('if(document.hidden||token!==epoch||S.busy||S.over||!S.auto)return;') == 1
    # Verify the complete generated lifecycle handler, not only its marker.
    import ast
    source = Path(__file__).resolve().parent/'prepare_source_aware_auto_v041.py'
    tree = ast.parse(source.read_text())
    ui = next(ast.literal_eval(node.value) for node in tree.body
              if isinstance(node, ast.Assign) and any(
                  isinstance(target, ast.Name) and target.id == 'ui' for target in node.targets))
    handler = ui.split('  function pauseForBackground()', 1)[1].split('  function kindFor(p)', 1)[0]
    assert '  function pauseForBackground()' + handler in html
    assert 'bf_global_offline_demo_v7' in html
    assert 'unit_anime_atlas_10025.png' in html
print('PASS v0.41 APK source-aware Auto Battle optional; all previous content and v7')
