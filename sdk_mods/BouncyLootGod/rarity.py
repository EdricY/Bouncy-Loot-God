import unrealsdk
import unrealsdk.unreal as unreal
from BouncyLootGod.archi_defs import item_id_to_name, loc_name_to_id, item_name_to_id
from BouncyLootGod.loot_pools import pathname, unique_shield_def_names, unique_grenade_def_names, unique_relic_def_names

def get_weap_red_text(definition_data):
    try:
        title_part = definition_data.TitlePartDefinition
        red_text = title_part.CustomPresentations[0].NoConstraintText
        if red_text:
            return red_text
    except:
        pass
    return None

# dd_rarity_dict = ['Common', 'Uncommon', 'Rare', 'Unique', 'VeryRare', 'Alien', 'Legendary']
# def get_dd_weapon_rarity(definition_data):
#     rarity_attempt = str(definition_data.BalanceDefinition).split(".")[-2].split("_")[-1]
#     if rarity_attempt in dd_rarities:
#         return rarity_attempt
#     rarity_attempt = str(definition_data.BalanceDefinition).split("_")[-1][:-1]
#     if rarity_attempt in dd_rarities:
#         return rarity_attempt
#     rarity_attempt = str(definition_data.MaterialPartDefinition).split("_")[-1][:-1]
#     if rarity_attempt in dd_rarities:
#         return rarity_attempt
#     # print('Rarity not found... assuming "Unique"')
#     # print(str(definition_data.BalanceDefinition))
#     # print(str(definition_data.MaterialPartDefinition))
#     return 'Unique'

def is_etech(definition_data):
    bdstr = str(definition_data.BalanceDefinition)
    pieces = bdstr.split("_")
    if len(pieces) > 1 and pieces[-1].startswith("Alien"):
        return True
    if len(pieces) > 2 and pieces[-2].startswith("Alien"):
        return True
    # gemstone etech is not detected currently. Probably won't fix that.
    # (if you want to, could change to check the Barrel)
    return False

rarity_dict = { 1: "Common", 2: "Uncommon", 3: "Rare", 4: "VeryRare", 5: "Legendary", 6: "Seraph", 7: "Rainbow", 500: "Pearlescent", 998: "E-Tech", 999: "Unique" }
weak_globals: unreal.WeakPointer = unreal.WeakPointer()
def get_rarity(inv_item):
    # adapted from equip_locker
    if "WillowMissionItem" == inv_item.Class.Name:
        # print("skipping mission item")
        return "unknown"
    if (globals_obj := weak_globals()) is None:
        globals_obj = unrealsdk.find_object("GlobalsDefinition", "GD_Globals.General.Globals")
        weak_globals.replace(globals_obj)

    rarity = globals_obj.GetRarityForLevel(inv_item.RarityLevel)

    # handle Pearlescent
    if inv_item.Class.Name == "WillowWeapon" and rarity == 0 and inv_item.RarityLevel == 500:
        rarity = 500
    if rarity == 3 or rarity == 4:
        # handle E-Tech
        if is_etech(inv_item.DefinitionData):
            rarity = 998
        # handle Unique Weapon
        elif inv_item.Class.Name == "WillowWeapon" and get_weap_red_text(inv_item.DefinitionData) is not None:
            # rarity = 999
            return "Unique"

    if inv_item.Class.Name == "WillowArtifact":
        ibd = inv_item.DefinitionData.BalanceDefinition
        pn = pathname(ibd)
        if pn in unique_relic_def_names:
            return "Unique"
        if "GD_Gladiolus" in pn:
            return "E-Tech"

    if inv_item.Class.Name == "WillowGrenadeMod":
        ibd = inv_item.DefinitionData.BalanceDefinition
        pn = pathname(ibd)
        if pn in unique_grenade_def_names:
            return "Unique"

    if inv_item.Class.Name == "WillowShield":
        pn = pathname(inv_item.DefinitionData.BalanceDefinition)
        if pn in unique_shield_def_names:
            return "Unique"

    rarity_str = rarity_dict.get(rarity)

    if not rarity_str:
        return "unknown"
    return rarity_str

ITEM_DICT = { "WillowShield": "Shield", "WillowGrenadeMod": "GrenadeMod", "WillowClassMod": "ClassMod", "WillowArtifact": "Relic" }
WEAPON_DICT = { 0: "Pistol", 1: "Shotgun", 2: "SMG", 3: "SniperRifle", 4: "AssaultRifle", 5: "RocketLauncher" }
def get_item_type(inv_item):
    if inv_item.Class.Name == "WillowWeapon":
        weap_def = inv_item.DefinitionData.WeaponTypeDefinition
        if weap_def is None:
            return "unknown"
        weapon_type = weap_def.WeaponType
        weapon_str = WEAPON_DICT.get(weapon_type)
        if not weapon_str:
            return "unknown"
        return weapon_str

    item_class = inv_item.Class.Name
    item_str = ITEM_DICT.get(item_class)
    if not item_str:
        return "unknown"
    return item_str

def get_gear_kind(inv_item):
    r = get_rarity(inv_item)
    if r == 'unknown': return 'unknown'
    t = get_item_type(inv_item)
    if t == 'unknown': return 'unknown'
    kind = r + " " + t
    return kind

def get_gear_loc_id(inv_item):
    kind = get_gear_kind(inv_item)
    return loc_name_to_id.get(kind)

def get_gear_item_id(inv_item):
    kind = get_gear_kind(inv_item)
    return item_name_to_id.get(kind)


def can_gear_item_id_be_equipped(blg, loc_id):
    if not blg.is_archi_connected:
        return True
    if loc_id is None:
        return True
    if loc_id not in item_id_to_name:
        # is a kind of gear we aren't handling yet
        return True
    # rarity_setting = blg.settings.get("gear_rarity_item_pool")
    # if rarity_setting == 0:
    #     return True
    # if rarity_setting <= 3 and loc_id % 10 == 7: # rainbow
    #     return True
    # if rarity_setting <= 2 and loc_id % 10 == 8: # pearl
    #     return True
    # if rarity_setting <= 1 and loc_id % 10 == 6: # seraph
    #     return True

    item_amt = blg.game_items_received.get(loc_id, 0)
    if item_amt > 0:
        return True
    return False

def can_inv_item_be_equipped(blg, inv_item):
    if not blg.is_archi_connected:
        return True
    item_id = get_gear_item_id(inv_item)
    return can_gear_item_id_be_equipped(blg, item_id)

def needs_rarity_check(blg, inv_item):
    setting = blg.settings.get("gear_rarity_checks")
    if setting == 0:
        return False
    kind = get_gear_kind(inv_item)
    if kind == "unknown":
        return False
    if setting <= 3 and kind.startswith("Rainbow"):
        return False
    if setting <= 2 and kind.startswith("Pearlescent"):
        return False
    if setting <= 1 and kind.startswith("Seraph"):
        return False

    loc_id = get_gear_loc_id(inv_item)
    if loc_id in blg.locations_checked:
        return False

    return True

