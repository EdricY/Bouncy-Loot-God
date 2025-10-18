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

from BouncyLootGod.Asdf import get_item_name_to_id, get_item_id_to_name
item_name_to_id = get_item_name_to_id()
item_id_to_name = get_item_id_to_name()

print("hello3")

show_chat_message("lkjasd")

head2def = None

class BLGGlobals:
    counter = 0
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
        show_chat_message("pulling...")
        blg.sock.sendall(bytes("items_all", "utf-8"))
        msg = blg.sock.recv(1024)
        msg_arr = msg.decode().split(",")
        blg.items_received.update(list(map(int, msg_arr)))
        show_chat_message(str(blg.items_received))
    except socket.error as error:
        show_chat_message(str(error))
        print(error)
        show_chat_message("pull_items something went wrong.")

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
        blg.sock.sendall(bytes("bl2hello", "utf-8"))
        msg = blg.sock.recv(1024)
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
    print("sample_task " + str(blg.task_should_run))
    while blg.task_should_run:
        blg.counter += 1
        show_chat_message(str(blg.counter))
        pull_items()
        push_locations()
        # blg.sock.sendall(bytes(str(blg.counter), "utf-8"))
        # msg = blg.sock.recv(1024)
        # print("server says " + str(msg))
        await asyncio.sleep(10)

def on_enable():
    blg.task_should_run = True
    print("enabled! 3" + str(blg.task_should_run))
    ConnectToSocketServer(None) #try to connect

    # trying this in our own thread for now. can move this to player tick or something else
    # stackoverflow.com/questions/59645272
    thread = threading.Thread(target=asyncio.run, args=(watcher_loop(),))
    thread.start()

    unrealsdk.load_package("SanctuaryAir_Dynamic")
    unrealsdk.find_object("StaticMesh", "Prop_Details.Meshes.PizzaBoxWhole")

    unrealsdk.load_package("Glacial_Dynamic") # maybe, nope
    # add to item pool
    # knuckitems2 = unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.EarlyGame.Pool_Knuckledragger_Pistol")
    # # head2 = unrealsdk.find_object("WeaponBalanceDefinition", "GD_Gladiolus_Weapons.AssaultRifle.AR_Bandit_6_Sawbar")
    # # head2 = unrealsdk.find_object("WeaponBalanceDefinition", "GD_Orchid_RaidWeapons.AssaultRifle.Seraphim.Orchid_Seraph_Seraphim_Balance")
    # head2 = unrealsdk.find_object("InventoryBalanceDefinition", "GD_Anemone_GrenadeMods.A_Item_Legendary.GM_Antifection")
    # # head2 = unrealsdk.find_object("InventoryBalanceDefinition", "GD_Assassin_Items_Aster.BalanceDefs.Assassin_Head_ZeroAster")
    # knuckitems2.BalancedItems[0].InvBalanceDefinition = head2

    # Increase the drop chance
    # knuckbalancedef = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_KnuckleDragger")
    # knuckbalancedef.DefaultItemPoolList[0].PoolProbability.BaseValueConstant = 1.000
    # knuckbalancedef.DefaultItemPoolList[0].PoolProbability.BaseValueAttribute = None

    # # create pizza
    # head2def = unrealsdk.find_object("UsableCustomizationItemDefinition", "GD_Assassin_Items_Aster.Assassin.Head_ZeroAster")
    # head2def.NonCompositeStaticMesh = unrealsdk.find_object("StaticMesh", "Prop_Details.Meshes.PizzaBoxWhole")
    # head2def.BaseRarity.BaseValueConstant = 5.0
    # head2def.CustomizationDef.CustomizationName = "AP Check ~ Grab me!"
    # head2def.ItemCardTopStatString = ""
    # head2def.CustomPresentations[0].TextColor = unrealsdk.make_struct("Color", R=128, G=64, B=0, A=255)
    # head2def.bPlayerUseItemOnPickup = True # allows pickup with full inventory (i think)
    # head2def.bDisallowAIFromGrabbingPickup = True

def disconnect_socket():
    try:
        if blg.is_sock_connected:
            blg.sock.shutdown(socket.SHUT_RDWR)
        blg.sock.close()
    except socket.error as error:
        print(error)

def on_disable():
    blg.task_should_run = False
    blg.items_received.clear()
    print("disable! 2")
    
    # try to shutdown, then try to close
    disconnect_socket()


