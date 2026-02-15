import os
import re
import sys

DOCS_DIR = 'docs'
PLAN_FILE = 'docs/picture/image_generation_plan.md'

def main():
    if not os.path.exists(DOCS_DIR):
        print(f"Directory {DOCS_DIR} not found.")
        return

    # 1. Check Markdown files for local and global duplicates
    files = [f for f in os.listdir(DOCS_DIR) if f.endswith('.md')]
    global_image_map = {} # filename -> list of markdown files

    print("Checking markdown files for duplicates...")
    for filename in files:
        filepath = os.path.join(DOCS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find all images
        images = re.findall(r'!\[.*?\]\((.*?)\)', content)
        html_images = re.findall(r'<img\s+[^>]*src=[\'"](.*?)[\'"]', content)
        all_images = images + html_images

        # Check local duplicates
        seen = set()
        local_dupes = []
        for img in all_images:
            basename = os.path.basename(img)
            if basename in seen:
                local_dupes.append(basename)
            seen.add(basename)

            # Add to global map
            if basename in global_image_map:
                global_image_map[basename].append(filename)
            else:
                global_image_map[basename] = [filename]

        if local_dupes:
            print(f"WARNING: File {filename} has duplicate images: {local_dupes}")

    # Report global duplicates
    found_global = False
    for img, file_list in global_image_map.items():
        if len(file_list) > 1:
            # Filter out duplicates within the same file (already reported)
            unique_files = sorted(list(set(file_list)))
            if len(unique_files) > 1:
                print(f"ERROR: Global Duplicate: {img} appears in {unique_files}")
                found_global = True

    if not found_global:
        print("OK: No global duplicates found across different markdown files.")

    # 2. Check Plan file for duplicates
    if os.path.exists(PLAN_FILE):
        print(f"\nChecking plan file {PLAN_FILE} for duplicates...")
        with open(PLAN_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        plan_filenames = {}
        plan_duplicates = []

        for line in lines:
            stripped = line.strip()
            if not stripped or not stripped.startswith('|'):
                continue

            parts = [p.strip() for p in stripped.split('|')]
            if len(parts) < 4:
                continue

            if 'ID' in parts[1] or '---' in parts[1]:
                continue

            filename = parts[3]
            if filename in plan_filenames:
                plan_duplicates.append((filename, parts[1]))
            else:
                plan_filenames[filename] = parts[1]

        if plan_duplicates:
            print(f"ERROR: Found {len(plan_duplicates)} duplicate filenames in plan:")
            for name, id in plan_duplicates:
                print(f"  {name} (ID: {id})")
        else:
            print("OK: No duplicate filenames found in plan.")

    # Exit with error if any issues found
    if found_global or plan_duplicates:
        sys.exit(1)

if __name__ == "__main__":
    main()
