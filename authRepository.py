import json
import os
from typing import Dict, List, Set

import CynanBotCommon.utils as utils


class AuthRepository():

    def __init__(
        self,
        authFile: str = 'authRepository.json'
    ):
        if not utils.isValidStr(authFile):
            raise ValueError(f'authRepository argument is malformed: \"{authFile}\"')

        self.__authFile: str = authFile

    def __readJson(self) -> Dict[str, object]:
        if not os.path.exists(self.__authFile):
            raise FileNotFoundError(f'Auth file not found: \"{self.__authFile}\"')

        with open(self.__authFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from auth file: \"{self.__authFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of auth file \"{self.__authFile}\" is empty')

        return jsonContents

    def requireNick(self) -> str:
        jsonContents = self.__readJson()

        nick = jsonContents.get('nick')
        if not utils.isValidStr(nick):
            raise ValueError(f'\"nick\" in auth file \"{self.__authFile}\" is malformed: \"{nick}\"')

        return nick

    def requireTwitchChannels(self) -> List[str]:
        jsonContents = self.__readJson()

        twitchChannelsJson: List[str] = jsonContents.get('twitchChannels')
        if not utils.areValidStrs(twitchChannelsJson):
            raise ValueError(f'\"twitchChannels\" in auth file \"{self.__authFile}\" is malformed: \"{twitchChannelsJson}\"')

        twitchChannelsSet: Set[str] = set()
        for twitchChannel in twitchChannelsJson:
            twitchChannelsSet.add(twitchChannel.lower())

        twitchChannelsList: List[str] = list(twitchChannelsSet)
        twitchChannelsList.sort()

        return twitchChannelsList

    def requireTwitchClientId(self) -> str:
        jsonContents = self.__readJson()

        twitchClientId = jsonContents.get('twitchClientId')
        if not utils.isValidStr(twitchClientId):
            raise ValueError(f'\"twitchClientId\" in auth file \"{self.__authFile}\" is malformed: \"{twitchClientId}\"')

        return twitchClientId

    def requireTwitchClientSecret(self) -> str:
        jsonContents = self.__readJson()

        twitchClientSecret = jsonContents.get('twitchClientSecret')
        if not utils.isValidStr(twitchClientSecret):
            raise ValueError(f'\"twitchClientSecret\" in auth file \"{self.__authFile}\" is malformed: \"{twitchClientSecret}\"')

        return twitchClientSecret

    def requireTwitchIrcAuthToken(self) -> str:
        jsonContents = self.__readJson()

        twitchIrcAuthToken = jsonContents.get('twitchIrcAuthToken')
        if not utils.isValidStr(twitchIrcAuthToken):
            raise ValueError(f'\"twitchIrcAuthToken\" in auth file \"{self.__authFile}\" is malformed: \"{twitchIrcAuthToken}\"')

        return twitchIrcAuthToken
