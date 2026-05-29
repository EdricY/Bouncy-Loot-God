from BouncyLootGod.state import get_globals, ApItemMesh
import unrealsdk
def modify_moonshot_intro():
    blg = get_globals()
    if blg.settings.get("delete_starting_gear") == 1:
        #make the loyalty pools empty to prevent giving the items
        try:
            loyalty_bullpup_pool = unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.EasterEggs.Pool_Loyalty_Bullpup")
            loyalty_bullpup_pool.BalancedItems = []
        except:
            pass
        try:
            loyalty_smasher_pool = unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.EasterEggs.Pool_Loyalty_Smasher")
            loyalty_smasher_pool.BalancedItems = []
        except:
            pass
        
    

map_modifications = {
    "moonshotintro_p": modify_moonshot_intro,
}
map_area_to_name = {
    "moonslaughter_p":          "Abandoned Training Facility",
    "ma_leftcluster_p":         "Cluster 00773 P4ND0R4",
    "ma_rightcluster_p":        "Cluster 99002 0V3RL00K",
    "spaceport_p":              "Concordia",
    "comfacility_p":            "Crisis Scar",
    "ma_deck13_p":              "Deck 13 ½",
    "ma_finalboss_p":           "Deck 13.5",
    "innercore_p":              "Eleseer",
    "laserboss_p":              "Eye of Helios",
    "moonshotintro_p":          "Helios Station",
    "centralterminal_p":        "Hyperion Hub of Heroism",
    "jacksoffice_p":            "Jack's Office",
    "laser_p":                  "Lunar Launching Station",
    "ma_motherboard_p":         "Motherlessboard",
    "digsite_rk5arena_p":       "Outfall Pumping Station",
    "outlands_p2":              "Outlands Canyon",
    "outlands_p":               "Outlands Spur",
    "wreck_p":                  "Pity's Fall",
    "deadsurface_p":            "Regolith Range",
    "randdfacility_p":          "Research and Development",
    "moonsurface_p":            "Serenity's Waste",
    "stantonsliver_p":          "Stanton's Liver",
    "sublevel13_p":             "Sub-Level 13",
    "ma_subconscious_p":        "Subconscious",
    "ma_subboss_p":             "The Cortex",
    "eridian_slaughter_p":      "The Holodome",
    "meriff_p":                 "The Meriff's Office",
    "ma_nexus_p":               "The Nexus",
    "dahlfactory_p":            "Titan Industrial Facility",
    "dahlfactory_boss":         "Titan Robot Production Plant",
    "moon_p":                   "Triton Flats",
    "access_p":                 "Tycho's Ribs",
    "innerhull_p":              "Veins of Helios",
    "digsite_p":                "Vorago Solitude",
}
