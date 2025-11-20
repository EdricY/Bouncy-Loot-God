# to run from console: pyexec BouncyLootGod\__init__.py
# note: above command doesn't seem to reload changes in other files
import unrealsdk
import unrealsdk.unreal as unreal
from mods_base import hook as Hook, build_mod, ButtonOption, get_pc, hook, ENGINE, ObjectFlags
from ui_utils import show_chat_message
from unrealsdk.hooks import Type, Block

import threading
import asyncio
import socket
import sys

# item_pool_defs start

orange = unrealsdk.make_struct("Color", R=128, G=64, B=0, A=255)


def setup_item_def(blg, item_def, check_name):
    item_def.NonCompositeStaticMesh = blg.pizza_mesh
    # AttributePresentationDefinition'GD_Z2_SplinterGroupData.ItemDefs.ID_MoxxisPizza:AttributePresentationDefinition_0'
    item_def.ItemName = "AP Check: " + check_name
    # item_def.CustomizationDef.CustomizationName = "AP Check: " + check_name
    # item_def.BaseRarity.BaseValueConstant = 500.0 # teal, like mission/pearl
    item_def.BaseRarity.BaseValueConstant = 5 # orange
    # item_def.LootBeamColorOverride = orange
    # item_def.ItemCardTopStatString = "Grab me!"
    # item_def.CustomPresentations[0].TextColor = orange
    item_def.CustomPresentations = []
    item_def.bPlayerUseItemOnPickup = True # allows pickup with full inventory (i think)
    item_def.bDisallowAIFromGrabbingPickup = True
    # item_def.AssociatedMissionObjective = None
    
    # print(unrealsdk.find_class("InventoryBalanceDefinition").ClassDefaultObject)


def modifyClaptrapsPlace(blg): 
    print("made it to Claptrap's Place!3!")
    # unrealsdk.load_package("SanctuaryAir_Dynamic")
    # unrealsdk.find_object("StaticMesh", "Prop_Details.Meshes.PizzaBoxWhole")

    # unrealsdk.load_package("Glacial_Dynamic") # maybe, nope

    # add to item pool

    # default_head = unrealsdk.find_class("InventoryBalanceDefinition").ClassDefaultObject

    # don't know why just the beer bottle works, can't find other mission items that work. might have to do with previously completed missions
    # head seems to be more stable. but has the "Already Unlocked" text, which is kinda annoying
    # sample_head = unrealsdk.find_object("InventoryBalanceDefinition", "GD_Anemone_Plot_Mission060.BalanceDefs.BD_BeerBottle")
    # sample_head = unrealsdk.find_object("InventoryBalanceDefinition", "GD_Anemone_Side_HypoOathPart1.BalanceDefs.BD_InfectedBodyPart")
    # sample_head = unrealsdk.find_object("CustomizationDefinition", "GD_AllCustoms_Anemone.BanditTech.Skin_Effer")
    # sample_head = unrealsdk.find_object("WeaponBalanceDefinition", "GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Dahl_5_Hornet")
    # sample_head = unrealsdk.find_object("InventoryBalanceDefinition", "GD_Episode06Data.BalanceDefs.BD_Ep6_BanditCarPart")
    sample_head = unrealsdk.find_object("InventoryBalanceDefinition", "GD_DefaultProfiles.IntroEchos.BD_SoldierIntroEcho")

    # create new head
    head = unrealsdk.construct_object(
        "InventoryBalanceDefinition",
        blg.package,
        "my_head",
        0x400004000,
        sample_head
        # unrealsdk.find_object("InventoryBalanceDefinition", "GD_Assassin_Items_Aster.BalanceDefs.Assassin_Head_ZeroAster")
    )
    head.Name = "archipelago_head"
    # print(head.GetPackageName())
    # print(head.GetFullDefinitionName())
    # print(head.GetStateName())
    # print(head.Name)
    # print(dir(sample_head))
    # CustomizationDefinition'GD_AllCustoms_Anemone.BanditTech.Skin_Effer'
    # head = unrealsdk.find_object("InventoryBalanceDefinition", "GD_Assassin_Items_Aster.BalanceDefs.Assassin_Head_ZeroAster")
    # head2 = unrealsdk.find_object("WeaponBalanceDefinition", "GD_Gladiolus_Weapons.AssaultRifle.AR_Bandit_6_Sawbar")
    # head2 = unrealsdk.find_object("WeaponBalanceDefinition", "GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Dahl_5_Hornet")
    # head2 = unrealsdk.find_object("WeaponBalanceDefinition", "GD_Orchid_RaidWeapons.AssaultRifle.Seraphim.Orchid_Seraph_Seraphim_Balance")
    # head2 = unrealsdk.find_object("InventoryBalanceDefinition", "GD_Anemone_GrenadeMods.A_Item_Legendary.GM_Antifection")
    
    # style the head
    # default_def = unrealsdk.find_class("UsableCustomizationItemDefinition").ClassDefaultObject
    head_def = unrealsdk.construct_object(
        "UsableCustomizationItemDefinition",
        blg.package,
        "my_def",
        0x400004000,
        unrealsdk.find_object("UsableItemDefinition", "GD_DefaultProfiles.IntroEchos.ID_SoldierIntroECHO")
        # unrealsdk.find_object("InventoryBalanceDefinition", "GD_Assassin_Items_Aster.BalanceDefs.Assassin_Head_ZeroAster")
    )

    # head_def = head.InventoryDefinition #unrealsdk.find_object("UsableCustomizationItemDefinition", "GD_Assassin_Items_Aster.Assassin.Head_ZeroAster")
    head.InventoryDefinition = head_def
    setup_item_def(blg, head_def, "KnuckleDragger1")

    # create new item pool

    # get knuckle dragger def
    knuck_balance_def = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_KnuckleDragger")
    knuck_item_pool = knuck_balance_def.DefaultItemPoolList[0].ItemPool
    # knuck_items_a = unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.EarlyGame.Pool_Knuckledragger_Pistol")
    print("equal??")
    # print(knuck_items == knuck_items_a)
    print(knuck_items_a == knuck_balance_def.DefaultItemPoolList[1].ItemPool)
    knuck_items.BalancedItems[0].InvBalanceDefinition = head
    # knuck_balance_def.DefaultItemPoolList[0].ItemPool
    # Increase the drop chance
    knuck_balance_def.DefaultItemPoolList[0].PoolProbability.BaseValueConstant = 1.000
    knuck_balance_def.DefaultItemPoolList[0].PoolProbability.BaseValueAttribute = None


    # head_def.NonCompositeStaticMesh = unrealsdk.find_object("StaticMesh", "Prop_Details.Meshes.PizzaBoxWhole")
    # head_def.NonCompositeStaticMesh = blg.pizza_mesh
    # head_def.BaseRarity.BaseValueConstant = 5.0
    # head_def.CustomizationDef.CustomizationName = "AP Check: KnuckleDragger"
    # head_def.ItemCardTopStatString = ""
    # head_def.CustomPresentations[0].TextColor = unrealsdk.make_struct("Color", R=128, G=64, B=0, A=255)
    # head_def.bPlayerUseItemOnPickup = True # allows pickup with full inventory (i think)
    # head_def.bDisallowAIFromGrabbingPickup = True
    print("Claptrap's Place Done")
    # TODO: remove from pools...
    # ItemPoolDefinition'GD_CustomItemPools_Aster.AllCustomizationsItemPool'
    # ItemPoolDefinition'GD_CustomItemPools_Aster.Assassin.AsterHead'
    # ItemPoolDefinition'GD_CustomItemPools_Aster.Assassin.Pool_Customs_Assassin_Rare'


