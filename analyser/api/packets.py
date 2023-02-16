import aiohttp
import bson
from ndn.encoding import SignatureType
from settings import DB, MONGO_COLLECTION_DATA

routes_packets = aiohttp.web.RouteTableDef()


@routes_packets.get('/packets/')
async def average_depth(request):
    r = {}
    for c_name in await DB.list_collection_names():
        r[c_name] = await DB[str(c_name)].count_documents({})

    return aiohttp.web.json_response(status=aiohttp.web.HTTPOk.status_code,
                                     data=r)


@routes_packets.get('/packets/{packet_id}/')
async def per_packet_info(request):
    r = None
    try:
        for c_name in await DB.list_collection_names():
            r = await DB[str(c_name)].find_one({'_id': bson.ObjectId(request.match_info['packet_id'])}, {'_id': 0})
            if r is not None:
                break
    except bson.errors.InvalidId:
        return aiohttp.web.json_response(status=aiohttp.web.HTTPNotFound.status_code,
                                         data={'error': f'Packet `{request.match_info["packet_id"]}` not found'})
    else:
        if r is None:
            return aiohttp.web.json_response(status=aiohttp.web.HTTPNotFound.status_code,
                                             data={'error': f'Packet `{request.match_info["packet_id"]}` not found'})

    return aiohttp.web.json_response(status=aiohttp.web.HTTPOk.status_code, data=r)


@routes_packets.get('/packets/data/signature/')
async def data_signature(request):
    sig = DB[MONGO_COLLECTION_DATA].aggregate([
        {
            '$facet': {
                'counts': [
                    {
                        '$group': {
                            '_id': {
                                '$ifNull': ['$_source.layers.ndn.ndn_signatureinfo.ndn_signaturetype',
                                            SignatureType.NOT_SIGNED]
                            },
                            'count': {'$sum': 1}
                        }
                    },
                    {
                        '$project': {
                            'type': '$_id',
                            'count': 1,
                            '_id': 0
                        }
                    }
                ],

                'data': [
                    {
                        '$match': {
                            '_source.layers.ndn.ndn_signatureinfo.ndn_signaturetype': {'$exists': True}
                        }
                    },
                    {
                        '$project': {
                            'packet_id': {'$toString': '$_id'},
                            '_id': 0,
                            'sig_info': '$_source.layers.ndn.ndn_signatureinfo'
                        }
                    },
                    {
                        '$skip': (int(request.query.get('page', 1)) - 1) * int(request.query.get('per_page', 10))
                    },
                    {
                        '$limit': int(request.query.get('per_page', 10))
                    }
                ]

            }
        }
    ])

    sig_m = {
        SignatureType.NOT_SIGNED: "NOT_SIGNED",
        SignatureType.DIGEST_SHA256: "DIGEST_SHA256",
        SignatureType.SHA256_WITH_RSA: "SHA256_WITH_RSA",
        SignatureType.SHA256_WITH_ECDSA: "SHA256_WITH_ECDSA",
        SignatureType.HMAC_WITH_SHA256: "HMAC_WITH_SHA256",
        SignatureType.ED25519: "ED25519",
        SignatureType.NULL: "NULL"
    }

    sig = [s async for s in sig]
    return aiohttp.web.json_response(status=aiohttp.web.HTTPOk.status_code, data={
        'counts': [{
            'type': sig_m.get(int(count['type'])),
            'count': count['count']
        } for count in sig[0]['counts']],
        'data': sig[0]['data'],
    })
