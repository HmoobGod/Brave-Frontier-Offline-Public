# Brave Frontier Global v66.00 — Curse Locks BB Gauge Items

Base: candidate v65.00 commit 2b0625b013f93c30d6b2c2b5ae1c02ce699bc425. The original 2022 item master identifies item #21000 as a one-ally BB gauge fill item. Global status documentation confirms that Curse (status code 5) prevents **all Brave Burst gauge charging** until cured, not merely normal attack BC gain. v46's prior source-item command bypassed that restriction: it could charge a cursed unit's gauge to 100% even while v59 correctly blocked normal charging.

Now the existing v46 `canBenefit` predicate consults v57's living ailment state. A cursed recipient is ineligible for #21000; the rejected command consumes **neither** temporary DEMO item stock nor the actor's Guard reservation. Cure item #20220 or natural Curse expiry restores eligibility. Other original-source item mechanics, Curse expiration, owned inventory/save schema, Android identity and signing are unaffected.

Verification: new v66 Chromium test covers blocked target, stock and action preserved, selective cure, successful item use, default training isolation and v7 save stability; all inherited browser/APK checks; exact v66 packaged artifact check. This is a source-backed rule across two previously independent modules, **not** a claim of decoded native item timing.
