import typing
from dataclasses import dataclass
from Options import Choice, Option, DeathLink, Range, Toggle, PerGameCommonOptions

class Goal(Choice):
    """The victory condition for your run."""

    display_name = "Goal"
    option_saturn_normal_mode = 0
    option_save_roland_normal_mode = 1
    # option_terramorphous_normal_mode = 2
    # option_warrior_tvhm = 3
    # option_warrior_uvhm = 4
    # option_op_10 = 5
    default = 1

class DeleteStartingGear(Choice):
    """Deletes your character's gear on first connection, avoids granting checks immediately for Skyrocket, Gearbox guns, etc.
    (Please be careful to back up your saves and load the correct character)"""
    display_name = "Delete Starting Gear"
    option_keep = 0
    option_delete = 1
    default = 0

class ReceiveGear(Choice):
    """When receiving guns/items, does it spawn for you or do you only get the ability to equip the ones you find."""
    display_name = "Equipment Receive Type"
    option_equip_only = 0
    option_receive_all = 1
    # option_receive_non_unique_only = 2
    # option_receive_unique_only = 3
    default = 1

class VaultSymbols(Choice):
    """Vault Symbols as location checks"""
    display_name = "Equipment Receive Type"
    option_none = 0
    option_all = 1
    # option_base_game_only = 2
    default = 1

# class Challenges(Choice):
#     """
#     Adds checks upon collecting badass challenges.
#     """
#
#     display_name = "Badass Challenges"
#     option_none = 0
#     option_level_1_only = 1
#     option_unique_only = 2
#     option_exclude_unique = 3
#     option_level_1_only_exclude_unique = 4
#     option_all = 5
#     default = 1


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
    This option is still under development
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
    receive_gear: ReceiveGear
    vault_symbols: VaultSymbols
    # challenges: Challenges
    # fill_extra_checks_with: FillExtraChecksWith
    # legendary_rando: LegendaryDropRandomizer
    # named_enemy_rando: NamedEnemyRandomizer
    # drop_multiplier_amt: DropChanceMultiplier
    death_link: DeathLink
    death_link_mode: DeathLinkMode



