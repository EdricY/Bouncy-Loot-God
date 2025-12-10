import unrealsdk
from mods_base import get_pc
from BouncyLootGod.oob import get_loc_in_front_of_player
from BouncyLootGod.archi_defs import gear_kind_to_id

gear_kind_to_item_pool = {
    # shields cannot spawn at level 1
    # "Common Shield": "GD_Itempools.ShieldPools.Pool_Shields_All_01_Common",
    # "Uncommon Shield": "GD_Itempools.ShieldPools.Pool_Shields_All_02_Uncommon",
    # "Rare Shield": "GD_Itempools.ShieldPools.Pool_Shields_All_04_Rare",
    # "VeryRare Shield": "GD_Itempools.ShieldPools.Pool_Shields_All_05_VeryRare",
    # "Legendary Shield": "GD_Itempools.ShieldPools.Pool_Shields_All_06_Legendary", # doesn't always spawn a legendary shield. see Roguelands/Looties.py

    # grenades can only be bandit and tediore at level 1
    # "Common GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_01_Common",
    # "Uncommon GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_02_Uncommon",
    # "Rare GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_04_Rare",
    # "VeryRare GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_05_VeryRare",
    "Legendary GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_06_Legendary", # this one is fine, but missing fire storm and chain lightning. And fastball/bouncing bonny are only explosive

    # "Common ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_01_Common",
    # "Uncommon ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_02_Uncommon",
    # "Rare ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_04_Rare",
    # "VeryRare ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_05_VeryRare",
    # "Legendary ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_06_Legendary",
    
    # "Common Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common", # this one sometimes spawns green
    # "Uncommon Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_02_Uncommon", # this is actually just white relics
    # "Rare Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_03_Rare", # this one sometimes spawns purple
    # "VeryRare Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_04_VeryRare", # this is actually just blue relics
    # "Legendary Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_05_Legendary", # this is also actually just blue relics

    "Common Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_01_Common', # some elements can't spawn
    "Uncommon Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_02_Uncommon',  # some elements can't spawn
    "Rare Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_04_Rare', # some elements can't spawn
    "VeryRare Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare', # some elements can't spawn
    "E-Tech Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare_Alien',# some elements can't spawn
    "Legendary Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_06_Legendary', # only missing hector's paradise, and infinity/gunerang cannot spawn with element

    "Common Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_01_Common', # elements and triple/quad barrels can't spawn
    "Uncommon Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_02_Uncommon',
    "Rare Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_04_Rare',
    "VeryRare Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare',
    "E-Tech Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare_Alien',
    "Legendary Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_06_Legendary', # missing overcompensator

    "Common SMG": 'GD_Itempools.WeaponPools.Pool_Weapons_SMG_01_Common',
    "Uncommon SMG": 'GD_Itempools.WeaponPools.Pool_Weapons_SMG_02_Uncommon',
    "Rare SMG": 'GD_Itempools.WeaponPools.Pool_Weapons_SMG_04_Rare',
    "VeryRare SMG": 'GD_Itempools.WeaponPools.Pool_Weapons_SMG_05_VeryRare',
    "E-Tech SMG": 'GD_Itempools.WeaponPools.Pool_Weapons_SMG_05_VeryRare_Alien',
    "Legendary SMG": 'GD_Itempools.WeaponPools.Pool_Weapons_SMG_06_Legendary',

    "Common SniperRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_01_Common',
    "Uncommon SniperRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_02_Uncommon',
    "Rare SniperRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_04_Rare',
    "VeryRare SniperRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_05_VeryRare',
    "E-Tech SniperRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_05_VeryRare_Alien',
    "Legendary SniperRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_06_Legendary', # missing longbow and amigosincero also elements

    "Common AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_01_Common',
    "Uncommon AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_02_Uncommon',
    "Rare AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_04_Rare',
    "VeryRare AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare',
    "E-Tech AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare_Alien',
    "Legendary AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_06_Legendary', # missing thumpston and ogre

    "Common RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_01_Common',
    "Uncommon RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_02_Uncommon',
    "Rare RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_04_Rare',
    "VeryRare RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_05_VeryRare',
    "E-Tech RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_05_VeryRare_Alien',
    "Legendary RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_06_Legendary',  # missing norfleet
}

