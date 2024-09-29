from select import select

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from databases.models import File


class FileDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def _get_file_by_file_key(self, file_key: str) -> File:
        query = select(File).where(File.file_key == file_key)
        result = await self.db_session.execute(query)
        file = result.scalar_one()
        return file

    async def get_file_keys_by_related_type_and_id(
        self, related_type: str, related_id: int
    ) -> list[str]:
        query = select(File.file_key).where(
            and_(File.related_type == related_type, File.related_id == related_id)
        )
        result = await self.db_session.execute(query)
        file_keys = result.scalars().all()
        return file_keys

    async def create_file(self, file_key: str, related_type: str, related_id: int):
        db_file = File(
            file_key=file_key, related_type=related_type, related_id=related_id
        )
        self.db_session.add(db_file)
        await self.db_session.commit()

    async def delete_file(self, file_key: str):
        db_file = await self._get_file_by_file_key(file_key)
        await self.db_session.delete(db_file)
