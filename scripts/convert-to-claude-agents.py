"""Convert Xcerebro Tier A/B YAML agents to Claude Code ~/.claude/agents/ markdown format."""
import os, re, pathlib

REPO_ROOT = pathlib.Path(__file__).parent.parent
AGENTS_DIR = pathlib.Path.home() / ".claude" / "agents"
AGENTS_DIR.mkdir(parents=True, exist_ok=True)

def extract_field(text, field):
    """Extract a YAML block scalar (> or |) or plain string value for a field."""
    pattern = rf"^{field}:\s*(>-?|\\|-)?\s*\n?(.*?)(?=\n\w|\Z)"
    m = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if not m:
        return ""
    # Plain single-line value
    if not m.group(1):
        return m.group(2).strip()
    # Block scalar — collect indented lines
    after = text[m.start():]
    lines = after.split("\n")[1:]
    indent = None
    result = []
    for line in lines:
        if line.strip() == "":
            result.append("")
            continue
        stripped = line.lstrip()
        current_indent = len(line) - len(stripped)
        if indent is None and stripped:
            indent = current_indent
        if indent is not None and current_indent < indent and stripped:
            break
        result.append(stripped)
    return " ".join(l for l in result if l).strip()

def extract_list(text, field):
    """Extract a YAML sequence under a field."""
    pattern = rf"^{field}:\s*\n((?:[ \t]+-[^\n]*\n?)+)"
    m = re.search(pattern, text, re.MULTILINE)
    if not m:
        return []
    items = re.findall(r"-\s*(.+)", m.group(1))
    return [i.strip().strip('"\'') for i in items]

def convert(yaml_path):
    raw = yaml_path.read_text(encoding="utf-8", errors="replace")

    agent_id   = extract_field(raw, "id") or yaml_path.stem
    name       = extract_field(raw, "name") or agent_id
    role       = extract_field(raw, "role")
    goal       = extract_field(raw, "goal")
    backstory  = extract_field(raw, "backstory")
    expected   = extract_field(raw, "expected_output")
    tasks      = extract_list(raw, "sample_tasks")
    tier       = extract_field(raw, "tier")

    # Description = first sentence of role (for Claude Code's agent picker)
    desc_base = role.split(".")[0].strip() if role else name
    description = f"{name} — {desc_base}" if desc_base != name else name

    parts = [f"# {name}\n"]
    if role:
        parts.append(f"## Role\n{role}\n")
    if goal:
        parts.append(f"## Goal\n{goal}\n")
    if backstory:
        parts.append(f"## Background\n{backstory}\n")
    if expected:
        parts.append(f"## Output format\n{expected}\n")
    if tasks:
        parts.append("## Example requests\n" + "\n".join(f"- {t}" for t in tasks) + "\n")
    if tier:
        parts.append(f"<!-- tier:{tier} source:xcerebro-2.0 -->")

    md = f"---\nname: {agent_id}\ndescription: {description}\n---\n\n" + "\n".join(parts)
    return agent_id, md

converted = []
for tier_dir in ["tier-a", "tier-b"]:
    for yaml_file in sorted((REPO_ROOT / "agents" / tier_dir).glob("*.yaml")):
        try:
            agent_id, md = convert(yaml_file)
            out = AGENTS_DIR / f"{agent_id}.md"
            out.write_text(md, encoding="utf-8")
            converted.append(agent_id)
        except Exception as e:
            print(f"  SKIP {yaml_file.name}: {e}")

print(f"\nInstalled {len(converted)} agents to {AGENTS_DIR}")
print("\n".join(f"  - {a}" for a in converted))