def modifySouthernShelf(blg): 
    print("arrived at SS!2!")


pool_modifications = {
  "glacial_p": modifyClaptrapsPlace,
  "southernshelf_p": modifySouthernShelf
}


# item_pool_defs end

from BouncyLootGod.archi_defs import item_name_to_id, item_id_to_name
# from BouncyLootGod.item_pool_defs import pool_modifications

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
    pizza_mesh = None
    current_map = ""
    temp_money = 12
    skill_points_allowed = 33
    package = unrealsdk.construct_object("Package", None, "BouncyLootGod")


blg = BLGGlobals()

akevent_cache: dict[str, unreal.UObject] = {}
def find_and_play_akevent(event_name: str) -> None:
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

def pull_items():
    if not blg.is_sock_connected:
        return
    try:
        blg.sock.sendall(bytes("items_all", "utf-8"))
        msg = blg.sock.recv(4096)
        if msg.decode() == "no":
            return
        msg_arr = msg.decode().split(",")
        msg_set = set(map(int, msg_arr))
        diff = msg_set - blg.items_received
        # print new ones
        if len(diff) > 0:
            for item_id in diff:
                show_chat_message("Can Equip: " + item_id_to_name[item_id])
        blg.items_received.update(msg_set)
    except socket.error as error:
        show_chat_message(str(error))
        print(error)
        show_chat_message("pull_items: something went wrong.")

def push_locations():
    if not blg.is_sock_connected:
        return
    # TODO: maybe we should track locations we've already sent and skip duplicates
    while len(blg.locs_to_send) > 0:
        check = blg.locs_to_send.pop(0)
        print('sending ' + str(check))
        blg.sock.send(bytes(str(check), 'utf8'))

def connect_to_socket_server(ButtonInfo):
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
        # show_chat_message(str(error))
        print(error)
        show_chat_message("failed to connect, please connect through the Mod Options Menu after starting AP client")
    return

