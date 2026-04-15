from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user_repository import UserRepository as userrepo
from src.schemas.user_schemas import UserMeResponseSchema


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = userrepo(session)

    async def get_user_me_data_service(
        self, user_id: UUID
    ) -> UserMeResponseSchema | None:
        user_data = await self.repo.get_user_me_data(user_id)
        if not user_data:
            return None

        return UserMeResponseSchema.model_validate(user_data)
