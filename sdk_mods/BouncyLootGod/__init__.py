# to run from console: pyexec BouncyLootGod\__init__.py
# note: above command doesn't seem to reload changes in other files
import unrealsdk
import unrealsdk.unreal as unreal
from mods_base import hook as Hook, build_mod, ButtonOption, get_pc, hook, ENGINE, ObjectFlags
from ui_utils import show_chat_message
from unrealsdk.hooks import Type, Block
try:
    assert __import__("coroutines").__version_info__ >= (1, 1), "Please install coroutines"
except (AssertionError, ImportError) as ex:
    import webbrowser
    webbrowser.open("https://bl-sdk.github.io/willow2-mod-db/requirements?mod=BouncyLootGod")
    raise ex

from coroutines import start_coroutine_tick, WaitForSeconds

import socket
import sys
import os
import json


mod_version = "0.1"


from BouncyLootGod.archi_defs import item_name_to_id, item_id_to_name, loc_name_to_id
from BouncyLootGod.lookups import gear_kind_to_item_pool, vault_symbol_id_to_name
from BouncyLootGod.map_modify import map_modifications
from BouncyLootGod.oob import get_loc_in_front_of_player


mod_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(mod_dir)
storage_dir = os.path.join(mod_dir, "blgstor")
if parent_dir.endswith(".sdkmod") or parent_dir.endswith(".zip"):
    storage_dir = os.path.join(os.path.dirname(parent_dir), "blgstor")
    os.makedirs(storage_dir, exist_ok=True)
    # show_chat_message("running from sdkmod, creating blgstor dir one level up")

class BLGGlobals:
    task_should_run = False
    sock = None
    is_sock_connected = False
    is_archi_connected = False
    is_setting_sdu = False
    # server setup:
    # (BL2 + this mod) <=====> (Socket Server + Archi Launcher BL 2 Client) <=====> (server/archipelago.gg)
    #             is_sock_connected                                   is_archi_connected
    # when is_archi_connected is False, we don't know what is and isn't unlocked.

    # items_received = [] # full list of items received, kept in sync with server

    game_items_received = dict()

    should_perform_initial_modify = False
    locations_checked = set()
    locs_to_send = []
    current_map = ""
    money_cap = 100
    weapon_slots = 2
    skill_points_allowed = 0
    package = unrealsdk.construct_object("Package", None, "BouncyLootGod", ObjectFlags.KEEP_ALIVE)
    # TODO: swap these when we have lookup-able items
    can_jump = False
    can_melee = False
    can_crouch = False
    can_sprint = False
    can_gear_level = False
    can_vehicle_fire = False

    active_vend = None
    settings = None

    items_filepath = None # store items that have successfully made it to the player to avoid dups
    log_filepath = None # scouting log o7


blg = BLGGlobals()

akevent_cache: dict[str, unreal.UObject] = {}
def find_and_play_akevent(event_name: str):
    if not get_pc() or not get_pc().Pawn:
        return
    # TODO: try ClientPlayAkEvent instead
    event = akevent_cache.get(event_name)
    if event is None:
        try:
            event = unrealsdk.find_object("AkEvent", event_name)
        except ValueError as e:
            return
        event.ObjectFlags |= ObjectFlags.KEEP_ALIVE
        akevent_cache[event_name] = event
    if get_pc() and get_pc().Pawn:
        get_pc().Pawn.PlayAkEvent(event)

def handle_item_received(item_id, is_init=False):
    # called only once per item, every init / reconnect
    # is_init means we are receiving this while reading from the file.
    #   so, do setup for received items, but skip granting duplicates
    if item_id == item_name_to_id["3 Skill Points"]:
        blg.skill_points_allowed += 3
    elif item_id == item_name_to_id["Progressive Money Cap"]:
        blg.money_cap *= 100
    elif item_id == item_name_to_id["Weapon Slot"]:
        blg.weapon_slots = min(4, blg.weapon_slots + 1)
    elif item_id == item_name_to_id["Jump"]:
        blg.can_jump = True
    elif item_id == item_name_to_id["Melee"]:
        blg.can_melee = True
    elif item_id == item_name_to_id["Crouch"]:
        blg.can_crouch = True
    elif item_id == item_name_to_id["Sprint"]:
        blg.can_sprint = True
    elif item_id == item_name_to_id["Gear Leveler"]:
        blg.can_gear_level = True
    elif item_id == item_name_to_id["Vehicle Fire"]:
        blg.can_vehicle_fire = True

    blg.game_items_received[item_id] = blg.game_items_received.get(item_id, 0) + 1

    if is_init:
        return

    current_map = get_current_map()
    if current_map in fake_maps:
        # skip for now, try again later
        return

    item_name = item_id_to_name.get(item_id)
    if not item_name:
        print("unknown item: " + str(item_id))
        return
    show_chat_message("Received: " + item_name)

    # spawn gear
    if blg.settings.get("receive_gear") != 0:
        pool = gear_kind_to_item_pool.get(item_name)
        if pool is not None:
            spawn_gear(pool)

    if item_id == item_name_to_id["$100"]:
        get_pc().PlayerReplicationInfo.AddCurrencyOnHand(0, 100)
    elif item_id == item_name_to_id["10 Eridium"]:
        get_pc().PlayerReplicationInfo.AddCurrencyOnHand(1, 10)

    # not init, do write.
    with open(blg.items_filepath, 'a') as f:
        f.write(str(item_id) + "\n")


