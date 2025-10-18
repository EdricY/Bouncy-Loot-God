import typing
from dataclasses import dataclass
from Options import Choice, Option, DeathLink, Range, Toggle, PerGameCommonOptions

class Goal(Choice):
    """The victory condition for your run."""

    display_name = "Goal"
    option_warrior_normal_mode = 0
    option_terramorphous_normal_mode = 1
    option_warrior_tvhm = 2
    option_warrior_uvhm = 3
    option_op_10 = 4
    default = 0


class Achievements(Choice):
    """
    Adds checks upon collecting achievements. Achievements for clearing bosses and events are excluded.
    "Exclude Grindy" also excludes fishing achievements.
    """

    display_name = "Achievements"
    option_none = 0
    option_exclude_grindy = 1
    option_exclude_fishing = 2
    option_all = 3
    default = 1


class FillExtraChecksWith(Choice):
    """
    Items are rewarded to all players in your Terraria world.
    """
    display_name = "Fill Extra Checks With"
    option_legendary_guns_and_items = 0
    option_legendary_items = 1
    option_legendary_guns = 2
    option_purple_rarity_stuff = 3
    default = 0


class DeathLinkMode(Choice):
    """
    If DeathLink is off, this option does nothing.
    ffyl_mode means you will enter FFYL when a DeathLink is received.
    deathlink_on means you will instantly die when a DeathLink is received.
    """
    display_name = "Death Link Mode"
    option_ffyl_mode = 0
    option_death_mode = 1
    default = 0


class DropChanceMultiplier(Range):
    """Runs the drop loot function extra times when any enemy dies. Multipliers will be added as items."""
    display_name = "Drop Chance Multipliers"
    range_start = 0
    range_end = 3
    default = 3


class LegendaryDropRandomizer(Toggle):
    """Legendary drops will be removed from loot pools and replaced with checks."""
    display_name = "Legendary Drop Randomizer"


class NamedEnemyRandomizer(Toggle):
    """Named Enemies without legendary drops like Bone Head 2.0, Bad Maw, and W4R-D3N
    will also have checks in their loot pools."""
    display_name = "Named Enemy Randomizer"


class RandomLegendariesReceived(Toggle):
    """Receive random legendaries."""
    display_name = "Legendary Drop Randomizer"

@dataclass
class Borderlands2Options(PerGameCommonOptions):
    goal: Goal
    achievements: Achievements
    fill_extra_checks_with: FillExtraChecksWith
    legendary_rando: LegendaryDropRandomizer
    named_enemy_rando: NamedEnemyRandomizer
    drop_multiplier_amt: DropChanceMultiplier
    death_link: DeathLink
    death_link_mode: DeathLinkMode



