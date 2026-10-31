# v231 — Renderer recovery dialog lifecycle (draft stacked on v230)

**Base:** PR #163 exact HEAD `0be4692ddea05a9c59e93fc96ac0d5534b9a0f15`, not merged main. This follow-up is held until v230's two Android builds pass, the guarded v230 merge is complete and v230 receives device acceptance before Current APK promotion.

## Purpose
The v226 renderer termination handler displayed a non-cancelable native dialog using `Builder.show()` without retaining its instance. During Activity destruction, the v229 page-load error dialog was dismissed, but the renderer-recovery dialog could stay attached and potentially leak a window.

## Change
Track only the existing renderer-recovery dialog in a private `AlertDialog` field; use `create()` and `show()`, then dismiss and release it in `onDestroy()`, before `super.onDestroy()`. The same Restart interface / Close buttons, wording and non-cancelable behavior remain. A source regression verifies lifecycle and original save-isolation boundaries in both exact-head UI preflight and the full Android CI.

No gameplay, original data, battle logic, saves, signing, permissions, UI navigation JS/CSS, manifest or application ID changes.

## Limitations / gates
Source checks do not reproduce Android window-manager lifecycles. Require exact-head CI/Android build, independent Claude review, merge after v230, and real-device renderer-kill/recovery and save preservation testing before Current APK promotion.
