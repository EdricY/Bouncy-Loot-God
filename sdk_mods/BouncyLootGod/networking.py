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
                show_chat_message(f"Sent \"{item_name}\" to {blg.settings["player_names"][str(receiving_player)]}")
        else:
            print(msg.decode())
            print(check)
        blg.locs_to_send.pop(0) # remove from list after successful send,

# TODO: move more functions into here

# helper function for socket to receive an exact amount over the socket.
def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def send_location_discovered(loc_id):
    blg = get_globals()
    scouted = blg.settings.get("locations_scouted", [])
    if not blg.is_archi_connected or str(loc_id) in scouted:
        return
    print('scouting ' + str(loc_id))
    blg.sock.send(bytes(f"hint_location:{str(loc_id)}", 'utf8'))
    msg = blg.sock.recv(4096)
    if msg.decode().startswith("ack"):
        scouted.append(loc_id)
    else:
        print(msg.decode())
        print(loc_id)
    