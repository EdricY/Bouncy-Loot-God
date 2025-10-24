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

Options are not done at all yet. blgsample.yaml is included, simply change the name for your desired slot name.

TODO:
- avoid naming conflicts with other bl2 development: rename "Borderlands 2 / bl2", replace with "Bouncy Loot God / blg"
- archi yaml options
- archi docs
- add checks to enemy drops
- automate zip process? (tar from bash did not work)