# many things here adapted from RoguelandsGamemode\Looties.py

orange = unrealsdk.make_struct("Color", R=128, G=64, B=0, A=255)

def pathname(obj):
    return obj.PathName(obj)

def clone_inv_bal_def(
    inv_bal_def,
    inv_bal_kind="WeaponBalanceDefinition",
    package_name="BouncyLootGod",
    remove_some_min_req=True,
    relic_rarity="",
    skip_alien=False,
):
    if type(inv_bal_def) is str:
        src_inv_bal_def = unrealsdk.find_object(inv_bal_kind, inv_bal_def)
    else:
        src_inv_bal_def = inv_bal_def
        inv_bal_kind = inv_bal_def.Class.Name

    package = unrealsdk.find_object("Package", package_name)
    cloned_inv_bal_def = unrealsdk.construct_object(inv_bal_kind, package, src_inv_bal_def.Name, 0, src_inv_bal_def)
    if remove_some_min_req and inv_bal_kind == "WeaponBalanceDefinition":
        src_rplc = cloned_inv_bal_def.RuntimePartListCollection
        if src_rplc:
            cloned_rplc = unrealsdk.construct_object("WeaponPartListCollectionDefinition", package, src_rplc.Name, 0, src_rplc)
            if len(cloned_rplc.ElementalPartData.WeightedParts):
                for wp in cloned_rplc.ElementalPartData.WeightedParts:
                    wp.MinGameStageIndex = 0
                cloned_inv_bal_def.RuntimePartListCollection = cloned_rplc

            if skip_alien and len(cloned_rplc.BarrelPartData.WeightedParts):
                for i in reversed(range(len(cloned_rplc.BarrelPartData.WeightedParts))):
                    wp = cloned_rplc.BarrelPartData.WeightedParts[i]
                    if "Alien" in wp.Part.Name:
                        wp.Part = None
                        # cloned_rplc.BarrelPartData.WeightedParts.pop(i)
                        # wp.MinGameStageIndex = 255
                cloned_inv_bal_def.RuntimePartListCollection = cloned_rplc


    if remove_some_min_req and inv_bal_kind == "InventoryBalanceDefinition":
        src_plc = cloned_inv_bal_def.PartListCollection
        if src_plc:
            cloned_plc = unrealsdk.construct_object("ItemPartListCollectionDefinition", package, src_plc.Name, 0, src_plc)
            # for grenade mod delivery and element
            for wp in cloned_plc.DeltaPartData.WeightedParts:
                wp.MinGameStageIndex = 0
            for wp in cloned_plc.BetaPartData.WeightedParts:
                wp.MinGameStageIndex = 0
            cloned_inv_bal_def.PartListCollection = cloned_plc
            if relic_rarity:
                theta_weighted_parts = []
                # only include specified relic rarity
                for wp in cloned_plc.ThetaPartData.WeightedParts:
                    if str(wp.Part.Rarity.BaseValueAttribute.Name).split("_")[-1] == relic_rarity:
                        theta_weighted_parts.append(wp)
                cloned_plc.ThetaPartData.WeightedParts = theta_weighted_parts

        manufacturers = cloned_inv_bal_def.Manufacturers
        # allow restricted manufacturers
        if manufacturers:
            for m in manufacturers:
                for g in m.Grades:
                    g.GameStageRequirement.MinGameStage = 0

    return cloned_inv_bal_def

