if __name__ != "__main__":
  print("run this script from command line")
  exit(1)

from pathlib import Path
import json
import os
import sys
from importlib.util import spec_from_file_location, module_from_spec
def load_module(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
def sync_to_game(game, output_path):
    json_obj = {"loc": game.loc_name_to_id, "item": game.item_name_to_id}

    file_content = "# auto generated from sync-defs.py\narchi_data = " + json.dumps(json_obj, indent=4) + '''
loc_name_to_id = archi_data["loc"]
item_name_to_id = archi_data["item"]
loc_id_to_name = {id: name for name, id in loc_name_to_id.items()}
item_id_to_name = {id: name for name, id in item_name_to_id.items()}
'''
    with open(output_path, 'w') as file:
        file.write(file_content)

    print(f"wrote to file: {output_path}")


# sync defs from worlds/borderlands2/archi_defs.py to sdk_mods/BouncyLootGod/archi_data.py

dir = os.path.dirname(__file__)
bl2_output_path = Path(dir) / "sdk_mods" / "BouncyLootGod" / "bl2" / "archi_data.py"
tps_output_path = Path(dir) / "sdk_mods" / "BouncyLootGod" / "bl_tps" / "archi_data.py"
print(bl2_output_path)
print(tps_output_path)

bl2 = load_module(
    "bl2_archi_defs",
    Path(dir) / "worlds" / "borderlands2" / "archi_defs.py"
)

tps = load_module(
    "tps_archi_defs",
    Path(dir) / "worlds" / "borderlands_tps" / "archi_defs.py"
)
sync_to_game(bl2, bl2_output_path)
sync_to_game(tps, tps_output_path)