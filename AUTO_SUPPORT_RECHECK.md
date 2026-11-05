# Smart Auto: recheck support before execution

Auto plans every unit's action at the start of a turn. Two ready healers could
both queue a healing BB while allies were injured; after the first filled every
HP bar, the second still spent its entire gauge without healing anyone.

When both Auto Battle and optional Smart Auto are active, support BB execution
now reuses the current Smart Auto decision before spending gauge. A support
action that the policy now considers unnecessary becomes a normal attack with
the same target. A still-needed heal or stronger buff remains queued. The lookup
uses the current public policy, so Advanced Auto thresholds and the verified
BB-level preview keep working. The original start-of-turn plan is unchanged.

Manual BB actions and default Smart-OFF Auto retain their previous behavior.
Offensive BBs and experimental SBBs are not reconsidered by this support-only
hook. Existing status, item reservation and execution guards remain in charge.
Smart Auto stays off by default; this is DEMO policy, not native Global AI.

The regression first reproduced the second healer losing gauge100→0 after full
recovery. It now executes real planned actions through the actual game and
existing ailment modules: heal once, then attack while preserving the second
gauge; if the first healer is paralyzed, the second still heals. Manual and
Smart-OFF controls still execute both explicitly queued BBs. At 70% ally HP,
Advanced thresholds 35/75 respectively preserve/spend gauge through real
execution. Control setup writes exactly one isolated QoL preference key; player
and other storage stay unchanged, and combat leaves the full synthetic
player/storage/write count unchanged. Existing Smart/Advanced Auto,
coordination, status and BB-level tests remain required; the APK gate checks the
hook and public method in packaged HTML.

No reward, source skill table, saved BB mastery, save schema, owner Gem/Imp
adjustment, Android runtime code or signing identity changes. No real saves or
installed APK are used. Physical-device acceptance remains unverified.
