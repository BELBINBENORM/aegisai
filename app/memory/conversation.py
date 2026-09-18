from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.models.message import Message


class ConversationMemory:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.session_factory = session_factory

    async def add_message(
        self,
        session_id: int,
        role: str,
        content: str,
    ) -> Message:
        async with self.session_factory() as session:
            message = Message(
                session_id=session_id,
                role=role,
                content=content,
            )

            session.add(message)
            await session.commit()
            await session.refresh(message)

            return message

    async def get_messages(
        self,
        session_id: int,
    ) -> list[Message]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Message)
                .where(Message.session_id == session_id)
                .order_by(Message.id)
            )

            return list(result.scalars().all())

    async def clear(self, session_id: int) -> None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Message).where(
                    Message.session_id == session_id
                )
            )

            messages = result.scalars().all()

            for message in messages:
                await session.delete(message)

            await session.commit()