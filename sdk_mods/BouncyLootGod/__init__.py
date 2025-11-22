# to run from console: pyexec BouncyLootGod\__init__.py
# note: above command doesn't seem to reload changes in other files
import unrealsdk
import unrealsdk.unreal as unreal
from mods_base import hook as Hook, build_mod, ButtonOption, get_pc, hook, ENGINE, ObjectFlags
from ui_utils import show_chat_message
from unrealsdk.hooks import Type, Block

try:
    assert __import__("coroutines").__version_info__ >= (1, 1), "Please update the SDK"
except (AssertionError, ImportError) as ex:
    import webbrowser
    webbrowser.open("https://bl-sdk.github.io/willow2-mod-db/requirements?mod=BouncyLootGod")
    raise ex

from coroutines import start_coroutine_tick, WaitForSeconds

import socket
import sys
# import threading
# import asyncio

mod_version = "0.0"


from BouncyLootGod.archi_defs import item_name_to_id, item_id_to_name, loc_name_to_id
from BouncyLootGod.item_pool_defs import pool_modifications

# item_name_to_id = get_item_name_to_id()
# item_id_to_name = get_item_id_to_name()


head2def = None

class BLGGlobals:
    task_should_run = False
    sock = None
    is_sock_connected = False
    is_archi_connected = False
    setting_sdu = False
    # server setup:
    # (BL2 + this mod) <=====> (Socket Server + Archi Launcher BL 2 Client) <=====> (server/archipelago.gg)
    #             is_sock_connected                                   is_archi_connected
    # when is_archi_connected is False, we don't know what is and isn't unlocked.
    items_received = []
    locs_to_send = []
    pizza_mesh = None
    current_map = ""
    money_cap = 100
    weapon_slots = 2
    skill_points_allowed = 0
    package = unrealsdk.construct_object("Package", None, "BouncyLootGod")
    can_jump = False
    can_melee = False
    can_crouch = False
    can_sprint = False
    can_gear_level = False
    can_vehicle_fire = False


blg = BLGGlobals()

akevent_cache: dict[str, unreal.UObject] = {}
def find_and_play_akevent(event_name: str):
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

def handle_item_received(item_id):
    if item_id == item_name_to_id["3 Skill Points"]:
        blg.skill_points_allowed += 3
    elif item_id == item_name_to_id["Money Cap"]:
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

def sync_vars_to_player():
    sync_skill_pts()
    sync_weapon_slots()
    unequip_invalid_inventory()

# compute a - b; a should be a superset of b, return -1 if not. a and b can both contain repeats
def list_diff(list_a, list_b):
    dict_a = {}
    dict_b = {}
    for x in list_a:
        dict_a[x] = dict_a.get(x, 0) + 1
    for x in list_b:
        dict_b[x] = dict_b.get(x, 0) + 1
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
        if msg.decode() == "no":
            return
        msg_strs = msg.decode().split(",")
        print("msg_strs")
        print(msg_strs)
        msg_list = list(map(int, msg_strs))
        print(msg_list)
        print(blg.items_received)
        diff = list_diff(msg_list, blg.items_received)
        print(diff)
        if diff == -1:
            show_chat_message("detected items out of sync or archi client has disconnected.")
            check_is_archi_connected()
            return

        if len(diff) > 0:
            find_and_play_akevent("Ake_VOCT_Contextual.Ak_Play_VOCT_Steve_HeyOo")
        # loop through new ones
        for item_id in diff:
            item_name = item_id_to_name.get(item_id)
            if item_name is not None:
                show_chat_message("Received: " + item_name)
                handle_item_received(item_id)
            else:
                show_chat_message("Unknown item: " + str(item_id))
        blg.items_received = msg_list

        sync_vars_to_player()

    except socket.error as error:
        print(error)
        show_chat_message("pull_items: something went wrong.")
        disconnect_socket()