def clone_item_pool(
    item_pool,
    package_name="BouncyLootGod",
    remove_some_min_req=True,
    relic_rarity="",
    skip_alien=False
):
    if type(item_pool) is str:
        src_pool = unrealsdk.find_object("ItemPoolDefinition", item_pool)
    else:
        src_pool = item_pool
    package = unrealsdk.find_object("Package", package_name)
    cloned_item_pool = unrealsdk.construct_object("ItemPoolDefinition", package, src_pool.Name, 0, src_pool)
    if remove_some_min_req:
        cloned_item_pool.MinGameStageRequirement = None
        for i in range(len(cloned_item_pool.BalancedItems)):
            if (sub_pool := cloned_item_pool.BalancedItems[i].ItmPoolDefinition):
                cloned_sub_pool = clone_item_pool(sub_pool, package_name=package_name, remove_some_min_req=remove_some_min_req, relic_rarity=relic_rarity, skip_alien=skip_alien)
                cloned_item_pool.BalancedItems[i].ItmPoolDefinition = cloned_sub_pool
            elif (inv_bal_def := cloned_item_pool.BalancedItems[i].InvBalanceDefinition):
                cloned_inv_bal_def = clone_inv_bal_def(inv_bal_def, package_name=package_name, remove_some_min_req=remove_some_min_req, relic_rarity=relic_rarity, skip_alien=skip_alien)
                cloned_item_pool.BalancedItems[i].InvBalanceDefinition = cloned_inv_bal_def

    return cloned_item_pool


def construct_item_pool(
    name,
    pool_names=[],
    inv_bal_def_names=[],
    inv_bal_kind="WeaponBalanceDefinition",
    package_name="BouncyLootGod",
    remove_some_min_req=True,
    src_pool_name=None,
    relic_rarity="",
    skip_alien=False
):
    if src_pool_name:
        item_pool = clone_item_pool(item_pool=src_pool_name, package_name=package_name, remove_some_min_req=remove_some_min_req, relic_rarity=relic_rarity, skip_alien=skip_alien)
        balanced_items = item_pool.BalancedItems
    else:
        package = unrealsdk.find_object("Package", package_name)
        item_pool = unrealsdk.construct_object("ItemPoolDefinition", package, name)
        balanced_items = []

    probability = unrealsdk.make_struct("AttributeInitializationData", BaseValueConstant=1, BaseValueScaleConstant=1)

    for name in pool_names:
        pool = clone_item_pool(name, relic_rarity=relic_rarity, skip_alien=skip_alien)
        balanced_item = unrealsdk.make_struct("BalancedInventoryData", ItmPoolDefinition=pool, Probability=probability, bDropOnDeath=True)
        balanced_items.append(balanced_item)
    
    for name in inv_bal_def_names:
        # clone so we don't mess with regular loot pools
        cloned_inv_bal_def = clone_inv_bal_def(name, inv_bal_kind=inv_bal_kind, package_name=package_name, remove_some_min_req=remove_some_min_req, relic_rarity=relic_rarity, skip_alien=skip_alien)
        balanced_item = unrealsdk.make_struct("BalancedInventoryData", InvBalanceDefinition=cloned_inv_bal_def, Probability=probability, bDropOnDeath=True)
        balanced_items.append(balanced_item)

    for bi in balanced_items:
        bi.Probability = probability

    item_pool.BalancedItems = balanced_items
    return item_pool


