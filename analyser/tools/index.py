import os
import json
import argparse
from settings import DB, MONGO_COLLECTION_INTEREST, \
    MONGO_COLLECTION_DATA, MONGO_COLLECTION_LP_PACKET


class Indexer:
    def __init__(self, db):
        self.db = db

    def __index_packet(self, type, packet):
        self.db[type].insert_one(packet)

    def index_json(self, file_path):
        with open(file_path) as json_file:
            data = json.load(json_file)

        for packet in data:
            ndn_layer = packet['_source']['layers']['ndn']
            if 'ndn_interest' in ndn_layer:
                self.__index_packet(MONGO_COLLECTION_INTEREST, packet)
            elif 'ndn_data' in ndn_layer:
                self.__index_packet(MONGO_COLLECTION_DATA, packet)
            elif 'ndn_lp_packet' in ndn_layer:
                self.__index_packet(MONGO_COLLECTION_LP_PACKET, packet)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Index JSON file into MongoDB.", prog='python -m analyser.tools.index')
    parser.add_argument("file_path", help="Path to JSON file.")
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"Error: The file {args.file_path} does not exist.")
        exit(1)

    indexer = Indexer(DB)
    indexer.index_json(args.file_path)
