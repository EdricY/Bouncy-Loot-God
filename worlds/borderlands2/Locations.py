from typing import Dict, NamedTuple, Optional

from BaseClasses import Location
from .archi_defs import loc_name_to_id

bl2_base_id: int = 2388000


class Borderlands2Location(Location):
    game = "Borderlands 2"


class Borderlands2LocationData(NamedTuple):
    region: str
    address: Optional[int] = None
    description: Optional[str] = None


location_data_table: Dict[str, Borderlands2LocationData] = {
    name: Borderlands2LocationData(region="Menu", address=bl2_base_id + loc_id, description="")
    for name, loc_id in loc_name_to_id.items()
}

location_name_to_id = {name: data.address for name, data in location_data_table.items() if data.address is not None}

location_descriptions = {name: data.description for name, data in location_data_table.items() if
                         data.address is not None}
