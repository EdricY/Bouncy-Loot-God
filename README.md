# Bouncy-Loot-God
An Archipelago.gg integration for Borderlands 2 and Borderlands The Pre-Sequel

## Setup for playing

### Requirements
1. You should have the latest [BL2/TPS mod manager](https://github.com/bl-sdk/willow2-mod-manager) (3.7+) ([release page](https://github.com/bl-sdk/willow2-mod-manager/releases/tag/v3.7))

2. The latest version of [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) (0.6.7+) ([release page](https://github.com/ArchipelagoMW/Archipelago/releases/tag/0.6.7))

3. The sdk mod requires [coroutines](https://bl-sdk.github.io/willow2-mod-db/mods/coroutines/) (1.1+) ([direct download](https://github.com/juso40/bl2sdk-mods/raw/refs/heads/main/coroutines/coroutines.sdkmod))  
Place it into the sdk_mods folder. A browser window will open if you still need to install this. When installing Coroutines, it is recommended to install it before any other mods and enable it/make sure it says it is Loaded, and then close Borderlands 2 so that BouncyLootGod may show up in the Mod Manager like it should.

For any GitHub Release Page, scroll to the bottom of the release notes to find the files you want (under "Assets"). Don't download the source code by accident.

### Installation
1. Download the `borderlands2.apworld` (or `borderlands_tps.apworld`) and `BouncyLootGod.sdkmod` file from the [release page](https://github.com/EdricY/Bouncy-Loot-God/releases)
2. `BouncyLootGod.sdkmod` goes into `.../Steam/steamapps/common/Borderlands 2/sdk_mods/` (for BL2) OR `.../Steam/steamapps/common/BorderlandsPreSequel/sdk_mods/` (for TPS)
3. The `.apworld` file goes into `.../Archipelago/custom_worlds/` OR use the `Install APWorld` tool from the Archipelago Launcher OR simply double click the .apworld file. Restart your Archipelago launcher after installing the apworld.

It is recommended when installing the BouncyLootGod mod; to load up the game, make sure it is enabled, and then close the game. This is done to ensure that your run is ready at the start.
It is then recommended that when you are ready to start up a run; to load up the Borderlands 2 Client through the Archipelago Launcher, connect to your Archipelago Room, and then turn on Borderlands 2. The mod misbehaves if the game is opened with the mod on, before the client is opened and connected to the room.
More information on [sdk mod setup](https://bl-sdk.github.io/willow2-mod-db/faq/)  
More information on [apworld](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/apworld%20specification.md)

### Options yaml
Pick and download a file from the sample-yamls. You can find sample-yamls.zip attached to your chosen release ([latest here](https://github.com/EdricY/Bouncy-Loot-God/releases/latest)). For Bleeding Edge, you can use the [current sample-yamls](/sample-yamls/).  
Heavy editing to the sample is not encouraged unless you know what you're doing. More samples coming soon.  
If you want to learn more about yaml options, select "Generate Template Options" in the Archipelago Launcher after installing the apworld. Then open `Borderlands 2.yaml` and read about the options.

#### Note on Options Creator
Only use the Options Creator if you are confident that you know what you're doing. Many options require you to know some location or item names, find them in archi_data.py.    
[[current bl2 archi_data.py](https://github.com/EdricY/Bouncy-Loot-God/blob/main/sdk_mods/BouncyLootGod/bl2/archi_data.py)]  
[[current tps archi_data.py](https://github.com/EdricY/Bouncy-Loot-God/blob/main/sdk_mods/BouncyLootGod/bl_tps/archi_data.py)]  

### Getting your multi world started
1. Place player yaml file(s): Archipelago Client > Browse Files > Players > insert yaml files here.
2. Generate world: Archipelago Client > Generate
3. The outputted .zip file is at Archipelago Client > Browse Files > output > `AP_<numbers>.zip`
4. Upload this .zip at https://archipelago.gg/uploads to create a room  
OR host locally with Archipelago Client > Host (if you know what you're doing)

### Running the mod
Backup your BL2 characters before proceeding! They are located at Documents/my games/Borderlands 2/WillowGame/SaveData/...

With a multiworld running, Open "Borderlands 2 Client" from the Archipelago Launcher (restart the launcher if it's not there), connect to the multiworld. Then open Borderlands 2 and enable the mod.

Double check from the ingame mod menu that coroutines says version 1.1 and "Loaded".

If you open the game first, use the Mod Options menu to disable and re-enable the mod once the Archipelago Client is open.

The mod is currently running the entire time it's enabled. Any character you "Continue" with will have their inventory checked.

If the game crashes when loading your character, please try disabling the mod, then loading your character, then enabling the mod from Esc > Mods > BouncyLootGod

### Note on versions
Ensure you use the same version for each of:

(1) The AP world used to generate the multiworld. 

(2) The AP world for the "Borderlands 2 Client" you are connecting to. 

(3) The sdkmod installed in your game mods folder. 

(4) The yaml used in the player folder for generating. A 0.5.3 yaml will be different from a 0.5.4 yaml for example and generating with an incorrect yaml may cause issues.

Do not update your AP world or sdkmod mid-run.

### Note on disabling
This mod does not properly clean up after itself when you disable it. Some values may remain modified after turning the mod off, and won't be reset until fully restarting the game (not just save-quit).
**Before doing any non-archipelago play in Borderlands 2, Disable the mod and Restart your game!!!**

## FAQ
### What should I own?
You should own at least Borderlands 2. This will let you do a basic run, but you will need to ensure that your yaml is set up to facilitate said run. So no traps, no random candy filler, having the DLCs disabled, having Quest_Reward_Items set to `only_included_regions` or `only_included_regions_gear`, having Gear_Rarity_Receivable_Items/Gear_Licenses set to `exclude_seraph_plus` so that you don't receive licenses for gear you don't have access to/can't use, having Gear_Rarity_Checks set to `exclude_seraph_plus` so that you don't have to pick up gear that you don't have access to, and making sure that the DLC checks for each DLC you don't own to be set to `remove`.

For a seemless and full experience, it is also recommended to own and have downloaded all 4 original Campaign DLCs, Gaige, Krieg, the 5 Headhunters, both UVHM upgrades, the Commander Lilith DLC, the Premiere Club, the Collector's Edition Pack, and the Creature Dome/Slaughterhouse.

### What gets randomized?
Items you receive include:
- Gear Licenses/Gear Rarity Receivable Items to gain the ability to equip gear. Can be fully enabled with `all`, fully disabled with `disabled`, specify you don't want to have licenses for Seraphs, Pearls, & Rainbow gear with `exclude_seraphs_plus`; Pearls & Rainbow gear with `exclude_pearl_plus`; or only Rainbow Gear with `exclude_rainbow`.
  - If you wanted to use Gear Licenses, but start with let's say Common Pistol and Common Shield;
  ```
  start_inventory_from_pool:
    'License: Common Pistol': 1
    'License: Common Shield': 1
  ```
- Your in-game abilities:
  - Melee. To start with Melee, edit your yaml
  ```
  start_inventory_from_pool: 
    Melee: 1
  ```
  - Crouch. To start with Crouch, edit your yaml
  ```
  start_inventory_from_pool:
    Crouch: 1
  ```
  - Jump. Option to make your jump an item can be enabled by choosing a number between 1 and 5 (whole numbers only) this is how many `Progressive Jump`s you will have in your generation, you can bypass the option entirely and keep your jump with `not_disabled`.
    - The option Max Jump Height can also be changed. Each `Progressive Jump` attained will give you an equivalent fraction of your max jump height. Units used in example are just how the game determines the height. If Jump is not an itemset, setting your jump height higher will affect it right away.
      - `None` = With no `Progressive Jump`s your jump height is 220 units.
      - `Regular` = Regular Max Jump Height = 630 units.
      - `High` = High Max Jump Height = 930 units.
      - `Extra High` = Extra High Max Jump Height = 1230 units.
  - Sprint. Option to make your sprint an item can be enabled by choosing a number between 1 and 5 (whole numbers only) this is how many `Progressive Sprint`s you will have in your generation, can bypass the option entirely and keep your sprint with `not_disabled`.
    - The option Max Sprint Speed can also be changed. Each `Progressive Sprint` attained will give you an equivalent fraction of your max sprint speed. If Sprint is not an itemset, setting your sprint speed faster will affect it right away.
      - `Regular` = Regular Sprint Speed = 1x
      - `Fast` = 1.7x Sprint Speed
      - `Extra Fast` = 2.4x Sprint Speed
      - `Supersonic` = 3.8x Sprint Speed
  - Vehicle Fire (using the weapons on a vehicle). To start with Vehicle Fire, edit your yaml
  ```
  start_inventory_from_pool: 
    Vehicle Fire: 1
  ```
- Quest Rewards. The option Quest Reward Items, when set to anything other than `none`, will make it so Quest rewards are not given at the time of quest completion. They are instead added to the item pool.
  - `all` - Includes all quest rewards to be in the item pool.
  - `only_gear` - Includes quest rewards in the item pool, but removes rewards that do not include gear.
    - ex. Best Minion Ever only grants money.
  - `only_included_regions` - Includes quest rewards in the item pool but remove quests associated with excluded regions (like DLC that has been turned off; use this if there's DLC you don't own).
  - `only_included_regions_gear` - Combination of `only_gear` and `only_included_regions`.
- Entrance Locks. The ability to move from one area to another (regular or fast travel) is disabled until the associated item is found. Can 
  - ex. In a normal run, you start in Windshear Waste and are meant to go to Southern Shelf. You will be unable to go to Southern Shelf until you find the item `Travel: Southern Shelf`
- Progressive Travel Groups. The same idea as Entrance Locks, but this time you will unlock the areas in order, dependent on their type: `basegame`, `basegame_side`, `ffs`, `tina`, `torgue`, `scarlett`, `hammerlock`, `headhunter`. You can find the order that these unlock in for each variety in the pins of the discord page.
  - ex. In a normal run, you start in Windshear Waste and are meant to go to Southern Shelf. You will be unable to go to Southern Shelf until you find a `Progressive Travel: Base Game` item.
  - ex. If you've attasined the ability to go to Southern Shelf, but now you need to go to Southern Shelf - Bay, you will need to find a `Progressive Travel: Side Area` item.
- Money Cap (affects how much money you can hold at one time). Items are called `Progressive Money Cap` and there are 8 per generation, making your caps go from $200 up to the cap of $99,999,999. To start with a higher amount of money cap, edit your yaml and replace the X with a whole number between `1` and `8`:
```
start_inventory_from_pool:
  Progressive Money Cap: X
```
- Filler Items. In the option Filler Item Rotation, these are the items that will fill out the rest of the item pool after everything that needs to be there. Filler items will be added to the item pool in a round robin fashion, so any item in this list will be added many times. Include more instances of an item by including it multiple times. Items will be added in the same ratio as they appear in the list on your yaml. You can delete a thing from your list, and it will not appear as a filler (for generation purposes, there will still be at least one instance of said filler item). The kinds of filler you can expect are:
  - `RandomCandy`. These filler items are only usable if you own and have downloaded Headhunter 1: The Bloody Harvest.
    - `RedCandy` increases damage.
    - `GreenCandy` gives health regeneration.
    - `YellowCandy` increases movement speed and reload speed.
    - `BlueCandy` gives ammo regeneration and applies a knockback nova when dealing melee damage.
  - `3 Skill Points`. They do just what they say on the tin. Skill Points are handled differently than other filler and will stop being added once you can reach 120 skill points.
  - `$100`. The only denomination of money that is filler at the moment is `$100`.
  - `10 Eridium`. You get 10 Eridium added to your Eridium Wallet.
  - `10% Exp`. You receive enough experience to go up a whole 10th of your Exp bar, regardless of your level.
  - `SDU`. You receive am SDU, like you would buy from Earl in Sanctuary (except not in this mod, because Earl is changed in this mod). 
  - Traps. You receive an extra trap of the variety that you specify. Only works if you own and have downloaded Digistruct Peak. These filler traps are separate from the yaml option Spawn Traps. Traps only work if you have Digistruct Peak. These are all of the traps currently:
    - `Trap Spawn: Assassins` - Spawns all 4 Assassins from Southpaw Steam & Power around you.
    - `Trap Spawn: Doc Mercy` - Spawns 2 Doc Mercy from Three Horns Valley around you.
    - `Trap Spawn: Creepers` - Spawns 8 Creepers from Caustic Caverns around you.
    - `Trap Spawn: Saturn` - Spawns 2 Saturn from Arid Nexus Badlands around you.
    - `Trap Spawn: Dukino's Mom` - Spawns 2 Dukino's Mom from Lynchwood around you.
    - `Trap Spawn: Black Queen` - Spawns 2 Black Queen from The Dust around you.
  - `Gear`. Will cycle through gear based on the choice in the yaml option Filler Gear.
    - Filler Gear set to `Rarity`. Gives you random gear based on rarities. 
      - ex. `Filler Gear: Common SniperRifle`, `Filler Gear: Uncommon RocketLauncher`, etc.
    - Filler Gear set to `Unique`. Gives you named gear. 
      - ex. `Filler Gear: Unkempt Harold`, `Filler Gear: Mongol`, `Filler Gear: Magic Missile`, etc.
    - Filler Gear set to `Both`. Does both `Rarity` and `Unique`.

Locations/Things you will be doing/Checks include: 
- Leveling up from 2 to 30.
- Killing a Named Enemy for the first time. 
- Finding each individual Vault Symbol. Can be enabled with `all` or disabled with `none` through yaml options. If disabled, while Challenge Checks is set to `all` or `region_based_only`, you will still need to find all of the Vault Symbols for the Cult of the Vault Challenges.
- Each Vending Machine's Item of the Day will be a pizza until you buy it. Can be enabled with `all` or disabled with `none` through yaml options.
- Each enemy type can have a chance to drop a pizza that is a Generic Mob Drop. After the first pickup for that variety of enemy, they should no longer drop that pizza on reload or map change. Can be enabled with choosing a nubmer between 1 and 10 (use only whole numbers, no decimals) or disabled with `disable` through yaml options.
- Completing BAR Challenges. Under yaml option Cahllenge Checks; can be fully enabled with `all`, disabled fully with `none`, or you can specify if you want `general_only` challenges (2nd wind kills, weapon specific kills, opening Pirate chests in the Scarlett DLC, etc.), or just `region_based_only` challenges (Killing the Assassins in Southpaw Steam & Power within 10 minutes, The Cult of the Vault challenges for finding each set of symbols in each area, Finding the echoes in certain areas, etc.).
- Opening Red Chests in each area. Under yaml option Chest Checks; can be enabled with `all` or disabled with `none` through yaml options. Red Chests checks include ([named here in the wiki:](https://borderlands.fandom.com/wiki/Lootable_object/Borderlands_2)) Regular Red Chests, Bandit Car Trunks, Dahl Red Weapon Chests, Hyperion Red Weapon Chests, Pirate Weapon Chests (Assuming you have Scarlett DLC checks on), & Dice Chests (Assuming you have Tina DLC checks on). The Hyperion Yellow Weapon Chests associated with the Nest Egg Challenge in Candlerakk's Crag in the Hammerlock DLC are also considered Red Chests only for the purposes of checks. The Lilith DLC Burrows chests associated with Challenge Burrows: Never Enough Tools, are not currently considered Red Chests for the purposes of chests.
- Gear Rarity Checks are checks based on you picking up a combination of type of gear and rarity of gear for the first time. Examples include, but are not limited to: Common Shield, Uncommon Relic, Rare Class Mod, VeryRare GrenadeMod, E-Tech AssaultRifle, Legendary Pistol, Seraph Shotgun, Rainbow SniperRifle, Pearlescent SMG, Unique Rocket Launcher, etc. Can be fully enabled with `all`, fully disabled with `disabled`, specify you don't want to acquire Seraphs, Pearls, & Rainbow gear with `exclude_seraphs_plus`; Pearls & Rainbow gear with `exclude_pearl_plus`; or just disable Rainbow Gear with `exclude_rainbow`.
- Quest completions. Can be fully enabled with `all` or disabled fully with `none`. Through yaml options, you can specify if you want `story_only` quests or `sidequest_only` quests.

### What version do I play?
For the most stable experience play the [latest stable version](https://github.com/EdricY/Bouncy-Loot-God/releases/latest).  
For the latest features and if you would like to participate in testing and reporting issues, play the bleeding edge version (find it on the [release page](https://github.com/EdricY/Bouncy-Loot-God/releases)).

### What yaml do I choose?
For syncs lasting around 2 hours, `bl2-basegame-short.yaml` is a good, well-tested choice.  
Specific yamls for other DLCs are available, and should also be sync viable.  
For longer runs, `bl2-basegame-med.yaml` goes through the full base game story and should be beatable in about 8 hours.

### What other mods do you recommend?
Playing with other mods is not officially supported (yet!). But people have found the following mods useful:  
[Always On Level](https://github.com/EdricY/EdricY-BL2-sdk-mods/tree/main/AlwaysOnLevel)  (No longer needed for releases 0.5.4+)

[Apples Borderlands Cheats](https://bl-sdk.github.io/willow2-mod-db/mods/apples-borderlands-cheats/)  (Mostly recommended for the Ghost feature. If you find yourself in a place where the logic of the mod thinks you should be able to do something, but it is incorrect, you may use the Ghost feature to go through a barrier/fly upwards/fly downwards/whatever you need so you can still do what is needed without haveing to manually send a check through the archipelago commands)

(There is a crash associated with the Ghost feature; do not do anything that could cause damage to an enemy and then use the Ghost feature right away. Doing damage to enemies while being in the ghost state crashes you. So don't: throw a grenade, apply a DoT, throw out Axton's Turret, summon Deathtrap, use Phaselock, etc)

[Dialog Skipper](https://bl-sdk.github.io/willow2-mod-db/mods/dialog-skipper/)  (Useful to save just a little bit more of your time. There is at least one dialog that this should be disabled for:) 

(In Rotgut Distillery, when you need to have Ed break through the gate, the mod seems to break this mission. If you find yourself in this situation, just turn off the mod and save and quit, and then reload the character, go back to Ed to talk with him, and then after he breaks the gate, you should be safe to reenable the mod.)

[EXP Adjuster](https://bl-sdk.github.io/willow2-mod-db/mods/expadjuster/)  (Useful to make the game go by just a bit quicker)

[Jump to Level Challenges](https://bl-sdk.github.io/willow2-mod-db/mods/jumptolevelchallenges/)  (Useful if you have all challenges on and just want to save time scrolling through the Badass Rank menu. Press a button and it brings you to challenges of your current map)

[Loot Collector](https://bl-sdk.github.io/willow2-mod-db/mods/lootcollector/)  (Press a button and bring any piece of gear on your current map to you. If you spawn in Sanctuary at the fast travel, and your gear disappears, and doesn't get collected; it is because the game ate them at the fast travel. You may go into the BouncyLootGod mod menu and resend your items to yourself if something important was deleted)

[Spawn Multiplier](https://bl-sdk.github.io/willow2-mod-db/mods/spawn-multiplier/)  (Incase you have the Generic Mob Checks option on, set to a low percentage, and are too far into a run to be able to regenerate with a corrected yaml)

[Time of Day Changer](https://bl-sdk.github.io/willow2-mod-db/mods/timeofdaychanger/)  (Useful for if you need to do a challenge at a certain time of day)

### I keep getting "client is not connected", what do I do?
Make sure you have followed the steps in [Requirements](#requirements) (check versions!). And make sure you open "Borderlands 2 Client" from the Archipelago launcher, not Text Client.  
Also try hitting the "Connect to Socket Server" button as well as disabling and re-enabling the mod.  
Another potential issue you can be running into is having multiple watcher loops running in game. The may happen if you quickly re-enabled the mod or connected the client after launching the game. To fix this, try disabling the mod, waiting 5 seconds, then re-enabling the mod.

### A browser window opens when I enable the mod, what do I do?
You need to install coroutines. See [step 3 in Requirements](#requirements)

### I can't deal damage and want to deal damage, what do I do?
You may add Melee to your beginning items. See [one of the sample yamls](https://github.com/EdricY/Bouncy-Loot-God/blob/main/sample-yamls/bl2-basegame-short.yaml#L54)  
Include something like this in your yaml:
```
  start_inventory_from_pool:
    Melee: 1
```
### Why isn't x item y rarity?
If you want specifics, currently "Unique" for guns specifically means Blue, Purple, or E-Tech with red text. "Unique" for other gear is checked against a specific list.  
Feel free to report these issues, but if it seems like a matter of opinion or you're just trying to flex your knowledge of Borderlands guns, you will be ignored. Ex. Gearbox white guns have been decided to be labeled Common, not Unique. Blood of Terramorphous is considered Unique for as it is the only Legendary Relic.

### The mission displays exp but I didn't get any?
When you receive a mission reward from the multiworld, it should give you no exp. If you don't open your menu within 5 seconds of receiving it in game, it may display the exp numbers without granting you that amount of experience.

### Can I use skill points before level 5?
You can but it's a little weird. It'll still have the greyed out look, but it works. Your skill trees will look normal again after level 5.

### I received a Travel item, can I go there early?
Open the in game chat (not the developer console) and type "travel" and the name of the map area. The default key to open chat on PC is `Y`.
ex. `travel Thousand Cuts`

### Help! I have a blocked quest that I need to complete!
Select the current story mission and enter Sanctuary. You should see a message that says to save-quit to make the quests appear at the bounty board. Save-quit, then find the quest at the bounty board. (This is a relatively new feature, please report any issues found with it)

You can also hit inacessible quest turn in points when Hammerlock leaves to Sanctuary but you don't have access to Sanctuary yet. In this case, approach the Southern Shelf Bounty Board and the blocked quests should appear there.

### What's up with the item called `3 Skill Points (p)`?
This is for AP world generation reasons. If you want the technical reasons read on... Skill points are fundamentally used as filler items, but there is one case where it needs to be treated as a progression item (i.e. something requires you to use your action skill). The `(p)` version is the progression version. Additionally, this should have the nice side effect of ensuring you receive skill points early with high progression balancing.

### What's the item called `Generic: Name_of_Enemy`?
This item is a pizza that types of enemies can drop in this mod. The yaml option `generic_mob_checks`, determines the percentage chance that killing an enemy (that has a generic item) will drop their pizza. If the pizza drops outside of the map, or falls through the map out of reach, you can use your crouch button (even if you dont have crouch unlocked) to bring all pizzas on your current map to you.

### Why are the items I'm receiving in-game different than the ones my client says?
This is a problem most commonly seen when there is a version mismatch. The mismatch may stem from your apworld not matching your sdkmod or the apworld used to generate the multiworld. This problem can occur most often because of miscommunication between a player and the host. The host may have grabbed a different version from the player (ex. bleeding edge vs newest stable version). However it happened, the player can usually fix this by changing out the mismatched file, whether it is their apworld or their sdkmod. If the problem persists, and the run is early enough, a regeneration may be in order and all parties involved should check to make sure everyone's files are in order. Also double-check that your yaml file is up-to-date; option names can change between versions and these changes may cause unintended issues in a run. If this problem still persists, please bring it up in the Discord channel.

### Can I do this with a character already in UVHM?
Not recommended. IDs for enemies and other entities in the world change between playthroughs, and the mod is only recommended for Normal runs right now. There are certain checks, like Vermivorous the Invincible or the Digistruct Peak chests 6 - 9 that require TVHM and UVHM (specifically OP5+) to get, but if you find yourself needing to get these checks, you may just send them or in the case of the chests, use the Ghost feature from Aplle's Borderlands Cheats to go get the chests yourself.

### Can I do this in Coop?
Coop is not recommeded right now at all. The only exceptions are the challenges that require coop stuff, but those can be done in spite of the issues the mod has with coop at the moment. Coop will be worked on in the future, but right now the solo experience is the focus.

### Is there any quirks I should know about?
Yes. If you are in a sync or an async and plan on saving and quitting and coming back to the game later, do not save and quit in Sanctuary. The Fast Travel room of Sanctuary is notorious for eating items that are dropped there. It is recommended to save and quit in any other place. S1 recommends the fast travel of Three Horns Divide because it is wide and open.

### An update got pushed, should I install the new version?
Only if you are starting a new run. The sdkmod and AP world must remain in-sync with the version you generated the world with.

### Where do I report issues?
You can message in the Discord or create an issue on GitHub. Please try to check if you are reporting a known issue on either the [release page](https://github.com/EdricY/Bouncy-Loot-God/releases) or searching in Discord. Make sure to include the version you are playing with the report!

## Development stuff (ignore if you're just wanting to play/test)

For developing the sdkmod, this is probably useful. Development things here are specific to Windows 11.
I probably can't help with a non-Windows development environment.

.../Steam/steamapps/common/Borderlands 2/Binaries/Win32/Plugins/unrealsdk.user.toml
```
[pyunrealsdk]
debugpy = true
pyexec_root = "C:\\path\\to\\repo\\BouncyLootGod\\sdk_mods"

[mod_manager]
extra_folders = [
   "C:\\path\\to\\repo\\BouncyLootGod\\sdk_mods"
]
```
In the console, use `pyexec BouncyLootGod\__init__.py` to re-execute the mod code. (You may still need to disable/re-enable the mod.)

If you don't want to run the Archipelago codebase from source, generate the `.apworld` file and open it or add it to your installed version of the Archipelago Launcher. Now just test it like it's live. The zip-it script makes this process faster: `python zip-it.py`

The folder locations can be overridden in `zi_my_dirs.py`. ex.  
`tpssdkmoddir = "E:\\Steam\\steamapps\\common\\BorderlandsPreSequel\\sdk_mods"`  
You can run `git update-index --skip-worktree zi_my_dirs.py` to avoid committing your local changes to that file.

Generation can be tested quickly by running the exe from command line (replace with your Archipelago path):
`C:\ProgramData\Archipelago\ArchipelagoGenerate.exe`  
or  
(cmd) `python zip-it.py deployap && C:\ProgramData\Archipelago\ArchipelagoGenerate.exe`  
(bash) `python zip-it.py deployap && /c/ProgramData/Archipelago/ArchipelagoGenerate.exe`

To test generation rules, one technique is to use plando. First, go to `C:\ProgramData\Archipelago\host.yaml` and set `plando_options` to `"items"` or `"bosses, items"`. Now add a testing placement to your player yaml such as...
```
  plando_items:
    - item: "Travel: Three Horns Divide"
      location: "Symbol SouthernShelfBay: Ice Flows Shipwreck"
      from_pool: true
      force: true
```
After generating, you can check the spoiler for if the rule was properly met.  
We might consider adding unit tests in the future.

To create files for release: `python zip-it.py`  
This puts borderlands2.apworld and BouncyLootGod.sdkmod into /dist, which are the files needed to play outside of development mode.

## More Links

[Trello Board](https://trello.com/b/y4WWZF3E/bl2-archipelago)  
[Discord](https://discord.com/channels/1085716850370957462/1522284807780831313)  
[Pop Tracker by DDogeOneeSama](https://github.com/DDogeOneeSama/Borderlands-2-PopTracker)  
[Interactive Maps](https://mapgenie.io/borderlands-2/maps/world)  
[Universal Tracker](https://github.com/FarisTheAncient/Archipelago/blob/tracker/worlds/tracker/docs/setup.md)

