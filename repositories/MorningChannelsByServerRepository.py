from cassandra.cqlengine.management import sync_table

from bot.utility import generate_objects_hash
from models.MorningChannelsByServer import MorningChannelsByServer


class MorningChannelsByServerRepository:
    def __init__(self, connector):
        self.connector = connector
        sync_table(MorningChannelsByServer)

    async def add_channel(self, server_id, channel_id):
        server_hash = generate_objects_hash(server_id)
        channel_id = str(channel_id)
        records = MorningChannelsByServer.objects(server_hash=server_hash, channel_id=channel_id).all()
        if records:
            record = records[0]
            record.save()
        else:
            MorningChannelsByServer.create(server_hash=server_hash, channel_id=channel_id)

    async def remove_channel(self, server_id, channel_id):
        server_hash = generate_objects_hash(server_id)
        channel_id = str(channel_id)
        records = MorningChannelsByServer.objects(server_hash=server_hash, channel_id=channel_id).all()
        for record in records:
            record.delete()

    async def get_channels(self, server_id) -> list[str]:
        server_hash = generate_objects_hash(server_id)
        records = MorningChannelsByServer.objects(server_hash=server_hash).all()
        return [str(record.channel_id) for record in records]

    async def clear_all_entries(self):
        records = MorningChannelsByServer.objects.all()
        for record in records:
            record.delete()
