import asyncio
from typing import List

import CynanBotCommon.utils as utils
from twitchio.abcs import Messageable
from twitchio.errors import IRCCooldownError


def getMaxMessageSize() -> int:
    return 500

async def safeSend(
    messageable: Messageable,
    message: str,
    perMessageMaxSize: int = 450,
    maxMessages: int = 5,
    sleepTimeSeconds: int = 40
):
    if messageable is None:
        raise ValueError(f'messageable argument is malformed: \"{messageable}\"')
    elif not utils.isValidNum(perMessageMaxSize):
        raise ValueError(f'perMessageMaxSize argument is malformed: \"{perMessageMaxSize}\"')
    elif perMessageMaxSize < 300:
        raise ValueError(f'perMessageMaxSize is too small: {perMessageMaxSize}')
    elif perMessageMaxSize > getMaxMessageSize():
        raise ValueError(f'perMessageMaxSize is too big: {perMessageMaxSize} (max size is {getMaxMessageSize()})')
    elif not utils.isValidNum(maxMessages):
        raise ValueError(f'maxMessages argument is malformed: \"{maxMessages}\"')
    elif maxMessages < 1:
        raise ValueError(f'maxMessages is out of bounds: {maxMessages}')
    elif not utils.isValidNum(sleepTimeSeconds):
        raise ValueError(f'sleepTimeSeconds is malformed: \"{sleepTimeSeconds}\"')
    elif sleepTimeSeconds < 40:
        raise ValueError(f'sleepTimeSeconds is out of bounds: {sleepTimeSeconds}')

    if not utils.isValidStr(message):
        return

    if len(message) < getMaxMessageSize():
        await messageable.send(message)
        return

    messages: List[str] = list()
    messages.append(message)

    index: int = 0

    while index < len(messages):
        m: str = messages[index]

        if len(m) >= getMaxMessageSize():
            spaceIndex = m.rfind(' ')

            while spaceIndex >= perMessageMaxSize:
                spaceIndex = m[0:spaceIndex].rfind(' ')

            if spaceIndex == -1:
                raise RuntimeError(f'This message is insane and can\'t be sent (len is {len(message)}):\n{message}')

            messages[index] = m[0:spaceIndex].strip()
            messages.append(m[spaceIndex:len(m)].strip())

        index = index + 1

    if len(messages) > maxMessages:
        raise RuntimeError(f'This message is too long and won\'t be sent (len is {len(message)}):\n{message}')

    for m in messages:
        try:
            await messageable.send(m)
        except:
            await asyncio.sleep(sleepTimeSeconds)
            await messageable.send(m)

async def waitThenSend(
    messageable: Messageable,
    delaySeconds: int,
    message: str,
    heartbeat = lambda: True,
    beforeSend = lambda: None,
    afterSend = lambda: None
):
    if messageable is None:
        raise ValueError(f'messageable argument is malformed: \"{messageable}\"')
    elif not utils.isValidNum(delaySeconds):
        raise ValueError(f'delaySeconds argument is malformed: \"{delaySeconds}\"')
    elif delaySeconds < 1:
        raise ValueError(f'delaySeconds argument is out of bounds: \"{delaySeconds}\"')
    elif not utils.isValidStr(message):
        return
    elif heartbeat is None:
        raise ValueError(f'heartbeat argument is malformed: \"{heartbeat}\"')

    await asyncio.sleep(delaySeconds)

    if heartbeat():
        beforeSend()
        await safeSend(messageable, message)
        afterSend()
