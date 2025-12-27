if __name__ != "__main__":
  print("run this script from command line")
  exit(1)

from pathlib import Path
import json
import os
import sys


# sync defs from worlds/borderlands2/archi_defs.py to sdk_mods/BouncyLootGod/archi_defs.json

dir = os.path.dirname(__file__)
output_path = Path(dir) / "sdk_mods" / "BouncyLootGod" / "archi_data.py"
print(output_path)

import_dir = Path(dir) / "worlds" / "borderlands2"
sys.path.append(str(import_dir))
from archi_defs import loc_name_to_id, item_name_to_id

json_obj = {"loc": loc_name_to_id, "item": item_name_to_id}

json_str = "# auto generated from sync-defs.py\narchi_data = " + json.dumps(json_obj, indent=4)

with open(output_path, 'w') as file:
    file.write(json_str)

print(f"wrote to file: {output_path}")
