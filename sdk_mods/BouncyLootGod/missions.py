import datetime
import unrealsdk
import unrealsdk.unreal as unreal
from unrealsdk.hooks import Type

from mods_base import get_pc
from ui_utils import show_chat_message, show_hud_message



mission_name_to_ue_str = {
"Sanctuary: The Road to Sanctuary":                          "GD_Episode03.M_Ep3_CatchARide",
"Sanctuary: Plan B":                                         "GD_Episode04.M_Ep4_WelcomeToSanctuary",
"Frostburn: Hunting the Firehawk":                           "GD_Episode05.M_Ep5_ThePhoenix",
"EndOfTheLine: A Train to Catch":                            "GD_Episode07.M_Ep7_ATrainToCatch",
"Fridge: Rising Action":                                     "GD_Episode08.M_Ep8_SanctuaryTakesOff",
"Highlands: Bright Lights, Flying City":                     "GD_Episode09.M_Ep9_GetBackToSanctuary",
"Badlands: Data Mining":                                     "GD_Episode15.M_Ep15_CharacterAssassination",
"Lynchwood: Breaking the Bank":                              "GD_Z2_TheBankJob.M_TheBankJob",
"Eridium Blight: Kill Yourself":                             "GD_Z3_KillYourself.M_KillYourself",
"Boneyard: This Just In":                                    "GD_Z3_ThisJustIn.M_ThisJustIn",
"WindshearWaste: My First Gun":                              "GD_Episode01.M_Ep1_Champion",
"HolySpirits: Clan War: Wakey Wakey":                        "GD_Z2_WakeyWakey.M_WakeyWakey",
"SouthernShelf: Handsome Jack Here!":                        "GD_Z1_HandsomeJackHere.M_HandsomeJackHere",
"SouthernShelf: This Town Ain't Big Enough":                 "GD_Z1_ThisTown.M_ThisTown",
"SouthernShelf: Shielded Favors":                            "GD_Episode02.M_Ep2b_Henchman",
"SouthernShelfBay: Symbiosis":                               "GD_Z1_Symbiosis.M_Symbiosis",
"Thousand Cuts: Defend Slab Tower":                          "GD_Z2_DefendSlabTower.M_DefendSlabTower",
"Highlands: Best Mother's Day Ever":                         "GD_Z2_MothersDayGift.BalanceDefs.M_MothersDayGift",
"Fridge: Note for Self-Person":                              "gd_z2_notetoself.M_NoteToSelf",
"Opportunity: The Bane":                                     "GD_Z3_Bane.M_Bane",
"Dust: The Good, the Bad, and the Mordecai":                 "GD_Z3_GoodBadMordecai.M_GoodBadMordecai",
"Sawtooth Cauldron: The Lost Treasure":                      "GD_Z3_LostTreasure.M_LostTreasure",
"Highlands: Arms Dealing":                                   "GD_Z2_ArmsDealer.M_ArmsDealer",
"Lynchwood: 3:10 to Kaboom":                                 "GD_Z2_BlowTheBridge.M_BlowTheBridge",
"Eridium Blight: Customer Service":                          "GD_Z3_CustomerService.M_CustomerService",
"ThreeHornsValley: Neither Rain nor Sleet nor Skags":        "gd_z3_neitherrainsleet.M_NeitherRainSleetSkags",
"SouthernShelf: Blindsided":                                 "GD_Episode02.M_Ep2_Henchman",
"SouthernShelf: Cleaning up the Berg":                       "GD_Episode02.M_Ep2a_MoreGuns",
"SouthernShelf: Best Minion Ever":                           "GD_Episode02.M_Ep2c_Henchman",
"Ramparts: A Dam Fine Rescue":                               "GD_Episode06.M_Ep6_RescueRoland",
"WildlifePreserve: Wildlife Preservation":                   "GD_Episode10.M_Ep10_BirdISTheWord",
"Thousand Cuts: The Once and Future Slab":                   "GD_Episode11.M_Ep11_LikeATonOf",
"Opportunity: The Man Who Would Be Jack":                    "GD_Episode12.M_Ep12_BecomingJack",
"Control Core Angel: Where Angels Fear to Tread":            "GD_Episode13.M_Ep13_KillAngel",
"Control Core Angel: Where Angels Fear to Tread (Part 2)":   "GD_Episode14.M_Ep14_SearchingTheWreckage",
"Sawtooth Cauldron: Toil and Trouble":                       "GD_Episode16.M_Ep16_LockAndLoad",
"WarriorVault: The Talon of God":                            "GD_Episode17.M_Ep17_KillJack",
"Southpaw: Assassinate the Assassins":                       "GD_Z1_Assasinate.M_AssasinateTheAssassins",
"SouthernShelf: Bad Hair Day":                               "GD_Z1_BadHairDay.M_BadHairDay",
"Control Core Angel: Bearer of Bad News":                    "GD_Z1_BearerBadNews.M_BearerBadNews",
"Sanctuary: BFFs":                                           "GD_Z1_BFFs.M_BFFs",
"Frostburn Canyon: Cult Following: Eternal Flame":           "GD_Z1_ChildrenOfPhoenix.M_EternalFlame",
"Frostburn Canyon: Cult Following: Lighting the Match":      "GD_Z1_ChildrenOfPhoenix.M_LightingTheMatch",
"Frostburn Canyon: Cult Following: The Enkindling":          "GD_Z1_ChildrenOfPhoenix.M_TheEnkindling",
"Sanctuary: Claptrap's Secret Stash":                        "GD_Z1_ClapTrapStash.M_ClapTrapStash",
"Tundra Express: You Are Cordially Invited: Party Prep":     "GD_Z1_CordiallyInvited.M_CordiallyInvited",
"EndOfTheLine: The Ice Man Cometh":                          "GD_Z1_IceManCometh.M_IceManCometh",
"ThreeHornsDivide: In Memoriam":                             "GD_Z1_InMemoriam.M_InMemoriam",
"Tundra Express: Mighty Morphin'":                           "GD_Z1_MightyMorphin.M_MightyMorphin",
"Tundra Express: Mine, All Mine":                            "GD_Z1_MineAllMine.M_MineAllMine",
"CausticCaverns: Minecart Mischief":                         "gd_z1_minecartmischief.M_MinecartMischief",
"Sanctuary: The Name Game":                                  "GD_Z1_NameGame.M_NameGame",
"Tundra Express: No Hard Feelings":                          "gd_z1_nohardfeelings.M_NoHardFeelings",
"ThreeHornsValley: No Vacancy":                              "GD_Z1_NoVacancy.BalanceDefs.M_NoVacancy",
"CausticCaverns: Perfectly Peaceful":                        "GD_Z1_PerfectlyPeaceful.M_PerfectlyPeaceful",
"Sanctuary: Rock, Paper, Genocide: Slag Weapons!":           "GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Amp",
"Sanctuary: Rock, Paper, Genocide: Fire Weapons!":           "GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Fire",
"Sanctuary: Do No Harm":                                     "GD_Z1_Surgery.M_PerformSurgery",
"Tundra Express: The Pretty Good Train Robbery":             "GD_Z1_TrainRobbery.M_TrainRobbery",
"Sanctuary: Won't Get Fooled Again":                         "GD_Z1_WontGetFooled.M_WontGetFooled",
"Eridium Blight: A Real Boy: Face Time":                     "GD_Z2_ARealBoy.M_ARealBoy_ArmLeg",
"Eridium Blight: A Real Boy: Clothes Make the Man":          "GD_Z2_ARealBoy.M_ARealBoy_Clothes",
"Sanctuary: Claptrap's Birthday Bash!":                      "GD_Z2_ClaptrapBirthdayBash.M_ClaptrapBirthdayBash",
"Dust: Clan War: Zafords vs. Hodunks":                       "GD_Z2_DuelingBanjos.M_DuelingBanjos",
"WildlifePreserve: Animal Rights":                           "GD_Z2_FreeWilly.M_FreeWilly",
"Opportunity: Hell Hath No Fury":                            "GD_Z2_HellHathNo.M_FloodingHyperionCity",
"Opportunity: Home Movies":                                  "GD_Z2_HomeMovies.M_HomeMovies",
"Opportunity: Statuesque":                                   "GD_Z2_HyperionStatue.M_MonumentsVandalism",
"Lynchwood: Showdown":                                       "GD_Z2_KillTheSheriff.M_KillTheSheriff",
"HolySpirits: Clan War: End of the Rainbow":                 "GD_Z2_LuckysDirtyMoney.M_LuckysDirtyMoney",
"Highlands: Clan War: Starting the War":                     "GD_Z2_MeetWithEllie.M_MeetWithEllie",
"Highlands: The Overlooked: Medicine Man":                   "GD_Z2_Overlooked.M_Overlooked",
"Highlands: The Overlooked: Shields Up":                     "GD_Z2_Overlooked2.M_Overlooked2",
"Highlands: The Overlooked: This Is Only a Test":            "GD_Z2_Overlooked3.M_Overlooked3",
"Thousand Cuts: Poetic License":                             "GD_Z2_PoeticLicense.M_PoeticLicense",
"Dust: Clan War: First Place":                               "GD_Z2_RiggedRace.M_RiggedRace",
"CausticCaverns: Safe and Sound":                            "GD_Z2_SafeAndSound.M_SafeAndSound",
"Lynchwood: Animal Rescue: Shelter":                         "GD_Z2_Skagzilla2.M_Skagzilla2_Den",
"Highlands: Slap-Happy":                                     "GD_Z2_SlapHappy.M_SlapHappy",
"Highlands: Stalker of Stalkers":                            "GD_Z2_TaggartBiography.M_TaggartBiography",
"Terramorphous Peak: You. Will. Die. (Seriously.)":          "GD_Z2_ThresherRaid.M_ThresherRaid",
"Dust: Clan War: Trailer Trashing":                          "GD_Z2_TrailerTrashin.M_TrailerTrashin",
"Opportunity: Written by the Victor":                        "GD_Z2_WrittenByVictor.M_WrittenByVictor",
"Sawtooth Cauldron: Capture the Flags":                      "GD_Z3_CaptureTheFlags.M_CaptureTheFlags",
"Sawtooth Cauldron: The Chosen One":                         "GD_Z3_ChosenOne.M_ChosenOne",
"Fridge: The Cold Shoulder":                                 "GD_Z3_ColdShoulder.M_ColdShoulder",
"Eridium Blight: To Grandmother's House We Go":              "GD_Z3_GrandmotherHouse.M_GrandmotherHouse",
"Sawtooth Cauldron: The Great Escape":                       "GD_Z3_GreatEscape.M_GreatEscape",
"Lynchwood: Hungry Like the Skag":                           "GD_Z3_HungryLikeSkag.M_HungryLikeSkag",
"Thousand Cuts: Hyperion Contract #873":                     "GD_Z3_HyperionContract873.M_HyperionContract873",
"ThreeHornsValley: Medical Mystery":                         "GD_Z3_MedicalMystery.M_MedicalMystery",
"ThreeHornsValley: Medical Mystery: X-Com-municate":         "GD_Z3_MedicalMystery2.M_MedicalMystery2",
"Ramparts: Out of Body Experience":                          "GD_Z3_OutOfBody.M_OutOfBody",
"OreChasm: Hyperion Slaughter: Round 1":                    "GD_Z3_RobotSlaughter.M_RobotSlaughter_1",
"OreChasm: Hyperion Slaughter: Round 2":                    "GD_Z3_RobotSlaughter.M_RobotSlaughter_2",
"OreChasm: Hyperion Slaughter: Round 3":                    "GD_Z3_RobotSlaughter.M_RobotSlaughter_3",
"OreChasm: Hyperion Slaughter: Round 4":                    "GD_Z3_RobotSlaughter.M_RobotSlaughter_4",
"OreChasm: Hyperion Slaughter: Round 5":                    "GD_Z3_RobotSlaughter.M_RobotSlaughter_5",
"Fridge: Swallowed Whole":                                   "GD_Z3_SwallowedWhole.M_SwallowedWhole",
"Dust: Too Close For Missiles":                              "gd_z3_toocloseformissiles.M_TooCloseForMissiles",
"Badlands: Uncle Teddy":                                     "GD_Z3_UncleTeddy.M_UncleTeddy",
"Badlands: Get to Know Jack":                                "GD_Z3_YouDontKnowJack.M_YouDontKnowJack",
"Tundra Express: You Are Cordially Invited: Tea Party":      "GD_Z1_CordiallyInvited.M_CordiallyInvited03",
"Tundra Express: You Are Cordially Invited: RSVP":           "GD_Z1_CordiallyInvited.M_CordiallyInvited02",
"Sanctuary: Rock, Paper, Genocide: Corrosive Weapons!":      "GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Corrosive",
"Sanctuary: Rock, Paper, Genocide: Shock Weapons!":          "GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Shock",
"Lynchwood: Animal Rescue: Medicine":                        "GD_Z2_Skagzilla2.M_Skagzilla2_Pup",
"BloodshotStronghold: Splinter Group":                       "GD_Z2_SplinterGroup.M_SplinterGroup",
"Thousand Cuts: Shoot This Guy in the Face":                 "GD_Z1_ShootMeInTheFace.M_ShootMeInTheFace",
"Fink's Slaughterhouse: Bandit Slaughter: Round 1":          "GD_Z1_BanditSlaughter.M_BanditSlaughter1",
"Fink's Slaughterhouse: Bandit Slaughter: Round 2":          "GD_Z1_BanditSlaughter.M_BanditSlaughter2",
"Fink's Slaughterhouse: Bandit Slaughter: Round 3":          "GD_Z1_BanditSlaughter.M_BanditSlaughter3",
"Fink's Slaughterhouse: Bandit Slaughter: Round 4":          "GD_Z1_BanditSlaughter.M_BanditSlaughter4",
"Fink's Slaughterhouse: Bandit Slaughter: Round 5":          "GD_Z1_BanditSlaughter.M_BanditSlaughter5",
"CreatureSlaughter: Creature Slaughter: Round 1":            "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_1",
"CreatureSlaughter: Creature Slaughter: Round 2":            "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_2",
"CreatureSlaughter: Creature Slaughter: Round 3":            "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_3",
"CreatureSlaughter: Creature Slaughter: Round 4":            "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_4",
"CreatureSlaughter: Creature Slaughter: Round 5":            "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_5",
"Sawtooth Cauldron: Monster Mash (Part 1)":                  "GD_Z3_MonsterMash1.M_MonsterMash1",
"Sawtooth Cauldron: Monster Mash (Part 2)":                  "GD_Z3_MonsterMash2.M_MonsterMash2",
"Boneyard: Monster Mash (Part 3)":                           "GD_Z3_MonsterMash3.M_MonsterMash3",
"Highlands: Torture Chairs":                                 "GD_Z1_HiddenJournalsFurniture.M_HiddenJournalsFurniture",
"WildlifePreserve: Doctor's Orders":                         "GD_Z2_DoctorsOrders.M_DoctorsOrders",
"Dust: Rakkaholics Anonymous":                               "GD_Z2_Rakkaholics.M_Rakkaholics",
"Highlands: Hidden Journals":                                "GD_Z3_HiddenJournals.M_HiddenJournals",
"Dust: Positive Self Image":                                 "GD_Z3_PositiveSelfImage.M_PositiveSelfImage",
"Frostburn Canyon: Cult Following: False Idols":             "GD_Z1_ChildrenOfPhoenix.M_FalseIdols",
"HolySpirits: Clan War: Reach the Dead Drop":                "GD_Z2_LuckysDirtyMoney.M_FamFeudDeadDrop",
"Eridium Blight: A Real Boy: Human":                         "GD_Z2_ARealBoy.M_ARealBoy_Human",
"Lynchwood: Demon Hunter":                                   "GD_Z2_DemonHunter.M_DemonHunter",
"Thousand Cuts: Rocko's Modern Strife":                      "GD_Z2_RockosModernStrife.M_RockosModernStrife",
"Lynchwood: Animal Rescue: Food":                            "GD_Z2_Skagzilla2.M_Skagzilla2_Adult",
"MercenaryDay: Get Frosty":                                  "GD_Allium_KillSnowman.M_KillSnowman",
"GlutGulch: The Hunger Pangs":                               "GD_Allium_TG_Plot_Mission01.M_Allium_ThanksgivingMission01",
"MercenaryDay: Special Delivery":                            "GD_Allium_Delivery.M_Delivery",
"GlutGulch: Grandma Flexington's Story":                     "GD_Allium_GrandmaFlexington.M_ListenToGrandma",
"GlutGulch: Grandma Flexington's Story: Raid Difficulty":    "GD_Allium_Side_GrandmaRaid.M_ListenToGrandmaRaid",
"FFSIntroSanctuary: The Dawn of New Pandora":                "GD_Anemone_Plot_Mission010.M_Anemone_PlotMission010",
"DahlAbandon: Winging It":                                   "GD_Anemone_Plot_Mission025.M_Anemone_PlotMission025",
"DahlAbandon: Spore Chores":                                 "GD_Anemone_Plot_Mission020.M_Anemone_PlotMission020",
"TheBurrows: A Hard Place":                                  "GD_Anemone_Plot_Mission030.M_Anemone_PlotMission030",
"HeliosFallen: Shooting The Moon":                           "GD_Anemone_Plot_Mission040.M_Anemone_PlotMission040",
"Mt.Scarab: The Cost of Progress":                           "GD_Anemone_Plot_Mission050.M_Anemone_PlotMission050",
"FFSBossFight: Paradise Found":                              "GD_Anemone_Plot_Mission060.M_Anemone_PlotMission060",
"Mt.Scarab: Claptocurrency":                                 "GD_Anemone_Side_Claptocurrency.M_Claptocurrency",
"HeliosFallen: BFFFs":                                       "GD_Anemone_Side_EyeSnipers.M_Anemone_EyeOfTheSnipers",
"DahlAbandon: Hypocritical Oath":                            "GD_Anemone_Side_HypoOathPart1.M_HypocriticalOathPart1",
"HeliosFallen: Cadeuceus":                                   "GD_Anemone_Side_HypoOathPart2.M_HypocriticalOathPart2",
"FFSBossFight: My Brittle Pony":                             "GD_Anemone_Side_MyBrittlePony.M_Anemone_MyBrittlePony",
"DahlAbandon: The Oddest Couple":                            "GD_Anemone_Side_OddestCouple.M_Anemone_OddestCouple",
"WrithingDeep: A Most Cacophonous Lure":                     "GD_Anemone_Side_RaidBoss.M_Anemone_CacophonousLure",
"HeliosFallen: Sirentology":                                 "GD_Anemone_Side_Sirentology.M_Anemone_Sirentology",
"DahlAbandon: Space Cowboy":                                 "GD_Anemone_Side_SpaceCowboy.M_Anemone_SpaceCowboy",
"DahlAbandon: The Vaughnguard":                              "GD_Anemone_Side_VaughnPart1.M_Anemone_VaughnPart1",
"HeliosFallen: The Hunt is Vaughn":                          "GD_Anemone_Side_VaughnPart2.M_Anemone_VaughnPart2",
"FFSBossFight: Chief Executive Overlord":                    "GD_Anemone_Side_VaughnPart3.M_Anemone_VaughnPart3",
"Mt.Scarab: Echoes of the Past":                             "GD_Anemone_Side_Echoes.M_Anemone_EchoesOfThePast",
"FlamerockRefuge: A Role-Playing Game":                     "GD_Aster_Plot_Mission01.M_Aster_PlotMission01",
"MinesOfAvarice: Dwarven Allies":                            "GD_Aster_Plot_Mission03.M_Aster_PlotMission03",
"Agony: The Amulet":                                         "GD_Aster_AmuletDoNothing.M_AmuletDoNothing",
"MinesOfAvarice: The Claptrap's Apprentice":                 "GD_Aster_ClaptrapApprentice.M_ClaptrapApprentice",
"MinesOfAvarice: The Beard Makes The Man":                   "GD_Aster_ClapTrapBeard.M_ClapTrapBeard",
"MinesOfAvarice: My Kingdom for a Wand":                     "GD_Aster_ClaptrapWand.M_WandMakesTheMan",
"Immortal Woods: Critical Fail":                             "GD_Aster_CriticalFail.M_CriticalFail",
"Lair of Infinite Agony: My Dead Brother":                   "GD_Aster_DeadBrother.M_MyDeadBrother",
"Immortal Woods: Lost Souls":                                "GD_Aster_DemonicSouls.M_DemonicSouls",
"TheForest: Ell in Shining Armor":                           "GD_Aster_EllieDress.M_EllieDress",
"FlamerockRefuge: Fake Geek Guy":                            "GD_Aster_FakeGeekGuy.M_FakeGeekGuy",
"FlamerockRefuge: Feed Butt Stallion":                       "GD_Aster_FeedButtStallion.M_FeedButtStallion",
"HatredsShadow: Loot Ninja":                                 "GD_Aster_LootNinja.M_LootNinja",
"Immortal Woods: MMORPGFPS":                                 "GD_Aster_MMORPGFPS.M_MMORPGFPS",
"FlamerockRefuge: Pet Butt Stallion":                        "GD_Aster_PetButtStallion.M_PettButtStallion",
"Immortal Woods: Denial, Anger, Initiative":                 "GD_Aster_Plot_Mission02.M_Aster_PlotMission02",
"HatredsShadow: A Game of Games":                            "GD_Aster_Plot_Mission04.M_Aster_PlotMission04",
"Lair of Infinite Agony: Post-Crumpocalyptic":               "GD_Aster_Post-Crumpocalyptic.M_Post-Crumpocalyptic",
"WingedStorm: Raiders of the Last Boss":                     "GD_Aster_RaidBoss.M_Aster_RaidBoss",
"FlamerockRefuge: Roll Insight":                             "GD_Aster_RollInsight.M_RollInsight",
"Forest: Tree Hugger":                                       "GD_Aster_TreeHugger.M_TreeHugger",
"HatredsShadow: Winter is a Bloody Business":                "GD_Aster_WinterIsComing.M_WinterIsComing",
"Murderlin's Temple: Magic Slaughter: Round 1":              "GD_Aster_TempleSlaughter.M_TempleSlaughter1",
"Murderlin's Temple: Magic Slaughter: Round 2":              "GD_Aster_TempleSlaughter.M_TempleSlaughter2",
"Murderlin's Temple: Magic Slaughter: Round 3":              "GD_Aster_TempleSlaughter.M_TempleSlaughter3",
"Murderlin's Temple: Magic Slaughter: Round 4":              "GD_Aster_TempleSlaughter.M_TempleSlaughter4",
"Murderlin's Temple: Magic Slaughter: Round 5":              "GD_Aster_TempleSlaughter.M_TempleSlaughter5",
"Murderlin's Temple: Magic Slaughter: Badass Round":         "GD_Aster_TempleSlaughter.M_TempleSlaughter6Badass",
"Murderlin's Temple: The Magic of Childhood":                "GD_Aster_TempleTower.M_TempleTower",
"Murderlin's Temple: Find Murderlin's Temple":               "GD_Aster_TempleSlaughter.M_TempleSlaughterIntro",
"UnassumingDocks: The Sword in The Stoner":                  "GD_Aster_SwordInStone.M_SwordInStoner",
"Hallowed Hollow: The Bloody Harvest":                       "GD_FlaxMissions.M_BloodHarvest",
"Hallowed Hollow: Trick or Treat":                           "GD_FlaxMissions.M_TrickOrTreat",
"BadassCrater: Highway To Hell":                             "GD_IrisEpisode01.M_IrisEp1_HighwayToHell",
"TorgueArena: Tier 2 Battle: Appetite for Destruction":      "GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoP2",
"TorgueArena: Tier 3 Battle: Appetite for Destruction":      "GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoP3",
"TorgueArena: Tier 3 Rematch: Appetite for Destruction":     "GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoPR3",
"Pyro Pete's Bar: Tier 2 Battle: Bar Room Blitz":            "GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFight2",
"Pyro Pete's Bar: Tier 3 Battle: Bar Room Blitz":            "GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFight3",
"Pyro Pete's Bar: Battle: Bar Room Blitz":                   "GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFight",
"Pyro Pete's Bar: Tier 3 Rematch: Bar Room Blitz":           "GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFightR3",
"BadassCrater: Tier 2 Battle: The Death Race":               "GD_IrisEpisode04_Battle.M_IrisEp4Battle_Race2",
"BadassCrater: Tier 3 Battle: The Death Race":               "GD_IrisEpisode04_Battle.M_IrisEp4Battle_Race4",
"BadassCrater: Battle: The Death Race":                      "GD_IrisEpisode04_Battle.M_IrisEp4Battle_Race",
"BadassCrater: Tier 3 Rematch: The Death Race":              "GD_IrisEpisode04_Battle.M_IrisEp4Battle_RaceR4",
"Forge: Tier 2 Battle: Twelve O' Clock High":                "GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyro2",
"Forge: Tier 3 Battle: Twelve O' Clock High":                "GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyro3",
"Forge: Battle: Twelve O' Clock High":                       "GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyro",
"Forge: Tier 3 Rematch: Twelve O' Clock High":               "GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyroR3",
"Beatdown: Mother-Lover":                                    "GD_IrisDL2_DontTalkAbtMama.M_IrisDL2_DontTalkAbtMama",
"Beatdown: Number One Fan":                                  "GD_IrisDL2_PumpkinHead.M_IrisDL2_PumpkinHead",
"Forge: Commercial Appeal":                                  "GD_IrisDL3_CommAppeal.M_IrisDL3_CommAppeal",
"Forge: My Husband the Skag":                                "GD_IrisDL3_MySkag.M_IrisDL3_MySkag",
"Forge: Say That To My Face":                                "GD_IrisDL3_PSYouSuck.M_IrisDL3_PSYouSuck",
"Torgue Arena: Welcome To The Jungle":                       "GD_IrisEpisode01.M_IrisEp1_WTTJ",
"Torgue Arena: Battle: Appetite for Destruction":            "GD_IrisEpisode02.M_IrisEp2_CultOfPersonality",
"Pyro Pete's Bar: Burn, Baby, Burn":                         "GD_IrisEpisode02.M_IrisEp2_FindBattle",
"Pyro Pete's Bar: Chop Suey":                                "GD_IrisEpisode03.M_IrisEp3_ChopSuey",
"BadassBar: A Montage":                                      "GD_IrisEpisode04.M_IrisEp4_AMontage",
"SouthernRaceway: Get Your Motor Running":                   "GD_IrisEpisode04.M_IrisEp4_CherryBomb",
"Torgue Arena Ring: Eat Cookies and Crap Thunder":           "GD_IrisEpisode04.M_IrisEp4_TrainningWithTina",
"Forge: Knockin' on Heaven's Door":                          "GD_IrisEpisode05.M_HeavensDoor",
"Forge: Breaking and Entering":                              "GD_IrisEpisode05.M_IrisEp5_CageMatch",
"Forge: Kickstart My Heart":                                 "GD_IrisEpisode05.M_IrisEp5_KickStartMyHeart",
"Torgue Arena: Long Way To The Top":                         "GD_IrisEpisode06.M_IrisEp6_LongWayToTheTop",
"SouthernRaceway: Gas Guzzlers":                             "GD_IrisHUB_GasGuzzlers.M_IrisHUB_GasGuzzlers",
"SouthernRaceway: Matter Of Taste":                          "GD_IrisHUB_MatterOfTaste.M_IrisHUB_MatterOfTaste",
"SouthernRaceway: Monster Hunter":                           "GD_IrisHUB_MonsterHunter.M_IrisHUB_MonsterHunter",
"SouthernRaceway: Interview with a Vault Hunter":            "GD_IrisHUB_SmackTalk.M_IrisHUB_SmackTalk",
"BadassBar: Walking the Dog":                                "GD_IrisHUB_WalkTheDog.M_IrisHUB_WalkTheDog",
"Pyro Pete's Bar: Pete the Invincible":                      "GD_IrisRaidBoss.M_Iris_RaidPete",
"Beatdown: Totally Recall":                                  "GD_IrisDL2_ProductRecall.M_IrisDL2_ProductRecall",
"SouthernRaceway: Everybody Wants to be Wanted":             "GD_IrisHUB_Wanted.M_IrisHUB_Wanted",
"DigistructInner: A History of Simulated Violence":          "GD_Lobelia_TestingZone.M_TestingZone",
"DigiPeakInner: More History of Simulated Violence":         "GD_Lobelia_TestingZone.M_TestingZoneRepeatable",
"DigiPeak: Dr. T and the Vault Hunters":                     "GD_Lobelia_UnlockDoor.M_Lobelia_UnlockDoor",
"WamBamIsland: Fun, Sun, and Guns":                          "GD_Nast_Easter_Plot_M01.M_Nast_Easter",
"RotgutDistillery: A Match Made on Pandora":                 "GD_Nast_Vday_Mission_Plot.M_Nast_Vday",
"WamBamIsland: Victims of Vault Hunters":                    "GD_Nast_Easter_Mission_Side01.M_Nast_Easter_Side01",
"RotgutDistillery: Learning to Love":                        "GD_Nast_Vday_Mission_Side01.M_Nast_Vday_Side01",
"Oasis: A Warm Welcome":                                     "GD_Orchid_Plot.M_Orchid_PlotMission01",
"Wurmwater: Message in a Bottle 2":                          "GD_Orchid_SM_Message.M_Orchid_MessageInABottle2",
"HaytorsFolly: Message in a Bottle 3":                       "GD_Orchid_SM_Message.M_Orchid_MessageInABottle3",
"Rustyards: Message in a Bottle 4":                          "GD_Orchid_SM_Message.M_Orchid_MessageInABottle4",
"MagnysLighthouse: Message In A Bottle 5":                   "GD_Orchid_SM_Message.M_Orchid_MessageInABottle6",
"Oasis: My Life For A Sandskiff":                            "GD_Orchid_Plot_Mission02.M_Orchid_PlotMission02",
"Wurmwater: A Study in Scarlett":                            "GD_Orchid_Plot_Mission03.M_Orchid_PlotMission03",
"Hayters: Two Easy Pieces":                                  "GD_Orchid_Plot_Mission04.M_Orchid_PlotMission04",
"Rustyards: The Hermit":                                     "GD_Orchid_Plot_Mission05.M_Orchid_PlotMission05",
"Rustyards: Crazy About You":                                "GD_Orchid_Plot_Mission06.M_Orchid_PlotMission06",
"Washburne: Whoops":                                         "GD_Orchid_Plot_Mission07.M_Orchid_PlotMission07",
"Magnys Lighthouse: Let There Be Light":                     "GD_Orchid_Plot_Mission08.M_Orchid_PlotMission08",
"LeviathansLair: X Marks The Spot":                          "GD_Orchid_Plot_Mission09.M_Orchid_PlotMission09",
"Oasis: Burying the Past":                                   "GD_Orchid_SM_BuryPast.M_Orchid_BuryingThePast",
"Rustyards: Just Desserts for Desert Deserters":             "GD_Orchid_SM_Deserters.M_Orchid_Deserters",
"LeviathansLair: Treasure of the Sands":                     "GD_Orchid_SM_EndGameClone.M_Orchid_EndGame",
"Oasis: Fire Water":                                         "GD_Orchid_SM_FireWater.M_Orchid_FireWater",
"Washburne: Freedom of Speech":                              "GD_Orchid_SM_Freedom.M_Orchid_FreedomOfSpeech",
"Washburne: I Know It When I See It":                        "GD_Orchid_SM_KnowIt.M_Orchid_KnowItWhenSeeIt",
"Washburne: Faster Than the Speed of Love":                  "GD_Orchid_SM_Race.M_Orchid_Race",
"Wurmwater: Smells Like Victory":                            "GD_Orchid_SM_Smells.M_Orchid_SmellsLikeVictory",
"Oasis: Wingman":                                            "GD_Orchid_SM_Wingman.M_Orchid_Wingman",
"Oasis: Giving Jocko A Leg Up":                              "GD_Orchid_SM_JockoLegUp.M_Orchid_JockoLegUp",
"Washburne: Don't Copy That Floppy":                         "GD_Orchid_SM_FloppyCopy.M_Orchid_DontCopyThatFloppy",
"Oasis: Message in a Bottle 1":                              "GD_Orchid_SM_Message.M_Orchid_MessageInABottle1",
"Washburne: Hyperius the Invincible":                        "GD_Orchid_Raid.M_Orchid_Raid1",
"Hayters: Master Gee the Invincible":                        "GD_Orchid_Raid.M_Orchid_Raid3",
"Wurmwater: Ye Scurvy Dogs":                                 "GD_Orchid_SM_Scurvy.M_Orchid_ScurvyDogs",
"Wurmwater: Declaration Against Independents":               "GD_Orchid_SM_Declaration.M_Orchid_DeclarationAgainstIndependents",
"Hayters: Grendel":                                          "GD_Orchid_SM_Grendel.M_Orchid_Grendel",
"Oasis: Man's Best Friend":                                  "GD_Orchid_SM_MansBestFriend.M_Orchid_MansBestFriend",
"Rustyards: Catch-A-Ride, and Also Tetanus":                 "GD_Orchid_SM_Tetanus.M_Orchid_CatchRideTetanus",
"HuntersGrotto: Savage Lands":                               "GD_Sage_Ep1.M_Sage_Mission01",
"HuntersGrotto: Professor Nakayama, I Presume?":             "GD_Sage_Ep3.M_Sage_Mission03",
"HuntersGrotto: A-Hunting We Will Go":                       "GD_Sage_Ep4.M_Sage_Mission04",
"Terminus: The Fall of Nakayama":                            "GD_Sage_Ep5.M_Sage_Mission05",
"HuntersGrotto: An Acquired Taste":                          "GD_Sage_SM_AcquiredTaste.M_Sage_AcquiredTaste",
"CandlerakksCrag: Big Feet":                                 "GD_Sage_SM_BigFeet.M_Sage_BigFeet",
"HuntersGrotto: Still Just a Borok in a Cage":               "GD_Sage_SM_BorokCage.M_Sage_BorokCage",
"ArdortonStation: The Rakk Dahlia Murder":                   "GD_Sage_SM_DahliaMurder.M_Sage_DahliaMurder",
"HuntersGrotto: Egg on Your Face":                           "GD_Sage_SM_EggOnFace.M_Sage_EggOnFace",
"ArdortonStation: Follow The Glow":                          "GD_Sage_SM_FollowGlow.M_Sage_FollowGlow",
"ScyllasGrove: Nakayama-rama":                               "GD_Sage_SM_Nakarama.M_Sage_Nakayamarama",
"CandlerakksCrag: Now You See It":                           "GD_Sage_SM_NowYouSeeIt.M_Sage_NowYouSeeIt",
"ScyllasGrove: Ol' Pukey":                                   "GD_Sage_SM_OldPukey.M_Sage_OldPukey",
"HuntersGrotto: Palling Around":                             "GD_Sage_SM_PallingAround.M_Sage_PallingAround",
"HuntersGrotto: I Like My Monsters Rare":                    "GD_Sage_SM_RareSpawns.M_Sage_RareSpawns",
"ScyllasGrove: Urine, You're Out":                           "GD_Sage_SM_Urine.M_Sage_Urine",
"CandlerakksCrag: Voracidous the Invincible":                "GD_Sage_Raid.M_Sage_Raid",

}