def sync_vars_to_player():
    sync_skill_pts()
    sync_weapon_slots()

# compute a - b; a should be a superset of b, return -1 if not. a and b can both contain repeats
def list_dict_diff(list_a, _dict_b):
    dict_a = {}
    dict_b = dict(_dict_b)
    for x in list_a:
        dict_a[x] = dict_a.get(x, 0) + 1
    # Subtract counts
    for x, count_b in dict_b.items():
        if dict_a.get(x) is None:
            # b has an item a doesn't
            return -1
        dict_a[x] -= count_b
        if dict_a[x] < 0:
            # b has more than a
            return -1
    # Reconstruct result, preserving order from a
    result = []
    temp_count = {}
    for x in list_a:
        # how many of this item we've already output
        used = temp_count.get(x, 0)
        if used < dict_a.get(x, 0):
            result.append(x)
            temp_count[x] = used + 1
    return result

def pull_items():
    if not blg.is_archi_connected:
        return
    try:
        blg.sock.sendall(bytes("items_all", "utf-8"))
        msg = blg.sock.recv(4096)
        msg_strs = msg.decode().split(",")
        if msg.decode() == "no":
            msg_strs = []
        msg_list = list(map(int, msg_strs))
        diff = list_dict_diff(msg_list, blg.game_items_received)
        if diff == -1:
            show_chat_message("detected items out of sync or archi client has disconnected.")
            check_is_archi_connected()
            return

        if len(diff) > 0:
            find_and_play_akevent("Ake_VOCT_Contextual.Ak_Play_VOCT_Steve_HeyOo")
        # loop through new ones
        for item_id in diff:
            handle_item_received(item_id)

        sync_vars_to_player()

    except socket.error as error:
        print(error)
        show_chat_message("pull_items: something went wrong.")
        disconnect_socket()

def pull_locations():
    if not blg.is_archi_connected:
        return
    try:
        blg.sock.sendall(bytes("locations_all", "utf-8"))
        msg = blg.sock.recv(4096)
        if msg.decode() == "no":
            return
        msg_strs = msg.decode().split(",")
        msg_set = set(map(int, msg_strs))
        # always defer to server's locations_checked
        blg.locations_checked = msg_set
    except socket.error as error:
        print(error)
        show_chat_message("pull_locations: something went wrong.")
        disconnect_socket()

def init_game_items_received():
    if blg.items_filepath is None:
        print("init_game_items_received: not connected")
        return
    if not os.path.exists(blg.items_filepath):
        print("init_game_items_received: no file exists")
        return
    # reset counters
    blg.money_cap = 100
    blg.weapon_slots = 2
    blg.skill_points_allowed = 0

    blg.game_items_received = dict()
    # read lines of file into dict
    with open(blg.items_filepath, 'r') as f:
        for line in f:
            item_id = int(line.strip())
            handle_item_received(item_id, True)

def fetch_settings():
    if not blg.is_archi_connected:
        return
    try:
        blg.sock.sendall(bytes("options", "utf-8"))
        msg = blg.sock.recv(4096)
        msg_str = msg.decode()
        blg.settings = json.loads(msg_str)
    except socket.error as error:
        print(error)
        show_chat_message("fetch_settings: something went wrong.")
        disconnect_socket()


def init_data():
    fetch_settings()
    seed = blg.settings.get("seed")
    show_chat_message("seed: " + str(seed))
    if not seed:
        show_chat_message("No seed detected!")
        seed = "blah"
    blg.items_filepath = os.path.join(storage_dir, seed + ".items.txt")
    blg.log_filepath = os.path.join(storage_dir, seed + ".log.txt")
    pull_locations()
    if len(blg.locations_checked) == 0 and not os.path.exists(blg.items_filepath):
        blg.should_perform_initial_modify = True
        show_chat_message("detected first conncection")
        print("detected first conncection")
        f = open(blg.items_filepath, "x")
        f.close()
        show_chat_message("items file created at " + blg.items_filepath)
    init_game_items_received()


