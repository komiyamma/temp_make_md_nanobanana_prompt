
filepath = 'docs/picture/image_generation_plan.md'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

header_lines = []
data_rows = []
seen_filenames = set()

for line in lines:
    stripped = line.strip()
    if not stripped:
        continue

    if stripped.startswith('|'):
        parts = [p.strip() for p in stripped.split('|')]
        # parts[0] is empty string before first pipe
        # parts[1] is ID
        # parts[2] is File Name
        # parts[3] is Proposed Image Filename

        if len(parts) > 3:
            col1 = parts[1]
            if 'ID' in col1 or '---' in col1:
                header_lines.append(line)
                continue

            image_filename = parts[3]
            if image_filename in seen_filenames:
                continue

            seen_filenames.add(image_filename)
            data_rows.append(line)
        else:
            header_lines.append(line)
    else:
        header_lines.append(line)

# Re-index IDs
new_rows = []
current_id = 1
for row in data_rows:
    parts = row.split('|')
    # Update ID column (index 1)
    parts[1] = f" {current_id} "
    new_rows.append("|".join(parts))
    current_id += 1

with open(filepath, 'w', encoding='utf-8') as f:
    for h in header_lines:
        f.write(h)
    for r in new_rows:
        f.write(r)

print(f"Deduplicated plan. Total rows: {len(new_rows)}")
