
import os

plan_file = 'docs/picture/image_generation_plan.md'

with open(plan_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

header_lines = []
data_rows = []

for line in lines:
    stripped = line.strip()
    if not stripped:
        continue
    if stripped.startswith('|'):
        parts = [p.strip() for p in stripped.split('|')]
        # parts[0] is empty, parts[1] is ID, parts[2] is File Name
        if len(parts) > 3 and not ('ID' in parts[1] or '---' in parts[1]):
             data_rows.append({'line': line, 'filename': parts[2], 'image': parts[3]})
        else:
             header_lines.append(line)
    else:
        header_lines.append(line)

to_remove = []

for row in data_rows:
    filename = row['filename']
    image = row['image']

    filepath = filename
    # Check if file exists relative to repo root
    if not os.path.exists(filepath):
        # try strictly under docs if not found
        if not filepath.startswith('docs/'):
             filepath = os.path.join('docs', filepath)

    if not os.path.exists(filepath):
        print(f"Warning: File {filepath} not found for {filename}")
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if image in content:
        # print(f"Found existing image {image} in {filepath}. Removing from plan.")
        to_remove.append(row)

# Construct new content
new_data_rows = []
for row in data_rows:
    if row not in to_remove:
        new_data_rows.append(row['line'])

# Re-index
final_lines = header_lines[:]
current_id = 1
for line in new_data_rows:
    parts = line.split('|')
    parts[1] = f" {current_id} "
    final_lines.append("|".join(parts))
    current_id += 1

with open(plan_file, 'w', encoding='utf-8') as f:
    for line in final_lines:
        f.write(line)

print(f"Original rows: {len(data_rows)}")
print(f"Removed rows: {len(to_remove)}")
print(f"Remaining rows: {len(new_data_rows)}")
