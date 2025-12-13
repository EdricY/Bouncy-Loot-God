import typing
from dataclasses import dataclass
from Options import Choice, Option, DeathLink, Range, Toggle, PerGameCommonOptions, StartInventoryPool

class Goal(Choice):
    """The victory condition for your run."""

    display_name = "Goal"
    option_save_roland_normal_mode = 0
    option_saturn_normal_mode = 1
    option_warrior_normal_mode = 2
    # option_terramorphous_normal_mode = 3
    # option_warrior_tvhm = 3
    # option_warrior_uvhm = 4
    # option_op_10 = 5
    default = 0

class DeleteStartingGear(Choice):
    """Deletes your character's gear on first connection, avoids granting checks immediately for Skyrocket, Gearbox guns, etc.
    (Please be careful to back up your saves and load the correct character)"""
    display_name = "Delete Starting Gear"
    option_keep = 0
    option_delete = 1
    default = 0

class GearRarityItemPool(Choice):
    """Gear kinds will be added to the item pool as receivable items.
    disabled = Exclude from Item Pool, ability to equip things is always unlocked.
    exclude_seraph_plus = Seraph, Pearlescent, and Effervescent are excluded
    exclude_pearl_plus = Pearlescent and Effervescent are excluded
    exclude_rainbow = Effervescent is excluded
    """
    display_name = "Gear Rarity Receivable Items"
    option_disabled = 0
    option_exclude_seraph_plus = 1
    option_exclude_pearl_plus = 2
    option_exclude_rainbow = 3
    option_all = 4
    default = 1

class ReceiveGearItems(Choice):
    """When receiving gear from the item pool, does it spawn for you or do you only get the ability to equip the ones you find?
    This option does nothing if gear_rarity_item_pool is disabled
    equip_only = Added to item pool, do not spawn gear
    receive_non_unique = Added to item pool, only spawn gear that is not Unique/Legendary/etc. (red-text) 
    receive_all = Added to item pool, spawn all gear
    """
    display_name = "Gear Receive Type"
    option_equip_only = 0
    option_receive_non_unique = 1
    option_receive_all = 2
    # option_receive_unique_only = 4
    default = 2

# class FillerItems(Choice):
#     """What items should be added to fill out the item pool?
#     money = Money
#     eridium = Money and Eridium
#     gear = Extra Gear Checks
#     candy = Halloween Candy Spawns 
#     xp = Experience
#     """
#     display_name = "Filler Items"
#     option_money = 0
#     option_eridium = 1
#     option_gear = 2
#     option_candy = 3
#     option_xp = 3
#     default = 3


class VaultSymbols(Choice):
    """Vault Symbols as location checks"""
    display_name = "Vault Symbols"
    option_none = 0
    option_all = 1
    # option_base_game_only = 2
    default = 1

class VendingMachines(Choice):
    """Vending Machines as location checks"""
    display_name = "Vending Machines"
    option_none = 0
    option_all = 1
    # option_base_game_only = 2
    default = 1

class EntranceLocks(Choice):
    """Moving to another map area (regular or fast travel) is disabled until the associated item is found"""
    display_name = "Entrance Locks"
    option_no_locks = 0
    option_all = 1
    # option_base_game_only = 2
    default = 1

class JumpChecks(Choice):
    """How many jump checks should be added to the pool. You will not start with the ability to jump unless you add "Progressive Jump" to your start_inventory"""
    display_name = "Jump Checks"
    option_not_disabled = 0
    option_1 = 1
    option_2 = 2
    option_3 = 3
    option_4 = 4
    option_5 = 5
    default = 3

class MaxJumpHeight(Choice):
    """Each jump check will give you an equivalent fraction of your max jump height.
    If Jump Checks is set to "not disabled" you will simply jump this high.
    high = 1.5x
    extra high = 2x"""
    display_name = "Max Jump Height"
    option_regular = 0
    option_high = 1
    option_extra_high = 2
    default = 0

class SpawnTraps(Choice):
    """Add Spawn Traps to the item pool"""
    display_name = "Entrance Locks"
    option_none = 0
    option_all = 1
    # option_base_game_only = 2
    default = 1

class QuestRewardRando(Choice):
    """Quest rewards are added to the item pool and Quests completions count as location checks"""
    display_name = "Quest Reward Rando"
    option_none = 0
    option_all = 1
    # option_base_game_only = 2
    default = 1


