from ..bl_game import BorderlandsGameInfo, ApItemMesh
from abc import abstractmethod
from . import missions
from .chests import chest_dict
from . import entrances
from . import archi_data
from . import map_modify

def InitTps(): 
    mesh = ApItemMesh(
        item_definition="GD_Baroness_Items_Marigold.Baroness.Head_Ma_Bar01",
        usable_item_definition="GD_Baroness_Items_crocus.Baroness.Head_Baron002",
        mesh="prop_rolandsresistance.Mesh.ResistancePoster",
        material="GD_Co_Followyourheartdata.Materials.Mati_Cat_INST",
        package="Deadsurface_Dynamic",
        loot_pool="GD_Itempools.Runnables.Pool_FlameKnuckle"
    )
    return BorderlandsGameInfo(
        name="Borderlands The Pre-Sequel",
        socket_port=9998,
        receive_sounds=["Ake_Cork_VO_Episode_03.Ak_Play_VO_Cork_EP3_PT01_1032_Enforcer", "Ake_Cork_VO_Episode_03.Ak_Play_VO_Cork_EP3_PT01_0020_Enforcer" ],
        missions=missions,
        locations={},
        chests=chest_dict,
        entrances=entrances,
        drop_item_mesh= mesh,
        vending_item_mesh= mesh,
        loc_id_to_name=archi_data.loc_id_to_name,
        item_id_to_name=archi_data.loc_id_to_name,
        map_modify=map_modify.modify_arid_nexus_badlands,
        item_dict = { "WillowShield": "Shield", "WillowGrenadeMod": "GrenadeMod", "WillowClassMod": "ClassMod", "WillowArtifact": "Oz Kit" },
        weapon_dict = { 0: "Pistol", 1: "Shotgun", 2: "SMG", 3: "SniperRifle", 4: "AssaultRifle", 5: "RocketLauncher", 6: "Laser" }
)