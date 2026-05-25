# Bouncy-Loot-God
An Archipelago.gg integration for Borderlands 2 and Borderlands The Pre-Sequel

## Setup for playing

### Requirements
1. You should have the latest [BL2/TPS mod manager](https://github.com/bl-sdk/willow2-mod-manager) (3.7+) ([release page](https://github.com/bl-sdk/willow2-mod-manager/releases/tag/v3.7))

2. the latest version of [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) (0.6.7+) ([release page](https://github.com/ArchipelagoMW/Archipelago/releases/tag/0.6.7))

3. the sdk mod requires [coroutines](https://bl-sdk.github.io/willow2-mod-db/mods/coroutines/) (1.1+) ([direct download](https://github.com/juso40/bl2sdk-mods/raw/refs/heads/main/coroutines/coroutines.sdkmod))  
place it into the sdk_mods folder. A browser window will open if you still need to install this.

For any GitHub Release Page, scroll to the bottom of the release notes to find the files you want (under "Assets"). Don't download the source code by accident.

### Installation
1. Download the `borderlands2.apworld` (or `borderlands_tps.apworld`) and `BouncyLootGod.sdkmod` file from the [release page](https://github.com/EdricY/Bouncy-Loot-God/releases)
2. `BouncyLootGod.sdkmod` goes into `.../Steam/steamapps/common/Borderlands 2/sdk_mods/` (for BL2) OR `.../Steam/steamapps/common/BorderlandsPreSequel/sdk_mods/` (for TPS)
3. The `.apworld` file goes into `.../Archipelago/custom_worlds/` OR use the `Install APWorld` tool from the Archipelago Launcher OR simply double click the .apworld file. Restart your Archipelago launcher after installing the apworld.

more information on [sdk mod setup](https://bl-sdk.github.io/willow2-mod-db/faq/)  
more information on [apworld](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/apworld%20specification.md)

### Options yaml
Pick and download a file from [sample-yamls](/sample-yamls/). Heavy editing to the sample is not encouraged unless you know what you're doing. More samples coming soon.

#### Note on Options Creator
Only use the Options Creator if you are confident that you know what you're doing. Many options require you to know some location or item names, find them in archi_data.py.
[[current bl2 archi_data.py](https://github.com/EdricY/Bouncy-Loot-God/blob/main/sdk_mods/BouncyLootGod/bl2/archi_data.py)]  
[[current tps archi_data.py](https://github.com/EdricY/Bouncy-Loot-God/blob/main/sdk_mods/BouncyLootGod/bl_tps/archi_data.py)]  
 [[v0.5.3 archi_data.py](https://github.com/EdricY/Bouncy-Loot-God/blob/v0.5.3/sdk_mods/BouncyLootGod/archi_data.py)]  

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

If you open the game first, use the Mod Options menu to "Connect to Socket Server" once the Archipelago Client is open.

The mod is currently running the entire time it's enabled. Any character you "Continue" with will have their inventory checked.

If the game crashes when loading your character, please try disabling the mod, then loading your character, then enabling the mod from Esc > Mods > BouncyLootGod

### Note on versions
Ensure you use the same version for each of (1) the AP world used to generate the multiworld (2) the AP world for the "Borderlands 2 Client" you are connecting to (3) the sdkmod installed in your game mods folder. Do not update your AP world or sdkmod mid-run.

### Note on disabling
This mod does not properly clean up after itself when you disable it. Some values may remain modified after turning the mod off, and won't be reset until fully restarting the game (not just save-quit).
**Before doing any non-archipelago play in Borderlands 2, Disable the mod and Restart your game!!!**

## FAQ
### What gets randomized?
Items include your in-game abilities: melee, jump, crouch, sprint, skill points, equip guns, and more. Edit your starting inventory for anything you would like to start with.  
Locations include quest completions, opening Red Chests, finding Vault Symbols, checking Vending Machines, completing BAR Challenges, and rarity-based checks (finding gear of a certain rarity for the first time).

### What version do I play?
For the most stable experience play the [latest stable version](https://github.com/EdricY/Bouncy-Loot-God/releases/latest).  
For the latest features and if you would like to participate in testing and reporting issues, play the bleeding edge version (find it on the [release page](https://github.com/EdricY/Bouncy-Loot-God/releases)).

### What yaml do I choose?
For syncs lasting around 2 hours, `bl2-basegame-short.yaml` is a good, well-tested choice.  
Specific yamls for other DLCs are available, and should also be sync viable.  
For longer runs, `bl2-basegame-med.yaml` goes through the full base game story and should be beatable in about 8 hours.

### What other mods do you recommend?
Playing with other mods is not officially supported (yet!). But people have found the following mods useful:  
[Always On Level](https://github.com/EdricY/EdricY-BL2-sdk-mods/tree/main/AlwaysOnLevel)  
[Apples Borderlands Cheats](https://bl-sdk.github.io/willow2-mod-db/mods/apples-borderlands-cheats/)  
[Dialog Skipper](https://bl-sdk.github.io/willow2-mod-db/mods/dialog-skipper/)  
[EXP Adjuster](https://bl-sdk.github.io/willow2-mod-db/mods/expadjuster/)  
[Jump to Level Challenges](https://bl-sdk.github.io/willow2-mod-db/mods/jumptolevelchallenges/)  
[Loot Collector](https://bl-sdk.github.io/willow2-mod-db/mods/lootcollector/)  

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
### Why isn't x gun y rarity?
If you want specifics, currently "Unique" for guns specifically means Blue, Purple, or E-Tech with red text. "Unique" for other gear is checked against a specific list.  
Feel free to report these issues, but if it seems like a matter of opinion or you're just trying to flex your knowledge of Borderlands guns, you will be ignored. Ex. Gearbox white guns have been decided to be labeled White, not Unique. Blood of Terramorphous is considered Unique for now.

### The mission displays exp but I didn't get any?
When you receive a mission reward from the multiworld, it should give you no exp. If you don't open your menu within 5 seconds of receiving it in game, it may display the exp numbers without granting you that amount of experience.

### Can I use skill points before level 5?
You can but it's a little weird. It'll still have the greyed out look, but it works. Your skill trees will look normal again after level 5.

### I received a Travel item can I go there early?
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
This is a problem most commonly seen when there is a mismatch. The mismatch may stem from your apworld not matching your sdkmod. It can be because your apworld is different from the one used to generate the multiworld. This problem can occur most often because of miscommunication between a player and the host. The host may not know the exact version the player intended and may grab the newest bleeding edge when you were going to use the newest stable version. However this may occur, the player may generally fix this via changing out the mismatched file, whether it is their apworld or their sdkmod. If the problem persists, and the run is early enough, a regeneration may be in order and all parties involved should check to make sure everyone's files are in order. Also as another point of order, make sure that your yaml file is an updated version; verbiage has changed between versions and these changes may cause unintended issues in a run. If this problem still persists, bring it up in the Discord channel.

### An update got pushed, should I install the new version?
Only if you are starting a new run. The sdkmod and AP world must remain in-sync with the version you generated the world with.

### Where do I report issues?
You can message in the Discord or create an issue on GitHub. Please try to check if you are reporting a known issue on either the [release page](https://github.com/EdricY/Bouncy-Loot-God/releases) or searching in Discord.

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
[Discord](https://discord.com/channels/1085716850370957462/1164256699608219698)  
[Pop Tracker by DDogeOneeSama](https://github.com/DDogeOneeSama/Borderlands-2-PopTracker)  
[Interactive Maps](https://mapgenie.io/borderlands-2/maps/world)  
[Universal Tracker](https://github.com/FarisTheAncient/Archipelago/blob/tracker/worlds/tracker/docs/setup.md)

