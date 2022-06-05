from asyncio import AbstractEventLoop

from twitchio import Channel, Message
from twitchio.ext import commands
from twitchio.ext.commands import Context
from twitchio.ext.commands.errors import CommandNotFound

from authRepository import AuthRepository
from commands import AbsCommand, DumpCommand
from CynanBotCommon.timber.timber import Timber


class ChatTextBot(commands.Bot):

    def __init__(
        self,
        eventLoop: AbstractEventLoop,
        authRepository: AuthRepository,
        timber: Timber
    ):
        super().__init__(
            client_secret = authRepository.requireTwitchClientSecret(),
            users = authRepository.requireTwitchChannels(),
            loop = eventLoop,
            nick = authRepository.requireNick(),
            prefix = '!',
            retain_cache = True,
            token = authRepository.requireTwitchIrcAuthToken()
        )

        if eventLoop is None:
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
        elif authRepository is None:
            raise ValueError(f'authRepository argument is malformed: \"{authRepository}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__eventLoop: AbstractEventLoop = eventLoop
        self.__authRepository: AuthRepository = authRepository
        self.__timber: Timber = timber

        self.__dumpCommand: AbsCommand = DumpCommand(timber)

        self.__timber.log('ChatTextBot', f'Finished initialization of {self.__authRepository.requireNick()}')

    async def event_command_error(self, context: Context, error: Exception):
        if isinstance(error, CommandNotFound):
            return
        else:
            raise error

    async def event_ready(self):
        self.__timber.log('ChatTextBot', f'{self.__authRepository.requireNick()} is ready!')

    @commands.command(name = 'dump')
    async def command_dump(self, ctx: Context):
        await self.__dumpCommand.handleCommand(ctx)
