import os
import random
from abc import ABC, abstractmethod
from typing import List, Set

import aiofile
import nltk.data
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
        splits.clear()

        self.__timber.log('DumpCommand', f'Preparing to read in \"{fileName}\"...')

        if not os.path.exists(fileName):
            self.__timber.log('DumpCommand', f'\"{fileName}\" does not exist!')
            return

        tokenizer = nltk.data.load('nltk:tokenizers/punkt/english.pickle')
        bufferSize: int = 100
        bufferIndex: int = 0
        lineNumber: int = -1
        readLines: int = 0
        discardedLines: int = 0

        async with aiofile.AIOFile(fileName, 'r') as file:
            async for line in aiofile.LineReader(file):
                lineNumber = lineNumber + 1
                self.__timber.log('DumpCommand', f'Reading in line number {lineNumber}...')

                cleanedSplits = utils.getCleanedSplits(line)
                if not utils.hasItems(cleanedSplits):
                    discardedLines = discardedLines + 1
                    continue

                readLines = readLines + 1
                splits.extend(cleanedSplits)
                bufferIndex = bufferIndex + 1

                if bufferIndex < bufferSize:
                    continue

                bufferIndex = 0
                joinedSplits = ' '.join(splits)
                splits.clear()

                parsed: List[str] = tokenizer.tokenize(joinedSplits)

                if random.random() <= 0.02:
                    additionalRngLines = await self.__readAdditionalLines()

                    if utils.hasItems(additionalRngLines):
                        additionalRngLine = random.choice(additionalRngLines)
                        parsed.append(additionalRngLine)
                        self.__timber.log('DumpCommand', f'Added RNG line: \"{additionalRngLine}\"')

                for sentence in parsed:
                    await twitchUtils.safeSend(ctx, sentence)

        self.__timber.log('DumpCommand', f'From \"{fileName}\", {readLines} line(s) were sent, and {discardedLines} line(s) were discarded.')

    async def __readAdditionalLines(self):
        if not os.path.exists('additionalLines.txt'):
            return list()

        additionalLines: Set[str] = set()

        async with aiofile.AIOFile('additionalLines.txt', 'r') as file:
            async for line in aiofile.LineReader(file):
                if utils.isValidStr(line):
                    additionalLines.add(line)

        return list(additionalLines)
