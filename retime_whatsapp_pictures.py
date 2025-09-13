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
from datetime import datetime
import re

import console_garnish as cg
from reused_tools import recursive_input_regex, recursive_number_input, simple_progress_bar

WA_IMAGE_REGEX = r"(IMG-)([0-9]{8})(-WA[0-9]{4}.jpg)"  # ? change this if you got like .jpeg or so
# ! match  group 2 must be the date


def _change_asset_date(creds: dict, photo_uuid: str, new_date: str) -> requests.Response:
    """
    Changes the dateTimeOriginal of a singular asset. Nothing more.

    As this functions works slightly different, you might already suspect that i lifted
    this from elsewhere. It was from a now unnecessary project that was changing the
    timezone and datetime of albums. I used it here as drop in, and it is probably
    the structure that all the API call functions should have had, no frills, only
    the pure call and giving back the request handle. You know, proper form.

    :param creds: Credential dictionary {'instance': <url>, 'api_key': <key>}
    :param photo_uuid: uuid oh a singular asset/image
    :param new_date: the new date in datetime.isoformat(timespec='milliseconds')
    :return: the pure request object from the request library
    """
    API_KEY = creds['api_key']
    INSTANCE = creds['instance']
    url = f"{INSTANCE}assets"
    payload = json.dumps({
        "dateTimeOriginal": new_date,
        "ids": [
            photo_uuid
        ]
    })
    headers: dict[str, str] = { # its so obvious that i c&p this from elsewhere
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': API_KEY
    }
    return requests.request("PUT", url, headers=headers, data=payload)


def _extract_wa_image_date(file_name: str) -> datetime | None:
    """
    Throws Regex on a provided file_name, also double as check
    if the file name actually fits the prescribed format

    :param file_name: random file name
    :return: None if no match was found, otherwise a datetime (with 12:04 and 6 seconds as time part)
    """
    pattern = re.compile(WA_IMAGE_REGEX)
    matches = pattern.match(file_name)
    if not matches:
        return None
    yearmonthday = matches.group(2)
    return datetime.strptime(f"{yearmonthday}-120406", "%Y%m%d-%H%M%S") #12:04:06 is just a random time


def _check_album_uuid(creds: dict, album_uuid: str) -> None | dict:
    """
    Sends an API call and checks if the album actually exists.

    :param creds:  Credential dictionary {'instance': <url>, 'api_key': <key>}
    :param album_uuid: Immich Album UUID
    :return: None if the UUID didn't yield, or a dict {AssetUUID: AssetFileName}
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
    name_list = {}
    for i, asset in enumerate(album_info['assets']):
        name_list[asset['id']] = asset['originalFileName']
        # ? names should be like "IMG-20150112-WA0017.jpg"
    return name_list


def _bulk_change_asset_date(creds:dict, dict_of_uuids: dict) -> bool:
    """
    Changes all provided assets to the accompanied date

    Provides rudimentary interface for error handling

    :param creds:  Credential dictionary {'instance': <url>, 'api_key': <key>}
    :param dict_of_uuids: {<UUID:str>: <ISODATE:str>}
    :return: Always True
    """
    countdown = len(dict_of_uuids)
    errors = {}
    for i, (key, value) in enumerate(dict_of_uuids.items()):
        simple_progress_bar(i, countdown, "PUT", f"{i + 1}/{countdown}")
        resp = _change_asset_date(creds, key, value)
        if resp.status_code != 204: # 204 NO CONTENT is to expected when doing a put
            errors[key] = f"{resp.status_code} - {resp.text}"
    simple_progress_bar(0, 0, clear=True)
    if len(errors) > 0:
        print(cg.color(f"There were {len(errors)} errors in the process (of {countdown} entries in total)", "pure_red"))
        print(f"There are two choices now")
        print("1 - Review Errors")
        print("2 - Ignore them and continue")
        number = recursive_number_input(1, 2)
        if number == 1:
            for uuid, text in errors.items():
                print(f"[{uuid}] {text}")
    print("Process done, press ENTER to continue")
    input()
    return True


def retime_whatsapp_pictures(creds) -> bool:
    """

    :param creds:  Credential dictionary {'instance': <url>, 'api_key': <key>}
    :return: True if everything went true, or False if the process was aborted
    """
    print(f"\x1b[2J\033[H{cg.color("Temporary Immich Help Scripts", "bright_purple")}")
    print("Let's scramble the dates of a few files")
    print(cg.color("Note: This works as follows: you first put the pictures you want manually into an album","grey"))
    print(cg.color("Then, you copy & paste the UUID here and \"I\" do the magic. Hopefully","grey"))
    album_uuid = input("Album UUID: ")
    names = _check_album_uuid(creds, album_uuid)
    new_dates = {}
    list_of_errors = []
    for key, value in names.items():
        if new_date := _extract_wa_image_date(value):
            new_dates[key] = new_date.isoformat(timespec='milliseconds')
        else:
            list_of_errors.append(value)
    print(f"\x1b[2J\033[H{cg.color("Temporary Immich Help Scripts", "bright_purple")}")
    print(f"<I/We> found {len(names)} entries in Album {album_uuid}")
    print(f"<We/I> already converted all file names to proper datetimes and back to an ISO Format")
    if len(list_of_errors) > 0:
        print(f"...but with {len(list_of_errors)} errors. Do you wish to review those? (Comes in 500 Batches)")
        print("1 - Review Errors")
        print("2 - Write those errors to an log file")
        print(cg.color("3 - Ignore those and just continue", "pure_red"))
        number = recursive_number_input(1, 3)
        if number == 1:
            for i, file_name in enumerate(list_of_errors):
                print(f"{i} - {file_name}")
                if i and i % 500 == 0:
                    print(f"Haltpoint - More entries ({(len(list_of_errors) - i)}) to come, press ENTER")
                    input()
        if number == 2:
            log_file = f"WA-Errors_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log"
            with open(log_file, "w") as log_io:
                for file_name in list_of_errors:
                    log_io.write(f"{file_name}\n")
            print(f"Written all errors to local log file {log_file}")
    else:
        print("...without any errors. Which is awesome by the way. Good job building that album!")
    print("\nDo you wish to carry on and set new dates for ALL files")
    print(cg.color("Note: Every single change is an https API call..that takes time", "grey"))
    print(f"1 - Continue and change all album assets ({len(new_dates)} Assets)")
    print("2 - Abort everything")
    number = recursive_number_input(1, 2)
    if number == 2:
        return False
    _bulk_change_asset_date(creds, new_dates)
