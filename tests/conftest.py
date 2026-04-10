# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
# from src.app.config import settings
# from src.app.application import get_app
# from src.db.db import get_session
#
#
# TEST_DATABASE_URL = settings.TEST_DATABASE_URL
#
# engine_test = create_async_engine(TEST_DATABASE_URL)
# session_maker_test = async_sessionmaker(engine_test, expire_on_commit=False)
#
# app = get_app()