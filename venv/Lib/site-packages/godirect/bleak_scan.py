import asyncio
from bleak import discover

async def _async_scan():
		devices = []
		bleak_devices = await discover()
		for d in bleak_devices:
			print("bleak scan: ", d)
			if d and d.name and d.name[0:3] == 'GDX':
				print("   bleak scan name: ", d.name)
			else:
				print("   bleak scan name: unknown")

loop = asyncio.get_event_loop()
loop.run_until_complete(_async_scan())
