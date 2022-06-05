import asyncio

from authRepository import AuthRepository
from chatTextBot import ChatTextBot
from CynanBotCommon.timber.timber import Timber


authRepository = AuthRepository()
eventLoop = asyncio.get_event_loop()
timber = Timber(
    eventLoop = eventLoop
)

chatTextBot = ChatTextBot(
    eventLoop = eventLoop,
    authRepository = authRepository,
    timber = timber
)

timber.log('initChatTextBot', 'Starting ChatTextBot...')
chatTextBot.run()
