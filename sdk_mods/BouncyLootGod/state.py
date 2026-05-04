import datetime
from BouncyLootGod.archi_defs import item_name_to_id
from BouncyLootGod.loot_pools import get_or_create_package
from BouncyLootGod import disconnect_socket

if 'blg' in globals():
    print("disconnecting")
    disconnect_socket()
blg = None

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
        self.traps_initalized = False
        self.blocked_missions = []

        self.active_vend = None
        self.active_vend_price = -1
        self.temp_reward = None
        self.loot_spawns_in_progress = set()
        self.settings = {}
        self.death_receive_pending = False
        self.deathlink_timestamp = datetime.datetime.now() # immune to sending deathlink until after this time. helps avoid deathlink loops.

        self.items_filepath = None # store items that have successfully made it to the player to avoid dups

    def reset_item_counters(self):
        self.money_cap = 200
        self.weapon_slots = 2
        self.skill_points_allowed = 0
        self.jump_z = calc_jump_height(blg)
        self.sprint_speed = calc_sprint_speed(blg)


    min_jump = 220
    def calc_jump_height(self):
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

    min_speed = 0.6
    def calc_sprint_speed(self):
        if not self.settings:
            return 0.6
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


def init_globals():
    global blg
    blg = BLGGlobals()

def set_globals(_blg):
    global blg
    blg = _blg


def get_globals():
    if blg is None:
        raise RuntimeError("Globals not initialized")
    return blg