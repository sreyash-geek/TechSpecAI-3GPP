import zipfile
import os

# Extract all ZIP files in the folder
save_folder = "3gpp_specs"
for file in os.listdir(save_folder):
    if file.endswith(".zip"):
        zip_path = os.path.join(save_folder, file)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(save_folder)
        print(f"Extracted: {zip_path}")
