# Auto Battle: choose a normal action while cursed

Curse already blocks BB use and gauge gain. Auto nevertheless queued `burst`
for a cursed unit with a full gauge. The later execution guard converted it to
an attack after normal critical/crystal handlers had inspected the original
action, so those normal-attack paths were missed.

Default and Smart Auto now consult the existing Curse API when choosing an
action. A cursed actor chooses `attack` before the handler chain. Advanced Auto
also preserves this choice instead of overriding it with a healing BB. Actual
normal damage, criticals and uncollected crystal records use existing code;
the existing execution guard still prevents gauge gain. Cure/expiry restores
ordinary BB choices. Without the optional Curse module, prior choices remain.

Manual commands, status durations/cures, damage formulas, source data, saved
mastery, rewards, saves and owner Gem/Imp settings are unchanged. This corrects
Auto orchestration; native Global AI/pickups are not reconstructed.

The regression uses actual scheduled Auto turns with real status and critical/
crystal handlers. Smart OFF/ON, a partial gauge, and an Advanced healer needing
recovery must retain normal critical/crystal processing and their existing
gauge. Cure and three-turn expiry restore BB choice. A phase observer isolates
one real round without replacing combat calculations. Full synthetic P/storage
is unchanged during combat; Advanced setup writes one isolated preference key
without changing P or other storage. The packaged gate checks both guards and
byte equality for the Advanced Auto asset. Android/device/save acceptance is
separate from these source checks; no install, signing or release is performed.
