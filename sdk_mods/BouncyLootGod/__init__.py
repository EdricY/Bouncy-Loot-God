# to run from console: pyexec \path\to\BouncyLootGod\__init__.py

# note regarding: rlm BouncyLootGod*
# above works, but coroutines starts a new loop without clearing the old one, so sticking with pyexec for now

# debug thing: py unrealsdk.hooks.log_all_calls(True)
# py unrealsdk.hooks.log_all_calls(False)

import unrealsdk
import unrealsdk.unreal as unreal
from math import sqrt
from mods_base import build_mod, ButtonOption, SliderOption, get_pc, hook, ENGINE, ObjectFlags
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


mod_version = "0.5"
if __name__ == "builtins":
    print("running from console, attempting to reload modules")
    get_pc().ConsoleCommand("rlm BouncyLootGod.*")

from BouncyLootGod.archi_defs import item_name_to_id, item_id_to_name, loc_name_to_id, gear_kinds
from BouncyLootGod.lookups import vault_symbol_pathname_to_name, vending_machine_position_to_name, enemy_class_to_loc_name
from BouncyLootGod.loot_pools import spawn_gear, spawn_gear_from_pool_name, get_or_create_package
from BouncyLootGod.map_modify import map_modifications, map_area_to_name, place_mesh_object, setup_generic_mob_drops
from BouncyLootGod.oob import get_loc_in_front_of_player
from BouncyLootGod.rarity import get_gear_item_id, get_gear_loc_id, can_gear_item_id_be_equipped, can_inv_item_be_equipped, get_gear_kind, needs_rarity_check
from BouncyLootGod.entrances import entrance_to_req_areas, travel_targets
from BouncyLootGod.traps import spawn_at_dist, trigger_spawn_trap
from BouncyLootGod.missions import grant_mission_reward, mission_ue_str_to_name
from BouncyLootGod.challenges import challenge_dict, reveal_annoying_challenges
from BouncyLootGod.chests import chest_dict


mod_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(mod_dir) # sdk_mods/ if running unzipped
if parent_dir.endswith(".sdkmod") or parent_dir.endswith(".zip"):
    parent_dir = os.path.dirname(parent_dir)

storage_dir = os.path.join(parent_dir, "blgstor")
# TODO: maybe move storage dir to SETTINGS_DIR (from mods_base)
os.makedirs(storage_dir, exist_ok=True)

class BLGGlobals:
    # server setup:
    # (BL2 + this mod) <=====> (Socket Server + Archi Launcher BL 2 Client) <=====> (server/archipelago.gg)
    #             is_sock_connected                                   is_archi_connected
    # when is_archi_connected is False, we don't know what is and isn't unlocked.
    def __init__(self):
        self.tick_count = 0
        self.sock = None
        self.is_sock_connected = False
        self.is_archi_connected = False
        self.has_shutdown = False

        self.game_items_received = dict() # full dict of items received, kept in sync with server
        self.should_do_fresh_character_setup = False
        self.should_do_initial_modify = False
        self.locations_checked = set()
        self.locs_to_send = []
        self.current_map = ""
        self.money_cap = 200
        self.weapon_slots = 2
        self.skill_points_allowed = 0
        self.jump_z = 630
        self.sprint_speed = 1.0
        self.package = get_or_create_package() #unrealsdk.construct_object("Package", None, "BouncyLootGod", ObjectFlags.KEEP_ALIVE)

        self.active_vend = None
        self.active_vend_price = -1
        self.temp_reward = None
        self.settings = {}
        self.death_receive_pending = False
        self.deathlink_timestamp = datetime.datetime.now() # immune to sending deathlink until after this time. helps avoid deathlink loops.

        self.items_filepath = None # store items that have successfully made it to the player to avoid dups
        self.log_filepath = None # scouting log o7

    def has_item(self, item_name):
        item_amt = self.game_items_received.get(item_name_to_id[item_name], 0)
        return item_amt > 0

if 'blg' in globals():
    print("disconnecting")
    disconnect_socket()
blg = None


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

min_jump = 220
def calc_jump_height(blg):
    if not blg.settings:
        return min_jump
    height_bonus = blg.settings.get("max_jump_height", 0) * 300
    max_height = 630 + height_bonus
    num_slices = blg.settings.get("jump_checks", 0)
    if num_slices == 0:
        return max_height
    num_checks = blg.game_items_received.get(item_name_to_id["Progressive Jump"], 0)
    frac = num_checks / num_slices
    frac = sqrt(frac)
    return max(min_jump, min(max_height, max_height * frac))

min_speed = 0.6
def calc_sprint_speed(blg):
    if not blg.settings:
        return 0.6
    speed_bonus = blg.settings.get("max_sprint_speed", 0) * 0.7
    max_speed = 1 + speed_bonus
    num_slices = blg.settings.get("sprint_checks", 0)
    if num_slices == 0:
        return max_speed
    num_checks = blg.game_items_received.get(item_name_to_id["Progressive Sprint"], 0)
    frac = num_checks / num_slices
    span = max_speed - min_speed
    return max(min_speed, min(max_speed, min_speed + span * frac))

def get_exp_for_current_level():
    pc = get_pc()
    level = pc.PlayerReplicationInfo.ExpLevel
    if level == pc.GetMaxExpLevel():
        return 0
    xp = pc.GetExpPointsRequiredForLevel(level + 1) - pc.GetExpPointsRequiredForLevel(level)
    return xp

def can_player_receive():
    pc = get_pc()
    print(pc)
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

def calc_skill_points_allowed():
    id1 = item_name_to_id["3 Skill Points"]
    id2 = item_name_to_id["3 Skill Points (p)"]
    return 3 * (blg.game_items_received.get(id1, 0) + blg.game_items_received.get(id2, 0))

