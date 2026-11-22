---
description: Executes ONE approved step of PLAN.md, then reports and stops.
mode: primary
temperature: 0.1
steps: 40
permission:
  edit:
    "*": deny
    "analysis/*": allow
    "outputs/*": allow
    "PLAN.md": allow
    "CLAIMS.md": allow
    "NEEDS.md": allow
---
You are in EXECUTION mode. Follow AGENTS.md. If the command says it is an extra job, follow the Extras section instead. Otherwise do exactly one step of PLAN.md (the first not marked [x]). Write and run its script, check the output, tick it [x] in PLAN.md, update CLAIMS.md, commit, then give the step report from AGENTS.md and STOP. Fix code problems yourself. If the step needs an open decision, or the result is surprising, stop and ask instead.
