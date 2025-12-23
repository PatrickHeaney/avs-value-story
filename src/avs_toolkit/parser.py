import re

def parse_markdown_story(content: str) -> dict:
    data = {}
    id_match = re.search(r"^#\s+(VS-\d+)", content, re.MULTILINE)
    data['story_id'] = id_match.group(1) if id_match else "VS-UNKNOWN"
    
    goal_match = re.search(r"(?i)## Goal\n+([\s\S]+?)(?=\n##|$)", content)
    data['goal'] = goal_match.group(1).strip() if goal_match else ""
    
    instr_block = re.search(r"(?i)## Instructions\n+([\s\S]+?)(?=\n##|$)", content)
    steps = []
    if instr_block:
        raw_steps = re.findall(r"(\d+)\.\s+(.+)", instr_block.group(1))
        for num, text in raw_steps:
            rule_match = re.search(r"\[Rule:\s*(.+?)\]", text)
            rule = rule_match.group(1) if rule_match else None
            action = text.split("[Rule:")[0].strip()
            steps.append({"step_number": int(num), "action": action, "validation_rule": rule})
    data['instructions'] = steps
    
    context_block = re.search(r"(?i)## Context\n+([\s\S]+?)(?=\n##|$)", content)
    assets = []
    if context_block:
        assets = re.findall(r"-\s+`?([\w\.\-/]+)`?", context_block.group(1))
    data['context'] = {"mandatory_assets": assets}
    
    return data
