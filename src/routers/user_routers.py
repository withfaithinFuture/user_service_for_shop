from fastapi import APIRouter
from fastapi.params import Depends

from src.core.exceptions import NotFoundError
from src.models.user import User
from src.app.dependencies import get_user_service
from src.services.user_service import UserService
from logreg.security import get_current_user


router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.get('/me')
async def get_me(current_user: User = Depends(get_current_user), user_service: UserService = Depends(get_user_service)):
    result = await user_service.get_user_me_data_service(user_id=current_user.userId)
    if result is None:
        raise NotFoundError(current_user.userId, 'User')

    return result