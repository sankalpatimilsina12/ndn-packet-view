import json
import os
import aiohttp
from aiohttp import web
from definitions import DATA_DIR
import gzip
import zstandard

routes_ws = web.RouteTableDef()


@routes_ws.get('/ws/')
async def websocket_handler(request):
    ws = web.WebSocketResponse(autoping=True, heartbeat=60)
    ready = ws.can_prepare(request=request)
    if not ready:
        await ws.close(code=aiohttp.WSCloseCode.PROTOCOL_ERROR)
        return ws
    await ws.prepare(request)

    filename = request.query.get('filename')
    ext = os.path.splitext(filename)[1]

    if ext == '.gz':
        file = gzip.open(os.path.join(DATA_DIR, filename), 'rt')
    elif ext == '.zst':
        file = zstandard.open(os.path.join(DATA_DIR, filename), 'rt')
    else:
        await ws.close(code=aiohttp.WSCloseCode.UNSUPPORTED_DATA)
        return ws

    try:
        for line in file.readlines():
            if ws.closed:
                break
            await ws.send_json(json.loads(line))
    except Exception as e:
        pass
    finally:
        await ws.close()

    file.close()
    return ws
