import os
from abc import ABC, abstractmethod

import aiofile
from twitchio.ext.commands import Context

import CynanBotCommon.utils as utils
import twitch.twitchUtils as twitchUtils
from CynanBotCommon.timber.timber import Timber


class AbsCommand(ABC):

    @abstractmethod
    async def handleCommand(self, ctx: Context):
        pass


class DumpCommand(AbsCommand):

    def __init__(self, timber: Timber):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__timber: Timber = timber

    async def handleCommand(self, ctx: Context):
        if not ctx.author.is_mod or ctx.author.name.lower() != ctx.channel.name.lower():
            return

        splits = utils.getCleanedSplits(ctx.message.content)
        if len(splits) < 2:
            return

        fileName = splits[2]
        self.__timber.log('DumpCommand', f'Preparing to read in \"{fileName}\"...')

        if not os.path.exists(fileName):
            self.__timber.log('DumpCommand', f'\"{fileName}\" does not exist!')
            return

        lines: int = 0
        discardedLines: int = 0

        async with aiofile.AIOFile(fileName, 'r') as file:
            async for line in aiofile.LineReader(file):
                if utils.isValidStr(line):
                    lines = lines + 1
                    await twitchUtils.safeSend(ctx, line)
                else:
                    discardedLines = discardedLines + 1

        self.__timber.log('DumpCommand', f'From \"{fileName}\", {lines} line(s) were sent, and {discardedLines} line(s) were discarded.')
