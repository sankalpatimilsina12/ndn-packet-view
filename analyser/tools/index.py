class Indexer:
    def __init__(self, coll):
        self.coll = coll

    def index_packet(self, type, packet):
        self.coll[type].insert_one(packet)
    