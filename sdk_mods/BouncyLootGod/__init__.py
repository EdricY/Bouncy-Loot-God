# to run from console: pyexec BouncyLootGod\__init__.py
import unrealsdk
import unrealsdk.unreal as unreal
from mods_base import hook as Hook, build_mod, ButtonOption, get_pc, hook
from ui_utils import show_chat_message
from unrealsdk.hooks import Type, Block

import threading
import asyncio
import socket
import sys

from BouncyLootGod.archi_defs import item_name_to_id, item_id_to_name
# item_name_to_id = get_item_name_to_id()
# item_id_to_name = get_item_id_to_name()


show_chat_message("BLG starting")

head2def = None

class BLGGlobals:
    task_should_run = False
    sock = None
    is_sock_connected = False
    items_received = set()
    locs_to_send = []

blg = BLGGlobals()

def pull_items():
    if not blg.is_sock_connected:
        return
    try:
        # show_chat_message("pulling...")
        blg.sock.sendall(bytes("items_all", "utf-8"))
        msg = blg.sock.recv(4096)
        msg_arr = msg.decode().split(",")
        msg_set = set(map(int, msg_arr))
        blg.items_received.update(msg_set)
        diff = blg.items_received - msg_set
        if len(diff) > 0:
            # print new ones
            for item_id in diff:
                show_chat_message("Can Equip: " + item_id_to_name[diff])
    except socket.error as error:
        show_chat_message(str(error))
        print(error)
        show_chat_message("pull_items: something went wrong.")

def push_locations():
    if not blg.is_sock_connected:
        return
    while len(blg.locs_to_send) > 0:
        check = blg.locs_to_send.pop(0)
        print('sending ' + str(check))
        blg.sock.send(bytes(str(check), 'utf8'))

def ConnectToSocketServer(ButtonInfo):
    try:
        # Connect to server and send data
        blg.sock = socket.socket()
        blg.sock.connect(("localhost", 9997))
        blg.sock.sendall(bytes("blghello", "utf-8"))
        msg = blg.sock.recv(4096)
        print(msg)
        blg.is_sock_connected = True
        pull_items()
    except socket.error as error:
        show_chat_message(str(error))
        print(error)
        show_chat_message("failed to connect, please connect through Options Menu after starting AP client")
    return

oidConnectToSocketServer: ButtonOption = ButtonOption(
    "Connect to Socket Server",
    on_press=ConnectToSocketServer,
    description="Connect to Socket Server",
)

async def watcher_loop():
    while blg.task_should_run:
        pull_items()
        push_locations()
        # blg.sock.sendall(bytes(str(blg.counter), "utf-8"))
        # msg = blg.sock.recv(4096)
        # print("server says " + str(msg))
        await asyncio.sleep(10)


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
    print(str(definition_data.BalanceDefinition))
    print(str(definition_data.MaterialPartDefinition))
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
    if not blg.is_sock_connected:
        return
    if self != get_pc().GetPawnInventoryManager():
        # not player inventory
        return
    # if (caller.NewItem.DefinitionData):
    #     print(caller.NewItem.DefinitionData)
    item_kind = get_item_kind(caller.NewItem)
    item_id = get_item_archie_id_from_kind(item_kind)
    if item_id is None:
        return
    blg.locs_to_send.append(item_id)
    push_locations()
    if item_id in blg.items_received:
        # allow pickup
        return None
    else:
        # block pickup, this deletes the item
        show_chat_message("unavailable: " + item_kind)
        return Block

