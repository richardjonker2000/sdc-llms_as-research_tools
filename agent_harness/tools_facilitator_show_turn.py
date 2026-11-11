"""Readable transcript of one turn: agent text, tool calls, blocked actions, tokens."""
import json, sys
ev = [json.loads(l) for l in open(sys.argv[1])]
tok = {"in": 0, "out": 0, "reason": 0, "cache": 0}; steps = 0
for e in ev:
    t, p = e.get("type"), e.get("part", {})
    if t == "text": print("\nAGENT:", p.get("text", ""))
    elif t == "tool_use":
        st = p.get("state", {}); i = st.get("input", {})
        what = i.get("command") or i.get("filePath") or i.get("name") or ""
        what = str(what).split("agent_v2/")[-1].replace("\n", " ")[:140]
        flag = "" if st.get("status") == "completed" else f"   <-- {st.get('status')}: {str(st.get('error', ''))[:160]}"
        print(f"  [{p.get('tool')}] {what}{flag}")
    elif t == "step_finish":
        steps += 1; k = p.get("tokens", {})
        tok["in"] += k.get("input", 0); tok["out"] += k.get("output", 0); tok["reason"] += k.get("reasoning", 0); tok["cache"] += k.get("cache", {}).get("read", 0)
    elif t == "error": print("ERROR:", json.dumps(e)[:400])
print(f"\n-- {steps} model steps, tokens: {tok}")
