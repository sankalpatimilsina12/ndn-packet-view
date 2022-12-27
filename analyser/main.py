from aiohttp import web
from api import routes_http, routes_ws
import asyncio
import aiohttp_cors


async def start_server(host='127.0.0.1', port=1337):
    app = web.Application()
    app.add_routes(routes_http)
    app.add_routes(routes_ws)

    cors = aiohttp_cors.setup(app, defaults={
        '*': aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers='*',
            allow_headers='*',
        )
    })

    for route in list(app.router.routes()):
        cors.add(route)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host, port)
    await site.start()
    print(f'Server started at http://{host}:{port}')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    loop.run_forever()
