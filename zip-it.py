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
    "./worlds/borderlands_tps",
]
output_files = [
    "BouncyLootGod.sdkmod",
    "borderlands2.apworld",
    "borderlands_tps.apworld",
]

zip_directories_with_custom_names(dirs_to_zip, output_files, output_dir="dist")

# run `python zip-it.py` to output zipped folders to dist
# run `python zip-it.py deploy` to also auto copy to these dirs
# run `python zip-it.py deployap` to zip but only deploy apworld
# run `python zip-it.py deploysdkmod` to zip but only deploy sdkmod

bl2sdkmoddir = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Borderlands 2\\sdk_mods"
tpssdkmoddir = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\BorderlandsPreSequel\\sdk_mods"
customworlddir = "C:\\ProgramData\\Archipelago\\custom_worlds" # unused

def deployap(game="all"):
    if game == "bl2" or game == "all": 
        shutil.copy("./dist/borderlands2.apworld", customworlddir)
    if game == "tps" or game == "all" :
        shutil.copy("./dist/borderlands_tps.apworld", customworlddir)

def deploysdkmod(sdkmoddir=bl2sdkmoddir):
    source_file = "./dist/BouncyLootGod.sdkmod"
    os.makedirs(sdkmoddir, exist_ok=True)
    shutil.copy(source_file, sdkmoddir)
    print(f"File '{source_file}' copied to '{sdkmoddir}'")

def deployall():
    deploysdkmod(bl2sdkmoddir)
    deploysdkmod(tpssdkmoddir)
    deployap("all")
def deployboth_tps():
    deploysdkmod(tpssdkmoddir)
    deployap("tps")
def deployboth_bl2():
    deploysdkmod(bl2sdkmoddir)
    deployap("bl2")

if len(sys.argv) > 1:
    if sys.argv[1] == "deploy":
        deployall()
    if sys.argv[1] == "deployall":
        deployall()

    if sys.argv[1] == "deployap" or sys.argv[1] == "ap":
        deployap()

    if sys.argv[1] == "deploybl2ap" or sys.argv[1] == "bl2ap":
        deployap("bl2")
    if sys.argv[1] == "deploytpsap" or sys.argv[1] == "tpsap":
        deployap("tps")

    if sys.argv[1] == "deploysdkmod" or sys.argv[1] == "sdkmod":
        deploysdkmod()
    if sys.argv[1] == "deploybl2sdkmod" or sys.argv[1] == "bl2sdkmod":
        deploysdkmod()
    if sys.argv[1] == "deploytpssdkmod" or sys.argv[1] == "tpssdkmod":
        deploysdkmod(tpssdkmoddir)

#TODO: maybe conditionally run sync-defs before zipping