def push_locations():
    if not blg.is_sock_connected:
        return
    # TODO: maybe we should track locations we've already sent and skip duplicates
    while len(blg.locs_to_send) > 0:
        check = blg.locs_to_send.pop(0)
        print('sending ' + str(check))
        blg.sock.send(bytes(str(check), 'utf8'))

def check_is_archi_connected():
    if not blg.is_sock_connected:
        return
    try:
        blg.sock.send(bytes("is_archi_connected", 'utf8'))
        msg = blg.sock.recv(4096)
        blg.is_archi_connected = msg.decode() == "True"
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
        yield WaitForSeconds(10)
        if not blg.is_archi_connected:
            check_is_archi_connected()
        pull_items()
        push_locations()


dd_rarities = ['Common', 'Uncommon', 'Rare', 'Unique', 'VeryRare', 'Legendary'] #TODO seraph and pearl
def get_dd_weapon_rarity(definition_data):
    rarity_attempt = str(definition_data.BalanceDefinition).split(".")[-2].split("_")[-1]
    if rarity_attempt in dd_rarities:
        return rarity_attempt
    rarity_attempt = str(definition_data.BalanceDefinition).split("_")[-1][:-1]
    if rarity_attempt in dd_rarities:
        return rarity_attempt
    rarity_attempt = str(definition_data.MaterialPartDefinition).split("_")[-1][:-1]
    if rarity_attempt in dd_rarities:
        return rarity_attempt
    # print('Rarity not found... assuming "Unique"')
    # print(str(definition_data.BalanceDefinition))
    # print(str(definition_data.MaterialPartDefinition))
    return 'Unique'

RARITY_DICT = {
    1: "Common",
    2: "Uncommon",
    3: "Rare",
    4: "VeryRare",
    5: "Legendary",
    6: "Seraph",
    7: "Rainbow",
    500: "Pearlescent",
    999: "Unique"
}

weak_globals: unreal.WeakPointer = unreal.WeakPointer()
def get_rarity(invItem):
    # adapted from equip_locker
    if "WillowMissionItem" == invItem.Class.Name:
        # print("skipping mission item")
        return "unknown"
    if (globals_obj := weak_globals()) is None:
        globals_obj = unrealsdk.find_object("GlobalsDefinition", "GD_Globals.General.Globals")
        weak_globals.replace(globals_obj)

    rarity = globals_obj.GetRarityForLevel(invItem.RarityLevel)

    if invItem.Class.Name == "WillowWeapon":
        # handle Pearlescent
        if rarity == 0 and invItem.RarityLevel == 500:
            rarity = 500
        # handle Unique (guns only, maybe relics in the future)
        if rarity == 3 or rarity == 4:
            if get_dd_weapon_rarity(invItem.DefinitionData) == "Unique":
                rarity = 999

    rarity_str = RARITY_DICT.get(rarity)

    if not rarity_str:
        return "unknown"
    return rarity_str

ITEM_DICT = {
    "WillowShield": "Shield",
    "WillowGrenadeMod": "GrenadeMod",
    "WillowClassMod": "ClassMod",
    "WillowArtifact": "Relic"
}

WEAPON_DICT = {
    0: "Pistol",
    1: "Shotgun",
    2: "SMG",
    3: "SniperRifle",
    4: "AssaultRifle",
    5: "RocketLauncher"
}

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

def get_item_kind(inv_item):
    r = get_rarity(inv_item)
    if r == 'unknown': return 'unknown'
    t = get_item_type(inv_item)
    if t == 'unknown': return 'unknown'
    kind = r + " " + t
    return kind

def get_item_archie_id_from_kind(kind):
    return item_name_to_id.get(kind)


def get_item_archie_id(inv_item):
    kind = get_item_kind(inv_item)
    return item_name_to_id.get(kind)