class GenericMobChecks(Choice):
    """Adds a few checks into the location pool for farming generic mobs. Select a drop chance (default 5%)"""
    display_name = "Generic Mob Checks"
    option_disabled = 0
    option_1_percent = 1
    option_2_percent = 2
    option_3_percent = 3
    option_4_percent = 4
    option_5_percent = 5
    option_6_percent = 6
    option_7_percent = 7
    option_8_percent = 8
    option_9_percent = 9
    option_10_percent = 10
    default = 5

class GearRarityChecks(Choice):
    """Adds checks into the location pool for the first time you pick up gear of each type + rarity combination
    exclude_seraph_plus = Seraph, Pearlescent, and Effervescent are excluded
    exclude_pearl_plus = Pearlescent and Effervescent are excluded
    exclude_rainbow = Effervescent is excluded
    """
    display_name = "Rarity Checks"
    option_disabled = 0
    option_exclude_seraph_plus = 1
    option_exclude_pearl_plus = 2
    option_exclude_rainbow = 3
    option_all = 4
    default = 1

class ChallengeChecks(Choice):
    """Adds checks into the location pool for completing BAR challenges
    """
    display_name = "BAR Challenge Checks"
    option_none = 0
    option_level_1 = 1
    # option_unique_only = 2
    # option_exclude_unique = 3
    # option_level_1_only_exclude_unique = 4
    # option_all = 5
    default = 1


# class ControlTraps(Choice):
#     """Add Control Traps to the item pool"""
#     display_name = "Entrance Locks"
#     option_none = 0
#     option_all = 1
#     default = 0



# class FillExtraChecksWith(Choice):
#     """
#     Fill extra checks with this kind of item
#     """
#     display_name = "Fill Extra Checks With"
#     option_legendary_guns_and_items = 0
#     option_legendary_items = 1
#     option_legendary_guns = 2
#     option_purple_rarity_stuff = 3
#     default = 0


class DeathLinkMode(Choice):
    """
    DeathLink is not implemented yet
    If DeathLink is off, this option does nothing.
    ffyl_mode means you will enter FFYL when a DeathLink is received.
    death_mode means you will instantly die when a DeathLink is received.
    """
    display_name = "Death Link Mode"
    option_ffyl_mode = 0
    option_death_mode = 1
    default = 0


# class DropChanceMultiplier(Range):
#     """Runs the drop loot function extra times when any enemy dies. Multipliers will be added as items."""
#     display_name = "Drop Chance Multipliers"
#     range_start = 0
#     range_end = 3
#     default = 3


# class LegendaryDropRandomizer(Toggle):
#     """Legendary drops will be removed from loot pools and replaced with checks."""
#     display_name = "Legendary Drop Randomizer"
#
#
# class NamedEnemyRandomizer(Toggle):
#     """Named Enemies without legendary drops like Bone Head 2.0, Bad Maw, and W4R-D3N
#     will also have checks in their loot pools."""
#     display_name = "Named Enemy Randomizer"
#
#
# class RandomLegendariesReceived(Toggle):
#     """Receive random legendaries."""
#     display_name = "Legendary Drop Randomizer"

@dataclass
class Borderlands2Options(PerGameCommonOptions):
    goal: Goal
    delete_starting_gear: DeleteStartingGear
    gear_rarity_item_pool: GearRarityItemPool
    receive_gear: ReceiveGearItems
    vault_symbols: VaultSymbols
    vending_machines: VendingMachines
    entrance_locks: EntranceLocks
    jump_checks: JumpChecks
    max_jump_height: MaxJumpHeight
    spawn_traps: SpawnTraps
    quest_reward_rando: QuestRewardRando
    generic_mob_checks: GenericMobChecks
    gear_rarity_checks: GearRarityChecks
    challenge_checks: ChallengeChecks
    # fill_extra_checks_with: FillExtraChecksWith
    # legendary_rando: LegendaryDropRandomizer
    # named_enemy_rando: NamedEnemyRandomizer
    # drop_multiplier_amt: DropChanceMultiplier
    death_link: DeathLink
    death_link_mode: DeathLinkMode
    start_inventory_from_pool: StartInventoryPool