def handle_item_received(item_id, is_init=False):
    # called only once per item, every init / reconnect
    # is_init means we are receiving this while reading from the file.
    # so... do setup for received items, but skip granting duplicates
    # return True if item properly received and sound should play
    blg.game_items_received[item_id] = blg.game_items_received.get(item_id, 0) + 1
    did_receive_simple = True
    if item_id == item_name_to_id["3 Skill Points"]:
        blg.skill_points_allowed = calc_skill_points_allowed()
    elif item_id == item_name_to_id["3 Skill Points (p)"]:
        blg.skill_points_allowed = calc_skill_points_allowed()
    elif item_id == item_name_to_id["Progressive Money Cap"]:
        blg.money_cap = 200 * (10 ** blg.game_items_received[item_id])
    elif item_id == item_name_to_id["Weapon Slot"]:
        blg.weapon_slots = min(4, blg.weapon_slots + 1)
    elif item_id == item_name_to_id["Progressive Jump"]:
        blg.jump_z = calc_jump_height(blg)
    elif item_id == item_name_to_id["Progressive Sprint"]:
        blg.sprint_speed = calc_sprint_speed(blg)
    else:
        did_receive_simple = False

    if is_init: # other items can be ignored on init
        return False

    if did_receive_simple:
        return True

    print("receiving " + str(item_id))
    if not can_player_receive():
        # skip for now, try again later
        blg.game_items_received[item_id] = blg.game_items_received.get(item_id, 1) - 1
        print("skipping")
        return False

    item_name = item_id_to_name.get(item_id)
    if not item_name:
        print("unknown item: " + str(item_id))
        return False
    show_chat_message("Received: " + item_name)

    # spawn gear
    receive_gear_setting = blg.settings.get("receive_gear")
    if item_name.startswith("Filler Gear: "):
        spawn_gear(item_name[13:])
    elif item_name in gear_kinds and receive_gear_setting != 0:
        spawn_gear(item_name) 
    else:
        # TODO: detect if it's actually spawnable first (candy, etc.)
        spawn_gear(item_name)

    # spawn traps
    if item_name.startswith("Trap Spawn: ") and blg.settings.get("spawn_traps") != 0:
        trigger_spawn_trap(item_name)

    # mission rewards
    if item_name.startswith("Reward: "):
        grant_mission_reward(item_name[8:])

    if item_id == item_name_to_id["$100"]:
        get_pc().PlayerReplicationInfo.AddCurrencyOnHand(0, 100)
    elif item_id == item_name_to_id["10 Eridium"]:
        get_pc().PlayerReplicationInfo.AddCurrencyOnHand(1, 10)
    elif item_id == item_name_to_id["10% Exp"]:
        get_pc().ExpEarn(int(get_exp_for_current_level() * 0.1), 0)
    elif item_id == item_name_to_id["Override Level 15"]:
        get_pc().ExpEarn(get_pc().GetExpPointsRequiredForLevel(15), 0)
    elif item_id == item_name_to_id["Override Level 30"]:
        get_pc().ExpEarn(get_pc().GetExpPointsRequiredForLevel(30), 0)
    elif item_id == item_name_to_id["Max Ammo AssaultRifle"]:
        get_pc().IncBlackMarketUpgrade(0)
    elif item_id == item_name_to_id["Max Ammo Pistol"]:
        get_pc().IncBlackMarketUpgrade(1)
    elif item_id == item_name_to_id["Max Ammo RocketLauncher"]:
        get_pc().IncBlackMarketUpgrade(2)
    elif item_id == item_name_to_id["Max Ammo Shotgun"]:
        get_pc().IncBlackMarketUpgrade(3)
    elif item_id == item_name_to_id["Max Ammo SMG"]:
        get_pc().IncBlackMarketUpgrade(4)
    elif item_id == item_name_to_id["Max Ammo SniperRifle"]:
        get_pc().IncBlackMarketUpgrade(5)
    elif item_id == item_name_to_id["Max Grenade Count"]:
        get_pc().IncBlackMarketUpgrade(6)
    elif item_id == item_name_to_id["Backpack Upgrade"]:
        get_pc().IncBlackMarketUpgrade(7)
    # elif item_id == item_name_to_id["Bank Storage Upgrade"]:
    #     get_pc().IncBlackMarketUpgrade(8)

    # not init, do write.
    with open(blg.items_filepath, 'a') as f:
        f.write(str(item_id) + "\n")

    return True

def sync_vars_to_player():
    sync_skill_pts()
    sync_weapon_slots()
    blg.sprint_speed = calc_sprint_speed(blg)
    blg.jump_z = calc_jump_height(blg)

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
            if datetime.datetime.now().second % 2 == 0:
                find_and_play_akevent("Ake_VOCT_Contextual.Ak_Play_VOCT_Steve_HeyOo") # heyoo
            else:
                find_and_play_akevent('Ake_VOSQ_Sidequests.Ak_Play_VOSQ_ShootInFace_09_live_ShootyFace') # thank you!

        sync_vars_to_player()

    except socket.error as error:
        print(error)
        show_chat_message("pull_items: something went wrong.")
        disconnect_socket()

def pull_locations():
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
        disconnect_socket()