@hook("WillowGame.WillowInventoryManager:AddInventory")
def add_inventory(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if self != get_pc().GetPawnInventoryManager():
        # not player inventory
        return
    # print(caller.NewItem)
    # if (caller.NewItem.DefinitionData):
    #     print(caller.NewItem.DefinitionData)
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
        # do nothing

    if not blg.is_archi_connected:
        return
    item_kind = get_item_kind(caller.NewItem)
    item_id = get_item_archie_id_from_kind(item_kind)
    if item_id is None:
        return
    blg.locs_to_send.append(item_id)
    push_locations()
 
    # if item_id in blg.items_received:
    #     # allow pickup
    #     return None
    # else:
    #     # block pickup, this deletes the item
    #     show_chat_message("unavailable: " + item_kind)
    #     return Block


@hook("WillowGame.WillowInventoryManager:OnEquipped")
def on_equipped(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if not blg.is_archi_connected:
        return

    if self != get_pc().GetPawnInventoryManager():
        # not player inventory
        return

    item_kind = get_item_kind(caller.Inv)
    item_id = get_item_archie_id_from_kind(item_kind)

    if item_id is None:
        return

    blg.locs_to_send.append(item_id)
    push_locations()
    if item_id in blg.items_received:
        # allow equip
        return None
    else:
        # block equip (I'm not sure this does anything)
        return Block

def get_total_skill_pts():
    # unused for now.
    pc = get_pc()
    a = pc.PlayerReplicationInfo.GeneralSkillPoints
    b = pc.PlayerSkillTree.GetSkillPointsSpentInTree()
    return a + b

def reset_skill_tree():
    pc = get_pc()
    PST = pc.PlayerSkillTree
    for Branch in PST.Branches:
        if Branch.Definition.BranchName:
            for Tier in Branch.Definition.Tiers:
                for Skill in Tier.Skills:
                    PST.SetSkillGrade(Skill, 0)
    PST.SetSkillGrade(pc.PlayerSkillTree.GetActionSkill(), 0)

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
    pc = get_pc()
    inventory_manager = pc.GetPawnInventoryManager()
    if pc and inventory_manager and inventory_manager.SetWeaponReadyMax:
        blg.setting_sdu = True
        inventory_manager.SetWeaponReadyMax(blg.weapon_slots)

def level_my_gear(ButtonInfo):
    if item_name_to_id["Gear Leveler"] not in blg.items_received:
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
    show_chat_message("All Items Received: ")
    items_str = ""
    for item_id in blg.items_received:
        item_name = item_id_to_name.get(item_id)
        if item_name is None:
            item_name = str(item_id)
            continue
        items_str += item_name
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
    item = inventory_manager.ItemChain
    while item:
        item_id = get_item_archie_id(item)
        if item_id not in blg.items_received:
            show_chat_message("can't equip: " + get_item_kind(item))
            inventory_manager.InventoryUnreadied(item, True)
        item = item.Inventory
    # equipment slots
    for i in [1, 2, 3, 4]:
        weapon = inventory_manager.GetWeaponInSlot(i)
        if weapon:
            item_id = get_item_archie_id(weapon)
            if item_id not in blg.items_received:
                show_chat_message("can't equip: " + get_item_kind(weapon))
                inventory_manager.InventoryUnreadied(weapon, True)

def on_enable():
    blg.task_should_run = True
    print("enabled! 5")
    unrealsdk.load_package("SanctuaryAir_Dynamic")
    blg.pizza_mesh = unrealsdk.find_object("StaticMesh", "Prop_Details.Meshes.PizzaBoxWhole")
    blg.pizza_mesh.ObjectFlags |= ObjectFlags.KEEP_ALIVE
    find_and_play_akevent("Ake_VOCT_Contextual.Ak_Play_VOCT_Steve_HeyOo") # Heyoo

    connect_to_socket_server(None) #try to connect
    change_map_area(None, None, None, None) # trigger "move" to current area

    # trying this in our own thread for now. if this causes problems, probably move to player tick or something else
    # stackoverflow.com/questions/59645272
    # thread = threading.Thread(target=asyncio.run, args=(watcher_loop(),))
    # thread.start()
    # threading definitely causing problems, switching to use juso's coroutines
    start_coroutine_tick(watcher_loop())


def disconnect_socket():
    if blg.sock is None:
        return
    try:
        if blg.is_sock_connected:
            blg.sock.shutdown(socket.SHUT_RDWR)
        blg.sock.close()
        blg.is_sock_connected = False
        blg.is_archi_connected = False
        show_chat_message("disconnected from socket server")
    except socket.error as error:
        print(error)

def on_disable():
    blg.task_should_run = False
    blg.items_received = []
    print("blg disable!")
    disconnect_socket()

@hook("WillowGame.WillowPlayerController:ClientSetPawnLocation")
def change_map_area(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    new_map_name = str(ENGINE.GetCurrentWorldInfo().GetMapName()).casefold()
    if new_map_name == "loader" or new_map_name == "fakeentry_p" or new_map_name == "menumap":
        print("skipping location " + new_map_name)
        return
    print("moved to " + new_map_name)

    sync_vars_to_player()

    if new_map_name != blg.current_map:
        # when we change location...
        blg.current_map = new_map_name
        if new_map_name in pool_modifications:
            func = pool_modifications[new_map_name]
            func(blg)

@hook("WillowGame.WillowPlayerInput:Jump")
def jump(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if not blg.can_jump:
        show_chat_message("jump disabled!")
        return Block

@hook("WillowGame.WillowPlayerInput:SprintPressed")
def sprint_pressed(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if not blg.can_crouch:
        show_chat_message("sprint disabled!")
        return Block

@hook("WillowGame.WillowPlayerInput:DuckPressed")
def duck_pressed(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if not blg.can_crouch:
        show_chat_message("crouch disabled!")
        return Block

@hook("WillowGame.WillowVehicleWeapon:BeginFire")
def vehicle_begin_fire(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if blg.current_map == "southernshelf_p": # allow use of big bertha
        return True
    if not can_vehicle_fire and self.MyVehicle and self.MyVehicle.PlayerReplicationInfo is not None:
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
        # show_chat_message("hit money cap!")
        get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, blg.money_cap)
    # also run unequip on this hook
    unequip_invalid_inventory()

@hook("WillowGame.WillowPlayerReplicationInfo:AddCurrencyOnHand", Type.POST)
def on_currency_changed(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # happens at vending machine, on quest completion, after respec
    if get_pc().PlayerReplicationInfo.GetCurrencyOnHand(0) > blg.money_cap:
        # show_chat_message("hit money cap!")
        get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, blg.money_cap)

@hook("WillowGame.WillowPlayerController:VerifySkillRespec_Clicked", Type.POST)
def post_verify_skill_respec(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    sync_skill_pts()

@hook("WillowGame.WillowPlayerController:ExpLevelUp", Type.POST)
def leveled_up(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    sync_skill_pts()
    level = get_pc().PlayerReplicationInfo.ExpLevel
    blg.locs_to_send.append(loc_name_to_id["Level " + str(level)])

@hook("WillowGame.WillowInventoryManager:SetWeaponReadyMax")
def set_weapon_ready_max(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if blg.setting_sdu:
        blg.setting_sdu = False
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

@hook("WillowGame.WillowPlayerPawn:SetInjuredDeadState")
def died(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    print("died")

def test_btn(ButtonInfo):
    show_chat_message("hello test2")
    show_chat_message("is_archi_connected: " + str(blg.is_archi_connected) + " is_sock_connected: " + str(blg.is_sock_connected))
    # get_pc().ExpEarn(1000, 0)
    # get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, 999999)

oid_test_btn: ButtonOption = ButtonOption(
    "Test Btn",
    on_press=test_btn,
    description="Test Btn",
)

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
        change_map_area,
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
    ]
)

# pyexec BouncyLootGod\__init__.py
