import os
import re

def generate_prompts():
    plan_file = 'image_generation_plan.md'
    template_file = 'nanobanana_template.md'

    if not os.path.exists(plan_file):
        print(f"Error: {plan_file} not found.")
        return
    if not os.path.exists(template_file):
        print(f"Error: {template_file} not found.")
        return

    # Read Template
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # Read Plan
    with open(plan_file, 'r', encoding='utf-8') as f:
        plan_lines = f.readlines()

    # Parse Plan
    # Table headers: | ID | File Name | Group | Proposed Image Filename | Relative Link Path | Prompt | Insertion Point |
    # We need "Proposed Image Filename" (index 3) and "Prompt" (index 5)
    # Indices might vary if valid split, let's be robust.
    
    header_found = False
    headers = []
    
    for line in plan_lines:
        line = line.strip()
        if not line.startswith('|'):
            continue
        
        # Split by pipe, ignore first and last empty strings from split
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3: # Not a valid table row
            continue
            
        # Clean up empty start/end if present (due to leading/trailing pipes)
        if parts[0] == '': parts.pop(0)
        if parts[-1] == '': parts.pop(-1)

        if not header_found:
            # Check if this is the header row
            if 'Proposed Image Filename' in parts and 'Prompt' in parts:
                headers = parts
                header_found = True
                try:
                    filename_idx = headers.index('Proposed Image Filename')
                    prompt_idx = headers.index('Prompt')
                except ValueError:
                    print("Error: Could not find required columns in header.")
                    return
            continue
        
        if '---' in line: # Separator line
            continue

        # Data row
        if len(parts) != len(headers):
            # Handle potential pipe inside content? 
            # Simple split might fail if content has pipes. 
            # But based on the file content seen, pipes seem to be delimiters.
            # If length mismatch, simple print warning and skip or try best effort.
            # The User's file seems clean.
             pass

        if len(parts) > max(filename_idx, prompt_idx):
            filename_raw = parts[filename_idx]
            prompt = parts[prompt_idx]

            if not filename_raw or not prompt:
                continue

            # Process Filename
            # "cnt_hm_activeperl_architecture_diagram.png" -> "cnt_hm_activeperl_architecture_diagram.txt"
            if filename_raw.lower().endswith('.png'):
                txt_filename = filename_raw[:-4] + '.txt'
            else:
                 # If it doesn't end in png, just append .txt or replace extension?
                 # User said: "Proposed Image Filename ... の「.png」を「.txt」というファイル名です"
                 # "cnt_hm_activeperl_architecture_diagram.png.txt" みたいにはならないように
                 root, ext = os.path.splitext(filename_raw)
                 txt_filename = root + '.txt'

            # Define output path (current directory)
            output_path = txt_filename

            if os.path.exists(output_path):
                print(f"Skipping existing file: {output_path}")
                continue

            # Apply Template
            file_content = template_content.replace('{{INSERT}}', prompt)

            # Write File
            try:
                with open(output_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(file_content)
                print(f"Created: {output_path}")
            except Exception as e:
                print(f"Error writing {output_path}: {e}")

if __name__ == "__main__":
    generate_prompts()