def get_item_pool_from_gear_kind_id(gear_kind_id):
    match gear_kind_id:
        # Shield
        case 100:
            return clone_item_pool("GD_Itempools.ShieldPools.Pool_Shields_All_01_Common")
        case 101:
            return clone_item_pool("GD_Itempools.ShieldPools.Pool_Shields_All_02_Uncommon")
        case 102:
            return clone_item_pool("GD_Itempools.ShieldPools.Pool_Shields_All_04_Rare")
        case 103:
            return clone_item_pool("GD_Itempools.ShieldPools.Pool_Shields_All_05_VeryRare")
        case 105:
            return construct_item_pool("BLGLegendaryShields", inv_bal_kind="InventoryBalanceDefinition", inv_bal_def_names=[
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Singularity",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryShock",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryNormal",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_ThresherRaid",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Phoenix",
            ])
        case 109:
            pass
            # Unique Shield
            # GD_Sage_Shields.A_Item_Custom.S_BucklerShield

        # GrenadeMod
        case 110:
            return clone_item_pool("GD_Itempools.GrenadeModPools.Pool_GrenadeMods_01_Common")
        case 111:
            return clone_item_pool("GD_Itempools.GrenadeModPools.Pool_GrenadeMods_02_Uncommon")
        case 112:
            return clone_item_pool("GD_Itempools.GrenadeModPools.Pool_GrenadeMods_04_Rare")
        case 113:
            return clone_item_pool("GD_Itempools.GrenadeModPools.Pool_GrenadeMods_05_VeryRare")
        case 115:
            return construct_item_pool("BLGLegendaryGrenadeMods", 
                src_pool_name="GD_Itempools.GrenadeModPools.Pool_GrenadeMods_06_Legendary",
                inv_bal_kind="InventoryBalanceDefinition",
                inv_bal_def_names=[
                    "GD_Aster_GrenadeMods.A_Item.GM_FireStorm",
                    "GD_Aster_GrenadeMods.A_Item.GM_ChainLightning",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_BonusPackage",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_BouncingBonny",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_Fastball",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_FireBee",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_Leech",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_Pandemic",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_Quasar",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_RollingThunder",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_StormFront",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_NastySurprise",
                ]
            )
        case 119:
            return construct_item_pool("BLGUniqueGrenadeMods",
                inv_bal_kind="InventoryBalanceDefinition",
                inv_bal_def_names=[
                    "GD_Aster_GrenadeMods.A_Item.GM_Fireball",
                    "GD_Aster_GrenadeMods.A_Item.GM_LightningBolt",
                    "GD_Aster_GrenadeMods.A_Item.GM_MagicMissileRare",
                    "GD_Orchid_GrenadeMods.A_Item_Custom.GM_Blade",
                    "GD_GrenadeMods.A_Item_Custom.GM_FusterCluck",
                    "GD_GrenadeMods.A_Item_Custom.GM_KissOfDeath",
                    "GD_GrenadeMods.A_Item_Custom.GM_SkyRocket",
                ]
            )

        # ClassMod
        case 120:
            return clone_item_pool("GD_Itempools.ClassModPools.Pool_ClassMod_01_Common")
        case 121:
            return clone_item_pool("GD_Itempools.ClassModPools.Pool_ClassMod_02_Uncommon")
        case 122:
            return clone_item_pool("GD_Itempools.ClassModPools.Pool_ClassMod_04_Rare")
        case 123:
            return clone_item_pool("GD_Itempools.ClassModPools.Pool_ClassMod_05_VeryRare")
        case 125:
            return construct_item_pool("BLGLegendaryClassMods",
                inv_bal_kind="InventoryBalanceDefinition",
                inv_bal_def_names=[
                    # "GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Soldier_05_Legendary",
                ],
                pool_names=[
                    "GD_Itempools.ClassModPools.Pool_ClassMod_06_Legendary",
                    "GD_Itempools.ClassModPools.Pool_ClassMod_06_SlayerOfTerramorphous",
                    # lobelia has 3 elements/character, so add it 3 times to balance
                    "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All", 
                    "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All",
                    "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All",
                ],
            )

        # Relic
        case 130:
            return construct_item_pool("BLGCommonRelic", inv_bal_kind="InventoryBalanceDefinition",
                pool_names=[
                    "GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
                ],
                relic_rarity="Common",
            )
        case 131:
            return construct_item_pool("BLGUnommonRelic", inv_bal_kind="InventoryBalanceDefinition",
                pool_names=[
                    "GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
                ],
                relic_rarity="Uncommon",
            )
        case 132:
            return construct_item_pool("BLGRareRelic", inv_bal_kind="InventoryBalanceDefinition",
                pool_names=[
                    # "GD_Itempools.ArtifactPools.Pool_Artifacts_03_Rare", # this should work but produces white relics. no clue.
                    "GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
                ],
                relic_rarity="Rare",
            )
        case 133:
            return construct_item_pool("BLGVeryRareRelic", inv_bal_kind="InventoryBalanceDefinition",
                pool_names=[
                    "GD_Itempools.ArtifactPools.Pool_Artifacts_03_Rare",
                ],
                relic_rarity="VeryRare",
            )
        case 134:
            return construct_item_pool("BLGETechRelic", inv_bal_kind="InventoryBalanceDefinition",
                pool_names=[
                    "GD_Gladiolus_Itempools.ArtifactPools.Pool_Artifacts_Ancient_AggressionTenacity"
                ],
                inv_bal_def_names=[
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityAssault_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityLauncher_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityPistol_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityShotgun_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacitySMG_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacitySniper_VeryRare",
                    "GD_Gladiolus_Artifacts.A_Item.A_ElementalProficiency_VeryRare",
                    "GD_Gladiolus_Artifacts.A_Item.A_ResistanceProtection_VeryRare",
                    "GD_Gladiolus_Artifacts.A_Item.A_VitalityStockpile_VeryRare",
                ],
            )
        case 139:
            return construct_item_pool("BLGUniqueRelic", inv_bal_kind="InventoryBalanceDefinition",
                inv_bal_def_names=[
                    "GD_Artifacts.A_Item_Unique.A_Afterburner",
                    "GD_Artifacts.A_Item_Unique.A_Deputy",
                    "GD_Artifacts.A_Item_Unique.A_Endowment",
                    "GD_Artifacts.A_Item_Unique.A_Opportunity",
                    "GD_Artifacts.A_Item_Unique.A_Sheriff",
                    "GD_Artifacts.A_Item_Unique.A_Terramorphous",
                    "GD_Artifacts.A_Item_Unique.A_VaultHunter",
                ],
            )

        # Pistol
        case 140:
            # return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Pistols_01_Common") # Maliwan breaks for this
            return construct_item_pool("BLGWhitePistols",
                inv_bal_def_names=[
                    "GD_Weap_Pistol.A_Weapons.Pistol_Bandit",
                    "GD_Weap_Pistol.A_Weapons.Pistol_Tediore",
                    "GD_Weap_Pistol.A_Weapons.Pistol_Dahl",
                    "GD_Weap_Pistol.A_Weapons.Pistol_Vladof",
                    "GD_Weap_Pistol.A_Weapons.Pistol_Torgue",
                    "GD_Weap_Pistol.A_Weapons.Pistol_Jakobs",
                    "GD_Weap_Pistol.A_Weapons.Pistol_Hyperion",
                    "GD_Weap_Pistol.A_Weapons.Pistol_Maliwan", # Maliwan has to be at the end? no idea what's going on
                ]
            )
        case 141:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Pistols_02_Uncommon")
        case 142:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Pistols_04_Rare")
        case 143:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare", skip_alien=True)
        case 144:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare_Alien")
        case 145:
            return construct_item_pool("BLGLegendaryPistols",
                src_pool_name="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_06_Legendary",
                pool_names=[
                    "GD_Anemone_ItemPools.WeaponPools.Pool_Pistol_Hector_Paradise"
                ]
            )
        # case   146:
        # case   147:
        # case   148:
        case 149:
            return construct_item_pool("BLGUniquePistols",
                inv_bal_def_names=[
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Fibber",
                    "GD_Orchid_BossWeapons.Pistol.Pistol_Jakobs_ScarletsGreed",
                    "GD_Aster_Weapons.Pistols.Pistol_Maliwan_3_GrogNozzle",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_GwensHead",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Judge",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_LadyFist",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Law",
                    "GD_Orchid_BossWeapons.Pistol.Pistol_Maliwan_3_LittleEvie",
                    "GD_Iris_Weapons.Pistols.Pistol_Torgue_3_PocketRocket",
                    "GD_Sage_Weapons.Pistols.Pistol_Jakobs_3_Rex",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Maliwan_3_Rubi",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Teapot",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Bandit_3_Tenderbox",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Vladof_3_Veritas",
                    # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_Starter",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Dahlminator",
                ],
                pool_names=[]
            )

        # Shotgun
        case 150:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_01_Common")
        case 151:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_02_Uncommon")
        case 152:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_04_Rare")
        case 153:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare")
        case 154:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare_Alien")
        case 155:
            return construct_item_pool("BLGLegendaryShotguns", 
                src_pool_name="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_06_Legendary",
                inv_bal_def_names=[
                    "GD_Anemone_Weapons.Shotgun.Overcompensator.SG_Hyperion_6_Overcompensator"
                ]
            )

        # case   156:
        # case   157:
        # case   158:
        case 159:
            return construct_item_pool("BLGUniqueShotguns",
                inv_bal_def_names=[
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Blockhead",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Dog",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_HeartBreaker",
                    "GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Hydra",
                    "GD_Orchid_BossWeapons.Shotgun.SG_Bandit_3_JollyRoger",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_Landscaper",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Octo",
                    "GD_Orchid_BossWeapons.Shotgun.SG_Jakobs_3_OrphanMaker",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_RokSalt",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_Shotgun1340",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Teeth",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_TidalWave",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_Triquetra",
                    "GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Twister",
                    "GD_Aster_Weapons.Shotguns.SG_Torgue_3_SwordSplosion",
                    "GD_Iris_Weapons.Shotguns.SG_Hyperion_3_SlowHand",
                ],
                pool_names=[]
            )

        # SMG
        case 160:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SMG_01_Common")
        case 161:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SMG_02_Uncommon")
        case 162:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SMG_04_Rare")
        case 163:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SMG_05_VeryRare")
        case 164:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SMG_05_VeryRare_Alien")
        case 165:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SMG_06_Legendary")
        # case   166:
        # case   167:
        # case   168:
        case 169:
        # GD_Weap_SMG.A_Weapons_Unique.SMG_Bandit_3_BoneShredder
        # GD_Weap_SMG.A_Weapons_Unique.SMG_Dahl_3_Lascaux
        # GD_Weap_SMG.A_Weapons_Unique.SMG_Gearbox_1
        # GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Bane
        # GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Commerce
        # GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch
        # GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_Chulainn
        # GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_GoodTouch
        # GD_Sage_Weapons.SMG.SMG_Hyperion_3_YellowJacket
        # GD_Orchid_BossWeapons.SMG.SMG_Dahl_3_SandHawk
        # Orc
            pass

        # SniperRifle
        case 170:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_01_Common")
        case 171:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_02_Uncommon")
        case 172:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_04_Rare")
        case 173:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_05_VeryRare", skip_alien=True)
        case 174:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_05_VeryRare_Alien")
        case 175:
            return construct_item_pool(
                "BLGLegendarySnipers", 
                src_pool_name="GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_06_Legendary",
                inv_bal_def_names=[
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Dahl_5_Pitchfork",
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Vladof_5_Lyudmila",
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Maliwan_5_Volcano",
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Jakobs_5_Skullmasher",
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Hyperion_5_Invader",
                    # "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Longbow",
                    "GD_Anemone_Weapons.A_Weapons_Unique.Sniper_Jakobs_3_Morde_Lt",
                ]
            )
        # case   176:
        # case   177:
        # case   178:
        case 179:

        # GD_Sage_Weapons.SniperRifles.Sniper_Jakobs_3_ElephantGun
        # GD_Orchid_BossWeapons.SniperRifles.Sniper_Maliwan_3_Pimpernel
            pass

        # AssaultRifle
        case 180:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_01_Common")
        case 181:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_02_Uncommon")
        case 182:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_04_Rare")
        case 183:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare")
        case 184:
            return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare_Alien")
        case 185:
        # GD_Aster_Weapons.AssaultRifles.AR_Bandit_3_Ogre
            pass
        # case   186:
        # case   187:
        # case   188:
        case 189:
        # GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_1_GBX
        # GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_3_Scorpio
        # GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Jakobs_3_Stomper
        # GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Torgue_3_EvilSmasher
        # GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Vladof_3_Hail
        # GD_Sage_Weapons.AssaultRifle.AR_Jakobs_3_DamnedCowboy
        # GD_Sage_Weapons.AssaultRifle.AR_Bandit_3_Chopper
        # GD_Iris_Weapons.AssaultRifles.AR_Torgue_3_BoomPuppy
        # GD_Iris_Weapons.AssaultRifles.AR_Vladof_3_Kitten
        # GD_Orchid_BossWeapons.AssaultRifle.AR_Jakobs_3_Stinkpot
        # GD_Orchid_BossWeapons.AssaultRifle.AR_Vladof_3_Rapier
            pass

        # RocketLauncher
        case 190:
            pass
        case 191:
            pass
        case 192:
            pass
        case 193:
            pass
        case 194:
            pass
        case 195:
            # GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_Alien_Norfleet
            pass
        # case   196:
        # case   197:
        # case   198:
        case 199:
            # GD_Weap_Launchers.A_Weapons_Unique.RL_Bandit_3_Roaster
            # GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_3_TheHive
            # GD_Weap_Launchers.A_Weapons_Unique.RL_Torgue_3_Creamer
            # GD_Orchid_BossWeapons.Launcher.RL_Torgue_3_12Pounder
            pass

        case 2000:
            return unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_YellowCandy")
        case 2001:
            return unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_RedCandy")
        case 2002:
            return unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_GreenCandy")
        case 2003:
            return unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_BlueCandy")
        case 2004:
            return unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_Candy")

    return None

