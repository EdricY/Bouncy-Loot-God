import datetime
import unrealsdk
import socket
from math import sqrt
from mods_base import ObjectFlags, Game
from ui_utils import show_chat_message

if Game.get_current().name == "TPS":
    from BouncyLootGod.bl_tps.archi_data import item_name_to_id
else:
    from BouncyLootGod.bl2.archi_data import item_name_to_id
if 'blg' in globals() and blg is not None:
    print("disconnecting")
    blg.disconnect_socket()

blg = None

def get_or_create_package(package_name="BouncyLootGod"):
    try:
        return unrealsdk.find_object("Package", package_name)
    except ValueError:
        return unrealsdk.construct_object("Package", None, "BouncyLootGod", ObjectFlags.KEEP_ALIVE)

class BLGGlobals:
    # server setup:
    # (BL2 + this mod) <=====> (Socket Server + Archi Launcher BL 2 Client) <=====> (server/archipelago.gg)
    #             is_sock_connected                                   is_archi_connected
    # when is_archi_connected is False, we don't know what is and isn't unlocked.
    def __init__(self, game_info):
        self.tick_count = 0
        self.sock = None
        self.is_sock_connected = False
        self.is_archi_connected = False
        self.has_shutdown = False
        self.game_info = game_info

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
        self.traps_initalized = False
        self.blocked_missions = []

        self.active_vend = None
        self.active_vend_price = -1
        self.temp_reward = None
        self.loot_spawns_in_progress = set() # store these temporarily to disable loot collision later 
        self.settings = {}
        self.death_receive_pending = False
        self.deathlink_timestamp = datetime.datetime.now() # immune to sending deathlink until after this time. helps avoid deathlink loops.

        self.items_filepath = None # store items that have successfully made it to the player to avoid dups

    def reset_item_counters(self):
        self.money_cap = 200
        self.weapon_slots = 2
        self.skill_points_allowed = 0
        self.jump_z = self.calc_jump_height()
        self.sprint_speed = self.calc_sprint_speed()


    def calc_jump_height(self):
        min_jump = 220
        if not self.settings:
            return min_jump
        height_bonus = self.settings.get("max_jump_height", 0) * 300
        max_height = 630 + height_bonus
        num_slices = self.settings.get("jump_checks", 0)
        if num_slices == 0:
            return max_height
        num_checks = self.game_items_received.get(item_name_to_id["Progressive Jump"], 0)
        frac = num_checks / num_slices
        frac = sqrt(frac)
        return max(min_jump, min(max_height, max_height * frac))

    def calc_sprint_speed(self):
        min_speed = 0.6
        if not self.settings:
            return min_speed
        speed_bonus = self.settings.get("max_sprint_speed", 0) * 0.7
        max_speed = 1 + speed_bonus
        num_slices = self.settings.get("sprint_checks", 0)
        if num_slices == 0:
            return max_speed
        num_checks = self.game_items_received.get(item_name_to_id["Progressive Sprint"], 0)
        frac = num_checks / num_slices
        span = max_speed - min_speed
        return max(min_speed, min(max_speed, min_speed + span * frac))

    def has_item(self, item_name, amt=1):
        item_amt = self.game_items_received.get(item_name_to_id[item_name], 0)
        return item_amt >= amt

    def calc_skill_points_allowed(self):
        id1 = item_name_to_id["3 Skill Points"]
        id2 = item_name_to_id["3 Skill Points (p)"]
        return 3 * (self.game_items_received.get(id1, 0) + self.game_items_received.get(id2, 0))

    def disconnect_socket(self):
        if self is None:
            print("blg is none")
            return
        if self.sock is None:
            print("blg no sock")
            return
        try:
            print("blg is_sock_connected " + str(self.is_sock_connected))
            if self.is_sock_connected:
                print("blg sock.shutdown")
                self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            # self.is_sock_connected = False
            # self.is_archi_connected = False
            if len(self.locs_to_send) > 0:
                show_chat_message("outstanding locations: ", self.locs_to_send)
                # TODO: maybe should handle this better, player may have completed a one-time location
            self.has_shutdown = True
            # blg = BLGGlobals()  # reset
            show_chat_message("disconnected from socket server")
        except socket.error as error:
            print(error)

def init_globals():
    global blg
    game_info = None
    if Game.get_current().name == "TPS":
        from .bl_tps import InitTps #there is probably a better way than this.
        game_info = InitTps()
        print(str(game_info.loc_id_to_name)[600:720])
    blg = BLGGlobals(game_info)

def set_globals(_blg):
    global blg
    blg = _blg


def get_globals():
    if blg is None:
        raise RuntimeError("Globals not initialized")
    return blg
