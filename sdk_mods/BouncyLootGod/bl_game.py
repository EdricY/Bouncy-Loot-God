from dataclasses import dataclass
from typing import Callable


@dataclass
class ApItemMesh:
    item_definition: str
    mesh: str
    package: str
    rotator_pitch: int = -134
    rotator_yaw: int = -14219
    rotator_roll: int = -7164
    material: str = None
    usable_item_definition: str = None
    loot_pool: str = None
@dataclass
class BorderlandsGameInfo:
    name: str
    socket_port: int
    receive_sounds: list[str]
    missions: object
    locations: dict
    chests: dict
    entrances: object
    drop_item_mesh: ApItemMesh
    vending_item_mesh: ApItemMesh
    loc_id_to_name: dict
    item_id_to_name: dict
    map_modify: Callable[[], None]