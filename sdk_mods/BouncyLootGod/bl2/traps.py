import unrealsdk

def init_game_traps(): #TODO add game separation
    try:
        unrealsdk.load_package("TESTINGZONE_COMBAT")
        keep_alive(unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_SpiderantBlackQueen_Digi.Population.PopDef_SpiderantBlackQueen_Digi:PopulationFactoryBalancedAIPawn_0"))
        keep_alive(unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_LoaderUltimateBadass_Digi.Population.PopDef_LoaderUltimateBadass_Digi:PopulationFactoryBalancedAIPawn_1"))
        keep_alive(unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_MrMercy_Digi.Population.PopDef_MrMercy_Digi:PopulationFactoryBalancedAIPawn_0"))
        keep_alive(unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Skagzilla_Digi.Population.PopDef_Skagzlla_Digi:PopulationFactoryBalancedAIPawn_1"))
        keep_alive(unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Assassin1_Digi.Population.PopDef_Assassin1_Digi:PopulationFactoryBalancedAIPawn_0"))
        keep_alive(unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Assassin2_Digi.Population.PopDef_Assassin2_Digi:PopulationFactoryBalancedAIPawn_0"))
        keep_alive(unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Assassin3_Digi.Population.PopDef_Assassin3_Digi:PopulationFactoryBalancedAIPawn_0"))
        keep_alive(unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Assassin4_Digi.Population.PopDef_Assassin4_Digi:PopulationFactoryBalancedAIPawn_0"))

        unrealsdk.load_package("caverns_p")
        keep_alive(unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Population_Creeper.Population.PopDef_CreeperMix_Regular:PopulationFactoryBalancedAIPawn_0"))
        return True
    except:
        return False

def keep_alive(obj) -> None:
    obj.ObjectFlags |= 0x4000
    return

trap_pawn_def = (
    "PawnBalance_Assassin1_Digi",
    "PawnBalance_Assassin2_Digi",
    "PawnBalance_Assassin3_Digi",
    "PawnBalance_Assassin4_Digi",
    "Pawn_Balance_BigLoaderTurret_Digi",
    "PawnBalance_LoaderUltimateBadass_Digi",
    "PawnBalance_MrMercy_Digi",
    "PawnBalance_Skagzilla_Digi",
    "PawnBalance_SpiderantBlackQueen_Digi",
    "PawnBalance_SpiderantRoyalGuard_Digi",
    "PawnBalance_Creeper",
    "PawnBalance_CreeperBadass" # technically not this one, but it also gets kept alive.
)
def trigger_game_trap(trap_name, is_retry=False):
    pass
def get_game_spawn_trap(spawn_name):
    if spawn_name == "Black Queen":
        return [
            {
                "ai_pawn": "GD_SpiderantBlackQueen_Digi.Population.PopDef_SpiderantBlackQueen_Digi:PopulationFactoryBalancedAIPawn_0", "dists": [1000, -1000]
            }
        ]
    elif spawn_name == "Saturn":
        return [
            {
                "ai_pawn": "GD_LoaderUltimateBadass_Digi.Population.PopDef_LoaderUltimateBadass_Digi:PopulationFactoryBalancedAIPawn_1", "dists": [1000, -1000] 
            }
        ]
    elif spawn_name == "Doc Mercy":
        return [
            {
                "ai_pawn": "GD_MrMercy_Digi.Population.PopDef_MrMercy_Digi:PopulationFactoryBalancedAIPawn_0", "dists": [1000, -1000]
            }
        ]
    elif spawn_name == "Dukino's Mom":
        return [
            {
                "ai_pawn": "GD_Skagzilla_Digi.Population.PopDef_Skagzlla_Digi:PopulationFactoryBalancedAIPawn_1", "dists": [1000, -1000]
            }
        ]
    elif spawn_name == "Creepers":
        return [
            {
                "ai_pawn": "GD_Population_Creeper.Population.PopDef_CreeperMix_Regular:PopulationFactoryBalancedAIPawn_0", 
                "relative_pos": [
                    {"x":1000},
                    {"x":-1000},
                    {"y":1000},
                    {"y":-1000},
                    {"x":1000, "y":1000},
                    {"x":-1000, "y":1000},
                    {"x":1000, "y":-1000},
                    {"x":-1000, "y":-1000}
                ]
            }
        ]
    elif spawn_name == "Assassins":
        return [
            {
                "ai_pawn": "GD_Assassin1_Digi.Population.PopDef_Assassin1_Digi:PopulationFactoryBalancedAIPawn_0", "relative_pos": [{"x": 1000}]
            },
            {
                "ai_pawn": "GD_Assassin1_Digi.Population.PopDef_Assassin2_Digi:PopulationFactoryBalancedAIPawn_0", "relative_pos": [{"x": -1000}]
            },
            {
                "ai_pawn": "GD_Assassin1_Digi.Population.PopDef_Assassin3_Digi:PopulationFactoryBalancedAIPawn_0", "relative_pos": [{"y": 1000}]
            },
            {
                "ai_pawn": "GD_Assassin1_Digi.Population.PopDef_Assassin4_Digi:PopulationFactoryBalancedAIPawn_0", "relative_pos": [{"y": 1000}]
            },
        ]
    return None