def push_locations():
    if not blg.is_archi_connected:
        return
    # TODO: bundle into one request instead of multiple
    while len(blg.locs_to_send) > 0:
        check = blg.locs_to_send[0]
        if check in blg.locations_checked:
            blg.locs_to_send.pop(0)
            continue
        print('sending ' + str(check))
        blg.sock.send(bytes(str(check), 'utf8'))
        msg = blg.sock.recv(4096)
        if msg.decode().startswith("ack"):
            blg.locations_checked.add(check)
        else:
            print(msg.decode())
            print(check)
        blg.locs_to_send.pop(0) # remove from list after successful send,

# checks for archi connection, then initializes
def check_is_archi_connected():
    if not blg.is_sock_connected:
        return
    try:
        blg.sock.send(bytes("is_archi_connected", 'utf8'))
        msg = blg.sock.recv(4096)
        blg.is_archi_connected = msg.decode() == "True"
        if blg.is_archi_connected:
            init_data()
        else:
            # reset items_received, maintain anything in locs_to_send
            blg.game_items_received = dict()
    except socket.error as error:
        print(error)
        show_chat_message("check_is_archi_connected: something went wrong.")
        disconnect_socket()

def connect_to_socket_server(ButtonInfo):
    if blg.is_sock_connected:
        disconnect_socket()
    try:
        blg.sock = socket.socket()
        blg.sock.connect(("localhost", 9997))
        # begin handshake
        blg.sock.sendall(bytes("blghello:" + mod_version, "utf-8"))
        msg = blg.sock.recv(4096)
        sock_version = msg.decode().split(":")[-1]
        print(msg.decode())
        show_chat_message("connected to socket server")
        if mod_version != sock_version:
            show_chat_message(f"Version Mismatch! Unexpected results ahead. mine: {mod_version} client: {sock_version}")

        blg.is_sock_connected = True
        check_is_archi_connected()
        pull_items()
    except socket.error as error:
        print(error)
        show_chat_message("failed to connect, please connect through the Mod Options Menu after starting AP client")
    return

oid_connect_to_socket_server: ButtonOption = ButtonOption(
    "Connect to Socket Server",
    on_press=connect_to_socket_server,
    description="Connect to Socket Server",
)

def watcher_loop():
    while blg.task_should_run:
        yield WaitForSeconds(5)
        print("tick")
        if not blg.is_archi_connected:
            show_chat_message("client is not connected!")
            check_is_archi_connected()
        pull_items()
        push_locations()

def get_red_text(definition_data):
    try:
        weapon_part_list_def = definition_data.BalanceDefinition.WeaponPartListCollection
        weap_part_def = weapon_part_list_def.BarrelPartData
        barrel_part = weap_part_def.TitleList[0]
        red_text = name_part_def.CustomPresentations[0].NoConstraintText
        return red_text
    except:
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
    if bdstr.split("_")[-1].startswith("Alien"):
        return True
    if bdstr.split("_")[-2].startswith("Alien"):
        return True
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
        red_text = get_red_text(inv_item.DefinitionData)
        if red_text is not None:
            rarity = 999

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

def can_gear_loc_id_be_equipped(loc_id):
    if not blg.is_archi_connected:
        return False
    if loc_id is None:
        return True
    # TODO: if pearlescent and others are added to the pool conditionally, need to either handle it here or del them on init
    item_amt = blg.game_items_received.get(loc_id, 0)
    if item_amt > 0:
        return True
    return False

def can_inv_item_be_equipped(inv_item):
    if not blg.is_archi_connected:
        return False
    loc_id = get_gear_loc_id(inv_item)
    return can_gear_loc_id_be_equipped(loc_id)


