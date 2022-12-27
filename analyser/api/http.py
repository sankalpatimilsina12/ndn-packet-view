from aiohttp import web
import glob
import os
from definitions import DATA_DIR

routes_http = web.RouteTableDef()


@routes_http.get('/files/')
async def files_handler(request):
    os.chdir(DATA_DIR)
    compressed_files = glob.glob('*.zst') + glob.glob('*.gz')

    return web.json_response(status=web.HTTPOk.status_code, data=compressed_files)
