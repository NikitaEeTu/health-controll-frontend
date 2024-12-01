import os
folder_path = "images"


for filename in os.listdir(folder_path):

    if " " in filename:

        new_name = filename.replace(" ", "_")

        old_file = os.path.join(folder_path, filename)
        new_file = os.path.join(folder_path, new_name)

        os.rename(old_file, new_file)
        print(f"Renamed: {filename} -> {new_name}")

print("All files renamed successfully!")

