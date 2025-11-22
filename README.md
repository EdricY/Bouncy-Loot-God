# Bouncy-Loot-God

## Setup
You should have the latest [BL2 mod manager](https://bl-sdk.github.io/willow2-mod-db/) set up
([github](https://github.com/bl-sdk/willow2-mod-manager))

and the latest version of [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases)

download borderlands2.apworld file and BouncyLootGod.sdkmod file from the [release page](https://github.com/EdricY/Bouncy-Loot-God/releases)

.sdkmod goes into `Steam/steamapps/common/Borderlands 2/sdk_mods/`

.apworld goes into `Archipelago/custom_worlds/` OR use the `Install APWorld` tool from the Archipelago Launcher.

for more information on sdk mod setup: https://bl-sdk.github.io/willow2-mod-db/faq/

for more information on apworld: https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/apworld%20specification.md

this mod requires coroutines https://bl-sdk.github.io/willow2-mod-db/mods/coroutines/

Options are not done at all yet. blgsample.yaml is included, simply change the name for your desired slot name.

To Generate a world: Archipelago Client > Browse Files > Players > insert yaml files here. Then, Archipelago Client > Generate

The outputted .zip can be uploaded at https://archipelago.gg/uploads to create a room.

With a multiworld running, Open "Borderlands 2 Client" from the Archipelago Launcher, connect to the multiworld. Then open Borderlands 2 and enable the mod.

The mod is currently running the entire time it's enabled. Any character you "Continue" with will have their inventory checked.

Backup your BL2 characters before proceeding! They are located at Documents/my games/Borderlands 2/WillowGame/SaveData/...

Before doing any non-archipelago play in Borderlands 2, Disable the mod and Restart your game!!!

## Development stuff

For developing the sdkmod, this is probably useful. I'm development things here are specific to Windows 11.
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
This doesn't seem to update other imported files, so if you made changes to files other than `__init__.py`, you will probably need to restart the game.

For developing the AP world, I don't have a good process haha... I just have the Archipelago project open in PyCharm and copy the files over to commit.  
You could probably create a symlink or something similar within Archipelago/custom_worlds to point to worlds/borderlands2 in this repo.

To create files for release: `python zip-it.py`  
This puts borderlands2.apworld and BouncyLootGod.sdkmod into /dist, which are the files needed to play outside of development mode.

TODO:
- avoid naming conflicts with other bl2 development: rename "Borderlands 2" and "bl2", replace with "Bouncy Loot God" and "blg"
- archi yaml options
- archi docs
- add checks to enemy drops
- run on specified character only
- automate zip process? (tar from bash did not work)
