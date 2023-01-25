from scapy.all import *
from ndn.encoding import *
from scapy.layers.inet import UDP
from definitions import MONGO_COLLECTION_NACK, MONGO_COLLECTION_INTEREST, MONGO_COLLECTION_DATA
from dataclasses import asdict


class Parser:
    def parse(self, packet):
        data = packet[UDP].load

        typ, _ = parse_tl_num(data)
        if typ == LpTypeNumber.LP_PACKET:
            try:
                nack_reason, fragment = parse_lp_packet(
                    data, with_tl=True)
            except (DecodeError, TypeError, ValueError, struct.error) as e:
                logging.warning('Unable to decode the LP packet')
                return
            data = fragment
            typ, _ = parse_tl_num(data)
        else:
            nack_reason = None

        if nack_reason is not None:
            try:
                name, _, _, _ = parse_interest(data, with_tl=True)
            except (DecodeError, TypeError, ValueError, struct.error):
                logging.warning(
                    'Unable to decode the fragment of LpPacket')
                return
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug('NetworkNack: %s, reason=%s' %
                              (Name.to_str(name), nack_reason))

            return MONGO_COLLECTION_NACK, {'name': Name.to_str(name), 'reason': nack_reason}
        else:
            if typ == TypeNumber.INTEREST:
                try:
                    name, param, app_param, sig = parse_interest(
                        data, with_tl=True)
                except (DecodeError, TypeError, ValueError, struct.error):
                    logging.warning('Unable to decode interest packet')
                    return
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug('Interest: %s' %
                                  Name.to_str(name))

                sig_type = None
                if sig.signature_info is not None:
                    sig_type = sig.signature_info.signature_type

                return MONGO_COLLECTION_INTEREST, {'name': Name.to_str(name), 'param': asdict(param),
                                                   'app_param': app_param, 'signature_type': sig_type}
            elif typ == TypeNumber.DATA:
                try:
                    name, meta_info, content, sig = parse_data(
                        data, with_tl=True)
                except (DecodeError, TypeError, ValueError, struct.error):
                    logging.warning('Unable to decode data packet')
                    return
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug('Data: %s' %
                                  Name.to_str(name))

                sig_type = None
                if sig.signature_info is not None:
                    sig_type = sig.signature_info.signature_type

                return MONGO_COLLECTION_DATA, {'name': Name.to_str(name), 'signature_type': sig_type}
            else:
                logging.warning('Unable to decode the packet')
                return
