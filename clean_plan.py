import re

filepath = 'docs/picture/image_generation_plan.md'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = []
data_map = {}

for line in lines:
    stripped = line.strip()
    if not stripped:
        continue

    # Check if it's a table row
    if stripped.startswith('|'):
        parts = stripped.split('|')
        if len(parts) > 1:
            first_col = parts[1].strip()

            # Check if header or separator
            if 'ID' in first_col or '---' in first_col:
                header.append(line)
                continue

            # Check if it's a data row with an ID
            if first_col.isdigit():
                current_id = int(first_col)
                data_map[current_id] = line
            else:
                # Some other table row? Should not happen in this strict format
                header.append(line)
    else:
        # Not a table row (maybe empty line or description? usually none in this file)
        header.append(line)

# Sort IDs
sorted_ids = sorted(data_map.keys())

with open(filepath, 'w', encoding='utf-8') as f:
    for h in header:
        f.write(h)
    for i in sorted_ids:
        f.write(data_map[i])

print(f"Cleaned {len(sorted_ids)} rows. Max ID: {max(sorted_ids) if sorted_ids else 0}")