def init_game_items_received():
    if blg.items_filepath is None:
        print("init_game_items_received: not connected")
        return
    if not os.path.exists(blg.items_filepath):
        print("init_game_items_received: no file exists")
        return
    # reset counters
    blg.money_cap = 200
    blg.weapon_slots = 2
    blg.skill_points_allowed = 0
    blg.jump_z = calc_jump_height(blg)
    blg.sprint_speed = calc_sprint_speed(blg)

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
    blg.should_do_initial_modify = True
    if len(blg.locations_checked) == 0 and not os.path.exists(blg.items_filepath):
        blg.should_do_fresh_character_setup = True
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
def add_inventory(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # TODO: maybe doesn't run on receiving quest reward
    # does not trigger on buy back from vending machine
    if self != get_pc().GetPawnInventoryManager():
        # not player inventory
        return
    if blg.should_do_fresh_character_setup:
        return
    try:
        cust_name = caller.NewItem.ItemName
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
    if blg.should_do_fresh_character_setup:
        return

    loc_id = get_gear_loc_id(caller.Inv)
    if loc_id is None:
        return

    if loc_id not in blg.locations_checked:
        blg.locs_to_send.append(loc_id)
        push_locations()

    item_id = get_gear_item_id(caller.Inv)
    if can_gear_item_id_be_equipped(blg, item_id):
        # allow equip
        return
    else:
        # block equip (I'm not sure this does anything)
        return Block

@hook("WillowGame.ItemCardGFxObject:SetItemCardEx", Type.POST)
def set_item_card_ex(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if (inv_item := caller.InventoryItem) is None:
        return
    
    if inv_item.ItemName.startswith("AP Check:") or inv_item.ItemName.startswith("Black Market:"):
        # removes things like skill and child grenade count
        self.SetFunStats("")
        # removes bottom icons and sets title color
        self.SetColor(Title=inv_item.ItemName, TypeIcon="", newColor=unrealsdk.make_struct("Color", R=0, G=255, B=255, A=255), Manufacturer="", ElementalIcon="", bIsReadied=False,)
        # removes stats in the middle AND "Already Unlocked" on skins
        self.SetTopStat(StatIndex=0, LabelText="", ValueText="", CompareArrow=0, AuxText="", IconName="")
        # self.SetTitle(
        #     Title=inv_item.ItemName,
        #     TypeIcon="",
        #     Rarity=unrealsdk.make_struct("Color", R=0, G=255, B=255, A=255),
        #     Manufacturer="",
        #     ElementalIcon="",
        #     bIsReadied=False,
        # )
        self.setHeight()
        return

    kind = get_gear_kind(inv_item)
    if not can_inv_item_be_equipped(blg, inv_item):
        self.SetLevelRequirement(True, False, False, f"lvl {inv_item.GameStage}, Can't Equip: {kind}")

    if needs_rarity_check(blg, inv_item):
        self.SetFunStats(f"<font size='18' color='#FFFF00'>{kind} is unchecked! Pick me up!</font>")

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
    if not blg.is_archi_connected:
        return
    pc = get_pc()
    inventory_manager = pc.GetPawnInventoryManager()
    if pc and inventory_manager and inventory_manager.SetWeaponReadyMax:
        with prevent_hooking_direct_calls():
            inventory_manager.SetWeaponReadyMax(blg.weapon_slots)

def level_my_gear():
    # if not blg.has_item("Gear Leveler"):
    #     show_chat_message("Need to unlock Gear Leveler.")
    #     return
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
        item.DefinitionData.ManufacturerGradeIndex = current_level
        item.DefinitionData.GameStage = current_level
        item.InitializeFromDefinitionData(item.DefinitionData, None)

    # go through item chain (relic, classmod, grenade, shield)
    item = inventory_manager.ItemChain
    while item:
        item.DefinitionData.ManufacturerGradeIndex = current_level
        item.DefinitionData.GameStage = current_level
        item.InitializeFromDefinitionData(item.DefinitionData, None)

        item = item.Inventory

    # go through equipment slots
    for i in [1, 2, 3, 4]:
        weapon = inventory_manager.GetWeaponInSlot(i)
        if weapon:
            weapon.DefinitionData.ManufacturerGradeIndex = current_level
            weapon.DefinitionData.GameStage = current_level
            weapon.InitializeFromDefinitionData(weapon.DefinitionData, None)

    show_chat_message("gear set to level " + str(current_level))
    return

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
    items_to_uneq = []
    item = inventory_manager.ItemChain
    while item:
        if not can_inv_item_be_equipped(blg, item):
            show_chat_message("can't equip: " + get_gear_kind(item))
            items_to_uneq.append(item)
        item = item.Inventory
    for i in items_to_uneq:
        inventory_manager.InventoryUnreadied(i, True)
    # equipment slots
    for i in [1, 2, 3, 4]:
        weapon = inventory_manager.GetWeaponInSlot(i)
        if weapon and not can_inv_item_be_equipped(blg, weapon):
            show_chat_message("can't equip: " + get_gear_kind(weapon))
            inventory_manager.InventoryUnreadied(weapon, True)

def check_full_inventory():
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

def on_enable():
    global blg
    blg = BLGGlobals()
    # print("enabled! 5")
    # unrealsdk.load_package("SanctuaryAir_Dynamic")
    # find_and_play_akevent("Ake_VOCT_Contextual.Ak_Play_VOCT_Steve_HeyOo") # Heyoo
    connect_to_socket_server(None) #try to connect
    modify_map_area(None, None, None, None) # trigger "move" to current area

    # trying this in our own thread for now. if this causes problems, probably move to player tick or something else
    # stackoverflow.com/questions/59645272
    # thread = threading.Thread(target=asyncio.run, args=(watcher_loop(),))
    # thread.start()
    # threading definitely causing problems, switching to use juso's coroutines
    start_coroutine_tick(watcher_loop(blg))


def disconnect_socket():
    global blg
    if blg is None:
        print("blg is none")
        return
    if blg.sock is None:
        print("blg no sock")
        return
    try:
        print("blg is_sock_connected " + str(blg.is_sock_connected))
        if blg.is_sock_connected:
            print("blg sock.shutdown")
            blg.sock.shutdown(socket.SHUT_RDWR)
        blg.sock.close()
        # blg.is_sock_connected = False
        # blg.is_archi_connected = False
        if len(blg.locs_to_send) > 0:
            show_chat_message("outstanding locations: ", blg.locs_to_send)
            # TODO: maybe should handle this better, player may have completed a one-time location
        blg.has_shutdown = True
        blg = BLGGlobals()  # reset
        show_chat_message("disconnected from socket server")
    except socket.error as error:
        print(error)

def on_disable():
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
        if not map_name:
            # TODO: I think we are missing Torgue DLC "kicked out" (or it might just be inside torgue arena ring)
            show_chat_message("Missing map name, please report issue: " + new_map_area)
            map_name = new_map_area # override with internal name
        else:
            exit_areas = set()
            for areas in entrance_to_req_areas.values():
                if len(areas) > 0 and areas[0] == map_name:
                    exit_areas.update(areas)
            warning_areas = []
            for a in exit_areas:
                if not blg.has_item("Travel: " + a):
                    warning_areas.append(a)
            if len(warning_areas) > 0:
                show_chat_message("Warning... Areas still locked: " + ", ".join(warning_areas))

        show_chat_message("Moved to map: " + map_name)
        log_to_file("moved to map: " + map_name)
        blg.current_map = new_map_area
        sync_vars_to_player()
        setup_generic_mob_drops(blg)
        if new_map_area in map_modifications:
            mod_func = map_modifications[new_map_area]
            mod_func(blg)


@hook("WillowGame.WillowPlayerInput:Jump")
def jump(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    pass
    # get_pc().Pawn.JumpZ = 1200 # 630 is default
    # den = unrealsdk.find_object("PopulationOpportunityDen", "Stockade_Combat.TheWorld:PersistentLevel.PopulationOpportunityDen_29") 
    # den.DoSpawning(popmaster)
    # ServerDeveloperSpawnAwesomeItems
    # print("jump2")
    # print(get_pc().Pawn.JumpZ)
    # a = unrealsdk.find_object("CameraAnim","Anim_1st_Person.Stunned")
    # a = unrealsdk.find_object("CameraAnim","Anim_CameraAnimations.Explosions.Canim_Explosion_WarriorEarthquake")
    # a = unrealsdk.find_object("CameraAnim","GD_Aster_Weapons.CameraAnims.CameraAnim_GrogDrunkLong")
    # get_pc().PlayAnimSeqCameraAnim(a, Rate=2, Scale=7, bLoop=True)
    # get_pc().PlayAnimSeqCameraAnim(a, Rate=0, Scale=0, bLoop=False)
    # get_pc().WorldInfo.TimeDilation = 3 - get_pc().WorldInfo.TimeDilation
    # ENGINE.GetCurrentWorldInfo().WorldGravityZ = -500
    # ENGINE.GetCurrentWorldInfo().DefaultGravityZ = -500
    # get_pc().Pawn.SuggestJumpVelocity()
    # return Block
    
    # print(get_pc().Pawn.PlayerFallDuration)
    # print(get_pc().Pawn.PlayerFallDuration)
    # get_pc().Pawn.PlayArmAnimation("GD_Soldier_Streaming.Anims.WeaponAnim_Melee", 10, 10)
    # get_pc().TakeDamage(600, None, unrealsdk.make_struct("Vector", X=0, Y=0, Z=0), unrealsdk.make_struct("Vector", X=0, Y=0, Z=0), None)
    # return Block
    # get_pc().ServerThrowInventory()
    # get_pc().SetCameraMode("3rd")
    # get_pc().SetPlayerFOV(165)
    # print(get_pc().PlayerMovementType)
    
    # 
    # get_pc().Resurrect()
    # get_pc().NotifyTakeHit(
    #     get_pc(),#Damage=1,
    #     get_pc().Pawn, #unrealsdk.find_class("WillowGame.WillowDmgSource_Grenade").ClassDefaultObject,#DamageType=unrealsdk.find_class("WillowGame.WillowDmgSource_Grenade").ClassDefaultObject,
    #     unrealsdk.make_struct("Vector", X=0, Y=0, Z=0),#HitLocation=None,
    #     10000,#HitPawn=None,
    #     DamageType=unrealsdk.find_class("WillowGame.WillowDmgSource_Grenade"),
    #     Momentum=unrealsdk.make_struct("Vector", X=0, Y=0, Z=0)
    # )
    # x = get_pc().GetFullInventory([])
    # traps
    # get_pc().InvertMouseLook(True)
    # get_pc().InvertGamepadLook(True)
    # get_pc().ServerResurrect()
    
    # for thing in x[1]:
    #     print(thing)
    # get_pc().DeveloperSpawnAwesomeItems()

@hook("WillowGame.WillowPlayerPawn:DoJump")
def do_jump(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if oid_jump_height_override.value != 0: # debug jump height, remove me later
        get_pc().Pawn.JumpZ = oid_jump_height_override.value
        return

    get_pc().Pawn.JumpZ = blg.jump_z
    # if not blg.has_item("Progressive Jump"):
    #     show_chat_message("jump disabled!")
    #     return Block

@hook("WillowGame.WillowPlayerPawn:DoSprint")
def sprint_pressed(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    self.SprintingPct = blg.sprint_speed
    # if not blg.has_item("Sprint"):
    #     show_chat_message("sprint disabled!")
    #     return Block

@hook("WillowGame.WillowPlayerInput:DuckPressed")
def duck_pressed(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    for pickup in get_pc().GetWillowGlobals().PickupList:
        if pickup.Inventory.ItemName.startswith("AP Check:"):
            print("moving:" + pickup.Inventory.ItemName)
            pickup.Location = get_loc_in_front_of_player(150, 50)
            pickup.AdjustPickupPhysicsAndCollisionForBeingDropped()
    # get_pc().PlayerReplicationInfo.AddCurrencyOnHand(1, 100)
    # print(get_pc().PlayerClass.Name)
    # spawn_gear("VeryRare Shotgun")
    # spawn_gear("VeryRare SMG")
    # spawn_gear("Legendary RocketLauncher")
    # spawn_gear("Unique Pistol")
    # popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_SarcasticSlab.Balance.PopDef_SarcasticSlab:PopulationFactoryBalancedAIPawn_0")
    # spawn_at_dist(popfactory, dist=1000)
    # spawn_at_dist(popfactory, dist=-1000)

    # gameinfo = unrealsdk.find_all("WillowCoopGameInfo")[-1]
    # gameinfo.TravelToStation(unrealsdk.find_object("FastTravelStationDefinition", "GD_FastTravelStations.Zone2.Grass_A"))


    if not blg.has_item("Crouch"):
        show_chat_message("crouch disabled!")
        return Block

@hook("WillowGame.WillowVehicleWeapon:BeginFire")
def vehicle_begin_fire(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if blg.current_map == "southernshelf_p": # allow use of big bertha
        return True
    if not blg.has_item("Vehicle Fire") and self.MyVehicle and self.MyVehicle.PlayerReplicationInfo is not None:
        show_chat_message("vehicle fire disabled!")
        return Block


# @hook("WillowGame.WillowPlayerController:ServerGrantMissionRewards")

@hook("WillowGame.WillowPlayerController:ServerCompleteMission")
def complete_mission(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # print(caller.Mission)
    if blg.settings.get("quest_reward_items", 0) != 0:
        # quest rewards are in the multiworld, replace with empty here
        empty_reward = unrealsdk.make_struct("RewardData",
            ExperienceRewardPercentage=caller.Mission.Reward.ExperienceRewardPercentage,
        )
        blg.temp_reward = (
            unrealsdk.make_struct("RewardData",
                ExperienceRewardPercentage=caller.Mission.Reward.ExperienceRewardPercentage,
                CurrencyRewardType=caller.Mission.Reward.CurrencyRewardType,
                CreditRewardMultiplier=caller.Mission.Reward.CreditRewardMultiplier,
                OtherCurrencyReward=caller.Mission.Reward.OtherCurrencyReward,
                RewardItems=caller.Mission.Reward.RewardItems,
                RewardItemPools=caller.Mission.Reward.RewardItemPools,
            ),
            unrealsdk.make_struct("RewardData",
                ExperienceRewardPercentage=caller.Mission.AlternativeReward.ExperienceRewardPercentage,
                CurrencyRewardType=caller.Mission.AlternativeReward.CurrencyRewardType,
                CreditRewardMultiplier=caller.Mission.AlternativeReward.CreditRewardMultiplier,
                OtherCurrencyReward=caller.Mission.AlternativeReward.OtherCurrencyReward,
                RewardItems=caller.Mission.AlternativeReward.RewardItems,
                RewardItemPools=caller.Mission.AlternativeReward.RewardItemPools,
            ),
        )
        caller.Mission.Reward = empty_reward
        caller.Mission.AlternativeReward = empty_reward

    # send quest completion 
    if blg.settings.get("quest_completion_checks", 0) != 0:
        loc_name = "Quest: " + mission_ue_str_to_name.get(caller.Mission.Name, "")
        loc_id = loc_name_to_id.get(loc_name)
        if loc_id is None:
            print("unknown quest: " + caller.Mission.Name + " " + loc_name)
            show_chat_message("unknown quest")
            return

        if loc_id in blg.locations_checked:
            return

        blg.locs_to_send.append(loc_id)
        push_locations()


@hook("WillowGame.WillowPlayerController:ServerCompleteMission", Type.POST)
def post_complete_mission(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if blg.settings.get("quest_reward_items", 0) != 0:
        # reset quest reward
        caller.Mission.Reward = blg.temp_reward[0]
        caller.Mission.AlternativeReward = blg.temp_reward[1]
        blg.temp_reward = None

@hook("WillowGame.WillowInventoryManager:AddInventoryToBackpack", Type.POST)
def post_add_to_backpack(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # print(f"add to backpack {caller}")
    # receiving items from quests
    if self != get_pc().GetPawnInventoryManager():
        # not player inventory
        return
    if blg.should_do_fresh_character_setup:
        return

    if not blg.is_archi_connected:
        return

    loc_id = get_gear_loc_id(caller.Inv)
    if loc_id is None or loc_id in blg.locations_checked:
        return
    blg.locs_to_send.append(loc_id)
    push_locations()

@hook("WillowGame.WillowInventoryManager:AddInventory", Type.POST)
def post_add_inventory(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if self != get_pc().GetPawnInventoryManager():
        # not player inventory
        return
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
    level_key = "Level " + str(level)
    loc_id = loc_name_to_id.get(level_key)
    if loc_id:
        blg.locs_to_send.append(loc_id)
        push_locations()

@hook("WillowGame.WillowInventoryManager:SetWeaponReadyMax")
def set_weapon_ready_max(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    return Block

@hook("WillowGame.WillowPlayerController:Behavior_Melee")
def behavior_melee(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if not blg.has_item("Melee"):
        show_chat_message("melee disabled!")
        return Block
    # TODO: Krieg's action skill is not disabled (maybe that's ok?)

@hook("WillowGame.WillowPlayerPawn:SetupPlayerInjuredState")
def enter_ffyl(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    send_setting = blg.settings.get("death_link_send_mode")
    if send_setting == 1 or send_setting == 4:
        send_deathlink()

    print("enter_ffyl")

def send_deathlink():
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
        disconnect_socket()

def query_deathlink():
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
            disconnect_socket()

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
def died(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # TODO: how does this interact with co-op?
    print("player died")
    send_setting = blg.settings.get("death_link_send_mode")
    if send_setting == 0 or send_setting == 3:
        send_deathlink()

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
    for pool_name in gear_kinds.keys():
        spawn_gear(pool_name, dist, dist)
        dist += 50

    # get_pc().ExpEarn(1000, 0)
    # get_pc().PlayerReplicationInfo.SetCurrencyOnHand(0, 999999)

oid_test_btn: ButtonOption = ButtonOption(
    "Test Btn",
    on_press=test_btn,
    description="Test Btn",
)

@hook("WillowGame.Behavior_DiscoverLevelChallengeObject:ApplyBehaviorToContext")
def discover_level_challenge_object(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # obj_id = str(caller.ContextObject)
    # check_name = vault_symbol_pathname_to_name.get(obj_id)
    pathname = caller.ContextObject.PathName(caller.ContextObject)
    check_name = vault_symbol_pathname_to_name.get(pathname)

    loc_id = loc_name_to_id.get(check_name)
    if loc_id is None:
        if check_name is not None:
            show_chat_message("Vault Symbol failed id lookup on: " + check_name + "  " + pathname)
            log_to_file("Vault Symbol failed id lookup on: " + check_name + "  " + pathname)
        return
    if loc_id not in blg.locations_checked:
        blg.locs_to_send.append(loc_id)
        push_locations()

@hook("WillowGame.Behavior_SpawnItems:ApplyBehaviorToContext")
def bunker_warrior_spawn_items(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    pathname = self.PathName(self)
    loc_id = None
    if pathname == "GD_FinalBoss.Character.AIDef_FinalBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_15":
        check_name = "Enemy: Warrior"
        loc_id = loc_name_to_id.get(check_name)
    elif pathname == "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_17":
        check_name = "Enemy: BNK-3R"
        loc_id = loc_name_to_id.get(check_name)

    if loc_id is None:
        return

    if loc_id not in blg.locations_checked and loc_id not in blg.locs_to_send:
        blg.locs_to_send.append(loc_id)
        push_locations()


@hook("WillowGame.PauseGFxMovie:CompleteQuitToMenu")
def complete_quit_to_menu(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    blg.current_map = "" # reset, now loading into map will trigger changing areas
    print("complete_quit_to_menu")
    send_setting = blg.settings.get("death_link_send_mode")
    if send_setting == 2 or send_setting == 3 or send_setting == 4:
        send_deathlink()

@hook("WillowGame.WillowPlayerController:ClientSetCurrentMapFullyExplored")
def set_current_map_fully_explored(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    log_line = "Map Fully Explored: " + blg.current_map
    log_to_file(log_line)
    print(log_line)

@hook("WillowGame.WillowGameInfo:InitiateTravel")
def initiate_travel(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # check for setting
    # print("InitiateTravel")
    station_name = caller.StationDefinition.Name
    # log_to_file("InitiateTravel: " + station_name)
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
        if not blg.has_item("Travel: " + area_name):
            req_areas_not_met.append(area_name)

    if len(req_areas_not_met) == 0:
        # requirement met
        return

    show_chat_message("Travel Disabled. Need: " + ", ".join(req_areas_not_met))
    print(station_name)
    print("Travel Disabled. Need: " + ", ".join(req_areas_not_met))
    return Block

# @hook("WillowGame.LevelTravelStation:GetDestinationMapName")
# def get_destination_map_name(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
#     pass
    # print("get_destination_map_name")
    # print(self)
    # print(caller)
    # return Block, "ASDFasdf"

# @hook("WillowGame.WillowInteractiveObject:InitializeFromDefinition")
# def initialize_from_definition(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
#     if self.Class.Name != "WillowVendingMachine":
#         return
#     print("vending machine init")

def get_vending_machine_pos_str(wvm):
    # old way: f"{str(wvm.Outer)}~{str(wvm.Location.X)},{str(wvm.Location.Y)}"
    return f"{int(wvm.Location.X)},{int(wvm.Location.Y)}"

@hook("WillowGame.WillowInteractiveObject:UseObject")
def use_vending_machine(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if self.Class.Name != "WillowVendingMachine":
        return

    if blg.settings.get("vending_machines") == 0:
        # skip if vending machine checks are off
        return
    # TODO: settings option to always remove iotd

    pos_str = get_vending_machine_pos_str(self)
    check_name = vending_machine_position_to_name.get(pos_str)
    if not check_name:
        log_to_file("opened unknown Vending Machine: " + pos_str)
        # show_chat_message("opened unknown Vending Machine: " + pos_str)
        return
    # print(check_name)
    loc_id = loc_name_to_id.get(check_name)
    if loc_id is None:
        return

    if loc_id in blg.locations_checked:
        return
    blg.active_vend = self
    blg.active_vend_price = self.FixedFeaturedItemCost
    if self.FormOfCurrency == 0:
        self.FixedFeaturedItemCost = 100
    else:
        # Torgue and Seraph vendors
        self.FixedFeaturedItemCost = 10

    # try to force the featured item to not be a weapon
    reroll_count = 0
    while self.FeaturedItem.Class.Name == "WillowWeapon" and reroll_count < 20:
        reroll_count += 1
        self.ResetInventory()

    if self.FeaturedItem.Class.Name == "WillowWeapon":
        # can't figure out how to display pizza mesh on weapon.
        # and swapping the weapon to an item results in an item that can't be purchased
        # maybe we could change the lootpool and reroll once? GD_ItemPools_Shop.Items.Shoppool_FeaturedItem 
        # GD_ItemPools_Shop.HealthShop.HealthShop_FeaturedItem 
        # GD_ItemPools_Shop.WeaponPools.Shoppool_FeaturedItem_WeaponMachine

        w_def = self.FeaturedItem.DefinitionData
        self.FeaturedItem.InitializeFromDefinitionData(
            unrealsdk.make_struct("WeaponDefinitionData",
                WeaponTypeDefinition=w_def.WeaponTypeDefinition,
                BalanceDefinition=w_def.BalanceDefinition,
                # ManufacturerDefinition=w_def.ManufacturerDefinition,
                # ManufacturerGradeIndex=w_def.ManufacturerGradeIndex,
                # BodyPartDefinition=w_def.BodyPartDefinition,
                # GripPartDefinition=w_def.GripPartDefinition,
                # BarrelPartDefinition=w_def.BarrelPartDefinition,
                # SightPartDefinition=w_def.SightPartDefinition,
                # StockPartDefinition=w_def.StockPartDefinition,
                # ElementalPartDefinition=w_def.ElementalPartDefinition,
                # Accessory1PartDefinition=unrealsdk.find_object("WeaponPartDefinition", "GD_Weap_AssaultRifle.Accessory.AR_Accessory_BanditClamp_Damage"),
                # Accessory2PartDefinition=w_def.Accessory2PartDefinition,
                # MaterialPartDefinition=clone_material_part,
                # PrefixPartDefinition=w_def.PrefixPartDefinition,
                # TitlePartDefinition=w_def.TitlePartDefinition,
                # GameStage=w_def.GameStage,
                # UniqueId=w_def.UniqueId,
            ),
            None
        )
        self.FeaturedItem.ItemName = "AP Check: " + check_name
    else:
        # print(self.FeaturedItem.Class.Name)
        sample_def = unrealsdk.find_object("UsableCustomizationItemDefinition", "GD_Assassin_Items_Aster.Assassin.Head_ZeroAster")
        item_def = unrealsdk.construct_object("UsableCustomizationItemDefinition", blg.package, "archi_venditem_def", 0, sample_def)

        try:
            pizza_mesh = unrealsdk.find_object("StaticMesh", "Prop_Details.Meshes.PizzaBoxWhole")
        except:
            unrealsdk.load_package("SanctuaryAir_Dynamic")
            pizza_mesh = unrealsdk.find_object("StaticMesh", "Prop_Details.Meshes.PizzaBoxWhole")

        item_def.NonCompositeStaticMesh = pizza_mesh
        item_def.ItemName = "AP Check: " + check_name
        item_def.CustomPresentations = []
        item_def.bPlayerUseItemOnPickup = True # allows pickup with full inventory (i think)
        item_def.bIsConsumable = True
        try:
            item_def.OverrideMaterial = unrealsdk.find_object("MaterialInstanceConstant", 'Prop_Details.Materials.Mati_PizzaBox')
        except:
            item_def.OverrideMaterial = None
        item_def.BaseRarity.BaseValueConstant = 500.0 # teal, like mission/pearl
        item_def.UIMeshRotation = unrealsdk.make_struct("Rotator", Pitch = -134, Yaw = -14219, Roll = -7164)
        self.FeaturedItem.InitializeFromDefinitionData(
            unrealsdk.make_struct("ItemDefinitionData", ItemDefinition=item_def),
            None
        )

# WillowGame.WillowItem:RemoveFromShop

# @hook("WillowGame.WillowPlayerController:PerformedUseAction")
# def performed_use_action(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
#     print("performed use action")
#     print(self)
#     print(caller)


# WillowGame.WillowVendingMachine:PlayerBuyItem and bWasItemOfTheDay

# WillowGame.PlayerSkillTree:UpgradeSkill


@hook("WillowGame.WillowPlayerController:GFxMenuClosed")
def gfx_menu_closed(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if blg.active_vend is not None:
        blg.active_vend.FixedFeaturedItemCost = blg.active_vend_price
        blg.active_vend = None

@hook("WillowGame.WillowAIPawn:Died")
def on_killed_enemy(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    print("on_killed_enemy")
    print(self.AIClass.Name)
    print(self.GetTransformedName())
    enemy_key = self.AIClass.Name
    loc_name = enemy_class_to_loc_name.get(enemy_key)
    if not loc_name:
        enemy_key += "~" + self.GetTransformedName()
        loc_name = enemy_class_to_loc_name.get(enemy_key)
    if not loc_name:
        return
    print("loc_name")
    print(loc_name)
    loc_id = loc_name_to_id[loc_name]
    blg.locs_to_send.append(loc_id)
    push_locations()

@hook("WillowGame.WillowPlayerController:ServerCompleteChallenge")
def on_challenge_complete(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    pn = caller.ChalDef.PathName(caller.ChalDef)
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
def use_chest(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    pos_str = get_chest_pos_str(self)
    loc_name = chest_dict.get(pos_str)
    if loc_name is None:
        # print(self.InteractiveObjectDefinition)
        # log_to_file("unknown chest: " + pos_str)
        return
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
def black_market_get_price(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if caller.InventoryForSale.ItemName.endswith("Bank SDU"):
        return
    return Block, bm_price

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
    inv_manager = pc.GetPawnInventoryManager()
    
    sample_def = unrealsdk.find_object("UsableCustomizationItemDefinition", "GD_Assassin_Items_Aster.Assassin.Head_ZeroAster")
    item_def = None
    def setup_item(item, purchasable_data):
        name = purchasable_data[0] if purchasable_data else "Blank"
        mesh = unrealsdk.find_object("StaticMesh", purchasable_data[1] if purchasable_data else "Prop_Details.Meshes.PizzaBoxWhole")
        mat = unrealsdk.find_object("MaterialInstanceConstant", purchasable_data[2] if purchasable_data else "Prop_Details.Materials.Mati_PizzaBox")

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
        
        item.InitializeFromDefinitionData(
            unrealsdk.make_struct("ItemDefinitionData", ItemDefinition=item_def),
            None
        )

    inv_list = bmvm.GetInventoryList([], pc)
    inv_items = inv_list[1]
    i = 0
    for inv in inv_items:
        if inv.Item.ItemName.endswith("Bank SDU"):
            continue
        purchasable_data = bm_purchasables[i] if i < len(bm_purchasables) else None
        i += 1
        setup_item(inv.Item, purchasable_data)

    # leaving this as normal purchase so. the whaddaya buyin challenge and Plan B mission remain possible
    featured = bmvm.GetFeaturedItem(pc)
    if featured and featured.Item:
        setup_item(featured.Item, ("Level My Gear", "Prop_Pickups.Meshes.EridiumContainer", "Prop_Pickups.Materials.Eridium_Pickups_Bar"))


@hook("WillowGame.BlackMarketDefinition:CurrentLevelIsBelowMaxForPlayer")
def current_level_is_below_max(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    # make black market items always appear
    # TODO this should probably not override for bank sdu
    return Block, True

@hook("WillowGame.WillowVendingMachineBase:ResetInventory")
def reset_black_market(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if self.Class.Name != "WillowVendingMachineBlackMarket":
        return
    change_bm_inventory(self)


@hook("WillowGame.WillowInteractiveObject:UseObject")
def use_black_market(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if self.Class.Name != "WillowVendingMachineBlackMarket":
        return
    change_bm_inventory(self)

@hook("WillowGame.WillowVendingMachineBlackMarket:PlayerBuyItem")
def black_market_buy_item(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    pc = get_pc()
    bought_item = caller.Item
    name = bought_item.ItemName
    if not name.startswith("Black Market: "):
        return
    name = name.split("Black Market: ")[-1]

    current_eridium = pc.PlayerReplicationInfo.GetCurrencyOnHand(1)
    if current_eridium < bm_price:
        show_chat_message("Not Enough Eridium")
        return Block
    else:
        pc.PlayerReplicationInfo.AddCurrencyOnHand(1, -bm_price)

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
        pc.PlayerReplicationInfo.AddCurrencyOnHand(2, 100)
    elif name == "Gemstone Package":
        spawns = random.sample(["Gemstone Pistol", "Gemstone Shotgun", "Gemstone SMG", "Gemstone SniperRifle", "Gemstone AssaultRifle" ], 3)
    elif name == "Level My Gear":
        level_my_gear()
    else:
        show_chat_message("Option not implemented")
        pc.PlayerReplicationInfo.AddCurrencyOnHand(1, bm_price)
        print(f"unknown black market purchase: {name}")

    # pc.PlayerReplicationInfo.AddCurrencyOnHand(4, 33) # torgue tokens

    spawn_loc = {"X": self.Location.X, "Y": self.Location.Y - 1000, "Z": self.Location.Z + 500}
    for s in spawns:
        spawn_loc["X"] += 20
        spawn_gear(s, override_loc=spawn_loc)


def log_to_file(line):
    print(line)
    if not blg.log_filepath:
        print("don't know where to log")
        with open(os.path.join(storage_dir, "unknown.log.txt"), 'a') as f:
            f.write(line + "\n")
        return
    with open(blg.log_filepath, 'a') as f:
        f.write(line + "\n")


oid_jump_height_override: SliderOption = SliderOption(
    identifier="jump z",
    value=0,
    min_value=0,
    max_value=2000,
    description=(
        "Override your jump z value. This is ignored if set to 0. This option is only meant for debug/testing/data collection"
    )
)

@hook("WillowGame.SkillTreeGFxObject:CanUpgradeSkill")
def can_upgrade_skill(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    if get_pc().PlayerReplicationInfo.ExpLevel < 5:
        # allow leveling skills before level 5, it's weird though.
        # somehow other behaviors are fine, ex. it still requires skill points
        return Block, 4


# @hook("WillowGame.WillowGameInfo:TravelToStation")
# def TravelToStation(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
#     st = unrealsdk.find_object("LevelTravelStationDefinition", "GD_Aster_LevelTravel.DeadForestToMines")
#     caller.DestTravelStation = st
#     with prevent_hooking_direct_calls():
#         self.TravelToStation(caller)
#     return Block

@hook("WillowGame.TextChatGFxMovie:AddChatMessage")
def add_chat_message(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
    msg = caller.msg[0:2].lower() + caller.msg[2:]
    if msg.startswith("/travel") or msg.startswith("travel"):
        travel_arg = msg.replace(":", "").split("travel ")[-1].strip()
        travel_item_name = f"Travel: {travel_arg}"
        if travel_arg == "Torgue Arena TAS" or travel_arg == "Torgue Arena Ring":
            travel_item_name = "Travel: Torgue Arena"
        item_id = item_name_to_id.get(travel_item_name)
        if not item_id:
            show_chat_message(f"unrecognized location: {travel_arg}")
            return
        if not blg.has_item(travel_item_name):
            show_chat_message(f"Travel item required: {travel_item_name}")
            return

        gameinfo = unrealsdk.find_all("WillowCoopGameInfo")[-1]
        gameinfo.TravelToStation(unrealsdk.find_object("Object", travel_targets[travel_arg]))




mod_instance = build_mod(
    options=[
        oid_connect_to_socket_server,
        oid_print_items_received,
        oid_test_btn,
        oid_jump_height_override,
    ],
    on_enable=on_enable,
    on_disable=on_disable,
    hooks=[
        add_inventory,
        post_add_inventory,
        on_equipped,
        modify_map_area,
        do_jump,
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
        use_vending_machine,
        set_item_card_ex,
        # player_sold_item,
        on_killed_enemy,
        gfx_menu_closed,
        complete_mission,
        post_complete_mission,
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
    ]
)

# (> pyexec \path\to\BouncyLootGod\__init__.py
