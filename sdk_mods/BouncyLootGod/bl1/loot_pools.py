from unrealsdk import find_class, find_object
from unrealsdk.unreal import UObject
from mods_base import get_pc

# TODO: unused so far

rarity_levels = {
    "Common": [2,4],
    "Uncommon": [5,10],
    "Rare": [11,15],
    "VeryRare": [16,49],
}

item_pool_default = find_class('ItemPool').ClassDefaultObject
pool = find_object("ItemPoolDefinition", "gd_itempools.TestPools.All_Com_Decks")

def spawn_item(pool_def:UObject,pawn:UObject,awesome_level:int) -> UObject:
    _, new_items = item_pool_default.SpawnBalancedInventoryFromPool(
                    pool_def, pawn.GetGameStage(), int(awesome_level), pawn, []
                    )
    return new_items[0]

def drop_item_of_rarity(item_pool:UObject, rarity:str):
    rarity_min, rarity_max = rarity_levels[rarity]
    for i in range(1000):
        item = spawn_item(item_pool,get_pc().Pawn,0)
        item_rarity = item.CalculateItemRarityLevel()
        if item_rarity >= rarity_min and item_rarity <= rarity_max:
            item.DropFrom(get_pc().Pawn.Location, IGNORE_STRUCT)
            break

# drop_item_of_rarity(pool, "VeryRare")
