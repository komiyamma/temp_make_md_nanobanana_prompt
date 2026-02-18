import json
import sys
import os
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/bulk_append_images.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]

    with open(json_file, 'r', encoding='utf-8') as f:
        plans = json.load(f)

    for plan in plans:
        # Create a temporary payload file for each plan
        payload_file = f"temp_payload_{plan.get('proposed_filename', 'unknown')}.json"
        with open(payload_file, 'w', encoding='utf-8') as f_out:
            json.dump(plan, f_out)

        # Call the original script
        try:
            subprocess.run(['python3', 'tools/append_image_plan.py', '--from-json', payload_file], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {plan.get('proposed_filename')}: {e}")
        finally:
            if os.path.exists(payload_file):
                os.remove(payload_file)

if __name__ == "__main__":
    main()
