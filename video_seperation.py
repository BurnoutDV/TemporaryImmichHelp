#!/usr/bin/env python3
# coding: utf-8
# Copyright 2025 by BurnoutDV, <development@burnoutdv.com>
#
# This file is part of TemporaryImmichHelp.
#
# TemporaryImmichHelp is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# TemporaryImmichHelp is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# @license GPL-3.0-only <https://www.gnu.org/licenses/gpl-3.0.en.html>

import requests
import json

import console_garnish as cg
from reused_tools import sizeof_fmt, recursive_number_input, recursive_minimum_str_input

def _fetch_videos_of_album(creds: dict, album_uuid: str) -> None | dict:
    """
    Sends an API call and checks if the album actually exists.

    :param creds:  Credential dictionary {'instance': <url>, 'api_key': <key>}
    :param album_uuid: Immich Album UUID
    :return: None if the UUID didn't yield, or a dict {AssetUUID: {'createdAt', 'fileSize', 'fileName'}
    """
    API_KEY = creds['api_key']
    INSTANCE = creds['instance']
    url = f"{INSTANCE}albums/{album_uuid}"

    payload = {}
    headers = {
        'Accept': 'application/json',
        'x-api-key': API_KEY
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code != 200: # so success
        return None
    album_info = response.json()
    video_files = {}
    for asset in album_info['assets']:
        if asset['type'] == "VIDEO":
            video_files[asset['id']] = {'createdAt': asset['createdAt'],
                                        'fileSize': asset['exifInfo']['fileSizeInByte'],
                                        'fileName': asset['originalFileName']}
    return video_files

def _put_assets_in_new_album(creds: dict, new_album_name: str, *asset_uuids) -> bool:
    """
    Does what it says in the title..it also creates the album in the first place, but this is all one
    API call which makes it very convinient, needs the `album.create` permission

    In theory it would probably be wise if it would give back the new albums UUID, but in this context its not needed
    For future reference, its response.json()['id'] if status_code is 201

    :param creds: Credential dictionary {'instance': <url>, 'api_key': <key>}
    :param new_album_name: any one string, probably with a max length, shouldn't be blank
    :param asset_uuids: a list of uuids of existing assets
    :return: True or False whether this whole operation worked, no details
    """
    API_KEY = creds['api_key']
    INSTANCE = creds['instance']
    url = f"{INSTANCE}albums"

    # ! despite the docs saying something different, you actually don't have to specify the owner of the album
    # ! it just defaults to the owner of the API key which is the desired behaviour anyway
    payload = json.dumps({
        "albumName": new_album_name,
        "assetIds": asset_uuids,
        "description": "Album of only videos"
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': API_KEY
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 201:
        return True # * the response contains the entire new album and in theory we could check if everything is there
    return False
    # 201 on success

def video_seperation(creds: dict) -> bool:
    """
    Console driven dialogue to create a new album that only contains the videos of another mixed album

    :param creds: Credential dictionary {'instance': <url>, 'api_key': <key>}
    :return: True if the deed was done, False if not
    """
    print(f"\x1b[2J\033[H{cg.color("Temporary Immich Help Scripts", "bright_purple")}")
    print(cg.color("Note: First we fetch an album, then we extract all videos, some decisions, and then we create an album. The rest is up to you.", "grey"))
    album_uuid = recursive_minimum_str_input("Album UUID: ", 35) # ? one would actually need
    album_videos = _fetch_videos_of_album(creds, album_uuid)                 # ? recursive_str_input_validated_by_regex
    if not album_uuid:
        ###
        ### DECISION
        ###
        print(f"\x1b[2J\033[H{cg.color("Temporary Immich Help Scripts", "bright_purple")}")
        print(f"Error: {cg.color("The request came back without data, try again?", "pure_red")}")
        print(cg.color("Note: We don't debug here. At this point the API Endpoint, key and rights should be okay. But a wrong UUID is not the only possibility for a bad request here.", "grey"))
        print("1 - Retry (with a different album UUID)")
        print("2 - <Abort/Quit>")
        number = recursive_number_input(1, 2)
        if number == 2:
            return False
        else:
            return video_seperation(creds)
    # * Calculating total file size..for now reason at all
    kumo_size = 0 # byte
    for item in album_videos.values():
        kumo_size+= int(item['fileSize'])
    print(f"\x1b[2J\033[H{cg.color("Temporary Immich Help Scripts", "bright_purple")}")
    print(f"Found {len(album_videos)} videos in the provided album, with a total size of {sizeof_fmt(kumo_size)}.")
    ###
    ### DECISION:
    ###
    print("Make a choice:")
    print("1 - List all Entries (in 500 Batches)")
    print("2 - Continue")
    print("3 - <Abort/Quit>")
    number = recursive_number_input(1, 3)
    if number == 3:
        return False
    if number == 1:
        print(f"\x1b[2J\033[H{cg.color("Temporary Immich Help Scripts", "bright_purple")}")
        for i, asset in enumerate(album_videos.values()):
            print(f"[{i}] {asset['fileName']}, {sizeof_fmt(asset['fileSize'])} - {asset['createdAt']}")
            if i and i % 500 == 0:
                print(f"Haltpoint - More entries ({(len(album_videos) - i)}) to come, press ENTER")
                input()
        input("Press the ENTER key to continue")
        print(f"\x1b[2J\033[H{cg.color("Temporary Immich Help Scripts", "bright_purple")}")
        print(f"Decision point, {len(album_videos)} Videos fetched, next step: creating a new album")
        print("1 - Continue")
        print("2 - <Abort/Quit>")
        number = recursive_number_input(1, 2)
        if number == 2:
            return False
    print(f"\x1b[2J\033[H{cg.color("Temporary Immich Help Scripts", "bright_purple")}")
    print("Choose a name for the new album")
    new_album_name = recursive_minimum_str_input("Album Name: ")
    return _put_assets_in_new_album(creds, new_album_name, *album_videos.keys())