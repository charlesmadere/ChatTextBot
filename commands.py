import os
from abc import ABC, abstractmethod
from typing import List

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

        fileName = splits[1]
        self.__timber.log('DumpCommand', f'Preparing to read in \"{fileName}\"...')

        if not os.path.exists(fileName):
            self.__timber.log('DumpCommand', f'\"{fileName}\" does not exist!')
            return

        lines: int = 0
        discardedLines: int = 0
        splits: List[str] = list()

        async with aiofile.AIOFile(fileName, 'r') as file:
            async for line in aiofile.LineReader(file):
                if not utils.isValidStr(line):
                    discardedLines = discardedLines + 1
                    continue

                cleanedSplits = utils.getCleanedSplits(line)
                if not utils.hasItems(cleanedSplits):
                    continue

                lines = lines + 1
                splits.extend(cleanedSplits)
                cleanedLine = ' '.join(cleanedSplits)

                if len(cleanedLine) >= twitchUtils.getMaxMessageSize():
                    await twitchUtils.safeSend(ctx, cleanedLine)
                    splits.clear()

        self.__timber.log('DumpCommand', f'From \"{fileName}\", {lines} line(s) were sent, and {discardedLines} line(s) were discarded.')
