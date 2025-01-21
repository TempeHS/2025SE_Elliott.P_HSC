import os

folders_to_scan = ['template', 'static', '.']

for folder in folders_to_scan:
    if os.path.exists(folder):
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                filename, file_extension = os.path.splitext(file)

                print(f"@{filename}{file_extension}")
