
from mods_base import Game
if Game.get_current().name == "TPS":
    from BouncyLootGod.bl_tps.archi_data import archi_data
else:
    from BouncyLootGod.bl2.archi_data import archi_data

loc_name_to_id = archi_data["loc"]
item_name_to_id = archi_data["item"]
loc_id_to_name = {id: name for name, id in loc_name_to_id.items()}
item_id_to_name = {id: name for name, id in item_name_to_id.items()}
