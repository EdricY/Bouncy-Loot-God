import datetime
import unrealsdk
import unrealsdk.unreal as unreal
from unrealsdk.hooks import Type

from mods_base import get_pc
from ui_utils import show_chat_message, show_hud_message



mission_name_to_ue_str = {
"The Road to Sanctuary":                               "GD_Episode03.M_Ep3_CatchARide",
"Plan B":                                              "GD_Episode04.M_Ep4_WelcomeToSanctuary",
"Hunting the Firehawk":                                "GD_Episode05.M_Ep5_ThePhoenix",
"A Train to Catch":                                    "GD_Episode07.M_Ep7_ATrainToCatch",
"Rising Action":                                       "GD_Episode08.M_Ep8_SanctuaryTakesOff",
"Bright Lights, Flying City":                          "GD_Episode09.M_Ep9_GetBackToSanctuary",
"Data Mining":                                         "GD_Episode15.M_Ep15_CharacterAssassination",
"Breaking the Bank":                                   "GD_Z2_TheBankJob.M_TheBankJob",
"Kill Yourself":                                       "GD_Z3_KillYourself.M_KillYourself",
"This Just In":                                        "GD_Z3_ThisJustIn.M_ThisJustIn",
"My First Gun":                                        "GD_Episode01.M_Ep1_Champion",
"Clan War: Wakey Wakey":                               "GD_Z2_WakeyWakey.M_WakeyWakey",
"Handsome Jack Here!":                                 "GD_Z1_HandsomeJackHere.M_HandsomeJackHere",
"This Town Ain't Big Enough":                          "GD_Z1_ThisTown.M_ThisTown",
"Shielded Favors":                                     "GD_Episode02.M_Ep2b_Henchman",
"Symbiosis":                                           "GD_Z1_Symbiosis.M_Symbiosis",
"Defend Slab Tower":                                   "GD_Z2_DefendSlabTower.M_DefendSlabTower",
"Best Mother's Day Ever":                              "GD_Z2_MothersDayGift.BalanceDefs.M_MothersDayGift",
"Note for Self-Person":                                "gd_z2_notetoself.M_NoteToSelf",
"The Bane":                                            "GD_Z3_Bane.M_Bane",
"The Good, the Bad, and the Mordecai":                 "GD_Z3_GoodBadMordecai.M_GoodBadMordecai",
"The Lost Treasure":                                   "GD_Z3_LostTreasure.M_LostTreasure",
"Arms Dealing":                                        "GD_Z2_ArmsDealer.M_ArmsDealer",
"3:10 to Kaboom":                                      "GD_Z2_BlowTheBridge.M_BlowTheBridge",
"Customer Service":                                    "GD_Z3_CustomerService.M_CustomerService",
"Neither Rain nor Sleet nor Skags":                    "gd_z3_neitherrainsleet.M_NeitherRainSleetSkags",
"Blindsided":                                          "GD_Episode02.M_Ep2_Henchman",
"Cleaning up the Berg":                                "GD_Episode02.M_Ep2a_MoreGuns",
"Best Minion Ever":                                    "GD_Episode02.M_Ep2c_Henchman",
"A Dam Fine Rescue":                                   "GD_Episode06.M_Ep6_RescueRoland",
"Wildlife Preservation":                               "GD_Episode10.M_Ep10_BirdISTheWord",
"The Once and Future Slab":                            "GD_Episode11.M_Ep11_LikeATonOf",
"The Man Who Would Be Jack":                           "GD_Episode12.M_Ep12_BecomingJack",
"Where Angels Fear to Tread":                          "GD_Episode13.M_Ep13_KillAngel",
"Where Angels Fear to Tread (Part 2)":                 "GD_Episode14.M_Ep14_SearchingTheWreckage",
"Toil and Trouble":                                    "GD_Episode16.M_Ep16_LockAndLoad",
"The Talon of God":                                    "GD_Episode17.M_Ep17_KillJack",
"Assassinate the Assassins":                           "GD_Z1_Assasinate.M_AssasinateTheAssassins",
"Bad Hair Day":                                        "GD_Z1_BadHairDay.M_BadHairDay",
"Bearer of Bad News":                                  "GD_Z1_BearerBadNews.M_BearerBadNews",
"BFFs":                                                "GD_Z1_BFFs.M_BFFs",
"Cult Following: Eternal Flame":                       "GD_Z1_ChildrenOfPhoenix.M_EternalFlame",
"Cult Following: Lighting the Match":                  "GD_Z1_ChildrenOfPhoenix.M_LightingTheMatch",
"Cult Following: The Enkindling":                      "GD_Z1_ChildrenOfPhoenix.M_TheEnkindling",
"Claptrap's Secret Stash":                             "GD_Z1_ClapTrapStash.M_ClapTrapStash",
"You Are Cordially Invited: Party Prep":               "GD_Z1_CordiallyInvited.M_CordiallyInvited",
"The Ice Man Cometh":                                  "GD_Z1_IceManCometh.M_IceManCometh",
"In Memoriam":                                         "GD_Z1_InMemoriam.M_InMemoriam",
"Mighty Morphin'":                                     "GD_Z1_MightyMorphin.M_MightyMorphin",
"Mine, All Mine":                                      "GD_Z1_MineAllMine.M_MineAllMine",
"Minecart Mischief":                                   "gd_z1_minecartmischief.M_MinecartMischief",
"The Name Game":                                       "GD_Z1_NameGame.M_NameGame",
"No Hard Feelings":                                    "gd_z1_nohardfeelings.M_NoHardFeelings",
"No Vacancy":                                          "GD_Z1_NoVacancy.BalanceDefs.M_NoVacancy",
"Perfectly Peaceful":                                  "GD_Z1_PerfectlyPeaceful.M_PerfectlyPeaceful",
"Rock, Paper, Genocide: Slag Weapons!":                "GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Amp",
"Rock, Paper, Genocide: Fire Weapons!":                "GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Fire",
"Do No Harm":                                          "GD_Z1_Surgery.M_PerformSurgery",
"The Pretty Good Train Robbery":                       "GD_Z1_TrainRobbery.M_TrainRobbery",
"Won't Get Fooled Again":                              "GD_Z1_WontGetFooled.M_WontGetFooled",
"A Real Boy: Face Time":                               "GD_Z2_ARealBoy.M_ARealBoy_ArmLeg",
"A Real Boy: Clothes Make the Man":                    "GD_Z2_ARealBoy.M_ARealBoy_Clothes",
"Claptrap's Birthday Bash!":                           "GD_Z2_ClaptrapBirthdayBash.M_ClaptrapBirthdayBash",
"Clan War: Zafords vs. Hodunks":                       "GD_Z2_DuelingBanjos.M_DuelingBanjos",
"Animal Rights":                                       "GD_Z2_FreeWilly.M_FreeWilly",
"Hell Hath No Fury":                                   "GD_Z2_HellHathNo.M_FloodingHyperionCity",
"Home Movies":                                         "GD_Z2_HomeMovies.M_HomeMovies",
"Statuesque":                                          "GD_Z2_HyperionStatue.M_MonumentsVandalism",
"Showdown":                                            "GD_Z2_KillTheSheriff.M_KillTheSheriff",
"Clan War: End of the Rainbow":                        "GD_Z2_LuckysDirtyMoney.M_LuckysDirtyMoney",
"Clan War: Starting the War":                          "GD_Z2_MeetWithEllie.M_MeetWithEllie",
"The Overlooked: Medicine Man":                        "GD_Z2_Overlooked.M_Overlooked",
"The Overlooked: Shields Up":                          "GD_Z2_Overlooked2.M_Overlooked2",
"The Overlooked: This Is Only a Test":                 "GD_Z2_Overlooked3.M_Overlooked3",
"Poetic License":                                      "GD_Z2_PoeticLicense.M_PoeticLicense",
"Clan War: First Place":                               "GD_Z2_RiggedRace.M_RiggedRace",
"Safe and Sound":                                      "GD_Z2_SafeAndSound.M_SafeAndSound",
"Animal Rescue: Shelter":                              "GD_Z2_Skagzilla2.M_Skagzilla2_Den",
"Slap-Happy":                                          "GD_Z2_SlapHappy.M_SlapHappy",
"Stalker of Stalkers":                                 "GD_Z2_TaggartBiography.M_TaggartBiography",
"You. Will. Die. (Seriously.)":                        "GD_Z2_ThresherRaid.M_ThresherRaid",
"Clan War: Trailer Trashing":                          "GD_Z2_TrailerTrashin.M_TrailerTrashin",
"Written by the Victor":                               "GD_Z2_WrittenByVictor.M_WrittenByVictor",
"Capture the Flags":                                   "GD_Z3_CaptureTheFlags.M_CaptureTheFlags",
"The Chosen One":                                      "GD_Z3_ChosenOne.M_ChosenOne",
"The Cold Shoulder":                                   "GD_Z3_ColdShoulder.M_ColdShoulder",
"To Grandmother's House We Go":                        "GD_Z3_GrandmotherHouse.M_GrandmotherHouse",
"The Great Escape":                                    "GD_Z3_GreatEscape.M_GreatEscape",
"Hungry Like the Skag":                                "GD_Z3_HungryLikeSkag.M_HungryLikeSkag",
"Hyperion Contract #873":                              "GD_Z3_HyperionContract873.M_HyperionContract873",
"Medical Mystery":                                     "GD_Z3_MedicalMystery.M_MedicalMystery",
"Medical Mystery: X-Com-municate":                     "GD_Z3_MedicalMystery2.M_MedicalMystery2",
"Out of Body Experience":                              "GD_Z3_OutOfBody.M_OutOfBody",
"Hyperion Slaughter: Round 1":                         "GD_Z3_RobotSlaughter.M_RobotSlaughter_1",
"Hyperion Slaughter: Round 2":                         "GD_Z3_RobotSlaughter.M_RobotSlaughter_2",
"Hyperion Slaughter: Round 3":                         "GD_Z3_RobotSlaughter.M_RobotSlaughter_3",
"Hyperion Slaughter: Round 4":                         "GD_Z3_RobotSlaughter.M_RobotSlaughter_4",
"Hyperion Slaughter: Round 5":                         "GD_Z3_RobotSlaughter.M_RobotSlaughter_5",
"Swallowed Whole":                                     "GD_Z3_SwallowedWhole.M_SwallowedWhole",
"Too Close For Missiles":                              "gd_z3_toocloseformissiles.M_TooCloseForMissiles",
"Uncle Teddy":                                         "GD_Z3_UncleTeddy.M_UncleTeddy",
"Get to Know Jack":                                    "GD_Z3_YouDontKnowJack.M_YouDontKnowJack",
"You Are Cordially Invited: Tea Party":                "GD_Z1_CordiallyInvited.M_CordiallyInvited03",
"You Are Cordially Invited: RSVP":                     "GD_Z1_CordiallyInvited.M_CordiallyInvited02",
"Rock, Paper, Genocide: Corrosive Weapons!":           "GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Corrosive",
"Rock, Paper, Genocide: Shock Weapons!":               "GD_Z1_RockPaperGenocide.M_RockPaperGenocide_Shock",
"Animal Rescue: Medicine":                             "GD_Z2_Skagzilla2.M_Skagzilla2_Pup",
"Splinter Group":                                      "GD_Z2_SplinterGroup.M_SplinterGroup",
"Shoot This Guy in the Face":                          "GD_Z1_ShootMeInTheFace.M_ShootMeInTheFace",
"Bandit Slaughter: Round 1":                           "GD_Z1_BanditSlaughter.M_BanditSlaughter1",
"Bandit Slaughter: Round 2":                           "GD_Z1_BanditSlaughter.M_BanditSlaughter2",
"Bandit Slaughter: Round 3":                           "GD_Z1_BanditSlaughter.M_BanditSlaughter3",
"Bandit Slaughter: Round 4":                           "GD_Z1_BanditSlaughter.M_BanditSlaughter4",
"Bandit Slaughter: Round 5":                           "GD_Z1_BanditSlaughter.M_BanditSlaughter5",
"Creature Slaughter: Round 1":                         "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_1",
"Creature Slaughter: Round 2":                         "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_2",
"Creature Slaughter: Round 3":                         "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_3",
"Creature Slaughter: Round 4":                         "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_4",
"Creature Slaughter: Round 5":                         "GD_Z2_CreatureSlaughter.M_CreatureSlaughter_5",
"Monster Mash (Part 1)":                               "GD_Z3_MonsterMash1.M_MonsterMash1",
"Monster Mash (Part 2)":                               "GD_Z3_MonsterMash2.M_MonsterMash2",
"Monster Mash (Part 3)":                               "GD_Z3_MonsterMash3.M_MonsterMash3",
"Torture Chairs":                                      "GD_Z1_HiddenJournalsFurniture.M_HiddenJournalsFurniture",
"Doctor's Orders":                                     "GD_Z2_DoctorsOrders.M_DoctorsOrders",
"Rakkaholics Anonymous":                               "GD_Z2_Rakkaholics.M_Rakkaholics",
"Hidden Journals":                                     "GD_Z3_HiddenJournals.M_HiddenJournals",
"Positive Self Image":                                 "GD_Z3_PositiveSelfImage.M_PositiveSelfImage",
"Cult Following: False Idols":                         "GD_Z1_ChildrenOfPhoenix.M_FalseIdols",
"Clan War: Reach the Dead Drop":                       "GD_Z2_LuckysDirtyMoney.M_FamFeudDeadDrop",
"A Real Boy: Human":                                   "GD_Z2_ARealBoy.M_ARealBoy_Human",
"Demon Hunter":                                        "GD_Z2_DemonHunter.M_DemonHunter",
"Rocko's Modern Strife":                               "GD_Z2_RockosModernStrife.M_RockosModernStrife",
"Animal Rescue: Food":                                 "GD_Z2_Skagzilla2.M_Skagzilla2_Adult",
"Get Frosty":                                          "GD_Allium_KillSnowman.M_KillSnowman",
"The Hunger Pangs":                                    "GD_Allium_TG_Plot_Mission01.M_Allium_ThanksgivingMission01",
"Special Delivery":                                    "GD_Allium_Delivery.M_Delivery",
"Grandma Flexington's Story":                          "GD_Allium_GrandmaFlexington.M_ListenToGrandma",
"Grandma Flexington's Story: Raid Difficulty":         "GD_Allium_Side_GrandmaRaid.M_ListenToGrandmaRaid",
"The Dawn of New Pandora":                             "GD_Anemone_Plot_Mission010.M_Anemone_PlotMission010",
"Winging It":                                          "GD_Anemone_Plot_Mission025.M_Anemone_PlotMission025",
"Spore Chores":                                        "GD_Anemone_Plot_Mission020.M_Anemone_PlotMission020",
"A Hard Place":                                        "GD_Anemone_Plot_Mission030.M_Anemone_PlotMission030",
"Shooting The Moon":                                   "GD_Anemone_Plot_Mission040.M_Anemone_PlotMission040",
"The Cost of Progress":                                "GD_Anemone_Plot_Mission050.M_Anemone_PlotMission050",
"Paradise Found":                                      "GD_Anemone_Plot_Mission060.M_Anemone_PlotMission060",
"Claptocurrency":                                      "GD_Anemone_Side_Claptocurrency.M_Claptocurrency",
"BFFFs":                                               "GD_Anemone_Side_EyeSnipers.M_Anemone_EyeOfTheSnipers",
"Hypocritical Oath":                                   "GD_Anemone_Side_HypoOathPart1.M_HypocriticalOathPart1",
"Cadeuceus":                                           "GD_Anemone_Side_HypoOathPart2.M_HypocriticalOathPart2",
"My Brittle Pony":                                     "GD_Anemone_Side_MyBrittlePony.M_Anemone_MyBrittlePony",
"The Oddest Couple":                                   "GD_Anemone_Side_OddestCouple.M_Anemone_OddestCouple",
"A Most Cacophonous Lure":                             "GD_Anemone_Side_RaidBoss.M_Anemone_CacophonousLure",
"Sirentology":                                         "GD_Anemone_Side_Sirentology.M_Anemone_Sirentology",
"Space Cowboy":                                        "GD_Anemone_Side_SpaceCowboy.M_Anemone_SpaceCowboy",
"The Vaughnguard":                                     "GD_Anemone_Side_VaughnPart1.M_Anemone_VaughnPart1",
"The Hunt is Vaughn":                                  "GD_Anemone_Side_VaughnPart2.M_Anemone_VaughnPart2",
"Chief Executive Overlord":                            "GD_Anemone_Side_VaughnPart3.M_Anemone_VaughnPart3",
"Echoes of the Past":                                  "GD_Anemone_Side_Echoes.M_Anemone_EchoesOfThePast",
"A Role-Playing Game":                                 "GD_Aster_Plot_Mission01.M_Aster_PlotMission01",
"Dwarven Allies":                                      "GD_Aster_Plot_Mission03.M_Aster_PlotMission03",
"The Amulet":                                          "GD_Aster_AmuletDoNothing.M_AmuletDoNothing",
"The Claptrap's Apprentice":                           "GD_Aster_ClaptrapApprentice.M_ClaptrapApprentice",
"The Beard Makes The Man":                             "GD_Aster_ClapTrapBeard.M_ClapTrapBeard",
"My Kingdom for a Wand":                               "GD_Aster_ClaptrapWand.M_WandMakesTheMan",
"Critical Fail":                                       "GD_Aster_CriticalFail.M_CriticalFail",
"Infinite Agony: My Dead Brother":                     "GD_Aster_DeadBrother.M_MyDeadBrother",
"Lost Souls":                                          "GD_Aster_DemonicSouls.M_DemonicSouls",
"Ell in Shining Armor":                                "GD_Aster_EllieDress.M_EllieDress",
"Fake Geek Guy":                                       "GD_Aster_FakeGeekGuy.M_FakeGeekGuy",
"Feed Butt Stallion":                                  "GD_Aster_FeedButtStallion.M_FeedButtStallion",
"Loot Ninja":                                          "GD_Aster_LootNinja.M_LootNinja",
"MMORPGFPS":                                           "GD_Aster_MMORPGFPS.M_MMORPGFPS",
"Pet Butt Stallion":                                   "GD_Aster_PetButtStallion.M_PettButtStallion",
"Denial, Anger, Initiative":                           "GD_Aster_Plot_Mission02.M_Aster_PlotMission02",
"A Game of Games":                                     "GD_Aster_Plot_Mission04.M_Aster_PlotMission04",
"Infinite Agony: Post-Crumpocalyptic":                 "GD_Aster_Post-Crumpocalyptic.M_Post-Crumpocalyptic",
"Raiders of the Last Boss":                            "GD_Aster_RaidBoss.M_Aster_RaidBoss",
"Roll Insight":                                        "GD_Aster_RollInsight.M_RollInsight",
"Tree Hugger":                                         "GD_Aster_TreeHugger.M_TreeHugger",
"Winter is a Bloody Business":                         "GD_Aster_WinterIsComing.M_WinterIsComing",
"Magic Slaughter: Round 1":                            "GD_Aster_TempleSlaughter.M_TempleSlaughter1",
"Magic Slaughter: Round 2":                            "GD_Aster_TempleSlaughter.M_TempleSlaughter2",
"Magic Slaughter: Round 3":                            "GD_Aster_TempleSlaughter.M_TempleSlaughter3",
"Magic Slaughter: Round 4":                            "GD_Aster_TempleSlaughter.M_TempleSlaughter4",
"Magic Slaughter: Round 5":                            "GD_Aster_TempleSlaughter.M_TempleSlaughter5",
"Magic Slaughter: Badass Round":                       "GD_Aster_TempleSlaughter.M_TempleSlaughter6Badass",
"The Magic of Childhood":                              "GD_Aster_TempleTower.M_TempleTower",
"Find Murderlin's Temple":                             "GD_Aster_TempleSlaughter.M_TempleSlaughterIntro",
"The Sword in The Stoner":                             "GD_Aster_SwordInStone.M_SwordInStoner",
"The Bloody Harvest":                                  "GD_FlaxMissions.M_BloodHarvest",
"Trick or Treat":                                      "GD_FlaxMissions.M_TrickOrTreat",
"Highway To Hell":                                     "GD_IrisEpisode01.M_IrisEp1_HighwayToHell",
"Tier 2 Battle: Appetite for Destruction":             "GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoP2",
"Tier 3 Battle: Appetite for Destruction":             "GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoP3",
"Tier 3 Rematch: Appetite for Destruction":            "GD_IrisEpisode02_Battle.M_IrisEp2Battle_CoPR3",
"Tier 2 Battle: Bar Room Blitz":                       "GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFight2",
"Tier 3 Battle: Bar Room Blitz":                       "GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFight3",
"Battle: Bar Room Blitz":                              "GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFight",
"Tier 3 Rematch: Bar Room Blitz":                      "GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFightR3",
"Tier 2 Battle: The Death Race":                       "GD_IrisEpisode04_Battle.M_IrisEp4Battle_Race2",
"Tier 3 Battle: The Death Race":                       "GD_IrisEpisode04_Battle.M_IrisEp4Battle_Race4",
"Battle: The Death Race":                              "GD_IrisEpisode04_Battle.M_IrisEp4Battle_Race",
"Tier 3 Rematch: The Death Race":                      "GD_IrisEpisode04_Battle.M_IrisEp4Battle_RaceR4",
"Tier 2 Battle: Twelve O' Clock High":                 "GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyro2",
"Tier 3 Battle: Twelve O' Clock High":                 "GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyro3",
"Battle: Twelve O' Clock High":                        "GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyro",
"Tier 3 Rematch: Twelve O' Clock High":                "GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyroR3",
"Mother-Lover":                                        "GD_IrisDL2_DontTalkAbtMama.M_IrisDL2_DontTalkAbtMama",
"Number One Fan":                                      "GD_IrisDL2_PumpkinHead.M_IrisDL2_PumpkinHead",
"Commercial Appeal":                                   "GD_IrisDL3_CommAppeal.M_IrisDL3_CommAppeal",
"My Husband the Skag":                                 "GD_IrisDL3_MySkag.M_IrisDL3_MySkag",
"Say That To My Face":                                 "GD_IrisDL3_PSYouSuck.M_IrisDL3_PSYouSuck",
"Welcome To The Jungle":                               "GD_IrisEpisode01.M_IrisEp1_WTTJ",
"Battle: Appetite for Destruction":                    "GD_IrisEpisode02.M_IrisEp2_CultOfPersonality",
"Burn, Baby, Burn":                                    "GD_IrisEpisode02.M_IrisEp2_FindBattle",
"Chop Suey":                                           "GD_IrisEpisode03.M_IrisEp3_ChopSuey",
"A Montage":                                           "GD_IrisEpisode04.M_IrisEp4_AMontage",
"Get Your Motor Running":                              "GD_IrisEpisode04.M_IrisEp4_CherryBomb",
"Eat Cookies and Crap Thunder":                        "GD_IrisEpisode04.M_IrisEp4_TrainningWithTina",
"Knockin' on Heaven's Door":                           "GD_IrisEpisode05.M_HeavensDoor",
"Breaking and Entering":                               "GD_IrisEpisode05.M_IrisEp5_CageMatch",
"Kickstart My Heart":                                  "GD_IrisEpisode05.M_IrisEp5_KickStartMyHeart",
"Long Way To The Top":                                 "GD_IrisEpisode06.M_IrisEp6_LongWayToTheTop",
"Gas Guzzlers":                                        "GD_IrisHUB_GasGuzzlers.M_IrisHUB_GasGuzzlers",
"Matter Of Taste":                                     "GD_IrisHUB_MatterOfTaste.M_IrisHUB_MatterOfTaste",
"Monster Hunter":                                      "GD_IrisHUB_MonsterHunter.M_IrisHUB_MonsterHunter",
"Interview with a Vault Hunter":                       "GD_IrisHUB_SmackTalk.M_IrisHUB_SmackTalk",
"Walking the Dog":                                     "GD_IrisHUB_WalkTheDog.M_IrisHUB_WalkTheDog",
"Pete the Invincible":                                 "GD_IrisRaidBoss.M_Iris_RaidPete",
"Totally Recall":                                      "GD_IrisDL2_ProductRecall.M_IrisDL2_ProductRecall",
"Everybody Wants to be Wanted":                        "GD_IrisHUB_Wanted.M_IrisHUB_Wanted",
"A History of Simulated Violence":                     "GD_Lobelia_TestingZone.M_TestingZone",
"More History of Simulated Violence":                  "GD_Lobelia_TestingZone.M_TestingZoneRepeatable",
"Dr. T and the Vault Hunters":                         "GD_Lobelia_UnlockDoor.M_Lobelia_UnlockDoor",
"Fun, Sun, and Guns":                                  "GD_Nast_Easter_Plot_M01.M_Nast_Easter",
"A Match Made on Pandora":                             "GD_Nast_Vday_Mission_Plot.M_Nast_Vday",
"Victims of Vault Hunters":                            "GD_Nast_Easter_Mission_Side01.M_Nast_Easter_Side01",
"Learning to Love":                                    "GD_Nast_Vday_Mission_Side01.M_Nast_Vday_Side01",
"A Warm Welcome":                                      "GD_Orchid_Plot.M_Orchid_PlotMission01",
"Message in a Bottle 2 (Wurmwater)":                   "GD_Orchid_SM_Message.M_Orchid_MessageInABottle2",
"Message in a Bottle 3 (HaytersFolly)":                "GD_Orchid_SM_Message.M_Orchid_MessageInABottle3",
"Message in a Bottle 4 (Rustyards)":                   "GD_Orchid_SM_Message.M_Orchid_MessageInABottle4",
"Message In A Bottle 5 (MagnysLighthouse)":            "GD_Orchid_SM_Message.M_Orchid_MessageInABottle6",
"My Life For A Sandskiff":                             "GD_Orchid_Plot_Mission02.M_Orchid_PlotMission02",
"A Study in Scarlett":                                 "GD_Orchid_Plot_Mission03.M_Orchid_PlotMission03",
"Two Easy Pieces":                                     "GD_Orchid_Plot_Mission04.M_Orchid_PlotMission04",
"The Hermit":                                          "GD_Orchid_Plot_Mission05.M_Orchid_PlotMission05",
"Crazy About You":                                     "GD_Orchid_Plot_Mission06.M_Orchid_PlotMission06",
"Whoops":                                              "GD_Orchid_Plot_Mission07.M_Orchid_PlotMission07",
"Let There Be Light":                                  "GD_Orchid_Plot_Mission08.M_Orchid_PlotMission08",
"X Marks The Spot":                                    "GD_Orchid_Plot_Mission09.M_Orchid_PlotMission09",
"Burying the Past":                                    "GD_Orchid_SM_BuryPast.M_Orchid_BuryingThePast",
"Just Desserts for Desert Deserters":                  "GD_Orchid_SM_Deserters.M_Orchid_Deserters",
"Treasure of the Sands":                               "GD_Orchid_SM_EndGameClone.M_Orchid_EndGame",
"Fire Water":                                          "GD_Orchid_SM_FireWater.M_Orchid_FireWater",
"Freedom of Speech":                                   "GD_Orchid_SM_Freedom.M_Orchid_FreedomOfSpeech",
"I Know It When I See It":                             "GD_Orchid_SM_KnowIt.M_Orchid_KnowItWhenSeeIt",
"Faster Than the Speed of Love":                       "GD_Orchid_SM_Race.M_Orchid_Race",
"Smells Like Victory":                                 "GD_Orchid_SM_Smells.M_Orchid_SmellsLikeVictory",
"Wingman":                                             "GD_Orchid_SM_Wingman.M_Orchid_Wingman",
"Giving Jocko A Leg Up":                               "GD_Orchid_SM_JockoLegUp.M_Orchid_JockoLegUp",
"Don't Copy That Floppy":                              "GD_Orchid_SM_FloppyCopy.M_Orchid_DontCopyThatFloppy",
"Message in a Bottle 1 (Oasis)":                       "GD_Orchid_SM_Message.M_Orchid_MessageInABottle1",
"Hyperius the Invincible":                             "GD_Orchid_Raid.M_Orchid_Raid1",
"Master Gee the Invincible":                           "GD_Orchid_Raid.M_Orchid_Raid3",
"Ye Scurvy Dogs":                                      "GD_Orchid_SM_Scurvy.M_Orchid_ScurvyDogs",
"Declaration Against Independents":                    "GD_Orchid_SM_Declaration.M_Orchid_DeclarationAgainstIndependents",
"Grendel":                                             "GD_Orchid_SM_Grendel.M_Orchid_Grendel",
"Man's Best Friend":                                   "GD_Orchid_SM_MansBestFriend.M_Orchid_MansBestFriend",
"Catch-A-Ride, and Also Tetanus":                      "GD_Orchid_SM_Tetanus.M_Orchid_CatchRideTetanus",
"Savage Lands":                                        "GD_Sage_Ep1.M_Sage_Mission01",
"Professor Nakayama, I Presume?":                      "GD_Sage_Ep3.M_Sage_Mission03",
"A-Hunting We Will Go":                                "GD_Sage_Ep4.M_Sage_Mission04",
"The Fall of Nakayama":                                "GD_Sage_Ep5.M_Sage_Mission05",
"An Acquired Taste":                                   "GD_Sage_SM_AcquiredTaste.M_Sage_AcquiredTaste",
"Big Feet":                                            "GD_Sage_SM_BigFeet.M_Sage_BigFeet",
"Still Just a Borok in a Cage":                        "GD_Sage_SM_BorokCage.M_Sage_BorokCage",
"The Rakk Dahlia Murder":                              "GD_Sage_SM_DahliaMurder.M_Sage_DahliaMurder",
"Egg on Your Face":                                    "GD_Sage_SM_EggOnFace.M_Sage_EggOnFace",
"Follow The Glow":                                     "GD_Sage_SM_FollowGlow.M_Sage_FollowGlow",
"Nakayama-rama":                                       "GD_Sage_SM_Nakarama.M_Sage_Nakayamarama",
"Now You See It":                                      "GD_Sage_SM_NowYouSeeIt.M_Sage_NowYouSeeIt",
"Ol' Pukey":                                           "GD_Sage_SM_OldPukey.M_Sage_OldPukey",
"Palling Around":                                      "GD_Sage_SM_PallingAround.M_Sage_PallingAround",
"I Like My Monsters Rare":                             "GD_Sage_SM_RareSpawns.M_Sage_RareSpawns",
"Urine, You're Out":                                   "GD_Sage_SM_Urine.M_Sage_Urine",
"Voracidous the Invincible":                           "GD_Sage_Raid.M_Sage_Raid",
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