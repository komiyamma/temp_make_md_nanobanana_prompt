
filepath = 'docs/picture/image_generation_plan.md'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.strip().startswith('|'):
        parts = line.split('|')
        if len(parts) > 2:
            filename = parts[2].strip()
            # If filename doesn't start with docs/ and isn't the header or separator
            if filename and filename != 'File Name' and '---' not in filename and not filename.startswith('docs/') and not filename.startswith('test_'):
                # Add docs/ prefix
                parts[2] = f" docs/{filename} "
                new_lines.append("|".join(parts))
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed filenames in plan.")
