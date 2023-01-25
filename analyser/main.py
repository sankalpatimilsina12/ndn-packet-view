from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient
from api import routes_http
import asyncio
import aiohttp_cors
import sys
from definitions import SITE_HOST, SITE_PORT, MONGO_HOST, MONGO_DB_NAME


async def start_server():
    app = web.Application()
    app.add_routes(routes_http)

    cors = aiohttp_cors.setup(app, defaults={
        '*': aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers='*',
            allow_headers='*',
        )
    })

    for route in list(app.router.routes()):
        cors.add(route)

    client = AsyncIOMotorClient(MONGO_HOST)
    app['db'] = client[MONGO_DB_NAME]

    async def cleanup():
        client.close()
    app.on_cleanup.append(cleanup)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, SITE_HOST, SITE_PORT)
    await site.start()
    print(f'Server started at http://{SITE_HOST}:{SITE_PORT}')

if __name__ == '__main__':
    if sys.version_info < (3, 7):
        loop = asyncio.get_event_loop()
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server())
    loop.run_forever()