@hook("WillowGame.WillowInventoryManager:AddInventory")
def add_inventory(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # TODO: maybe doesn't run on receiving quest reward
    # does not trigger on buy back from vending machine
    if self != get_pc().GetPawnInventoryManager():
        # not player inventory
        return
    if blg.should_perform_initial_modify:
        return
    print("add_inv")
    print(caller.NewItem.ItemName)
    try:
        cust_name = caller.NewItem.ItemName
        if cust_name.startswith("AP Check: "):
            print(cust_name)
            location_name = cust_name.split("AP Check: ")[1]
            blg.locs_to_send.append(loc_name_to_id[location_name])
            push_locations()
            return Block
    except AttributeError:
        pass

    if not blg.is_archi_connected:
        return

    loc_id = get_gear_loc_id(caller.NewItem)
    if loc_id is None or loc_id in blg.locations_checked:
        return
    blg.locs_to_send.append(loc_id)
    push_locations()


@hook("WillowGame.WillowInventoryManager:OnEquipped")
def on_equipped(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if not blg.is_archi_connected:
        return
    if self != get_pc().GetPawnInventoryManager():
        # not player inventory
        return
    if blg.should_perform_initial_modify:
        return

    loc_id = get_gear_loc_id(caller.Inv)
    if loc_id is None:
        return

    if loc_id not in blg.locations_checked:
        blg.locs_to_send.append(loc_id)
        push_locations()

    if can_gear_loc_id_be_equipped(loc_id):
        # allow equip
        return
    else:
        # block equip (I'm not sure this does anything)
        return Block

@hook("WillowGame.ItemCardGFxObject:SetItemCardEx", Type.POST)
def set_item_card_ex(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if (inv_item := caller.InventoryItem) is None:
        return
    if can_inv_item_be_equipped(inv_item):
        return
    kind = get_gear_kind(inv_item)
    self.SetLevelRequirement(True, False, False, "Can't Equip: " + kind)

def get_total_skill_pts():
    # unused for now.
    pc = get_pc()
    a = pc.PlayerReplicationInfo.GeneralSkillPoints
    b = pc.PlayerSkillTree.GetSkillPointsSpentInTree()
    return a + b

def reset_skill_tree():
    pc = get_pc()
    pst = pc.PlayerSkillTree
    for Branch in pst.Branches:
        if Branch.Definition.BranchName:
            for Tier in Branch.Definition.Tiers:
                for Skill in Tier.Skills:
                    pst.SetSkillGrade(Skill, 0)
    pst.SetSkillGrade(pc.PlayerSkillTree.GetActionSkill(), 0)

def sync_skill_pts():
    if not blg.is_archi_connected:
        return
    pc = get_pc()
    # TODO: small thing... can we allow player to unlock action skill before level 5?
    if pc.PlayerSkillTree is None:
        return
    unallocated = blg.skill_points_allowed - pc.PlayerSkillTree.GetSkillPointsSpentInTree()
    if unallocated < 0:
        show_chat_message('too many skill points allocated, forcing respec')
        reset_skill_tree()
        pc.PlayerReplicationInfo.GeneralSkillPoints = blg.skill_points_allowed
    else:
        pc.PlayerReplicationInfo.GeneralSkillPoints = unallocated

def sync_weapon_slots():
    if not blg.is_archi_connected:
        return
    pc = get_pc()
    inventory_manager = pc.GetPawnInventoryManager()
    if pc and inventory_manager and inventory_manager.SetWeaponReadyMax:
        blg.is_setting_sdu = True
        inventory_manager.SetWeaponReadyMax(blg.weapon_slots)

def level_my_gear(ButtonInfo):
    if blg.can_gear_level: # TODO: change to lookup dict
        show_chat_message("Need to unlock Gear Leveler.")
        return
    pc = get_pc()
    currentLevel = pc.PlayerReplicationInfo.ExpLevel
    inventory_manager = pc.GetPawnInventoryManager()

    if not inventory_manager:
        show_chat_message('no inventory, skipping')
        return

    backpack = inventory_manager.Backpack
    if not backpack:
        show_chat_message('no backpack loaded')
        return
    # go through backpack
    for item in backpack:
        item.DefinitionData.ManufacturerGradeIndex = currentLevel
        item.DefinitionData.GameStage = currentLevel

    # go through item chain (relic, classmod, grenade, shield)
    item = inventory_manager.ItemChain
    while item:
        item.DefinitionData.ManufacturerGradeIndex = currentLevel
        item.DefinitionData.GameStage = currentLevel
        item = item.Inventory

    # go through equipment slots
    for i in [1, 2, 3, 4]:
        weapon = inventory_manager.GetWeaponInSlot(i)
        if weapon:
            weapon.DefinitionData.ManufacturerGradeIndex = currentLevel
            weapon.DefinitionData.GameStage = currentLevel


    show_chat_message("gear set to level " + str(currentLevel))
    show_chat_message("save quit and continue to see changes.")
    return

oid_level_my_gear: ButtonOption = ButtonOption(
    "Level Up My Gear",
    on_press=level_my_gear,
    description="Level Up My Gear",
)

def print_items_received(ButtonInfo):
    # TODO: this needs work. consider replacing with something like "sync now"
    if not blg.is_archi_connected:
        return
    pull_items()
    print(blg.game_items_received)
    show_chat_message("All Items Received: ")
    items_str = ""
    for item_id, item_amt in blg.game_items_received.items():
        item_name = item_id_to_name.get(item_id)
        if item_name is None:
            item_name = str(item_id)
            continue
        items_str += item_name
        items_str += ':'
        items_str += str(item_amt)
        items_str += ", "
        if len(items_str) > 60:
            show_chat_message(items_str)
            print(items_str)
            items_str = ""
    show_chat_message(items_str)
    print(items_str)


oid_print_items_received: ButtonOption = ButtonOption(
    "Print Items Received",
    on_press=print_items_received,
    description="Print Items Received",
)

def unequip_invalid_inventory():
    # this can result in an overfull inventory, which really doesn't bother the game.
    if not blg.is_archi_connected:
        return
    pc = get_pc()
    if pc.Pawn is None:
        return
    inventory_manager = pc.GetPawnInventoryManager()
    # go through item chain (relic, classmod, grenade, shield)
    # TODO: does this work properly? if it unequips classmod, does the chain break/will it also unequip shield?
    items_to_uneq = []
    item = inventory_manager.ItemChain
    while item:
        item_id = get_gear_loc_id(item)
        item_amt = blg.game_items_received.get(item_id, 0)
        if item_amt == 0:
            show_chat_message("can't equip: " + get_gear_kind(item))
            items_to_uneq.append(item)
        item = item.Inventory
    for i in items_to_uneq:
        inventory_manager.InventoryUnreadied(i, True)
    # equipment slots
    for i in [1, 2, 3, 4]:
        weapon = inventory_manager.GetWeaponInSlot(i)
        if weapon:
            item_id = get_gear_loc_id(weapon)
            item_amt = blg.game_items_received.get(item_id, 0)
            if item_amt == 0:
                show_chat_message("can't equip: " + get_gear_kind(weapon))
                inventory_manager.InventoryUnreadied(weapon, True)

def check_full_inventory():
    # TODO: unused so far. maybe call during init
    if not blg.is_archi_connected:
        return

    pc = get_pc()
    currentLevel = pc.PlayerReplicationInfo.ExpLevel
    inventory_manager = pc.GetPawnInventoryManager()

    if not inventory_manager:
        show_chat_message('no inventory, skipping')
        return

    backpack = inventory_manager.Backpack
    if not backpack:
        show_chat_message('no backpack loaded')
        return
    # go through backpack
    for inv_item in backpack:
        loc_id = get_gear_loc_id(inv_item)
        if loc_id not in blg.locations_checked:
            blg.locs_to_send.push(loc_id)
    push_locations()

    unequip_invalid_inventory()

def delete_gear():
    show_chat_message("deleting gear")
    pc = get_pc()
    inventory_manager = pc.GetPawnInventoryManager()
    items = []
    item = inventory_manager.ItemChain
    while item:
        items.append(item)
        item = item.Inventory
    for i in items:
        inventory_manager.InventoryUnreadied(i, True)
    # equipment slots
    for i in [1, 2, 3, 4]:
        weapon = inventory_manager.GetWeaponInSlot(i)
        if weapon:
            inventory_manager.InventoryUnreadied(weapon, True)

    inventory_manager.Backpack = []

def on_enable():
    blg.task_should_run = True
    # print("enabled! 5")
    # unrealsdk.load_package("SanctuaryAir_Dynamic")
    # blg.pizza_mesh = unrealsdk.find_object("StaticMesh", "Prop_Details.Meshes.PizzaBoxWhole")
    # blg.pizza_mesh.ObjectFlags |= ObjectFlags.KEEP_ALIVE
    # find_and_play_akevent("Ake_VOCT_Contextual.Ak_Play_VOCT_Steve_HeyOo") # Heyoo

    connect_to_socket_server(None) #try to connect
    modify_map_area(None, None, None, None) # trigger "move" to current area

    # trying this in our own thread for now. if this causes problems, probably move to player tick or something else
    # stackoverflow.com/questions/59645272
    # thread = threading.Thread(target=asyncio.run, args=(watcher_loop(),))
    # thread.start()
    # threading definitely causing problems, switching to use juso's coroutines
    start_coroutine_tick(watcher_loop())


def disconnect_socket():
    global blg
    if blg is None or blg.sock is None:
        return
    try:
        if blg.is_sock_connected:
            blg.sock.shutdown(socket.SHUT_RDWR)
        blg.sock.close()
        # blg.is_sock_connected = False
        # blg.is_archi_connected = False
        if len(blg.locs_to_send) > 0:
            show_chat_message("outstanding locations: ", locs_to_send)
            # TODO: maybe should handle this better

        blg = BLGGlobals()  # reset
        show_chat_message("disconnected from socket server, please reconnect through mod options")
    except socket.error as error:
        print(error)

def on_disable():
    if blg is not None:
        blg.task_should_run = False
    print("blg disable!")
    disconnect_socket()

def get_current_map():
    if ENGINE and ENGINE.GetCurrentWorldInfo:
        wi = ENGINE.GetCurrentWorldInfo()
        if wi and wi.GetMapName:
            return str(wi.GetMapName()).casefold()
    return "none"

fake_maps = ["none", "loader", "fakeentry", "fakeentry_p", "menumap"]
@hook("WillowGame.WillowPlayerController:ClientSetPawnLocation")
def modify_map_area(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # TODO: this is potentially the wrong hook. it runs on twice on death, and potentially other times.
    new_map_name = get_current_map()
    print("modify_map_area " + new_map_name)
    if new_map_name in fake_maps:
        print("skipping map area: " + new_map_name)
        return

    # run initial setup on character
    if blg.should_perform_initial_modify:
        print("performing initial modify")
        blg.should_perform_initial_modify = False
        # remove starting inv
        if blg.settings.get("delete_starting_gear") == 1:
            delete_gear()

    if new_map_name != blg.current_map:
        # when we change map location...
        print("moved to map: " + new_map_name)
        log_to_file("moved to map: " + new_map_name)
        blg.current_map = new_map_name
        sync_vars_to_player()
        if new_map_name in map_modifications:
            mod_func = map_modifications[new_map_name]
            mod_func(blg)

def spawn_gear(item_pool_name, dist=100, height=0):
    # spawns item at player
    pc = get_pc()
    if not pc or not pc.Pawn:
        print("skipped spawn")
        return
    sbsl_obj = unrealsdk.construct_object("Behavior_SpawnLootAroundPoint", blg.package, "blg_spawn")
    sbsl_obj.ItemPools = [unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.WeaponPools.Pool_Weapons_Pistols_02_Uncommon")]
    sbsl_obj.SpawnVelocityRelativeTo = 0
    sbsl_obj.bTorque = False
    sbsl_obj.CircularScatterRadius = 0
    # loc = pc.LastKnownLocation
    loc = get_loc_in_front_of_player(dist, height)
    sbsl_obj.CustomLocation = unrealsdk.make_struct("AttachmentLocationData", 
        Location=loc, #unrealsdk.make_struct("Vector", X=loc.X, Y=loc.Y, Z=loc.Z),
        AttachmentBase=None, AttachmentName=""
    )

    # print("spawn_gear: " + item_pool_name)
    # # use booster shield definition
    # sbsl_obj = unrealsdk.construct_object(
    #     "Behavior_SpawnLootAroundPoint",
    #     blg.package,
    #     "blg_spawn",
    #     0x000000000,
    #     unrealsdk.find_object("Behavior_SpawnLootAroundPoint", "GD_Shields.Skills.Booster_Shield_Skill:BehaviorProviderDefinition_0.Behavior_SpawnLootAroundPoint_11")
    # )
    # doesn't work at level 1, probably due to the game believing shields are not available.

    # item_pool = unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.WeaponPools.Pool_Weapons_Pistols_02_Uncommon")
    item_pool = unrealsdk.find_object("ItemPoolDefinition", item_pool_name)
    if not item_pool or item_pool is None:
        print("can't find item pool: " + item_pool_name)
        return
    print(item_pool)
    item_pool.MinGameStageRequirement = None
    sbsl_obj.ItemPools = [item_pool]

    sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=0.000000, Y=0.000000, Z=200.000000)
    sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))

    # 4 direction spawn
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=100.000000, Y=0.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=-100.000000, Y=0.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=0.000000, Y=100.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=0.000000, Y=-100.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))


