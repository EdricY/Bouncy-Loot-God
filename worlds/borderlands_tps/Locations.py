from typing import Dict, NamedTuple, Optional
import re

from BaseClasses import Location
from .archi_defs import loc_data_table
from .Regions import region_data_table

bltps_base_id: int = 2388000

class BorderlandsTPSLocation(Location):
    game = "Borderlands The Pre-Sequel"

location_data_table = loc_data_table

start_id = bltps_base_id + 1

location_name_to_id = {name: start_id + i for i, name in enumerate(loc_data_table.keys())}
location_descriptions = {name: data.description for name, data in loc_data_table.items()}