oid_connect_to_socket_server: ButtonOption = ButtonOption(
    "Connect to Socket Server",
    on_press=connect_to_socket_server,
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
    if self != get_pc().GetPawnInventoryManager():
        # not player inventory
        return
    print(caller.NewItem)
    try:
        # cust_name = caller.NewItem.DefinitionData.ItemDefinition.CustomizationDef.CustomizationName
        cust_name = caller.NewItem.ItemName
        if cust_name.startswith("AP Check: "):
            print(cust_name)
            location_name = cust_name.split("AP Check: ")[1]
            show_chat_message(location_name)
            # TODO: send check to sock server
            return Block
    except AttributeError:
        pass
        # do nothing

    if not blg.is_sock_connected:
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
    if not blg.is_sock_connected:
        return
    pc = get_pc()
    unallocated = blg.skill_points_allowed - pc.PlayerSkillTree.GetSkillPointsSpentInTree()
    if unallocated < 0:
        show_chat_message('too many skill points allocated, forcing respec')
        reset_skill_tree()
        pc.PlayerReplicationInfo.GeneralSkillPoints = blg.skill_points_allowed
    else:
        pc.PlayerReplicationInfo.GeneralSkillPoints = unallocated


def level_my_gear(ButtonInfo):
    pc = get_pc()
    currentLevel = pc.PlayerReplicationInfo.ExpLevel

    inventory_manager = pc.GetPawnInventoryManager()
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

oid_print_items_received: ButtonOption = ButtonOption(
    "Print Items Received",
    on_press=print_items_received,
    description="Print Items Received",
)

def test_btn(ButtonInfo):
    show_chat_message("hello test2")

oid_test_btn: ButtonOption = ButtonOption(
    "Test Btn",
    on_press=test_btn,
    description="Test Btn",
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
    print("enabled! 5")
    unrealsdk.load_package("SanctuaryAir_Dynamic")
    blg.pizza_mesh = unrealsdk.find_object("StaticMesh", "Prop_Details.Meshes.PizzaBoxWhole")
    # blg.pizza_mesh = unrealsdk.find_object("StaticMesh", "Prop_Details.Meshes.Pizza")
    blg.pizza_mesh.ObjectFlags |= ObjectFlags.KEEP_ALIVE
    find_and_play_akevent("Ake_VOCT_Contextual.Ak_Play_VOCT_Steve_HeyOo")
    
    # ConnectToSocketServer(None) #try to connect
    unequip_invalid_inventory()
    sync_skill_pts()
    set_pawn_location(None, None, None, None) # trigger "move" to current area


    #SDU unlock
    #get_pc().GetPawnInventoryManager().WeaponReadyMax = 2 # 3 4

    # trying this in our own thread for now. if this causes problems, probably move to player tick or something else
    # stackoverflow.com/questions/59645272
    thread = threading.Thread(target=asyncio.run, args=(watcher_loop(),))
    thread.start()


def disconnect_socket():
    if blg.sock is None:
        return
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

@hook("WillowGame.WillowPlayerController:ClientSetPawnLocation")
def set_pawn_location(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    new_map_name = str(ENGINE.GetCurrentWorldInfo().GetMapName()).casefold()
    if new_map_name == "loader" or new_map_name == "fakeentry_p" or new_map_name == "menumap":
        print("skipping location " + new_map_name)
        return
    print("moved to " + new_map_name)

    sync_skill_pts()

    if new_map_name != blg.current_map:
        # when we change location...
        blg.current_map = new_map_name
        if new_map_name in pool_modifications:
            func = pool_modifications[new_map_name]
            func(blg)

@hook("WillowGame.WillowPlayerInput:Jump")
def jump(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    show_chat_message("jump disabled!")
    # return Block

@hook("WillowGame.WillowPlayerInput:SprintPressed")
def sprint_pressed(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    show_chat_message("sprint disabled!")
    # return Block

@hook("WillowGame.WillowPlayerInput:DuckPressed")
def duck_pressed(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # particle_params = unrealsdk.make_struct(
            # unrealsdk.find_object("ParticleSystem", "FX_Lilac_PsychoBandit.Particles.Part_SilenceVoice_Screen"),
            # "ParticleSysParam",
            # unrealsdk.find_object("ParticleSystem", "FX_ENV_Misc.Particles.Part_Confetti")
            # ScreenParticleModifiers=[],
            # TemplateScreenParticleMaterial=None,
            # MatParamName="",
            # bHideWhenFinished=True,
            # ParticleTag="",
            # ContentDims=(16, 9),
            # ScalingMode=4,
            # StopParamsOT=(),
            # bOnlyOwnerSee=True,
        # )
    # get_pc().ShowScreenParticle(unrealsdk.find_object("ParticleSystem", "FX_ENV_Misc.Particles.Part_Confetti"))

    # unrealsdk.load_package("FX_Lilac_PsychoBandit")
    # ENGINE.GetCurrentWorldInfo().MyEmitterPool.SpawnEmitter(
    #     unrealsdk.find_object("ParticleSystem","FX_WEP_Explosions.Particles.Default.Part_ExplosiveExplosion_Small"),
    #     # unrealsdk.find_object("ParticleSystem","FX_Lilac_PsychoBandit.Particles.Part_ActionSkill_Blood_Screen"),
    #     unrealsdk.make_struct("Vector", X=get_pc().Location.X, Y=get_pc().Location.Y, Z=get_pc().Location.Z),
    # )
    # print(get_pc().Location)
    # find_and_play_akevent("Ake_VOCT_Contextual.Ak_Play_VOCT_Steve_HeyOo")
    show_chat_message("crouch disabled!")
    
    return Block

@hook("WillowGame.WillowVehicleWeapon:BeginFire")
def vehicle_begin_fire(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if blg.current_map == "southernshelf_p": # allow use of big bertha
        return True
    if self.MyVehicle and self.MyVehicle.PlayerReplicationInfo is not None:
        show_chat_message("vehicle fire disabled!")
        return Block

# @hook("WillowGame.WillowVehicle:DriverEnter")
# def driver_enter(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
#     # behaves strangely when you click "teleport to vehicle"
#     show_chat_message("DriverEnter")
#     return Block

@hook("WillowGame.WillowInventoryManager:AddInventory", Type.POST)
def post_add_inventory(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # does not trigger when selling at a vending machine.
    # probably does not trigger on quest completion with no item
    # Could in the future actually check if the picked up item was currency.
    if get_pc().PlayerReplicationInfo.GetCurrencyOnHand(0) > 9999:
        show_chat_message("money capped 1")
        get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, 9999)

@hook("WillowGame.WillowPlayerReplicationInfo:AddCurrencyOnHand", Type.POST)
def on_currency_changed(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # happens at vending machine, on quest completion, after respec
    if get_pc().PlayerReplicationInfo.GetCurrencyOnHand(0) > 9999:
        show_chat_message("money capped 2")
        get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, 9999)


@hook("WillowGame.WillowPlayerController:VerifySkillRespec_Clicked")
def verify_skill_respec(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    print("verify_skill_respec")
    # # don't allow insufficient funds to happen.
    # blg.temp_money = get_pc().PlayerReplicationInfo.GetCurrencyOnHand(0)
    # get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, 99999999)
    # ENGINE.GamePlayers[0].Actor.VerifySkillRespec()

@hook("WillowGame.WillowPlayerController:VerifySkillRespec_Clicked", Type.POST)
def post_verify_skill_respec(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    print("post verify_skill_respec")
    if get_pc().PlayerSkillTree.GetSkillPointsSpentInTree() > 0:
        # respec didn't happen, insufficient funds
        print("respec didn't happen")
        return
    # get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, blg.temp_money)
    get_pc().PlayerReplicationInfo.GeneralSkillPoints = blg.skill_points_allowed

@hook("WillowGame.WillowPlayerController:ExpLevelUp", Type.POST)
def leveled_up(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    print("leveled_up")
    sync_skill_pts()


@hook("WillowGame.WillowPlayerController:Behavior_Melee")
def behavior_melee(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # print(get_pc().PlayerReplicationInfo.GeneralSkillPoints)
    # print(get_pc().PlayerSkillTree.GetSkillPointsSpentInTree())
    # get_pc().PlayerReplicationInfo.ExpLevel = 50 # not like this
    # get_pc().Pawn.SetExpLevel(50)
    inventory_manager = get_pc().GetPawnInventoryManager()
    weapon = inventory_manager.GetWeaponInSlot(1)
    print(weapon.DefinitionData)
    print(weapon.DefinitionData.ManufacturerGradeIndex)
    # get_pc().ExpEarn(1000, 0)
    # print(get_pc().GetExpPoints())
    # # WillowGame.WillowGameInfo
    # # print (dir(ENGINE))
    # reset_skill_tree()
    # get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, 999999)
    # print(dir(get_pc().PlayerSkillTree)[100:])
    # ENGINE.GamePlayers[0].Actor.VerifySkillRespec()
    # show_chat_message("melee disabled!")
    # return Block

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
        set_pawn_location,
        jump,
        sprint_pressed,
        duck_pressed,
        # driver_enter,
        # try_to_teleport_into_vehicle,
        vehicle_begin_fire,
        behavior_melee,
        on_currency_changed,
        verify_skill_respec,
        post_verify_skill_respec,
        leveled_up,
        # inventory_should_be_readied_when_equipped,
        # set_item_card_ex
    ]
)

# pyexec BouncyLootGod\__init__.py