@hook("WillowGame.WillowPlayerInput:Jump")
def jump(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if not blg.can_jump:
        show_chat_message("jump disabled!")
        return Block

@hook("WillowGame.WillowPlayerInput:SprintPressed")
def sprint_pressed(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if not blg.can_sprint:
        show_chat_message("sprint disabled!")
        return Block

@hook("WillowGame.WillowPlayerInput:DuckPressed")
def duck_pressed(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    for pickup in get_pc().GetWillowGlobals().PickupList:
        if pickup.Inventory.ItemName.startswith("AP Check:"):
            print("moving:" + pickup.Inventory.ItemName)
            pickup.Location = get_loc_in_front_of_player(150, 50)
            pickup.AdjustPickupPhysicsAndCollisionForBeingDropped()

    # unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.WeaponPools.Pool_Weapons_Pistols_04_Rare")
    # get_pc().PlayerReplicationInfo.ExpLevel = 1
    # get_pc().ExpEarn
    # get_pc().ExpEarn(100000, 0)
    if not blg.can_crouch:
        show_chat_message("crouch disabled!")
        return Block

@hook("WillowGame.WillowVehicleWeapon:BeginFire")
def vehicle_begin_fire(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if blg.current_map == "southernshelf_p": # allow use of big bertha
        return True
    if not blg.can_vehicle_fire and self.MyVehicle and self.MyVehicle.PlayerReplicationInfo is not None:
        show_chat_message("vehicle fire disabled!")
        return Block

@hook("WillowGame.WillowInventoryManager:AddInventory", Type.POST)
def post_add_inventory(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if self != get_pc().GetPawnInventoryManager():
        # not player inventory
        return
    # does not trigger when selling at a vending machine.
    # probably does not trigger on quest completion with no item
    # TODO: actually check if the picked up item was currency.
    if get_pc().PlayerReplicationInfo.GetCurrencyOnHand(0) > blg.money_cap:
        show_chat_message("money cap: " + str(blg.money_cap))
        get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, blg.money_cap)

    if blg.should_perform_initial_modify:
        return
    # also run unequip on this hook
    unequip_invalid_inventory()

@hook("WillowGame.WillowPlayerReplicationInfo:AddCurrencyOnHand", Type.POST)
def on_currency_changed(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # happens at vending machine, on quest completion, after respec
    if get_pc().PlayerReplicationInfo.GetCurrencyOnHand(0) > blg.money_cap:
        show_chat_message("money cap: " + str(blg.money_cap))
        get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, blg.money_cap)

@hook("WillowGame.WillowPlayerController:VerifySkillRespec_Clicked", Type.POST)
def post_verify_skill_respec(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    sync_skill_pts()

@hook("WillowGame.WillowPlayerController:ExpLevelUp", Type.POST)
def leveled_up(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    print("ExpLevelUp" + str(get_pc().PlayerReplicationInfo.ExpLevel))
    sync_skill_pts()
    level = get_pc().PlayerReplicationInfo.ExpLevel
    # print("level")
    # print(loc_name_to_id["Level " + str(level)])
    blg.locs_to_send.append(loc_name_to_id["Level " + str(level)])
    push_locations()

@hook("WillowGame.WillowInventoryManager:SetWeaponReadyMax")
def set_weapon_ready_max(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if blg.is_setting_sdu:
        blg.is_setting_sdu = False
        return
    else:
        return Block

@hook("WillowGame.WillowPlayerController:Behavior_Melee")
def behavior_melee(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if not blg.can_melee:
        show_chat_message("melee disabled!")
        return Block
    # TODO: how does this interact with Krieg's action skill?

@hook("WillowGame.WillowPlayerPawn:SetupPlayerInjuredState")
def enter_ffyl(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    print("enter_ffyl")

@hook("WillowGame.WillowPlayerPawn:StartInjuredDeathSequence")
def died(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # TODO: how does this interact with co-op?
    print("died")

def test_btn(ButtonInfo):
    show_chat_message("hello test " + str(mod_version))
    print("\nlocations_checked")
    print(blg.locations_checked)
    print("\nsettings")
    print(blg.settings)
    print("\nfilepaths")
    print(blg.log_filepath)
    show_chat_message("is_archi_connected: " + str(blg.is_archi_connected) + " is_sock_connected: " + str(blg.is_sock_connected))

    dist = 0
    for _, pool in gear_kind_to_item_pool.items():
        spawn_gear(pool, dist, dist)
        dist +=50

    # get_pc().ExpEarn(1000, 0)
    # get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, 999999)

oid_test_btn: ButtonOption = ButtonOption(
    "Test Btn",
    on_press=test_btn,
    description="Test Btn",
)

@hook("WillowGame.Behavior_DiscoverLevelChallengeObject:ApplyBehaviorToContext")
def discover_level_challenge_object(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    obj_id = str(caller.ContextObject)
    check_name = vault_symbol_id_to_name.get(obj_id)
    if check_name is not None:
        blg.locs_to_send.append(loc_name_to_id[check_name])
        push_locations()

    obj_def = str(caller.ContextObject.InteractiveObjectDefinition)
    log_line = "Discover Challenge Object: " + obj_id + " - " + obj_def
    log_to_file(log_line)

@hook("WillowGame.PauseGFxMovie:CompleteQuitToMenu")
def complete_quit_to_menu(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    blg.current_map = "" # reset, now loading into map will trigger changing areas
    print("complete_quit_to_menu")

@hook("WillowGame.WillowPlayerController:ClientSetCurrentMapFullyExplored")
def set_current_map_fully_explored(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    log_line = "Map Fully Explored: " + blg.current_map
    log_to_file(log_line)
    print(log_line)

@hook("WillowGame.WillowGameInfo:InitiateTravel")
def initiate_travel(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    log_line = "Initiate Travel: " + str(caller.StationDefinition)
    log_to_file(log_line)
    print(log_line)
    # return Block

# @hook("WillowGame.WillowInteractiveObject:InitializeFromDefinition")
# def initialize_from_definition(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
#     if self.Class.Name != "WillowVendingMachine":
#         return
#     print("vending machine init")

blg.active_vend = None
@hook("WillowGame.WillowInteractiveObject:UseObject")
def use_object(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    print("use object")
    if self.Class.Name != "WillowVendingMachine":
        return
    blg.active_vend = self
    vname = str(self)
    print(vname)
    print(self.FeaturedItemPickupAttachmentPoint)
    print(self.CommerceMarkup)
    print(self.FeaturedItemAwesomeLevel)
    # self.ClearInventory()


    # print(dir(self.FeaturedItem)[:100])
    # print(self.FeaturedItem.Mark)
    # print(self.FeaturedItem.Owner)
    # print(self.FeaturedItem.PlayerOwner)
    # self.GenerateInventory()
    # sample_def = unrealsdk.find_object("InventoryBalanceDefinition", "GD_DefaultProfiles.IntroEchos.BD_SoldierIntroEcho")
    # sample_def = unrealsdk.find_object("UsableItemDefinition", "GD_Ammodrops.Shop.AmmoShop_Assault_Rifle_Bullets")
    # sample_def = unrealsdk.find_object("UsableCustomizationItemDefinition", "GD_Assassin_Items_MainGame.Assassin.Skin_VladofB")
    sample_def = unrealsdk.find_object("UsableItemDefinition", "GD_DefaultProfiles.IntroEchos.ID_SoldierIntroECHO")

    item_def = unrealsdk.construct_object(
        "UsableItemDefinition",
        blg.package,
        "archi_venditem_def",
        0,
        sample_def
    )
    pizza = unrealsdk.find_object("StaticMesh", "Prop_Details.Meshes.PizzaBoxWhole")
    item_def.NonCompositeStaticMesh = pizza
    item_def.ItemName = "AP Check: asdf"
    item_def.CustomPresentations = []
    item_def.bPlayerUseItemOnPickup = True # allows pickup with full inventory (i think)
    item_def.bIsConsumable = True
    item_def.BaseRarity.BaseValueConstant = 500.0 # teal, like mission/pearl
    r = 18
    item_def.UIMeshRotation = unrealsdk.make_struct("Rotator",
        Pitch = -134,
        Yaw = -14219,
        Roll = -7164,
    )

    def_item = unrealsdk.find_class('WillowItem').ClassDefaultObject
    new_item = def_item.CreateItemFromDef(
        unrealsdk.make_struct("ItemDefinitionData",
            ItemDefinition=item_def,
        ),
        NewQuantity=1,
        PlayerOwner=get_pc().Pawn,
    )
    self.SetFeaturedItem(new_item, "")

    # self.SetFeaturedItem(None, "")

    # inventory_manager.ClientAddItemToBackpack(
    #     # item_def,
    #     unrealsdk.make_struct("ItemDefinitionData",
    #         ItemDefinition=item_def,
    #         # Mark=0,
    #         # bReadyAfterAdd=False,
    #     ),
    #     Mark=0,
    #     Quantity=1,
    # )

    # self.ResetInventory()

    # print(self)
    # print(dir(self))

    # WillowGame.WillowItem:RemoveFromShop

# @hook("WillowGame.WillowPlayerController:PerformedUseAction")
# def performed_use_action(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
#     print("performed use action")
#     print(self)
#     print(caller)


# WillowGame.WillowDialogAct_RandomBranch:Activate

@hook("WillowGame.WillowInventoryManager:PlayerSoldItem")
def PlayerSoldItem(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # Vending machine check counts as "sell". I think because it's initialized with PlayerOwner *shrug*
    print("PlayerSoldItem")
    print(self)
    if caller.Inv.ItemName.startswith("AP Check:"):
        print(blg.active_vend)
        blg.active_vend.SetFeaturedItem(None, "")
        # blg.active_vend.ResetInventory()
        blg.active_vend = None
        return Block

    # if caller.InventoryForSale.ItemName.startswith("AP"):
    #     print(caller.InventoryForSale.ItemName)

@hook("WillowGame.WillowVendingMachine:GetSellingPriceForInventory")
def GetSellingPriceForInventory(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # print("GetSellingPriceForInventory")
    if caller.InventoryForSale.ItemName.startswith("AP"):
        print(caller.InventoryForSale.ItemName)
        
# @hook("WillowGame.InteractiveObjectBalanceDefinition:SetupInteractiveObjectLoot")
# def on_chest_opened(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
#     log_line = "on_chest_opened: " + str(caller)
#     print(log_line)
#     # log_to_file(log_line)
#     # return Block

# WillowGame.Default__Behavior_SetChallengeCompleted

# WillowGame.ItemOfTheDayPanelGFxObject:SetItemOfTheDayItem

def log_to_file(line):
    print(line)
    if not blg.log_filepath:
        print("don't know where to log")
        return
    with open(blg.log_filepath, 'a') as f:
        f.write(line + "\n")


build_mod(
    options=[
        oid_connect_to_socket_server,
        oid_level_my_gear,
        oid_print_items_received,
        oid_test_btn
    ],
    on_enable=on_enable,
    on_disable=on_disable,
    hooks=[
        add_inventory,
        post_add_inventory,
        on_equipped,
        modify_map_area,
        jump,
        sprint_pressed,
        duck_pressed,
        vehicle_begin_fire,
        behavior_melee,
        on_currency_changed,
        post_verify_skill_respec,
        leveled_up,
        set_weapon_ready_max,
        enter_ffyl,
        died,
        discover_level_challenge_object,
        complete_quit_to_menu,
        set_current_map_fully_explored,
        initiate_travel,
        use_object,
        set_item_card_ex,
        PlayerSoldItem,
        GetSellingPriceForInventory,
        # on_chest_opened,
    ]
)

# pyexec BouncyLootGod\__init__.py
