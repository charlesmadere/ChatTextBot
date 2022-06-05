import json
import os
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Set

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
        bufferSize: int = 128,
        dumpSettingsFile: str = 'dumpSettings.json'
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidNum(bufferSize):
            raise ValueError(f'bufferSize argument is malformed: \"{bufferSize}\"')
        elif bufferSize < 64 or bufferSize > 2048:
            raise ValueError(f'bufferSize argument is out of bounds: {bufferSize}')
        elif not utils.isValidStr(dumpSettingsFile):
            raise ValueError(f'dumpSettingsFile argument is malformed: \"{dumpSettingsFile}\"')

        self.__timber: Timber = timber
        self.__bufferSize: int = bufferSize
        self.__dumpSettingsFile: str = dumpSettingsFile

    async def __getAdditionalLine(self) -> str:
        additionalLines = await self.__readAdditionalLines()

        if utils.hasItems(additionalLines):
            return random.choice(additionalLines)
        else:
            return None

    async def __getAdditionalLineChance(self) -> float:
        jsonContents = await self.__readJson()
        return utils.getFloatFromDict(jsonContents, 'additionalLineChance', 0.02)

    async def __getAdditionalLinesFile(self) -> str:
        jsonContents = await self.__readJson()
        return utils.getStrFromDict(jsonContents, 'additionalLinesFile', 'additionalLines.txt')

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

                self.__timber.log('DumpCommand', f'Buffer is now filled at line number {lineNumber}')

                bufferIndex = 0
                joinedSplits = ' '.join(splits)
                splits.clear()

                sentences: List[str] = tokenizer.tokenize(joinedSplits)

                if random.random() <= self.__getAdditionalLineChance():
                    additionalLine = await self.__getAdditionalLine()

                    if utils.isValidStr(additionalLine):
                        sentences.append(additionalLine)
                        self.__timber.log('DumpCommand', f'Added line: \"{additionalLine}\"')

                for sentence in sentences:
                    await twitchUtils.safeSend(ctx, sentence)

        self.__timber.log('DumpCommand', f'From \"{fileName}\", {readLines} line(s) were sent, and {discardedLines} line(s) were discarded.')

    async def __readAdditionalLines(self):
        additionalLinesFile = await self.__getAdditionalLinesFile()

        if not os.path.exists(additionalLinesFile):
            return list()

        additionalLines: Set[str] = set()

        async with aiofile.AIOFile(additionalLinesFile, 'r') as file:
            async for line in aiofile.LineReader(file):
                if utils.isValidStr(line):
                    additionalLines.add(line.strip())

        return list(additionalLines)

    async def __readJson(self) -> Dict[str, object]:
        if not os.path.exists(self.__dumpSettingsFile):
            raise FileNotFoundError(f'Dump settings file not found: \"{self.__dumpSettingsFile}\"')

        with open(self.__dumpSettingsFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from dump settings file: \"{self.__dumpSettingsFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of dump settings file \"{self.__dumpSettingsFile}\" is empty')

        return jsonContents
