import asyncio
import json
import os
import requests
import time
import re
from NetUtils import ClientStatus
import Utils
from CommonClient import gui_enabled, logger, get_base_parser, CommonContext, server_loop

# import ModuleUpdate
# ModuleUpdate.update()

# Testing:
# import colorama
# from asyncio import Task
#

from worlds.borderlands2.Locations import location_name_to_id

class Borderlands2Context(CommonContext):
    game = "Borderlands 2"
    items_handling = 0b111  # Indicates you get items sent from other worlds. possibly should be 0b011

    def __init__(self, server_address, password):
        super(Borderlands2Context, self).__init__(server_address, password)

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(Borderlands2Context, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    async def connection_closed(self):
        self.server_state_synchronized = False
        await super(Borderlands2Context, self).connection_closed()

    async def shutdown(self):
        await super(Borderlands2Context, self).shutdown()

    def run_gui(self):
        """Import kivy UI system and start running it as self.ui_task."""
        from kvui import GameManager

        class BL2Manager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago BL2 Client"

        self.ui = BL2Manager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

checks = []
async def main(launch_args):
    ctx = Borderlands2Context(launch_args.connect, launch_args.password)
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()

    print('main 1321 ')

    async def handle_sock_client(reader, writer):
        """
        Handles communication with a single client asynchronously.
        """
        addr = writer.get_extra_info('peername')
        print(f"sock connection from {addr}")
        ctx.command_processor.output(ctx.command_processor, f"connection from {addr}")

        while True:
            try:
                data = await reader.read(100)  # Read data asynchronously
                if not data:
                    break
                message = data.decode()
                print(f"Received from {addr}: {message}")
                if message == 'bl2hello':
                    print("asdf1")
                    # loc_id = location_name_to_id["Common Pistol"]
                    # await ctx.check_locations([loc_id])
                    response = "whatsssup"
                    writer.write(response.encode())  # Write data asynchronously
                    await writer.drain()  # Ensure data is sent

                    print("qwer1")
                elif message == 'items_all':
                    item_ids = [str(x.item) for x in ctx.items_received]

                    response = ",".join(item_ids).encode()
                    print("sending:")
                    print(response)
                    writer.write(response)  # Write data asynchronously
                    await writer.drain()  # Ensure data is sent
                else:
                    # TODO: check to ensure this is a number
                    print("msg_check: " + str(message))
                    item_id = int(message)
                    await ctx.check_locations([item_id])
                    # response = f"Echo: {message}".encode()
                    # writer.write(response)  # Write data asynchronously
                    # await writer.drain()  # Ensure data is sent

            except asyncio.CancelledError:
                print(f"Client {addr} disconnected (cancelled).")
                ctx.command_processor.output(ctx.command_processor,f"sock client {addr} disconnected.")
            except Exception as e:
                print(f"Error with client {addr}: {e}")
                ctx.command_processor.output(ctx.command_processor,f"Error with sock client {addr}: {e}")
                break
            # finally:
            #     writer.close()
            #     await writer.wait_closed()
            #     print(f"Client {addr} disconnected.")
        #done with client
        print(f"Client disconnected from: {addr}")
        writer.close()
        await writer.wait_closed()



    server = await asyncio.start_server(
        handle_sock_client, 'localhost', 9997
    )
    ctx.command_processor.output(ctx.command_processor,"hello from client.py, sock server started on 9997")
    # progression_watcher = asyncio.create_task(
    #     game_watcher(ctx), name="BL2ProgressionWatcher")

    await ctx.exit_event.wait()
    ctx.server_address = None
    # await progression_watcher
    await ctx.shutdown()
def launch():
    import colorama
    parser = get_base_parser(description="Borderlands 2 Client, for text interfacing.")
    args, rest = parser.parse_known_args()
    colorama.init()
    asyncio.run(main(args))
    colorama.deinit()
