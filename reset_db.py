import os

folders_to_scan = ['api', 'templates', 'static']

for folder in folders_to_scan:
    if os.path.exists(folder):
        print(f"\n=== Files in {folder} folder ===")
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, folder)
                print(f"@{relative_path}")
