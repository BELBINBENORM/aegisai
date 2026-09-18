import pytest

from app.database.connection import AsyncSessionLocal
from app.database.models.session import Session
from app.memory.conversation import ConversationMemory


@pytest.mark.asyncio
async def test_conversation_memory(test_user):
    async with AsyncSessionLocal() as db:
        chat_session = Session(
            user_id=test_user.id,
            title="Memory test",
        )

        db.add(chat_session)
        await db.commit()
        await db.refresh(chat_session)

        session_id = chat_session.id

    memory = ConversationMemory(AsyncSessionLocal)

    await memory.add_message(
        session_id,
        "user",
        "Hello",
    )

    await memory.add_message(
        session_id,
        "assistant",
        "Hello! How can I help?",
    )

    messages = await memory.get_messages(session_id)

    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == "Hello"
    assert messages[1].role == "assistant"

    await memory.clear(session_id)

    messages = await memory.get_messages(session_id)

    assert messages == []

    async with AsyncSessionLocal() as db:
        session = await db.get(Session, session_id)

        if session:
            await db.delete(session)
            await db.commit()