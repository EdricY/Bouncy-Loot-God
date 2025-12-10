import unrealsdk

gear_kind_to_item_pool = {
    "Common Shield": "GD_Itempools.ShieldPools.Pool_Shields_All_01_Common",
    "Uncommon Shield": "GD_Itempools.ShieldPools.Pool_Shields_All_02_Uncommon",
    "Rare Shield": "GD_Itempools.ShieldPools.Pool_Shields_All_04_Rare",
    "VeryRare Shield": "GD_Itempools.ShieldPools.Pool_Shields_All_05_VeryRare",
    "Legendary Shield": "GD_Itempools.ShieldPools.Pool_Shields_All_06_Legendary", # doesn't always spawn a legendary shield. see Roguelands/Looties.py

    "Common GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_01_Common",
    "Uncommon GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_02_Uncommon",
    "Rare GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_04_Rare",
    "VeryRare GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_05_VeryRare",
    "Legendary GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_06_Legendary",

    "Common ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_01_Common",
    "Uncommon ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_02_Uncommon",
    "Rare ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_04_Rare",
    "VeryRare ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_05_VeryRare",
    "Legendary ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_06_Legendary",
    
    "Common Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
    # "Uncommon Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_02_Uncommon", # this is actually just white relics
    "Rare Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_03_Rare", 
    # "VeryRare Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_04_VeryRare", # this is actually just blue relics
    # "Legendary Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_05_Legendary", # this is also actually just blue relics

    "Common Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_01_Common',
    "Uncommon Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_02_Uncommon',
    "Rare Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_04_Rare',
    "VeryRare Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare',
    "E-Tech Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare_Alien',
    "Legendary Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_06_Legendary',

    "Common Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_01_Common',
    "Uncommon Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_02_Uncommon',
    "Rare Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_04_Rare',
    "VeryRare Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare',
    "E-Tech Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare_Alien',
    "Legendary Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_06_Legendary',

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
    "Legendary SniperRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_06_Legendary',

    "Common AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_01_Common',
    "Uncommon AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_02_Uncommon',
    "Rare AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_04_Rare',
    "VeryRare AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare',
    "E-Tech AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare_Alien',
    "Legendary AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_06_Legendary',

    "Common RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_01_Common',
    "Uncommon RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_02_Uncommon',
    "Rare RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_04_Rare',
    "VeryRare RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_05_VeryRare',
    "E-Tech RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_05_VeryRare_Alien',
    "Legendary RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_06_Legendary',
}

# item_pool = unrealsdk.construct_object("ItemPoolDefinition", LootBehavior, name)