def spawn_gear(gear_kind, dist=150, height=0):
    if type(gear_kind) is int:
        gear_kind_id = gear_kind
    else:
        gear_kind_id = gear_kind_to_id.get(gear_kind, -1)

    item_pool = get_item_pool_from_gear_kind_id(gear_kind_id)
    # if not item_pool or item_pool is None:
    #     print("can't find item pool: " + item_pool_name)
    #     return
    spawn_gear_from_pool(item_pool, dist, height)

def spawn_gear_from_pool_name(item_pool_name, dist=150, height=0):
    item_pool = unrealsdk.find_object("ItemPoolDefinition", item_pool_name)
    if not item_pool or item_pool is None:
        print("can't find item pool: " + item_pool_name)
        return
    spawn_gear_from_pool(item_pool, dist, height)


def spawn_gear_from_pool(item_pool, dist=150, height=0, package_name="BouncyLootGod"):
    if not item_pool:
        return

    # spawns item at player
    pc = get_pc()
    if not pc or not pc.Pawn:
        print("skipped spawn")
        return
    package = unrealsdk.find_object("Package", package_name)

    sbsl_obj = unrealsdk.construct_object("Behavior_SpawnLootAroundPoint", package, "blg_spawn")
    # sbsl_obj.ItemPools = [unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.WeaponPools.Pool_Weapons_Pistols_02_Uncommon")]
    sbsl_obj.SpawnVelocityRelativeTo = 0
    sbsl_obj.bTorque = False
    sbsl_obj.CircularScatterRadius = 0
    # loc = pc.LastKnownLocation
    loc = get_loc_in_front_of_player(dist, height, pc)
    sbsl_obj.CustomLocation = unrealsdk.make_struct("AttachmentLocationData", 
        Location=loc, #unrealsdk.make_struct("Vector", X=loc.X, Y=loc.Y, Z=loc.Z),
        AttachmentBase=None, AttachmentName=""
    )

    # item_pool.MinGameStageRequirement = None
    sbsl_obj.ItemPools = [item_pool]

    sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=0.000000, Y=0.000000, Z=200.000000)
    sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))

    # 4 direction spawn
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=100.000000, Y=0.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=-100.000000, Y=0.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=0.000000, Y=100.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=0.000000, Y=-100.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
