# to run from console: pyexec \path\to\BouncyLootGod\__init__.py

# note regarding: rlm BouncyLootGod*
# above works, but coroutines starts a new loop without clearing the old one, so sticking with pyexec for now

# debug thing: py unrealsdk.hooks.log_all_calls(True)
# py unrealsdk.hooks.log_all_calls(False)
# find the output file at ...\Steam\steamapps\common\Borderlands 2\Binaries\Win32\Plugins\unrealsdk.calls.tsv

import unrealsdk
import unrealsdk.unreal as unreal
from mods_base import build_mod, ButtonOption, SpinnerOption, SliderOption, get_pc, keybind, hook, ENGINE, ObjectFlags, Game
from ui_utils import show_chat_message, show_hud_message
from unrealsdk.hooks import Type, Block, prevent_hooking_direct_calls

try:
    assert __import__("coroutines").__version_info__ >= (1, 1), "Please install coroutines"
except (AssertionError, ImportError) as ex:
    import webbrowser
    webbrowser.open("https://bl-sdk.github.io/willow2-mod-db/mods/coroutines/")
    raise ex

from coroutines import start_coroutine_tick, WaitForSeconds

import socket
import sys
import os
import json
import datetime
import random


mod_version = "0.5.5"
if __name__ == "builtins":
    print("running from console, attempting to reload modules")
    get_pc().ConsoleCommand("rlm BouncyLootGod.*")
# print(Game.get_current().name)
if Game.get_current().name == "TPS":
    from BouncyLootGod.bl_tps.vault_symbols import vault_symbol_pathname_to_name
    from BouncyLootGod.bl_tps.loot_pools import spawn_gear, spawn_gear_from_pool_name, get_or_create_package, activate_moxxtail
    from BouncyLootGod.bl_tps.map_modify import map_area_to_name, map_modifications
    from BouncyLootGod.bl_tps.entrances import entrance_to_req_areas, travel_targets, region_translation_dict
    from BouncyLootGod.bl_tps.challenges import challenge_dict, reveal_annoying_challenges
    from BouncyLootGod.bl_tps.chests import chest_dict
    socket_port = 9998
    receive_sounds = [
        "AKe_cork_vosq_sidequests.RaidBoss.Ak_Play_VOSQ_Cork_RaidBoss_0200_TinyTina", #yay
        "AKe_cork_vosq_sidequests.RaidBoss.Ak_Play_VOSQ_Cork_RaidBoss_0250_TinyTina" #woo-WOO (fast)
    ]
else:
    from BouncyLootGod.bl2.entrances import entrance_to_req_areas, travel_targets, region_translation_dict
    from BouncyLootGod.bl2.vault_symbols import vault_symbol_pathname_to_name
    from BouncyLootGod.loot_pools import spawn_gear, spawn_gear_from_pool_name, get_or_create_package
    from BouncyLootGod.map_modify import map_area_to_name, map_modifications
    from BouncyLootGod.challenges import challenge_dict, reveal_annoying_challenges
    from BouncyLootGod.chests import chest_dict
    socket_port = 9997
    receive_sounds = [
        "Ake_VOCT_Contextual.Ak_Play_VOCT_Steve_HeyOo", # heyoo
        "Ake_VOSQ_Sidequests.Ak_Play_VOSQ_ShootInFace_09_live_ShootyFace", # thank you!
    ]
from BouncyLootGod.enemies import enemy_class_to_loc_name, oid_generic_drop_chance_override
from BouncyLootGod.vending import vending_machine_position_to_name, use_vending_machine
from BouncyLootGod.archi_data import item_name_to_id, item_id_to_name, loc_name_to_id
from BouncyLootGod.missions import grant_mission_reward, mission_ue_str_to_name, move_southern_shelf_blocked_missions
from BouncyLootGod.travel import can_travel_to_region, get_travel_req_string, get_newly_unlocked_region_name, get_entrance_lock_warnings, get_translated_map_name
from BouncyLootGod.map_modify import place_mesh_object, setup_generic_mob_drops
from BouncyLootGod.traps import trigger_spawn_trap, init_traps, trigger_trap
from BouncyLootGod.rarity import get_gear_item_id, get_gear_loc_id, can_gear_item_id_be_equipped, can_inv_item_be_equipped, get_gear_kind, needs_rarity_check
from BouncyLootGod.state import get_globals, init_globals, set_globals, ApItemMesh
from BouncyLootGod.oob import get_loc_in_front_of_player
from BouncyLootGod.always_on_level import set_always_on_level
from BouncyLootGod.objectives import update_objective
from BouncyLootGod.networking import push_locations

mod_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(mod_dir) # sdk_mods/ if running unzipped
if parent_dir.endswith(".sdkmod") or parent_dir.endswith(".zip"):
    parent_dir = os.path.dirname(parent_dir)

storage_dir = os.path.join(parent_dir, "blgstor")
# TODO: maybe move storage dir to SETTINGS_DIR (from mods_base)
os.makedirs(storage_dir, exist_ok=True)

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

def get_exp_for_current_level():
    pc = get_pc()
    level = pc.PlayerReplicationInfo.ExpLevel
    if level == pc.GetMaxExpLevel():
        return 0
    xp = pc.GetExpPointsRequiredForLevel(level + 1) - pc.GetExpPointsRequiredForLevel(level)
    return xp

def can_player_receive():
    pc = get_pc()
    if not pc:
        return False
    pawn = get_pc().Pawn
    if not pawn:
        return False
    current_map = get_current_map()
    if current_map in fake_maps:
        return False
    if pawn.Class.Name != "WillowPlayerPawn":
        # in vehicle or otherwise not controlling the player directly
        return False
    if pawn.Location.Z < -180000:
        # not sure how else to detect if you're in the blue respawning zone (HoldingCell)
        return False

    if pc.Pawn.InjuredDeadState != 0:
        return False

    if pc.GetExpPoints() > pc.GetExpPointsRequiredForLevel(pc.PlayerReplicationInfo.ExpLevel + 1):
        # you're over the current amount xp count, allow level up behaviors to happen first
        return False

    # if pc.GFxUIManager.IsBlockingMoviePlaying():
    #     # cutscenes and menus, probably fine without this
    #     print("IsBlockingMoviePlaying")
    #     return False

    return True

def handle_item_received(item_id, is_init=False):
    # called only once per item, every init / reconnect
    # is_init means we are receiving this while reading from the file.
    # so... do setup for received items, but skip granting duplicates
    # return True if item properly received and sound should play
    blg = get_globals()
    blg.game_items_received[item_id] = blg.game_items_received.get(item_id, 0) + 1
    item_name = item_id_to_name.get(item_id)
    did_receive_simple = True
    if item_id == item_name_to_id["3 Skill Points"]:
        blg.skill_points_allowed = blg.calc_skill_points_allowed()
    elif item_id == item_name_to_id["3 Skill Points (p)"]:
        blg.skill_points_allowed = blg.calc_skill_points_allowed()
    elif item_id == item_name_to_id["Progressive Money Cap"]:
        blg.money_cap = 200 * (10 ** blg.game_items_received[item_id])
    elif item_id == item_name_to_id["Progressive Weapon Slot"]:
        blg.weapon_slots = min(4, blg.weapon_slots + 1)
    elif item_id == item_name_to_id["Progressive Jump"]:
        blg.jump_z = blg.calc_jump_height()
    elif item_id == item_name_to_id["Progressive Sprint"]:
        blg.sprint_speed = blg.calc_sprint_speed()
    else:
        did_receive_simple = False

    if is_init: # other items can be ignored on init
        return False

    if did_receive_simple:
        with open(blg.items_filepath, 'a') as f:
            f.write(str(item_id) + "\n")
        show_chat_message("Received: " + item_name)
        return True

    print("receiving " + str(item_id))
    if not can_player_receive():
        # skip for now, try again later
        blg.game_items_received[item_id] = blg.game_items_received.get(item_id, 1) - 1
        print("skipping")
        return False

    if not item_name:
        print("unknown item: " + str(item_id))
        return False
    show_chat_message("Received: " + item_name)
    if item_name.startswith("Progressive Travel: "):
        region_name = get_newly_unlocked_region_name(item_name, blg.game_items_received[item_id])
        if region_name:
            show_chat_message("Area Unlocked: " + region_name)

    # spawn gear
    receive_gear_setting = blg.settings.get("receive_gear")
    if item_name.startswith("Filler Gear: "):
        spawn_gear(item_name[13:])
    elif item_name.startswith("License: "):
        gear_kind = item_name.split("License: ")[-1]
        if receive_gear_setting != 0:
            spawn_gear(gear_kind)
    elif item_name.endswith("Candy"):
        spawn_gear(item_name)
    elif item_name in {"Seraph Crystals"}: # any other spawnables
        spawn_gear(item_name)

    # spawn traps
    if item_name.startswith("Trap Spawn: "):
        trigger_spawn_trap(item_name)
    if item_name.startswith("Trap: "):
        trigger_trap(item_name)

    # mission rewards
    if item_name.startswith("Reward: "):
        grant_mission_reward(item_name[8:])

    if item_id == item_name_to_id.get("$100"):
        get_pc().PlayerReplicationInfo.AddCurrencyOnHand(0, 100)
    elif item_id == item_name_to_id.get("10 Eridium") or item_id == item_name_to_id.get('10 Moonstones'):
        get_pc().PlayerReplicationInfo.AddCurrencyOnHand(1, 10)
    elif item_id == item_name_to_id.get("10% Exp"):
        get_pc().ExpEarn(int(get_exp_for_current_level() * 0.1), 0)
    elif item_id == item_name_to_id.get("Override Level 15"):
        get_pc().ExpEarn(get_pc().GetExpPointsRequiredForLevel(15), 0)
    elif item_id == item_name_to_id.get("Override Level 30"):
        get_pc().ExpEarn(get_pc().GetExpPointsRequiredForLevel(30), 0)
    elif item_id == item_name_to_id.get("Max Ammo AssaultRifle"):
        get_pc().IncBlackMarketUpgrade(0)
    elif item_id == item_name_to_id.get("Max Ammo Pistol"):
        get_pc().IncBlackMarketUpgrade(1)
    elif item_id == item_name_to_id.get("Max Ammo RocketLauncher"):
        get_pc().IncBlackMarketUpgrade(2)
    elif item_id == item_name_to_id.get("Max Ammo Shotgun"):
        get_pc().IncBlackMarketUpgrade(3)
    elif item_id == item_name_to_id.get("Max Ammo SMG"):
        get_pc().IncBlackMarketUpgrade(4)
    elif item_id == item_name_to_id.get("Max Ammo SniperRifle"):
        get_pc().IncBlackMarketUpgrade(5)
    elif item_id == item_name_to_id.get("Max Ammo Laser"):
        get_pc().IncBlackMarketUpgrade(9)
    elif item_id == item_name_to_id.get("Max Grenade Count"):
        get_pc().IncBlackMarketUpgrade(6)
    elif item_id == item_name_to_id.get("Backpack Upgrade"):
        get_pc().IncBlackMarketUpgrade(7)
    # elif item_id == item_name_to_id.get("Bank Storage Upgrade"):
    #     get_pc().IncBlackMarketUpgrade(8)
    elif item_name.startswith("Moxxtail: ") and Game.get_current().name == "TPS":
        activate_moxxtail(item_id)
        
    # not init, do write.
    with open(blg.items_filepath, 'a') as f:
        f.write(str(item_id) + "\n")

    return True

