from mods_base import get_pc, Game

def add_money(amt):
    pc = get_pc()
    if Game.get_tree() == Game.Willow1:
        pc.PlayerReplicationInfo.AddCurrencyOnHand(amt)
    else:
        pc.PlayerReplicationInfo.AddCurrencyOnHand(0, amt)

def set_money(amt):
    pc = get_pc()
    if Game.get_tree() == Game.Willow1:
        pc.PlayerReplicationInfo.SetCurrencyOnHand(amt)
    else:
        pc.PlayerReplicationInfo.SetCurrencyOnHand(0, amt)