import motor.motor_asyncio
from info import DATABASE_NAME, DATABASE_URI


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.perm = self.db.permissions
        self.restr = self.db.restrictions

    def new_locks(self, chat_id, locked):
        return dict(
            chat_id=str(chat_id),
            audio=locked, voice=locked,
            contact=locked, video=locked,
            document=locked, photo=locked,
            sticker=locked, gif=locked,
            url=locked, bots=locked,
            forward=locked, game=locked,
            location=locked,
        )

    def new_restrictions(self, chat_id, locked):
        return dict(
            chat_id=str(chat_id),
            messages=locked, media=locked,
            other=locked, preview=locked,
        )

    async def add_locks(self, chat_id, locked):
        locks = self.new_locks(chat_id, locked)
        await self.perm.insert_one(locks)

    async def add_restrictions(self, chat_id, locked):
        restr = self.new_locks(chat_id, locked)
        await self.restr.insert_one(restr)

    async def is_locks_exist(self, chat_id):
        locks = await self.perm.find_one({'chat_id': int(chat_id)})
        return bool(locks)

    async def update_locks(self, chat_id, lock_type, locked):
        if lock_type == "audio":
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'audio': locked}})
        elif lock_type == "voice":
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'voice': locked}})
        elif lock_type == "contact":
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'contact': locked}})
        elif lock_type == "video":
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'video': locked}})
        elif lock_type == "document":
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'document': locked}})
        elif lock_type == "photo":
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'photo': locked}})
        elif lock_type == "sticker":
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'sticker': locked}})
        elif lock_type == "gif":
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'gif': locked}})
        elif lock_type == 'url':
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'url': locked}})
        elif lock_type == 'bots':
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'bots': locked}})
        elif lock_type == 'forward':
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'forward': locked}})
        elif lock_type == 'game':
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'game': locked}})
        elif lock_type == 'location':
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'location': locked}})

    async def update_restrictions(self, chat_id, restr_type, locked):
        if restr_type == "messages":
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'messages': locked}})
        elif restr_type == "media":
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'media': locked}})
        elif restr_type == "other":
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'other': locked}})
        elif restr_type == "previews":
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'preview': locked}})
        elif restr_type == "all":
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'messages': locked}})
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'media': locked}})
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'other': locked}})
            await self.perm.update_one({'chat_id': chat_id}, {'$set': {'preview': locked}})


l_db = Database(DATABASE_URI, DATABASE_NAME)