dd_rarities = ['Common', 'Uncommon', 'Rare', 'Unique', 'VeryRare', 'Legendary'] #TODO seraph and pearl
def get_dd_weapon_rarity(definition_data):
    rarity_attempt = str(definition_data.BalanceDefinition).split(".")[-2].split("_")[-1]
    if rarity_attempt in dd_rarities:
        return rarity_attempt
    rarity_attempt = str(definition_data.MaterialPartDefinition).split("_")[-1][:-1]
    if rarity_attempt in dd_rarities:
        return rarity_attempt
    # print('Rarity not found... assuming "Unique"')
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
        print("skipping mission item")
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

def get_item_type(invItem):
    if invItem.Class.Name == "WillowWeapon":
        # print("get_item_type " + str(invItem) + " as "+ str(invItem.DefinitionData.WeaponTypeDefinition.WeaponType))
        weap_def = invItem.DefinitionData.WeaponTypeDefinition
        if weap_def is None:
            return "unknown"
        weapon_type = weap_def.WeaponType
        weapon_str = WEAPON_DICT.get(weapon_type)
        if not weapon_str:
            return "unknown"
        return weapon_str

    item_class = invItem.Class.Name
    item_str = ITEM_DICT.get(item_class)
    if not item_str:
        return "unknown"
    return item_str

@hook("WillowGame.WillowInventoryManager:AddInventory")
def AddInventory(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    r = get_rarity(caller.NewItem)
    if r == 'unknown': return
    t = get_item_type(caller.NewItem)
    if t == 'unknown': return
    name = r + " " + t
    show_chat_message("AddInventory " + name)
    print("AddInventory " + name)
    print("\nself")
    print(self)
    print("\ncaller")
    print(caller)
    print("\nfunction")
    print(function)
    print("\nparams")
    print(params)
    if (caller.NewItem.DefinitionData):
        print(caller.NewItem.DefinitionData)
    # item_id = item_name_to_id.get(name)
    # if item_id in blg.items_received:
    #     # allow equip
    #     return None
    # else:
    #     blg.locs_to_send.append(item_id)
    #     push_locations()
    #     return Block

@hook("WillowGame.WillowInventoryManager:OnEquipped")
def OnEquipped(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    r = get_rarity(caller.Inv)
    # if r == 'unknown': return
    # t = get_item_type(caller.Inv)
    # if t == 'unknown': return
    # name = r + " " + t
    # show_chat_message("OnEquipped " + name)
    # print("OnEquipped " + name)
    # print(caller.Inv)
    # item_id = item_name_to_id[name]
    # if item_id in blg.items_received:
    #     # allow equip
    #     return None
    # else:
    #     blg.locs_to_send.append(item_id)
    #     push_locations()
    #     return Block


def LevelMyGear(ButtonInfo):
    print("LevelMyGear 3")
    pc = get_pc()
    print(pc)
    currentLevel = pc.PlayerReplicationInfo.ExpLevel

    inventoryManager = pc.GetPawnInventoryManager()
    backpack = inventoryManager.Backpack
    if not backpack:
        show_chat_message('no backpack loaded')
        return
    # go through backpack
    for item in backpack:
        item.DefinitionData.ManufacturerGradeIndex = currentLevel
        print(item.DefinitionData.ManufacturerGradeIndex)

    # go through item chain (relic, classmod, grenade, shield)
    item = inventoryManager.ItemChain
    while item:
        item.DefinitionData.ManufacturerGradeIndex = currentLevel
        item = item.Inventory

    # equipment slots
    for i in [1, 2, 3, 4]:
        weapon = inventoryManager.GetWeaponInSlot(i)
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

def test_btn_fn(ButtonInfo):
    show_chat_message("hi there1")
    pull_items()

oidTestBtn: ButtonOption = ButtonOption(
    "Test Button",
    on_press=test_btn_fn,
    description="Test Button",
)

print("build mod 1")

@hook("WillowGame.WillowInventoryManager:InventoryShouldBeReadiedWhenEquipped")
def inventory_should_be_readied_when_equipped(obj, args, _ret, _func):
    print("\nInventoryShouldBeReadiedWhenEquipped")
    print(obj)


build_mod(
    options=[oidConnectToSocketServer, oidLevelMyGear, oidTestBtn],
    on_enable=on_enable,
    on_disable=on_disable,
    hooks=[
        AddInventory,
        OnEquipped,
        inventory_should_be_readied_when_equipped
    ]
)

# pyexec BouncyLootGod\__init__.py