def sync_vars_to_player():
    sync_skill_pts()
    sync_weapon_slots()
    blg = get_globals()
    blg.sprint_speed = blg.calc_sprint_speed()
    blg.jump_z = blg.calc_jump_height()

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
    blg = get_globals()
    if not blg.is_archi_connected:
        return
    try:
        done_receiving = False
        offset = 0
        server_items = []
        while not done_receiving:
            blg.sock.sendall(bytes(f"items_all:{offset}", "utf-8"))
            msg = blg.sock.recv(4096)
            msg_strs = msg.decode().split(",")
            msg_list = list(map(int, msg_strs))
            if msg_list[-1] == 0:
                done_receiving = True
                msg_list.pop()
            else:
                offset += len(msg_list)
            server_items.extend(msg_list)

        diff = list_dict_diff(server_items, blg.game_items_received)
        if diff == -1:
            show_chat_message("detected items out of sync or archi client has disconnected.")
            check_is_archi_connected()
            return
        should_play_sound = False
        # loop through new ones
        for item_id in diff:
            did_send = handle_item_received(item_id)
            if did_send:
                should_play_sound = True
        
        if should_play_sound:
            find_and_play_akevent(random.choice(receive_sounds))

        sync_vars_to_player()

    except socket.error as error:
        print(error)
        show_chat_message("pull_items: something went wrong.")
        blg.disconnect_socket()

def pull_locations():
    blg = get_globals()
    if not blg.is_archi_connected:
        return
    try:
        done_receiving = False
        offset = 0
        server_locs = []
        while not done_receiving:
            blg.sock.sendall(bytes(f"locations_all:{offset}", "utf-8"))
            msg = blg.sock.recv(4096)
            msg_strs = msg.decode().split(",")
            if msg_strs[-1] == "0":
                done_receiving = True
                msg_strs.pop()
            else:
                offset += len(msg_strs)
            server_locs.extend(msg_strs)

        locations_set = set(map(int, server_locs))
        # always defer to server's locations_checked
        blg.locations_checked = locations_set
    except socket.error as error:
        print(error)
        show_chat_message("pull_locations: something went wrong.")
        blg.disconnect_socket()

def init_game_items_received():
    blg = get_globals()
    if blg.items_filepath is None:
        print("init_game_items_received: not connected")
        return
    if not os.path.exists(blg.items_filepath):
        print("init_game_items_received: no file exists")
        return
    # reset counters
    blg.reset_item_counters()
    # blg.money_cap = 200
    # blg.weapon_slots = 2
    # blg.skill_points_allowed = 0
    # blg.jump_z = calc_jump_height(blg)
    # blg.sprint_speed = calc_sprint_speed(blg)

    blg.game_items_received = dict()
    # read lines of file into dict
    with open(blg.items_filepath, 'r') as f:
        for line in f:
            item_id = int(line.strip())
            handle_item_received(item_id, True)

def fetch_settings():
    blg = get_globals()
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
        blg.disconnect_socket()


def init_data():
    blg = get_globals()
    fetch_settings()
    seed = blg.settings.get("seed")
    show_chat_message("seed: " + str(seed))
    if not seed:
        show_chat_message("No seed detected!")
        seed = "blah"
    blg.items_filepath = os.path.join(storage_dir, seed + ".items.txt")
    pull_locations()
    blg.should_do_initial_modify = True
    if len(blg.locations_checked) == 0 and not os.path.exists(blg.items_filepath):
        blg.should_do_fresh_character_setup = True
        show_chat_message("detected first conncection")
        print("detected first conncection")
        f = open(blg.items_filepath, "x")
        f.close()
        show_chat_message("items file created at " + blg.items_filepath)
    init_game_items_received()



# checks for archi connection, then initializes
def check_is_archi_connected():
    blg = get_globals()
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
        blg.disconnect_socket()

def connect_to_socket_server(ButtonInfo):
    blg = get_globals()
    # TODO restart loop
    if blg.is_sock_connected:
        blg.disconnect_socket()
    try:
        blg.sock = socket.socket()
        blg.sock.connect(("localhost", socket_port))
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

def send_region(region):
    blg = get_globals()
    if not blg.is_sock_connected:
        return
    try:
        blg.sock.send(bytes("cur_reg:" + region, 'utf8'))
        msg = blg.sock.recv(4096)
        if msg.decode() != "ok":
            print(msg.decode())
    except socket.error as error:
        print(error)
        show_chat_message("send_region: something went wrong.")
        blg.disconnect_socket()

oid_connect_to_socket_server: ButtonOption = ButtonOption(
    "Connect to Socket Server",
    on_press=connect_to_socket_server,
    description="Connect to Socket Server",
)

#this feels like an bad way to do this, should find a hook instead
# mission is given before the items are, same with challenges
# no obvious hook for the initialization hud GFx
def tps_delay_start_delay(blg):
    if blg.settings.get("delete_starting_gear") == 0:
        blg.should_do_fresh_character_setup = False
        return None #dont need to do anything here if the delete starting gear setting is "keep"
    can_show = False
    tick = 0
    print("Awaiting character ready for TPS")
    while not can_show:
        yield WaitForSeconds(0.3)
        tick += 1
        (can_show, bit_value) = get_pc().CanShowModalMenu(0)
    yield WaitForSeconds(0.8)
    print("Done with fresh char for TPS")
    blg.should_do_fresh_character_setup = False
    return None
def watcher_loop(blg):
    while True:
        yield WaitForSeconds(5)
        print("tick " + str(blg.tick_count))
        blg.tick_count += 1
        if not blg.is_archi_connected:
            show_chat_message("client is not connected!")
            check_is_archi_connected()
        pull_items()
        push_locations()
        query_deathlink()

        if not mod_instance.is_enabled or not blg or blg.has_shutdown:
            print("Exiting watcher_loop")
            return None  # Break out of the coroutine

