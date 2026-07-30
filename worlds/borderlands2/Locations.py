from typing import Dict, NamedTuple, Optional
import re

from BaseClasses import Location
from .archi_defs import loc_data_table
from .Regions import region_data_table

bl2_base_id: int = 2388000
bl2_tvhm_base_id: int = bl2_base_id + 10000
bl2_uvhm_base_id: int = bl2_base_id + 20000

class Borderlands2Location(Location):
    game = "Borderlands 2"


def convert_to_tvhm_level(level):
    # 0 -> 30; 30 -> 50
    return int(30 + (20 * level / 30))

location_data_table = loc_data_table

location_name_to_id = {name: bl2_base_id + 1 + i for i, name in enumerate(loc_data_table.keys())}
location_name_to_id.update({f"{name} TVHM": bl2_tvhm_base_id + 1 + i for i, name in enumerate(loc_data_table.keys())})
location_name_to_id.update({f"{name} UVHM": bl2_uvhm_base_id + 1 + i for i, name in enumerate(loc_data_table.keys())})


location_descriptions = {name: data.description for name, data in loc_data_table.items()}
location_descriptions.update({f"{name} TVHM": data.description for name, data in loc_data_table.items()})
location_descriptions.update({f"{name} UVHM": data.description for name, data in loc_data_table.items()})
