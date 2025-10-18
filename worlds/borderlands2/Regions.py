from typing import Dict, List, NamedTuple


class Borderlands2RegionData(NamedTuple):
    connecting_regions: List[str] = []


region_data_table: Dict[str, Borderlands2RegionData] = {
    "Menu": Borderlands2RegionData(["Main Region"]),
    "Main Region": Borderlands2RegionData(),
}