@hook("WillowGame.WillowInventoryManager:OnEquipped")
def on_equipped(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if not blg.is_sock_connected:
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


def LevelMyGear(ButtonInfo):
    print("LevelMyGear 3")
    pc = get_pc()
    print(pc)
    currentLevel = pc.PlayerReplicationInfo.ExpLevel

    inventory_manager = pc.GetPawnInventoryManager()
    backpack = inventory_manager.Backpack
    if not backpack:
        show_chat_message('no backpack loaded')
        return
    # go through backpack
    for item in backpack:
        item.DefinitionData.ManufacturerGradeIndex = currentLevel
        print(item.DefinitionData.ManufacturerGradeIndex)

    # go through item chain (relic, classmod, grenade, shield)
    item = inventory_manager.ItemChain
    while item:
        item.DefinitionData.ManufacturerGradeIndex = currentLevel
        item = item.Inventory

    # equipment slots
    for i in [1, 2, 3, 4]:
        weapon = inventory_manager.GetWeaponInSlot(i)
        if weapon:
            weapon.DefinitionData.ManufacturerGradeIndex = currentLevel

    show_chat_message("done " + str(currentLevel))
    show_chat_message("save quit and continue to see changes.")
    return

oidLevelMyGear: ButtonOption = ButtonOption(
    "Level Up My Gear",
    on_press=LevelMyGear,
    description="Level Up My Gear",
)

def print_items_received(ButtonInfo):
    pull_items()
    show_chat_message("All Items Received: ")
    items_str = ""
    for item_id in blg.items_received:
        item_kind = item_id_to_name.get(item_id)
        if item_kind is None:
            continue
        items_str += item_kind
        items_str += ", "
        if len(items_str) > 60:
            show_chat_message(items_str)
            items_str = ""
    show_chat_message(items_str)

oidPrintItemsReceived: ButtonOption = ButtonOption(
    "Print Items Received",
    on_press=print_items_received,
    description="Print Items Received",
)

# @hook("WillowGame.WillowInventoryManager:InventoryShouldBeReadiedWhenEquipped")
# def inventory_should_be_readied_when_equipped(self, caller, ret, func):
#     return
#     # Triggers for pickup of any equipment (weapon or item)
#     # Does trigger for shop purchase
#     # Does trigger for quest rewards
#     # Still triggers if equipment slots are full
#     # Does not trigger for money/ammo, customizations, mission items
#     # Does not trigger on hold 'e' to equip (may be a problem...)
#     # returning Block causes item to not be equipped, and just go into backpack (can cause backpack overflow, which is fine)
#     r = get_rarity(caller.WillowInv)
#     if r == 'unknown': return
#     t = get_item_type(caller.WillowInv)
#     if t == 'unknown': return
#     name = r + " " + t
#     show_chat_message("nInventoryShouldBeReadiedWhenEquipped " + name)
#     return Block

# @hook("WillowGame.ItemCardGFxObject:SetItemCardEx", Type.POST)
# def set_item_card_ex(self, caller, ret, func) -> None:
#     # if (item := args.InventoryItem) is None:
#     #     return
#     # if can_item_be_equipped(item):
#     #     return
#     self.SetLevelRequirement(True, False, False, "qwoieur")

def unequip_invalid_inventory():
    if not blg.is_sock_connected:
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
            inventory_manager.InventoryUnreadied(item, True)
        item = item.Inventory
    # equipment slots
    for i in [1, 2, 3, 4]:
        weapon = inventory_manager.GetWeaponInSlot(i)
        if weapon:
            print("slot " + get_item_kind(weapon))
            item_id = get_item_archie_id(weapon)
            if item_id not in blg.items_received:
                inventory_manager.InventoryUnreadied(weapon, True)

def on_enable():
    blg.task_should_run = True
    print("enabled! 3" + str(blg.task_should_run))
    ConnectToSocketServer(None) #try to connect
    unequip_invalid_inventory()

    # trying this in our own thread for now. if this causes problems, probably move to player tick or something else
    # stackoverflow.com/questions/59645272
    thread = threading.Thread(target=asyncio.run, args=(watcher_loop(),))
    thread.start()


def disconnect_socket():
    try:
        if blg.is_sock_connected:
            blg.sock.shutdown(socket.SHUT_RDWR)
        blg.sock.close()
        blg.is_sock_connected = False
    except socket.error as error:
        print(error)

def on_disable():
    blg.task_should_run = False
    blg.items_received.clear()
    print("blg disable!")
    disconnect_socket()

build_mod(
    options=[oidConnectToSocketServer, oidLevelMyGear, oidPrintItemsReceived],
    on_enable=on_enable,
    on_disable=on_disable,
    hooks=[
        add_inventory,
        on_equipped,
        # inventory_should_be_readied_when_equipped,
        # set_item_card_ex
    ]
)

# pyexec BouncyLootGod\__init__.py
