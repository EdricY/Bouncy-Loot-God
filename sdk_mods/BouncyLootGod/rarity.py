import unrealsdk
import unrealsdk.unreal as unreal
from BouncyLootGod.archi_defs import item_id_to_name, loc_name_to_id

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
            rarity = 999
        #TODO: handle unique items

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

def can_gear_loc_id_be_equipped(blg, loc_id):
    if not blg.is_archi_connected:
        return True
    if loc_id is None:
        return True
    if loc_id not in item_id_to_name:
        # is a kind of gear we aren't handling yet
        return True
    # TODO: if pearlescent and others are added to the pool conditionally, need to either handle it here or del them on init
    item_amt = blg.game_items_received.get(loc_id, 0)
    if item_amt > 0:
        return True
    return False

def can_inv_item_be_equipped(blg, inv_item):
    if not blg.is_archi_connected:
        return True
    loc_id = get_gear_loc_id(inv_item)
    return can_gear_loc_id_be_equipped(blg, loc_id)