mission_ue_str_to_name = {v.split('.')[-1]: k for k, v in mission_name_to_ue_str.items()}

def call_later(time, call):
    """Call the given callable after the given time has passed."""
    timer = datetime.datetime.now()
    future = timer + datetime.timedelta(seconds=time)

    # Create a wrapper to call the routine that is suitable to be passed to add_hook.
    def tick(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
        # Invoke the routine when enough time has passed and unregister its tick hook.
        if datetime.datetime.now() >= future:
            call()
            unrealsdk.hooks.remove_hook("WillowGame.WillowGameViewportClient:Tick", Type.PRE, "CallLater" + str(call))
        return True

    # Hook the wrapper.
    unrealsdk.hooks.add_hook("WillowGame.WillowGameViewportClient:Tick", Type.PRE, "CallLater" + str(call), tick)

# # unused for now
# def temp_set_prop(obj, prop_name, val, time=1):
#     backup = getattr(obj, prop_name)
#     if backup == val:
#         print(prop_name + " already set to val")
#         return
#     setattr(obj, prop_name, val)
#     def reset_prop(obj, prop_name, backup):
#         setattr(obj, prop_name, backup)
#     call_later(time, lambda obj=obj, prop_name=prop_name, backup=backup: reset_prop(obj, prop_name, backup))


def grant_mission_reward(mission_name) -> None:
    ue_str = mission_name_to_ue_str.get(mission_name)
    if not ue_str:
        print("unknown mission: " + mission_name)
        show_chat_message("unknown mission: " + mission_name)
        return
    mission_def = unrealsdk.find_object("MissionDefinition", ue_str)
    # mission_def.GameStage = get_pc().PlayerReplicationInfo.ExpLevel

    r = mission_def.Reward
    ar = mission_def.AlternativeReward

    # duplicate reward if there's only one
    if sum(x is not None for x in r.RewardItems or []) == 1:
        if len(ar.RewardItems):
            extra = ar.RewardItems[0]
        else:
            extra = r.RewardItems[0]
        r.RewardItems = [r.RewardItems[0], extra]
    elif sum(x is not None for x in r.RewardItemPools or []) == 1:
        if len(ar.RewardItemPools):
            extra = ar.RewardItemPools[0]
        else:
            extra = r.RewardItemPools[0]
        r.RewardItemPools = [r.RewardItemPools[0], extra]

    backup_xp_struct = unrealsdk.make_struct("AttributeInitializationData",
        BaseValueConstant = r.ExperienceRewardPercentage.BaseValueConstant,
        BaseValueAttribute = r.ExperienceRewardPercentage.BaseValueAttribute,
        InitializationDefinition = r.ExperienceRewardPercentage.InitializationDefinition,
        BaseValueScaleConstant = r.ExperienceRewardPercentage.BaseValueScaleConstant,
    )
    r.ExperienceRewardPercentage = unrealsdk.make_struct("AttributeInitializationData", 
        BaseValueConstant=0,
        BaseValueAttribute=None,
        InitializationDefinition=None,
        BaseValueScaleConstant=0
    )
    show_hud_message("Quest Reward Received", mission_name, 4)
    get_pc().ServerGrantMissionRewards(mission_def, False)
    def reset_xp(r, backup_xp_struct):
        r.ExperienceRewardPercentage = backup_xp_struct

    # if mission is opened after 5 seconds, it will display the xp amount, but not reward that amount.
    call_later(5, lambda r=r, backup_xp_struct=backup_xp_struct: reset_xp(r, backup_xp_struct))

    # if len(mission_def.Reward.RewardItemPools or []) == 0 and len(mission_def.Reward.RewardItems or []) == 0:
    # get_pc().ShowStatusMenu()

# useful for testing, you can repeat digi peak quest
# set GD_Lobelia_UnlockDoor.M_Lobelia_UnlockDoor bRepeatable True
# !getitem questrewarddrtandthevaulthunters