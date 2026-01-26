import os
import shutil
import sys

def zip_directories_with_custom_names(directories, output_files, output_dir="."):
    if len(directories) != len(output_files):
        raise ValueError("directories and output_files must have the same length")
    
    os.makedirs(output_dir, exist_ok=True)
    # TODO: maybe remove pycache

    for d, final_name in zip(directories, output_files):
        d = os.path.abspath(d)
        parent = os.path.dirname(d)
        folder_name = os.path.basename(d)

        # shutil requires a base name without any extension
        temp_zip_base = os.path.join(output_dir, "_temp_zip_" + folder_name)

        # create standard .zip file
        temp_zip_path = shutil.make_archive(
            base_name=temp_zip_base,
            format="zip",
            root_dir=parent,
            base_dir=folder_name
        )

        # rename it to whatever the user requested
        final_path = os.path.join(output_dir, final_name)
        os.replace(temp_zip_path, final_path)

        print(f"Created {final_path}")


dirs_to_zip = [
    "./sdk_mods/BouncyLootGod",
    "./worlds/borderlands2",
]
output_files = [
    "BouncyLootGod.sdkmod",
    "borderlands2.apworld",
]

zip_directories_with_custom_names(dirs_to_zip, output_files, output_dir="dist")

# run `python zip-it.py` to output zipped folders to dist
# run `python zip-it.py deploy` to also auto copy to these dirs
# run `python zip-it.py deployap` to zip but only deploy apworld
# run `python zip-it.py deploysdkmod` to zip but only deploy sdkmod

sdkmoddir = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Borderlands 2\\sdk_mods"
customworlddir = "C:\\ProgramData\\Archipelago\\custom_worlds" # unused

def deployap():
    os.startfile(".\\dist\\borderlands2.apworld")

def deploysdkmod():
    source_file = "./dist/BouncyLootGod.sdkmod"
    os.makedirs(sdkmoddir, exist_ok=True)
    shutil.copy(source_file, sdkmoddir)
    print(f"File '{source_file}' copied to '{sdkmoddir}'")

def deployboth():
    deploysdkmod()
    deployap()

if len(sys.argv) > 1:
    if sys.argv[1] == "deploy":
        deployboth()

    if sys.argv[1] == "deployap" or sys.argv[1] == "ap":
        deployap()

    if sys.argv[1] == "deploysdkmod" or sys.argv[1] == "sdkmod":
        deploysdkmod()

#TODO: maybe conditionally run sync-defs before zipping