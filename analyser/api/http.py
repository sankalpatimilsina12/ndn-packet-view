from scapy.utils import PcapReader
import aiohttp
import glob
import os
import time

from definitions import DATA_DIR
from tools import Parser, Indexer

routes_http = aiohttp.web.RouteTableDef()


@routes_http.get('/files/')
async def files_handler(request):
    os.chdir(DATA_DIR)
    compressed_files = glob.glob('*.pcap') + glob.glob('*.pcapng')

    return aiohttp.web.json_response(status=aiohttp.web.HTTPOk.status_code, data=compressed_files)


@routes_http.get('/index/{filename}')
async def index_handler(request):
    filename = request.query.get('filename')
    ext = os.path.splitext(filename)[1]

    if ext == '.pcap' or ext == '.pcapng':
        fp = PcapReader(os.path.join(DATA_DIR, filename))
    else:
        return aiohttp.web.json_response(status=aiohttp.web.HTTPUnsupportedMediaType.status_code,
                                         data='Unsupported file type. Supported types: pcap, pcapng')

    try:
        start_time = time.time()
        p = Parser()
        i = Indexer(request.app['db'])
        for packet in fp:
            info = p.parse(packet)
            if info is not None:
                i.index_packet(info[0], info[1])
    except Exception as e:
        return aiohttp.web.json_response(status=aiohttp.web.HTTPInternalServerError.status_code)

    fp.close()
    print(f'File: `{filename}` indexed in {time.time() - start_time} seconds.')
    return aiohttp.web.json_response(status=aiohttp.web.HTTPOk.status_code,
                                     data=f'File `{filename}` indexed in {time.time() - start_time} seconds.')