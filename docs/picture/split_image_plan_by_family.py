import re
from pathlib import Path

# Adjusted path to match user's context (assuming execution from project root)
# The file is likely at g:\temp_make_md_nanobanana_prompt\docs\picture\image_generation_plan.md
# So if we run from g:\temp_make_md_nanobanana_prompt, the path "docs/picture/image_generation_plan.md" is correct.

src = Path("docs/picture/image_generation_plan.md")

# Fallback for robustness if run from within docs/picture
if not src.exists() and Path("image_generation_plan.md").exists():
    src = Path("image_generation_plan.md")

if not src.exists():
    print(f"Error: Source file {src} not found.")
    exit(1)

out_dir = src.parent
lines = src.read_text(encoding="utf-8").splitlines()

if len(lines) < 2:
    print("Error: Source file is empty or too short.")
    exit(1)

header = lines[0]
separator = lines[1]
rows = lines[2:]

pattern = re.compile(r"([A-Za-z0-9]+_(?:cs|ts))_")
groups = {}

for row in rows:
    # Skip empty lines or lines that don't look like table rows
    if not row.strip().startswith("|"):
        continue

    cols = [c.strip() for c in row.strip().strip("|").split("|")]
    if len(cols) < 2:
        continue

    file_name = cols[1]
    matched = pattern.search(file_name)
    if not matched:
        continue

    key = matched.group(1)
    groups.setdefault(key, []).append(row)

for key, grouped_rows in sorted(groups.items()):
    out = out_dir / f"image_generation_plan.{key}.md"
    content = "\n".join([header, separator, *grouped_rows]) + "\n"
    out.write_text(content, encoding="utf-8")
    print(f"{out} ({len(grouped_rows)} rows)")
