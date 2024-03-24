import asyncio
import logging
from chargepoint import ChargePoint

import websockets

from ocpp.routing import on
from ocpp.v16 import call, call_result
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import RegistrationStatus, Action

logging.basicConfig(level=logging.DEBUG)

async def heartbeat_send(cp):
    while True:
        await cp.send_heartbeat()
        await asyncio.sleep(cp.heartbeat_interval)

async def main():
    # Azure grecsms
    async with websockets.connect(
        'ws://127.0.0.1:8000/ws/ocpp/grevcli01',
        # subprotocols=['ocpp1.6']
    ) as ws:

        cp = ChargePoint('grevcli01', ws) # EVNest

        await asyncio.gather(
          cp.start(), 
          cp.send_boot_notification(),
          cp.send_status_notification('Available'),
          heartbeat_send(cp),
        #   cp.send_authorize()
        #   heartbeat_send(cp, heartbeat_interval)
        )

if __name__ == '__main__':
    try:
        # asyncio.run() is used when running this example with Python 3.7 and
        # higher.
        asyncio.run(main())
    except AttributeError:
        # For Python 3.6 a bit more code is required to run the main() task on
        # an event loop.
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
