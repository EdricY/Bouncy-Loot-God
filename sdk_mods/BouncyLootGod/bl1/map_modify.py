import unrealsdk
from unrealsdk.hooks import Type
import unrealsdk.unreal as unreal
from BouncyLootGod.enemies import setup_check_drop, oid_generic_drop_chance_override
from BouncyLootGod.state import get_globals
from BouncyLootGod.bl_tps.enemies import generic_enemy_lookup
from mods_base import ENGINE

def get_current_map():
    if ENGINE and ENGINE.GetCurrentWorldInfo:
        wi = ENGINE.GetCurrentWorldInfo()
        if wi and wi.GetMapName:
            return str(wi.GetMapName()).casefold()
    return "none"

map_modifications = {
    # "innerhull_p": modify_veins_of_helios,
}

map_area_to_name = {
    # TODO
    "arid_p": "Arid",
    "arid_skaggully_p": "Arid_Skaggully",
    "dry_p": "Dry",
    "arid_bunker_p": "Arid_Bunker",
    "arid_cave_p": "Arid_Cave",
    "arid_mine_p": "Arid_Mine",
    "interlude_1_p": "Interlude_1",
    "scrap_newhaven_p": "Scrap_Newhaven",
    "scrap_trashcave_p": "Scrap_Trashcave",
    "scrap_p": "Scrap",
    "scrap_scrapyard_p": "Scrap_Scrapyard",
    "scrap_piratebay_p": "Scrap_Piratebay",
    "trash_p": "Trash",
    "scrap_canyon_p": "Scrap_Canyon",
    "scrap_oldhaven_p": "Scrap_Oldhaven",
    "scrap_trashcoast_p": "Scrap_Trashcoast",
    "interlude_2_p": "Interlude_2",
    "interlude_2_cave_p": "Interlude_2_Cave",
    "waste_crimsonbunker_p": "Waste_Crimsonbunker",
    "waste_crimson_p": "Waste_Crimson",
    "waste_descent_p": "Waste_Descent",
    "waste_digsite_p": "Waste_Digsite",
}
