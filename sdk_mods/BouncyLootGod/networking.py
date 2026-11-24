from BouncyLootGod.state import get_globals
from ui_utils import show_chat_message

def push_locations():
    blg = get_globals()
    if not blg.is_archi_connected:
        return
    # TODO: bundle into one request instead of multiple
    while len(blg.locs_to_send) > 0:
        check = blg.locs_to_send[0]

        if check == blg.settings.get("goal"): # look for if check is goal
            print("GOAL!")
        elif check in blg.locations_checked:  # otherwise skip already checked
            blg.locs_to_send.pop(0)
            continue

        print('sending ' + str(check))
        blg.sock.send(bytes(str(check), 'utf8'))
        msg = blg.sock.recv(4096)
        if msg.decode().startswith("ack"):
            blg.locations_checked.add(check)
            location_data = blg.settings["location_data"][str(check)]
            item_name = location_data['item_name']
            receiving_player = location_data['player_id']
            if receiving_player != -1:
                show_chat_message(f"Sent {item_name} to {receiving_player}")
        else:
            print(msg.decode())
            print(check)
        blg.locs_to_send.pop(0) # remove from list after successful send,

# TODO: move more functions into here