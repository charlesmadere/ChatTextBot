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

    def __init__(
        self,
        timber: Timber,
        bufferSize: int = 100,
        additionalLinesFile: str = 'additionalLines.txt'
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidNum(bufferSize):
            raise ValueError(f'bufferSize argument is malformed: \"{bufferSize}\"')
        elif bufferSize < 64 or bufferSize > 2048:
            raise ValueError(f'bufferSize argument is out of bounds: {bufferSize}')
        elif not utils.isValidStr(additionalLinesFile):
            raise ValueError(f'additionalLinesFile argument is malformed: \"{additionalLinesFile}\"')

        self.__timber: Timber = timber
        self.__bufferSize: int = bufferSize
        self.__additionalLinesFile: str = additionalLinesFile

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
        bufferIndex: int = 0
        lineNumber: int = -1
        readLines: int = 0
        discardedLines: int = 0

        async with aiofile.AIOFile(fileName, 'r') as file:
            async for line in aiofile.LineReader(file):
                lineNumber = lineNumber + 1

                cleanedSplits = utils.getCleanedSplits(line)
                if not utils.hasItems(cleanedSplits):
                    discardedLines = discardedLines + 1
                    continue

                readLines = readLines + 1
                splits.extend(cleanedSplits)
                bufferIndex = bufferIndex + 1

                if bufferIndex < self.__bufferSize or not utils.hasItems(splits):
                    continue

                self.__timber.log('DumpCommand', f'Buffer now filled at line number {lineNumber}')

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
        if not os.path.exists(self.__additionalLinesFile):
            return list()

        additionalLines: Set[str] = set()

        async with aiofile.AIOFile(self.__additionalLinesFile, 'r') as file:
            async for line in aiofile.LineReader(file):
                if utils.isValidStr(line):
                    additionalLines.add(line.strip())

        return list(additionalLines)
