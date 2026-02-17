import json
import subprocess
import os
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/bulk_append_images.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    with open(json_file, 'r') as f:
        data = json.load(f)

    filename = data.get('filename')
    items = data.get('items', [])

    for item in items:
        payload = {
            "filename": filename,
            "proposed_filename": item.get('proposed_filename'),
            "relative_link": item.get('relative_link'),
            "prompt": item.get('prompt'),
            "insertion_point": item.get('insertion_point')
        }

        temp_payload_file = f"temp_payload_{item.get('proposed_filename')}.json"
        with open(temp_payload_file, 'w') as f:
            json.dump(payload, f)

        try:
            subprocess.run(['python3', 'tools/append_image_plan.py', '--from-json', temp_payload_file], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error appending {item.get('proposed_filename')}: {e}")
        finally:
            if os.path.exists(temp_payload_file):
                os.remove(temp_payload_file)

if __name__ == "__main__":
    main()