@hook("WillowGame.WillowInventoryManager:AddInventory")
def add_inventory(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    # TODO: maybe doesn't run on receiving quest reward
    # does not trigger on buy back from vending machine
    if obj != get_pc().GetPawnInventoryManager():
        # not player inventory
        return
    if blg.should_do_fresh_character_setup:
        if blg.settings.get("delete_starting_gear") == 1:
            return Block
        return
    try:
        cust_name = args.NewItem.ItemName
        if cust_name.startswith("AP Check: "):
            print("add_inventory: " + cust_name)
            location_name = cust_name.split("AP Check: ")[1]
            blg.locs_to_send.append(loc_name_to_id[location_name])
            push_locations()
            return Block
    except AttributeError:
        pass

    if not blg.is_archi_connected:
        return

    # TODO maybe conditionally check SourceDefinitionName

    loc_id = get_gear_loc_id(args.NewItem)
    if loc_id is None or loc_id in blg.locations_checked:
        return
    blg.locs_to_send.append(loc_id)
    push_locations()


@hook("WillowGame.WillowInventoryManager:OnEquipped")
def on_equipped(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    if not blg.is_archi_connected:
        return
    if obj != get_pc().GetPawnInventoryManager():
        # not player inventory
        return
    if blg.should_do_fresh_character_setup:
        return

    loc_id = get_gear_loc_id(args.Inv)
    if loc_id is None:
        return

    # TODO maybe conditionally check SourceDefinitionName

    if loc_id not in blg.locations_checked:
        blg.locs_to_send.append(loc_id)
        push_locations()

    item_id = get_gear_item_id(args.Inv)
    if can_gear_item_id_be_equipped(item_id):
        # allow equip
        return
    else:
        # block equip (I'm not sure this does anything)
        return Block

@hook("WillowGame.ItemCardGFxObject:SetItemCardEx", Type.POST)
def set_item_card_ex(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if (inv_item := args.InventoryItem) is None:
        return
    
    if inv_item.ItemName.startswith("AP Check:") or inv_item.ItemName.startswith("Black Market:"):
        # removes things like skill and child grenade count
        obj.SetFunStats("")
        # removes bottom icons and sets title color
        if Game.get_current().name == "TPS":
            obj.SetTitle(
                Title=inv_item.ItemName,
                TypeIcon="",
                Rarity=unrealsdk.make_struct("Color", R=0, G=255, B=255, A=255),
                Manufacturer="",
                ElementalIcon="",
                bIsReadied=False,
            )
        else:
            obj.SetColor(Title=inv_item.ItemName, TypeIcon="", newColor=unrealsdk.make_struct("Color", R=0, G=255, B=255, A=255), Manufacturer="", ElementalIcon="", bIsReadied=False,)
        # removes stats in the middle AND "Already Unlocked" on skins
        obj.SetTopStat(StatIndex=0, LabelText="", ValueText="", CompareArrow=0, AuxText="", IconName="")

        obj.setHeight()
        return

    kind = get_gear_kind(inv_item)
    if not can_inv_item_be_equipped(inv_item):
        obj.SetLevelRequirement(True, False, False, f"lvl {inv_item.GameStage}, Can't Equip: {kind}")

    if needs_rarity_check(inv_item):
        obj.SetFunStats(f"<font size='18' color='#FFFF00'>\"{kind} Found\" is unchecked! Pick me up!</font>")

def get_total_skill_pts():
    # unused for now.
    pc = get_pc()
    a = pc.PlayerReplicationInfo.GeneralSkillPoints
    b = pc.PlayerSkillTree.GetSkillPointsSpentInTree()
    return a + b

# TODO: I think this doesn't reset some skills until save-quit (tested with money shot)
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
    blg = get_globals()
    if not blg.is_archi_connected:
        return
    pc = get_pc()
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
    blg = get_globals()
    if not blg.is_archi_connected:
        return
    pc = get_pc()
    inventory_manager = pc.GetPawnInventoryManager()
    if pc and inventory_manager and inventory_manager.SetWeaponReadyMax:
        with prevent_hooking_direct_calls():
            inventory_manager.SetWeaponReadyMax(blg.weapon_slots)
    # TODO: should also potentially unequip weapons in slots 3 and 4

def level_my_gear():
    pc = get_pc()
    # could use pc.GetFullInventory([])
    current_level = pc.PlayerReplicationInfo.ExpLevel
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
        try:
            # skip skyrocket, it gets deleted for some reason
            if item.DefinitionData.ItemDefinition.Name == "GrenadeMod_SkyRocket":
                continue
        except:
            pass
        item.DefinitionData.ManufacturerGradeIndex = current_level
        item.DefinitionData.GameStage = current_level
        with prevent_hooking_direct_calls():
            item.InitializeFromDefinitionData(item.DefinitionData, None)

        # item.ExpLevel = current_level
        # item.GameStage = current_level


    # go through item chain (relic, classmod, grenade, shield)
    item = inventory_manager.ItemChain
    while item:
        # skip skyrocket, it gets deleted for some reason
        if item.DefinitionData.ItemDefinition.Name != "GrenadeMod_SkyRocket":
            item.DefinitionData.ManufacturerGradeIndex = current_level
            item.DefinitionData.GameStage = current_level
            with prevent_hooking_direct_calls():
                item.InitializeFromDefinitionData(item.DefinitionData, None)
        item = item.Inventory

    # go through equipment slots
    for i in [1, 2, 3, 4]:
        weapon = inventory_manager.GetWeaponInSlot(i)
        if weapon:
            weapon.DefinitionData.ManufacturerGradeIndex = current_level
            weapon.DefinitionData.GameStage = current_level
            with prevent_hooking_direct_calls():
                weapon.InitializeFromDefinitionData(weapon.DefinitionData, None)

    show_chat_message("gear set to level " + str(current_level))
    return

def print_items_received(ButtonInfo):
    blg = get_globals()
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
    blg = get_globals()
    # this can result in an overfull inventory, which really doesn't bother the game.
    if not blg.is_archi_connected:
        return
    pc = get_pc()
    if pc.Pawn is None:
        return
    inventory_manager = pc.GetPawnInventoryManager()
    # go through item chain (relic, classmod, grenade, shield)
    items_to_uneq = []
    item = inventory_manager.ItemChain
    while item:
        if not can_inv_item_be_equipped(item):
            show_chat_message("can't equip: " + get_gear_kind(item))
            items_to_uneq.append(item)
        item = item.Inventory
    for i in items_to_uneq:
        inventory_manager.InventoryUnreadied(i, True)
    # equipment slots
    for i in [1, 2, 3, 4]:
        weapon = inventory_manager.GetWeaponInSlot(i)
        if weapon and not can_inv_item_be_equipped(weapon):
            show_chat_message("can't equip: " + get_gear_kind(weapon))
            inventory_manager.InventoryUnreadied(weapon, True)

def check_full_inventory():
    blg = get_globals()
    if not blg.is_archi_connected:
        return

    if blg.should_do_fresh_character_setup:
        return

    pc = get_pc()
    inventory_manager = pc.GetPawnInventoryManager()
    # could use pc.GetFullInventory([])

    if not inventory_manager:
        print('no inventory, skipping')
        return

    backpack = inventory_manager.Backpack
    if not backpack:
        print('no backpack loaded')
        return
    # go through backpack
    for inv_item in backpack:
        loc_id = get_gear_loc_id(inv_item)
        if loc_id is not None and loc_id not in blg.locations_checked:
            blg.locs_to_send.append(loc_id)
    push_locations()
    unequip_invalid_inventory()

def delete_gear():
    show_chat_message("deleting gear")
    pc = get_pc()
    inventory_manager = pc.GetPawnInventoryManager()
    items = []
    item = inventory_manager.ItemChain
    # TODO might need with prevent_hooking_direct_calls for InventoryUnreadied calls
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

    # TODO: maybe avoid deleting mission items or starting echo
    inventory_manager.Backpack = []
    inventory_manager.ServerUpdateBackpackInventoryCount(0)

def on_enable():
    init_globals()
    connect_to_socket_server(None) #try to connect
    modify_map_area(None, None, None, None) # trigger "move" to current area

    # trying this in our own thread for now. if this causes problems, probably move to player tick or something else
    # stackoverflow.com/questions/59645272
    # thread = threading.Thread(target=asyncio.run, args=(watcher_loop(),))
    # thread.start()
    # threading definitely causing problems, switching to use juso's coroutines
    blg = get_globals()
    start_coroutine_tick(watcher_loop(blg))

def on_disable():
    print("blg disable!")
    try:
        get_globals().disconnect_socket()
    except:
        pass


def get_current_map():
    if ENGINE and ENGINE.GetCurrentWorldInfo:
        wi = ENGINE.GetCurrentWorldInfo()
        if wi and wi.GetMapName:
            return str(wi.GetMapName()).casefold()
    return "none"

fake_maps = ("none", "loader", "fakeentry", "fakeentry_p", "menumap")
@hook("WillowGame.WillowPlayerController:ClientSetPawnLocation")
def modify_map_area(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # TODO: this is potentially the wrong hook. it runs on twice on death, and potentially other times.
    blg = get_globals()
    new_map_area = get_current_map()
    print("modify_map_area " + new_map_area)
    if new_map_area in fake_maps:
        print("skipping map area: " + new_map_area)
        return

    # run initial setup on character
    if blg.should_do_fresh_character_setup:
        print("performing fresh character setup")
        # remove starting inv
        if blg.settings.get("delete_starting_gear") == 1:
            delete_gear()
        if Game.get_current().name == "TPS": #TPS is not done yet
            #we need to wait a bit more once this swaps to true
            start_coroutine_tick(tps_delay_start_delay(blg))
        else:
            blg.should_do_fresh_character_setup = False

    # run other first load setup
    if blg.should_do_initial_modify:
        print("performing initial modify")
        # still requires a save-quit
        reveal_annoying_challenges()

    if new_map_area != blg.current_map:
        # when we change map location...
        check_full_inventory()
        map_name = map_area_to_name.get(new_map_area)
        send_region(map_name)
        if not map_name:
            show_chat_message("Missing map name, please report issue: " + new_map_area)
            map_name = new_map_area # override with internal name
        if blg.settings.get("entrance_locks", 0) != 0:
            warning_areas = get_entrance_lock_warnings(map_name)
            if len(warning_areas) > 0:
                show_chat_message("Warning! Areas still locked: " + ", ".join(warning_areas))

        show_chat_message("Moved to map: " + map_name)
        blg.current_map = new_map_area
        sync_vars_to_player()
        if new_map_area in map_modifications:
            mod_func = map_modifications[new_map_area]
            mod_func()
        setup_generic_mob_drops()
        
        if not blg.traps_initalized:
            init_traps()
            blg.traps_initalized = True

@hook("WillowGame.WillowPlayerPawn:DoJump")
def do_jump(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if oid_jump_z_override.value != 0: # for debug, remove me later
        obj.JumpZ = oid_jump_z_override.value
        return

    blg = get_globals()
    obj.JumpZ = blg.jump_z * (oid_jump_z_downscale.value / 100)
    # if not blg.has_item("Progressive Jump"):
    #     show_chat_message("jump disabled!")
    #     return Block

@hook("WillowGame.WillowPlayerPawn:DoSprint")
def sprint_pressed(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if oid_sprint_override.value != 0: # for debug, remove me later
        obj.SprintingPct = oid_sprint_override.value
        return

    blg = get_globals()
    obj.SprintingPct = blg.sprint_speed * (oid_sprint_downscale.value / 100)
    # if not blg.has_item("Sprint"):
    #     show_chat_message("sprint disabled!")
    #     return Block

@hook("WillowGame.WillowPlayerInput:DuckPressed")
def duck_pressed(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    for pickup in get_pc().GetWillowGlobals().PickupList:
        if pickup.Inventory.ItemName.startswith("AP Check:"):
            print("moving:" + pickup.Inventory.ItemName)
            pickup.Location = get_loc_in_front_of_player(150, 50)
            pickup.AdjustPickupPhysicsAndCollisionForBeingDropped()
    # get_pc().PlayerReplicationInfo.AddCurrencyOnHand(1, 100)
    # print(get_pc().PlayerClass.Name)
    # spawn_gear("Seraph Crystals")
    # spawn_gear("VeryRare SMG")
    # spawn_gear("Legendary RocketLauncher")
    # spawn_gear("Unique Pistol")
    # spawn_gear("Seraph Crystals")
    # spawn_gear("Unique RocketLauncher")
    # spawn_gear("YellowCandy")
    # spawn_gear("The Sham")
    # spawn_gear("Common Shield")

    # popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_SarcasticSlab.Balance.PopDef_SarcasticSlab:PopulationFactoryBalancedAIPawn_0")
    # spawn_at_dist(popfactory, dist=1000)
    # spawn_at_dist(popfactory, dist=-1000)

    # gameinfo = unrealsdk.find_all("WillowCoopGameInfo")[-1]
    # gameinfo.TravelToStation(unrealsdk.find_object("FastTravelStationDefinition", "GD_FastTravelStations.Zone2.Grass_A"))
    # loc = get_loc_in_front_of_player(100, -50)
    # print(loc)
    # place_mesh_object(
    #     -8283, -2775, -2438,
    #     "Orchid_Caves_P.TheWorld:PersistentLevel.StaticMeshCollectionActor_9",
    #     "Prop_Furniture.Chair",
    #     0, 0, 14000
    # )
    blg = get_globals()
    if not blg.has_item("Crouch"):
        show_chat_message("crouch disabled!")
        return Block

@hook("WillowGame.WillowVehicleWeapon:BeginFire")
def vehicle_begin_fire(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    if blg.current_map == "southernshelf_p": # allow use of big bertha
        return True

    if not blg.has_item("Vehicle Fire") and obj.MyVehicle:
        if obj.MyVehicle.PlayerReplicationInfo is not None or obj.MyVehicle.Instigator.Class.Name == "WillowPlayerPawn":
            show_chat_message("vehicle fire disabled!")
            return Block


# @hook("WillowGame.WillowPlayerController:ServerGrantMissionRewards")

@hook("WillowGame.WillowPlayerController:ServerCompleteMission")
def complete_mission(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    # print(args.Mission)
    if blg.settings.get("quest_reward_items", 0) != 0:
        # quest rewards are in the multiworld, replace with empty here
        empty_reward = unrealsdk.make_struct("RewardData",
            ExperienceRewardPercentage=args.Mission.Reward.ExperienceRewardPercentage,
        )
        blg.temp_reward = (
            unrealsdk.make_struct("RewardData",
                ExperienceRewardPercentage=args.Mission.Reward.ExperienceRewardPercentage,
                CurrencyRewardType=args.Mission.Reward.CurrencyRewardType,
                CreditRewardMultiplier=args.Mission.Reward.CreditRewardMultiplier,
                OtherCurrencyReward=args.Mission.Reward.OtherCurrencyReward,
                RewardItems=args.Mission.Reward.RewardItems,
                RewardItemPools=args.Mission.Reward.RewardItemPools,
            ),
            unrealsdk.make_struct("RewardData",
                ExperienceRewardPercentage=args.Mission.AlternativeReward.ExperienceRewardPercentage,
                CurrencyRewardType=args.Mission.AlternativeReward.CurrencyRewardType,
                CreditRewardMultiplier=args.Mission.AlternativeReward.CreditRewardMultiplier,
                OtherCurrencyReward=args.Mission.AlternativeReward.OtherCurrencyReward,
                RewardItems=args.Mission.AlternativeReward.RewardItems,
                RewardItemPools=args.Mission.AlternativeReward.RewardItemPools,
            ),
        )
        args.Mission.Reward = empty_reward
        args.Mission.AlternativeReward = empty_reward

    # send quest completion 
    if blg.settings.get("quest_completion_checks", 0) != 0:
        loc_name = "Quest: " + mission_ue_str_to_name.get(args.Mission.Name, "")
        loc_id = loc_name_to_id.get(loc_name)
        if loc_id is None:
            print("unknown quest: " + args.Mission.Name + " " + loc_name)
            show_chat_message("unknown quest")
            return

        if loc_id in blg.locations_checked:
            return

        blg.locs_to_send.append(loc_id)
        push_locations()


@hook("WillowGame.WillowPlayerController:ServerCompleteMission", Type.POST)
def post_complete_mission(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    if blg.settings.get("quest_reward_items", 0) != 0:
        # reset quest reward
        args.Mission.Reward = blg.temp_reward[0]
        args.Mission.AlternativeReward = blg.temp_reward[1]
        blg.temp_reward = None

# just to detect Talon of God, which doesn't call ServerCompleteMission
@hook("WillowGame.Behavior_CompleteMission:ApplyBehaviorToContext")
def behavior_complete_mission(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    pn = obj.PathName(obj)
    if pn == "GD_Episode17.M_Ep17_KillJack:Behavior_CompleteMission_62":
        if blg.settings.get("quest_completion_checks", 0) != 0:
            loc_name = "Quest: The Talon of God"
            loc_id = loc_name_to_id.get(loc_name)
            blg.locs_to_send.append(loc_id)
            push_locations()

@hook("WillowGame.WillowInventoryManager:AddInventoryToBackpack", Type.POST)
def post_add_to_backpack(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # print(f"add to backpack {args}")
    # receiving items from quests
    if obj != get_pc().GetPawnInventoryManager():
        # not player inventory
        return
    blg = get_globals()
    if blg.should_do_fresh_character_setup:
        return

    if not blg.is_archi_connected:
        return

    # TODO maybe conditionally check SourceDefinitionName

    loc_id = get_gear_loc_id(args.Inv)
    if loc_id is None or loc_id in blg.locations_checked:
        return
    blg.locs_to_send.append(loc_id)
    push_locations()

@hook("WillowGame.WillowInventoryManager:AddInventory", Type.POST)
def post_add_inventory(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if obj != get_pc().GetPawnInventoryManager():
        # not player inventory
        return
    blg = get_globals()
    # does not trigger when selling at a vending machine.
    # probably does not trigger on quest completion with no item
    # TODO: maybe doesn't run on receiving quest reward
    # TODO: actually check if the picked up item was currency.
    if get_pc().PlayerReplicationInfo.GetCurrencyOnHand(0) > blg.money_cap:
        show_chat_message("money cap: " + str(blg.money_cap))
        get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, blg.money_cap)

    if blg.should_do_fresh_character_setup:
        return
    # also run unequip on this hook
    unequip_invalid_inventory()


@hook("WillowGame.WillowPlayerReplicationInfo:AddCurrencyOnHand", Type.POST)
def on_currency_changed(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # happens at vending machine, on quest completion, after respec
    blg = get_globals()
    if get_pc().PlayerReplicationInfo.GetCurrencyOnHand(0) > blg.money_cap:
        show_chat_message("money cap: " + str(blg.money_cap))
        get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, blg.money_cap)

@hook("WillowGame.WillowPlayerController:VerifySkillRespec_Clicked", Type.POST)
def post_verify_skill_respec(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    sync_skill_pts()

@hook("WillowGame.WillowPlayerController:ExpLevelUp", Type.POST)
def leveled_up(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    sync_skill_pts()
    level = get_pc().PlayerReplicationInfo.ExpLevel
    # print("level")
    # print(loc_name_to_id["Level " + str(level)])
    level_key = "Level " + str(level) + " Reached"
    loc_id = loc_name_to_id.get(level_key)
    if loc_id:
        blg.locs_to_send.append(loc_id)
        push_locations()

@hook("WillowGame.WillowInventoryManager:SetWeaponReadyMax")
def set_weapon_ready_max(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    return Block

@hook("WillowGame.WillowPlayerController:Behavior_Melee")
def behavior_melee(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    if not blg.has_item("Melee"):
        show_chat_message("melee disabled!")
        return Block
    # TODO: Krieg's action skill is not disabled (maybe that's ok?)

@hook("WillowGame.WillowPlayerPawn:SetupPlayerInjuredState")
def enter_ffyl(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    send_setting = blg.settings.get("death_link_send_mode")
    if send_setting == 1 or send_setting == 4:
        send_deathlink()

    print("enter_ffyl")

def send_deathlink():
    blg = get_globals()
    if not blg.is_archi_connected:
        return
    if datetime.datetime.now() < blg.deathlink_timestamp:
        print("too soon, skipping deathlink")
        return
    try:
        blg.sock.sendall(bytes("died", "utf-8"))
        msg = blg.sock.recv(4096)
        print(msg)
    except socket.error as error:
        print(error)
        show_chat_message("send_deathlink: something went wrong.")
        blg.disconnect_socket()

def query_deathlink():
    blg = get_globals()
    if not blg.is_archi_connected:
        return
    if not blg.settings.get("death_link"):
        return
    if not blg.death_receive_pending:
        try:
            blg.sock.sendall(bytes("deathlink", "utf-8"))
            msg = blg.sock.recv(4096)
            if msg.decode() == "yes":
                blg.death_receive_pending = True
            # print(msg)
        except socket.error as error:
            print(error)
            show_chat_message("send_deathlink: something went wrong.")
            blg.disconnect_socket()

    if blg.death_receive_pending: # try propagate death
        if get_current_map() in fake_maps:
            return
        pc = get_pc()
        if not pc or not pc.Pawn:
            return
        blg.death_receive_pending = False
        blg.deathlink_timestamp = datetime.datetime.now() + datetime.timedelta(seconds=30)
        show_chat_message("Deathlink Received.")
        punishment_setting = blg.settings.get("death_link_punishment", 0)
        if punishment_setting == 0:
            pc.Pawn.SetHealth(2)
            pc.Pawn.SetShieldStrength(0)
            pc.TakeDamage(1, None, unrealsdk.make_struct("Vector", X=0, Y=0, Z=0), unrealsdk.make_struct("Vector", X=0, Y=0, Z=0), None)
        elif punishment_setting == 1:
            pc.Pawn.SetHealth(1)
            pc.Pawn.SetShieldStrength(0)
            pc.TakeDamage(1, None, unrealsdk.make_struct("Vector", X=0, Y=0, Z=0), unrealsdk.make_struct("Vector", X=0, Y=0, Z=0), None)
        elif punishment_setting == 2:
            pc.ServerResurrect()

@hook("WillowGame.WillowPlayerPawn:StartInjuredDeathSequence")
def died(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # TODO: how does this interact with co-op?
    blg = get_globals()
    print("player died")
    send_setting = blg.settings.get("death_link_send_mode")
    if send_setting == 0 or send_setting == 3:
        send_deathlink()

def test_btn(ButtonInfo):
    package = unrealsdk.construct_object("Package", None, "Test", flags=ObjectFlags.KEEP_ALIVE)
    test_def = unrealsdk.construct_object("FastTravelStationDefinition", package, "Luckys_FastTravel")
    test_def.StationDisplayName = "Claptrap's Place"
    test_def.StationLevelName = "Glacial_P"
    willow_globals = unrealsdk.find_class("WillowGlobals").ClassDefaultObject.GetWillowGlobals()
    travels_lookup = willow_globals.GetFastTravelStationsLookup()
    travels_lookup.FastTravelStationLookupList.append(test_def)
    get_pc().RegisterStationForPlayer(test_def, None, None)
    print(travels_lookup.FastTravelStationLookupList)
    # doesn't save to player


    # blg = get_globals()
    # show_chat_message("hello test " + str(mod_version))
    # print("\nlocations_checked")
    # print(blg.locations_checked)
    # print("\nsettings")
    # print(blg.settings)
    # print("\nfilepaths")
    # show_chat_message("is_archi_connected: " + str(blg.is_archi_connected) + " is_sock_connected: " + str(blg.is_sock_connected))

    # dist = 0
    # for pool_name in gear_kinds.keys():
    #     spawn_gear(pool_name, dist, dist)
    #     dist += 50

    # get_pc().ExpEarn(1000, 0)
    # get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, 999999)

oid_test_btn: ButtonOption = ButtonOption(
    "Test Btn",
    on_press=test_btn,
    description="Test Btn",
)

oid_collision: SpinnerOption = SpinnerOption(
    "Disable Loot Collision",
    "AP Spawned",
    ["Never", "AP Spawned", "Always"],
    True,
    description=("Turns off loot collision, avoiding the massive spray of loot when multiple items are spawned."
                "\nAP Spawned = Only for items granted from Archipelago"
    ),
)

def resend_all(ButtonInfo):
    blg = get_globals()
    show_chat_message("resending all items...")
    print(f"clearing {blg.items_filepath}")
    # clear out .items.txt
    with open(blg.items_filepath, 'w') as f:
        f.truncate(0)
    # attempt to re-receive them
    init_game_items_received()
    pull_items()

oid_resend_all: ButtonOption = ButtonOption(
    "Resend All Items",
    on_press=resend_all,
    description="Attempt to re-receive all items for this seed",
)

def resend_last_3(ButtonInfo):
    blg = get_globals()
    show_chat_message("resending last 3 items...")
    # remove last 3 lines
    with open(blg.items_filepath, 'rb+') as f:
        f.seek(0, os.SEEK_END)
        end_pos = f.tell()
        count = 0
        
        # Scan backward for newline characters
        while f.tell() > 0 and count <= 3:
            f.seek(-1, os.SEEK_CUR)
            char = f.read(1)
            if char == b'\n':
                count += 1
                if count == 3 + 1:
                    # Found the position just after the 4th newline from end
                    f.truncate()
                    break
            f.seek(-1, os.SEEK_CUR)
            
        # If the file had fewer than 3 lines, empty it
        if count <= 3:
            f.seek(0)
            f.truncate()
    # attempt to re-receive them
    init_game_items_received()
    pull_items()

oid_resend_last_3: ButtonOption = ButtonOption(
    "Resend Last 3 Items",
    on_press=resend_last_3,
    description="Attempt to re-receive the last 3 items received for this seed.",
)

@hook("WillowGame.Behavior_DiscoverLevelChallengeObject:ApplyBehaviorToContext")
def discover_level_challenge_object(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # if blg.settings.get("vault_symbols", 0) == 0:
    #     return

    # obj_id = str(args.ContextObject)
    # check_name = vault_symbol_pathname_to_name.get(obj_id)
    blg = get_globals()
    pathname = args.ContextObject.PathName(args.ContextObject)
    check_name = vault_symbol_pathname_to_name.get(pathname)

    loc_id = loc_name_to_id.get(check_name)
    if loc_id is None:
        if check_name is not None:
            show_chat_message("Vault Symbol failed id lookup on: " + check_name + "  " + pathname)
        return
    if loc_id not in blg.locations_checked:
        blg.locs_to_send.append(loc_id)
        push_locations()

@hook("WillowGame.Behavior_SpawnItems:ApplyBehaviorToContext")
def bunker_warrior_spawn_items(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    pathname = obj.PathName(obj)
    loc_id = None
    if pathname == "GD_FinalBoss.Character.AIDef_FinalBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_15":
        check_name = "Enemy: Warrior"
        loc_id = loc_name_to_id.get(check_name)
    elif pathname == "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_17":
        check_name = "Enemy: BNK-3R"
        loc_id = loc_name_to_id.get(check_name)

    if loc_id is None:
        return

    blg = get_globals()
    if loc_id not in blg.locations_checked and loc_id not in blg.locs_to_send:
        blg.locs_to_send.append(loc_id)
        push_locations()


@hook("WillowGame.PauseGFxMovie:CompleteQuitToMenu")
def complete_quit_to_menu(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    blg.current_map = "" # reset, now loading into map will trigger changing areas
    print("complete_quit_to_menu")
    send_setting = blg.settings.get("death_link_send_mode")
    if send_setting == 2 or send_setting == 3 or send_setting == 4:
        send_deathlink()

@hook("WillowGame.WillowPlayerController:ClientSetCurrentMapFullyExplored")
def set_current_map_fully_explored(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    log_line = "Map Fully Explored: " + blg.current_map
    print(log_line)

@hook("WillowGame.WillowGameInfo:InitiateTravel")
def initiate_travel(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # check for setting
    # print("InitiateTravel")
    blg = get_globals()
    station_name = args.StationDefinition.Name
    req_areas = entrance_to_req_areas.get(station_name)
    if blg.settings.get("entrance_locks", 0) == 0:
        return

    if req_areas is None:
        print("unknown travel station: " + station_name)
        return
    if len(req_areas) == 0:
        print("travel has no requirements: " + station_name)
        return

    req_areas_not_met = []
    for area_name in req_areas:
        if not can_travel_to_region(area_name):
            req_areas_not_met.append(area_name)

    if len(req_areas_not_met) == 0:
        # requirement met
        return

    for a in req_areas_not_met:
        show_chat_message(f"Travel locked, Need: {get_travel_req_string(a)}")

    print(station_name)
    return Block

# @hook("WillowGame.LevelTravelStation:GetDestinationMapName")
# def get_destination_map_name(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
#     pass
    # print("get_destination_map_name")
    # print(self)
    # print(args)
    # return Block, "ASDFasdf"

# @hook("WillowGame.WillowInteractiveObject:InitializeFromDefinition")
# def initialize_from_definition(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
#     if self.Class.Name != "WillowVendingMachine":
#         return
#     print("vending machine init")


# WillowGame.WillowItem:RemoveFromShop

# @hook("WillowGame.WillowPlayerController:PerformedUseAction")
# def performed_use_action(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
#     print("performed use action")
#     print(obj)
#     print(args)


# WillowGame.WillowVendingMachine:PlayerBuyItem and bWasItemOfTheDay

# WillowGame.PlayerSkillTree:UpgradeSkill


@hook("WillowGame.WillowPlayerController:GFxMenuClosed")
def gfx_menu_closed(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    if blg.active_vend is not None:
        blg.active_vend.FixedFeaturedItemCost = blg.active_vend_price
        blg.active_vend = None

# TODO: move into enemies.py
@hook("WillowGame.WillowAIPawn:Died")
def on_killed_enemy(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    loc_name = ""
    if obj.AIClass:
        enemy_key = obj.AIClass.Name
        loc_name = enemy_class_to_loc_name.get(enemy_key)

    if not loc_name:
        # use pawn balance def
        enemy_key = getattr(obj.BalanceDefinitionState.BalanceDefinition, "Name", "")
        loc_name = enemy_class_to_loc_name.get(enemy_key)
        if isinstance(loc_name, dict):
            # use dict lookup for GOD-liath and Omnd-Omnd-Ohk
            loc_name = loc_name.get(obj.GetTransformedName(), None)

    if not loc_name:
        # still nothing, it's not in the dictionary.
        # print("unnamed enemy")
        # print(obj.AIClass.Name)
        # print(obj.GetTransformedName())
        # print(obj.BalanceDefinitionState.BalanceDefinition.Name)
        return

    blg = get_globals()
    loc_id = loc_name_to_id[loc_name]
    blg.locs_to_send.append(loc_id)
    push_locations()

@hook("WillowGame.WillowPlayerController:ServerCompleteChallenge")
def on_challenge_complete(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    if blg.settings.get("challenge_checks", 0) == 0:
        # TODO: challenge could be included in include_locations with the challenge_checks setting off
        return
    pn = args.ChalDef.PathName(args.ChalDef)
    loc_name = challenge_dict.get(pn)
    if not loc_name:
        print("unknown challenge: " + pn)
        return
    loc_id = loc_name_to_id.get(loc_name)
    if loc_id in blg.locations_checked:
        return
    blg.locs_to_send.append(loc_id)
    push_locations()

# WillowGame.Default__Behavior_SetChallengeCompleted

# WillowGame.ItemOfTheDayPanelGFxObject:SetItemOfTheDayItem

def get_chest_pos_str(obj):
    # old way: f"{str(wvm.Outer)}~{str(wvm.Location.X)},{str(wvm.Location.Y)}"
    map_area = get_current_map()
    return f"{map_area}~{int(obj.Location.X)},{int(obj.Location.Y)}"


@hook("WillowGame.WillowInteractiveObject:UseObject")
def use_chest(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    if blg.settings.get("chest_checks", 0) == 0:
        # TODO: chest could be included in include_locations with the chest_checks setting off
        return
    pos_str = get_chest_pos_str(obj)
    loc_name = chest_dict.get(pos_str)
    if loc_name is None:
        # print(obj.InteractiveObjectDefinition)
        # log_to_file("unknown chest: " + pos_str)
        return
    check_chest_type = blg.settings.get("chest_type_checks") #list of prefixes for chests, TPS has "Chest ", "Red Chest " and "MoonChest " 
    if check_chest_type is not None:
        if not any(loc_name.startswith(prefix) for prefix in check_chest_type):
            return  # chest type is excluded, don't send it
    loc_id = loc_name_to_id.get(loc_name)
    if not loc_id:
        print("Failed id lookup: " + str(loc_name))
        return
    if loc_id in blg.locations_checked:
        return
    blg.locs_to_send.append(loc_id)
    push_locations()


bm_price = 50

@hook("WillowGame.WillowVendingMachineBlackMarket:GetSellingPriceForInventory")
def black_market_get_price(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if args.InventoryForSale.DefinitionData.ItemDefinition.Name == "INV_SDU_Bank":
        return
    return Block, bm_price

if Game.get_current().name == "TPS":
    bm_purchasables = [
        ("Shield Package", "Prop_Co_ShiftItems.Meshes.Paint", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"),
        ("Class Mod Package", "Prop_Co_ShiftItems.Meshes.Co_ShiftItems_BoxofGears", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"),
        ("Grenade Mod Package", "Prop_Co_ShiftItems.Meshes.Shift_Candy", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"),
        ("Oz Kit Package", "Prop_Co_Oxygencanister.Mesh.Co_Oxygencanister", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"),
        ("Glitch Package", "Prop_Co_ShiftItems.Meshes.Co_DahlShift_SatellitePhone", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"),
        ("Laser Package", "Prop_Details.Meshes.GiftBow", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"),
        ("RocketLauncher Package", "Prop_Details.Meshes.BeerBottle", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"), #TODO: Replace with moonstone loot when implemented as filler
        ("Money", "Prop_Details.Meshes.Crumpets", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"),
    ]
else:
    bm_purchasables = [
        ("E-Tech Package", "prop_lightfixtures.Meshes.WallLight_02", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
        ("Shield Package", "Prop_Tires.RubberTire", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
        ("Class Mod Package", "Prop_Signs_02.Meshes.SanctuaryClaptrap", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
        ("Grenade Mod Package", "Prop_Papers.Meshes.CrumpledPaper", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
        # ("Tina COM Package", "Prop_Details.Meshes.Radio", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
        ("Gemstone Package", "Prop_Details.Books", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
        ("Seraph Crystals", "Prop_Bank.Meshes.Vault", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
        ("Money", "Prop_Pickups.Meshes.Money_02", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
    ]

def change_bm_inventory(bmvm):
    if bmvm is None:
        return
    pc = get_pc()
    blg = get_globals()
    item_mesh_details = blg.vending_item_mesh or ApItemMesh(
        item_definition="GD_Assassin_Items_Aster.Assassin.Head_ZeroAster",
        mesh="Prop_Details.Meshes.PizzaBoxWhole",
        material="Prop_Details.Materials.Mati_PizzaBox",
        package="SanctuaryAir_Dynamic"
    )
    sample_def = unrealsdk.find_object("UsableCustomizationItemDefinition", item_mesh_details.item_definition)
    def setup_item(item, purchasable_data):
        blg = get_globals()
        name = purchasable_data[0] if purchasable_data else "Blank"
        mesh = unrealsdk.find_object("StaticMesh", purchasable_data[1] if purchasable_data else item_mesh_details.mesh)
        mat = unrealsdk.find_object("MaterialInstanceConstant", purchasable_data[2] if purchasable_data else item_mesh_details.material)

        item_def_name = f"archi_bm_def_{name.replace(' ', '_').replace(':', '')}"
        item_def = unrealsdk.construct_object("UsableCustomizationItemDefinition", blg.package, item_def_name, 0, sample_def)
        item_def.OverrideMaterial = mat
        item_def.NonCompositeStaticMesh = mesh
        item_def.ItemName = f"Black Market: {name}"
        item_def.CustomPresentations = []
        item_def.bPlayerUseItemOnPickup = True 
        item_def.bIsConsumable = True
        item_def.BaseRarity.BaseValueConstant = 500.0 
        item_def.UIMeshRotation = unrealsdk.make_struct("Rotator", Pitch = -134, Yaw = -14219, Roll = -7164)
        item_def.FormOfCurrency = 1 # unrealsdk.find_enum("ECurrencyType")["CURRENCY_Eridium"]
        
        item.InitializeFromDefinitionData(
            unrealsdk.make_struct("ItemDefinitionData", ItemDefinition=item_def),
            None
        )

    inv_list = bmvm.GetInventoryList([], pc)
    inv_items = inv_list[1]
    i = 0
    for inv in inv_items:
        if inv.Item.DefinitionData.ItemDefinition.Name == "INV_SDU_Bank":
            continue
        purchasable_data = bm_purchasables[i] if i < len(bm_purchasables) else None
        i += 1
        setup_item(inv.Item, purchasable_data)

    featured = bmvm.GetFeaturedItem(pc)
    if featured and featured.Item:
        if Game.get_current().name == "TPS":
            setup_item(featured.Item, ("Level My Gear", "Prop_Details.Meshes.PizzaBoxWhole", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"))
        else:
            setup_item(featured.Item, ("Level My Gear", "Prop_Pickups.Meshes.EridiumContainer", "Prop_Pickups.Materials.Eridium_Pickups_Bar"))
        


@hook("WillowGame.BlackMarketDefinition:CurrentLevelIsBelowMaxForPlayer")
def current_level_is_below_max(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # make black market items always appear
    # TODO this should probably not override for bank sdu
    return Block, True

@hook("WillowGame.WillowVendingMachineBase:ResetInventory")
def reset_black_market(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if obj.Class.Name != "WillowVendingMachineBlackMarket":
        return
    change_bm_inventory(obj)


@hook("WillowGame.WillowInteractiveObject:UseObject")
def use_black_market(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if obj.Class.Name != "WillowVendingMachineBlackMarket":
        return

    # get_pc().WorldInfo.GRI.MissionTracker.UpdateObjective(unrealsdk.find_object("MissionObjectiveDefinition", "GD_Episode04.M_Ep4_WelcomeToSanctuary:BuyFuelCell"))
    change_bm_inventory(obj)

@hook("WillowGame.WillowVendingMachineBlackMarket:PlayerBuyItem")
def black_market_buy_item(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    pc = get_pc()
    blg = get_globals()

    bought_item = args.Item
    name = bought_item.ItemName
    if not name.startswith("Black Market: "):
        return

    # take money, hook does not trigger if can't afford
    pc.PlayerReplicationInfo.AddCurrencyOnHand(1, -bm_price)

    name = name.split("Black Market: ")[-1]


    show_chat_message(f"Purchased {name}!")
    spawns = []
    if name == "E-Tech Package":
        spawns = random.sample(["E-Tech Relic", "E-Tech Pistol", "E-Tech Shotgun", "E-Tech SMG", "E-Tech SniperRifle", "E-Tech AssaultRifle", "E-Tech RocketLauncher"], 3)
    elif name == "Shield Package":
        spawns = ["Legendary Shield", "VeryRare Shield", "Unique Shield"]
    elif name == "Class Mod Package":
        spawns = ["Legendary ClassMod", "Rare ClassMod", "VeryRare ClassMod"]
    elif name == "Grenade Mod Package":
        spawns = ["Legendary GrenadeMod", "Seraph GrenadeMod", "VeryRare GrenadeMod"]
    elif name == "Money":
        pc.PlayerReplicationInfo.AddCurrencyOnHand(0, blg.money_cap)
    elif name == "Seraph Crystals":
        spawns = ["Seraph Crystals"] * 80
        # pc.PlayerReplicationInfo.AddCurrencyOnHand(2, 80)
    elif name == "Gemstone Package":
        spawns = random.sample(["Gemstone Pistol", "Gemstone Shotgun", "Gemstone SMG", "Gemstone SniperRifle", "Gemstone AssaultRifle" ], 3)
    elif name == "Glitch Package":
        spawns = random.sample(["Glitch Pistol", "Glitch Laser", "Glitch Shotgun", "Glitch SMG", "Glitch SniperRifle", "Glitch AssaultRifle", "Glitch RocketLauncher"], 3)
    elif name == "RocketLauncher Package":
        spawns = ["Legendary RocketLauncher", "Rare RocketLauncher", "VeryRare RocketLauncher"]
    elif name == "Laser Package":
        spawns = ["Legendary Laser", "Rare Laser", "VeryRare Laser"]
    elif name == "Oz Kit Package":
        spawns = ["Legendary Oz Kit", "Rare Oz Kit", "VeryRare Oz Kit"]
    elif name == "Level My Gear":
        level_my_gear()
    else:
        show_chat_message("Option not implemented")
        pc.PlayerReplicationInfo.AddCurrencyOnHand(1, bm_price)
        print(f"unknown black market purchase: {name}")

    # pc.PlayerReplicationInfo.AddCurrencyOnHand(4, 33) # torgue tokens
    if Game.get_current().name == "TPS":
        spawn_loc = {"X": obj.Location.X-600, "Y": obj.Location.Y - 600, "Z": obj.Location.Z + 500}
    else:
        spawn_loc = {"X": obj.Location.X, "Y": obj.Location.Y - 1000, "Z": obj.Location.Z + 500}
    for s in spawns:
        spawn_loc["X"] += 20
        spawn_gear(s, override_loc=spawn_loc)

    # for the Whaddaya Buyin challenge and Plan B mission
    player_stats_list = unrealsdk.find_all("WillowGame.WillowPlayerStats") # coop host will see other player's in this list.
    my_stats = next((x for x in player_stats_list if x.Owner == pc), player_stats_list[-1])
    my_stats.IncrementIntStat("STAT_PLAYER_NUM_BLACK_MARKET_ITEMS_PURCHASED", 1)
    my_stats.IncrementIntStat("STAT_PLAYER_INVENTORY_PURCHASED_WITH_ERIDIUM", 1)
    if Game.get_current().name == "TPS":
        get_pc().WorldInfo.GRI.MissionTracker.UpdateObjective(unrealsdk.find_object("MissionObjectiveDefinition", "GD_Co_Chapter03.M_Co_Ch03_Concordia:16_BuyUpgrade"))
    else:
        get_pc().WorldInfo.GRI.MissionTracker.UpdateObjective(unrealsdk.find_object("MissionObjectiveDefinition", "GD_Episode04.M_Ep4_WelcomeToSanctuary:BuyFuelCell"))

    return Block

def log_to_file(line):
    print(line)
    with open(os.path.join(storage_dir, "log.txt"), 'a') as f:
        f.write(line + "\n")
        return
@keybind("Increment Jump 1 (DEBUG)", None)
def increment_oid_jump_z_override_1():
    add_to_oid_jump_z_override(1)
@keybind("Increment Jump 10 (DEBUG)", None)
def increment_oid_jump_z_override_10():
    add_to_oid_jump_z_override(10)
@keybind("Increment Jump 100 (DEBUG)", None)
def increment_oid_jump_z_override_100():
    add_to_oid_jump_z_override(100)
@keybind("Decrement Jump 1 (DEBUG)", None)
def decrement_oid_jump_z_override_1():
    add_to_oid_jump_z_override(-1)
@keybind("Decrement Jump 10 (DEBUG)", None)
def decrement_oid_jump_z_override_10():
    add_to_oid_jump_z_override(-10)
@keybind("Decrement Jump 100 (DEBUG)", None)
def decrement_oid_jump_z_override_100():
    add_to_oid_jump_z_override(-100)
@keybind("Set Jump to Mod minimum (DEBUG)", None)
def set_oid_jump_z_override_220():
    add_to_oid_jump_z_override(220 - oid_jump_z_override.value, " (Minimum in AP)")
@keybind("Set Jump to Game Default (DEBUG)", None)
def set_oid_jump_z_override_630():
    add_to_oid_jump_z_override(630 - oid_jump_z_override.value, " (Game Default)")
def add_to_oid_jump_z_override(val:int, suffix=""):
    oid_jump_z_override.value = max(0, min(oid_jump_z_override.value + val, 2000))
    show_chat_message("Current Jump: " + str(oid_jump_z_override.value) + suffix)
oid_jump_z_override: SliderOption = SliderOption(
    identifier="Jump Z (Debug)",
    value=0,
    min_value=0,
    max_value=2000,
    description=(
        "Override your jump z value, ignoring unlocked amount and downscale. This option is ignored if set to 0. This option is only meant for debug/testing/data collection"
    )
)

@keybind("Increment Sprint (DEBUG)", None)
def increment_oid_sprint_override():
    add_to_oid_sprint_override(1)
@keybind("Decrement Sprint (DEBUG)", None)
def decrement_oid_sprint_override():
    add_to_oid_sprint_override(-1)
def add_to_oid_sprint_override(val:int):
    oid_sprint_override.value = max(0, min(oid_sprint_override.value + val, 4))
    show_chat_message("Current Sprint: " + str(oid_sprint_override.value))
    
oid_sprint_override: SliderOption = SliderOption(
    identifier="Sprint (Debug)",
    value=0,
    min_value=0,
    max_value=4,
    step=1,
    description=(
        "Override your sprint value, ignoring unlocked amount and downscale. This option is ignored if set to 0. This option is only meant for debug/testing/data collection"
    )
)


oid_jump_z_downscale: SliderOption = SliderOption(
    identifier="Jump Percent",
    value=100,
    min_value=0,
    max_value=100,
    step=1, 
    description=(
        "Scale your jump z down if your unlocked amount is too high. Set to 100 for full unlocked amount."
    )
)

oid_sprint_downscale: SliderOption = SliderOption(
    identifier="Sprint Percent",
    value=100,
    min_value=0,
    max_value=100,
    step=1,
    description=(
        "Scale your sprint speed down if your unlocked amount is too high. Set to 100 for full unlocked amount."
    )
)

# Is initialized in enemies.py and imported
#
# oid_generic_drop_chance_override: SliderOption = SliderOption(
#     identifier="Generic Drop Chance",
#     value=0,
#     min_value=0,
#     max_value=100,
#     step=1,
#     description=(
#         "Override your current drop chance for Generic Item Drops. Set to 0 for your default set chance."
#     )
# )

@hook("WillowGame.SkillTreeGFxObject:CanUpgradeSkill")
def can_upgrade_skill(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if get_pc().PlayerReplicationInfo.ExpLevel < 5:
        # allow leveling skills before level 5, it's weird though.
        # somehow other behaviors are fine, ex. it still requires skill points
        return Block, 4

# @hook("WillowGame.WillowGameInfo:TravelToStation")
# def TravelToStation(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
#     st = unrealsdk.find_object("LevelTravelStationDefinition", "GD_Aster_LevelTravel.DeadForestToMines")
#     args.DestTravelStation = st
#     with prevent_hooking_direct_calls():
#         obj.TravelToStation(args)
#     return Block

@hook("WillowGame.TextChatGFxMovie:AddChatMessage")
def add_chat_message(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    msg = args.msg[0:2].lower() + args.msg[2:]
    if msg.startswith("/travel") or msg.startswith("travel"):
        travel_arg = msg.replace(":", "").split("travel ")[-1].strip()
        map_name = get_translated_map_name(travel_arg)

        if not map_name:
            show_chat_message(f"unrecognized location: {travel_arg}")
            return

        blg = get_globals()
        if not can_travel_to_region(map_name):
            show_chat_message(f"Travel locked, Need: {get_travel_req_string(map_name)}")
            return

        gameinfo = unrealsdk.find_all("WillowCoopGameInfo")[-1]
        gameinfo.TravelToStation(unrealsdk.find_object("Object", travel_targets[map_name]))

@hook("WillowGame.WillowPickup:EnableRagdollCollision")
def disable_collision(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # channel = unrealsdk.find_enum("ERBCollisionChannel")["RBCC_WillowPickup"]
    # obj.CollisionComponent.SetRBCollidesWithChannel(channel, False)
    blg = get_globals()
    if oid_collision.value == "Never":
        blg.loot_spawns_in_progress.discard(obj)
        return
    if oid_collision.value == "AP Spawned" and obj in blg.loot_spawns_in_progress:
        blg.loot_spawns_in_progress.remove(obj)
        return Block
    if oid_collision.value == "Always":
        blg.loot_spawns_in_progress.discard(obj)
        return Block

@hook("WillowGame.WillowInteractiveObject:Touch")
def touch_southern_shelf_bounty_board(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if str(obj) != "WillowInteractiveObject'SouthernShelf_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_673'":
        return

    move_southern_shelf_blocked_missions()

@hook("WillowGame.MissionTracker:UpdateObjective", Type.POST)
def show_mission_obj_message(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # print("UpdateObjective")
    # print(args.MissionObjective)
    # print(args.MissionObjective.Name)
    pn = args.MissionObjective.PathName(args.MissionObjective)
    if pn == "GD_Episode08.M_Ep8_SanctuaryTakesOff:LeaveSanctuary":
        show_chat_message("To reach any remaining checks in Sanctuary, use the chat command \"travel Sanctuary\"")


@hook("WillowGame.WillowGameInfo:InitiateTravel", Type.POST)
def show_travel_message(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # print(args.StationDefinition.Name)
    if args.StationDefinition.Name == "CraterToKickedOut":
        show_chat_message("If you can't jump to the exit, use the chat command \"travel Badass Crater\"")

@hook("Engine.WillowInventory:GetInventorySpaceRequirement")
def block_space_requirement(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    if blg.has_item("Infinite Backpack") or blg.has_item("Backpack Upgrade", 10):
        return Block, 0

@hook("WillowGame.FastTravelStationGFxObject:SendLocationData", Type.POST)
def send_fast_travel_data(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    print("SendLocationData")
    print(args)
    print(obj)
    # # print(args.LocationData)
    # args.LocationDisplayNames.append("   asdf")
    # args.LocationDisplayNames.append("   asdf1")
    # args.LocationDisplayNames.append("   asdf2")
    # args.LocationDisplayNames.append("   asdf2")
    # args.LocationDisplayNames.append("   asdf2")
    # args.LocationStationNames.append("Borderlands 2")
    # args.LocationStationNames.append("Borderlands 2")
    # args.LocationStationNames.append("Borderlands 2")
    # args.LocationStationNames.append("Borderlands 2")
    # args.LocationStationNames.append("Borderlands 2")

    # obj.Outer.LocationIsHeader.append(False)
    # obj.Outer.LocationIsHeader.append(True)
    # obj.Outer.LocationIsHeader.append(False)
    # obj.Outer.LocationDisplayNames.append("   asdf")
    # obj.Outer.LocationDisplayNames.append("   asdf1")
    # obj.Outer.LocationDisplayNames.append("   asdf2")
    # with prevent_hooking_direct_calls():
    #     func(args)
    

    # return Block

@hook("WillowGame.FastTravelStationGFxMovie:BuildLocationData", Type.POST)
def build_location_data(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    obj.LocationIsHeader.append(True)
    obj.LocationIsHeader.append(False)
    obj.LocationIsHeader.append(False)
    obj.LocationDisplayNames.append("AP Travel")
    obj.LocationDisplayNames.append("   asdf1")
    obj.LocationDisplayNames.append("   asdf2")
    obj.LocationDisplayNamesAlphabetical.append("AP Travel")
    obj.LocationDisplayNamesAlphabetical.append("   asdf1")
    obj.LocationDisplayNamesAlphabetical.append("   asdf2")

    # obj.LocationStationNames.append("GrassA")
    # obj.LocationStationNames.append("GrassB")
    # obj.LocationStationNames.append("GrassC")

    print("BuildLocationData")
    print(args)
    # obj.LocationDisplayNames.append("   asdf")
    # obj.LocationDisplayNames.append("   asdf1")
    # obj.LocationDisplayNames.append("   asdf2")

    # print(args.LocationData)


@hook("WillowGame.FastTravelStationGFxMovie:extActivate")
def activate_fs(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    print(args)
    print(obj.LocationDisplayNames)
    
    print(obj.LocationDisplayNames[args.LocationIndex])


mod_instance = build_mod(
    options=[
        oid_connect_to_socket_server,
        oid_print_items_received,
        oid_test_btn,
        oid_collision,
        oid_resend_all,
        oid_resend_last_3,
        oid_jump_z_override,
        oid_sprint_override,
        oid_jump_z_downscale,
        oid_sprint_downscale,
        oid_generic_drop_chance_override,
    ],
    on_enable=on_enable,
    on_disable=on_disable,
    hooks=[
        send_fast_travel_data,
        build_location_data,
        activate_fs,
        add_inventory,
        post_add_inventory,
        on_equipped,
        modify_map_area,
        do_jump,
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
        use_vending_machine,
        set_item_card_ex,
        # player_sold_item,
        on_killed_enemy,
        gfx_menu_closed,
        complete_mission,
        post_complete_mission,
        behavior_complete_mission,
        on_challenge_complete,
        use_chest,
        can_upgrade_skill,
        bunker_warrior_spawn_items,
        # TravelToStation,
        add_chat_message,
        use_black_market,
        black_market_get_price,
        reset_black_market,
        black_market_buy_item,
        current_level_is_below_max,
        post_add_to_backpack,
        disable_collision,
        touch_southern_shelf_bounty_board,
        show_mission_obj_message,
        show_travel_message,
        set_always_on_level,
        update_objective,
        block_space_requirement,
    ]
)

# (> pyexec \path\to\BouncyLootGod\__init__.py
