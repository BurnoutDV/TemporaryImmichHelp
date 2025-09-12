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

import datetime

import requests
import re
import json
import console_garnish as cg

from copy import copy
from reused_tools import recursive_input_regex, recursive_number_input, simple_progress_bar

LINE_TRESHHOLD = 30 # number of Lines that get show for Regex Filters

def _get_all_tags(cred:dict) -> dict:
    """
    Retrieves all available tags from the API

    :param cred: API Credentials
    :return: dictionary {name: UUID}
    """
    API_KEY = cred['api_key']
    INSTANCE = cred['instance']
    url = INSTANCE + "tags"
    payload = {}
    headers = {
        'Accept': 'application/json',
        'x-api-key': API_KEY
    }
    resp = requests.request("GET", url, headers=headers, data=payload)
    resp_dict = resp.json()
    keyvalue = dict()
    for tag_dict in resp_dict:
        keyvalue[tag_dict['name']] = tag_dict['id']
    return keyvalue

def _filter_tags_by_regex(regex:str, tags: dict):
    """
    Filters the given dictionary with the provided regex
    and gives back all those hits and discards the rest
    :param regex: Regex string
    :param tags: dictionary of tags {Name: UUID}
    :return:
    """
    pattern = re.compile(regex)
    hits = {} # I just add the entire thing instead of just the name
    for key, value in tags.items():
        if pattern.match(key):
            hits[key] = value
    return hits

def _get_assoc_assets(cred: dict, tag_id: str, page:int=1, recursive_list:list = []) -> list | bool:
    """
    Retrieves the asset IDs for one tag for later use (in this context mostly for rollback
    :param tag_id: UUID of the tag that is searched of
    :param page: results might be paginated, with more than 250 hits per page
    :param recursive_list: transfer list for the recursive use of this
    :return:
    """
    API_KEY = cred['api_key']
    INSTANCE = cred['instance']
    url = INSTANCE + "search/metadata"
    payload = json.dumps({
      "tagIds": [
        tag_id
      ],
      "page": page # turns out, this is paginated if there are more than 250 of them
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': API_KEY
    }
    resp = requests.request("POST", url, headers=headers, data=payload)
    data = resp.json()
    new_page = None
    saved_entries = [] # for rollbacks
    if recursive_list:
        saved_entries = copy(recursive_list) # i had this without copy before and it was accumulating..but it shouldn't?
    try:
        if 'nextPage' in data['assets']:
            new_page = data['assets']['nextPage']
        for item in data['assets']['items']:
            saved_entries.append(item['id'])
        if new_page:
            return _get_assoc_assets(cred, tag_id, new_page, recursive_list) # I really love recursion in the project
        else:
            return saved_entries
    except KeyError:
        print(cg.color("Response seems to be malformed", "pure_red"))
        print(data)
        return False

def _actually_delete_tags(creds: dict, tag_ids: dict) -> bool:
    """
    Deletes all provided tags

    :param creds: Credentials for the API (Instance url & API key)
    :param tag_ids:
    :return: If _everything_ worked True, if there were errors, False
    """
    countdown = len(tag_ids.items())
    errors = {}
    for i, (key, value) in enumerate(tag_ids.items()):
        resp = _delete_one_tag(creds, value)
        simple_progress_bar(i, countdown, "DEL", f"{i+1}/{countdown}")
        if resp['statusCode'] != 200:
            errors[key] = {'value': value, 'message': resp['error']}
    simple_progress_bar(0, 0, clear=True) # * Reset line to empty
    print(f"Deleted {countdown} tags", end="")
    if len(errors) <= 0:
        print(" with no errors.")
        return True
    else:
        print(f"With {len(errors)} errors. Listing:")
        for key, value in errors.items():
            print(f"\t{key} - {value['message']}")
        return False

def _delete_one_tag_from_assets(creds:dict, tag_id: str, asset_ids: list):
    """
    EDIT: Nevermind, this is not the case, IMMICH actually works the way I thought it would

    This is just great, to actually delete a tag you first need to get rid of every single
    instance where that tag is used, I mean, its logical, but I was really hoping that
    immich just does this automatically and does everything in the backroom without
    bothering me about details. On other hand, I am glad that I got this level
    of control

    :param creds:
    :param tag_id:
    :param asset_id:
    :return:
    """
    API_KEY = creds['api_key']
    INSTANCE = creds['instance']
    url = INSTANCE + "tags/" + tag_id + "/assets"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': API_KEY
    }
    payload = json.dumps({
        "ids": asset_ids
    })
    print(f"Deleting TAG [{tag_id}] from Assets [{", ".join(asset_ids)}]")
    resp = requests.request("DELETE", url, headers=headers, data=payload)
    print(resp.text)
    #400 BAD REQUEST
    #404 NOT FOUND

def _delete_one_tag(creds: dict, tag_id: str):
    """
    Apparently one has to delete all instances of the used tag first. Pain.
    :param creds:
    :param tag_id:
    :return:
    """
    API_KEY = creds['api_key']
    INSTANCE = creds['instance']
    url = INSTANCE + "tags/" + tag_id
    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': API_KEY
    }
    resp = requests.request("DELETE", url, headers=headers, data=payload)
    if resp.status_code == 204: # HTML 204 NO CONTENT
        return {'statusCode': 200, 'message': "Success"} # there is actually no text response upon success, so I craft my own for unified output
    else:
        return json.loads(resp.text)

def tag_delete_by_regex(creds: dict, default_regex:str="") -> bool:
    """
    Console input routine for deleting a number of tags that match
    a regex

    :param creds: Credentials for the Immich API
    :param default_regex: pre filled regex for recursion purpose
    :return: If everything was successfully, True
    """
    print(f"\x1b[2J\033[H{cg.color("Temporary Immich Help Scripts", "bright_purple")}")
    print("Let's delete some tags..within reason of course.")
    print(cg.color("Note: tags wont be deleted right away, you get to review them first and alter your regex if needed.", "grey"))
    ###
    ### DECISION: REGEX INPUT
    ###
    print(cg.color("Enter a valid python regex", "bold"))
    my_regex = recursive_input_regex("Regex Str: ", default_regex)
    tags = _get_all_tags(creds)
    #print(tags)
    filtered_tags = _filter_tags_by_regex(my_regex, tags)
    number_of_tags = len(filtered_tags)
    if number_of_tags <= 0:
        print(f"Error: {cg.color("Not a single hit, you might want to try again", "pure_red")}")
        input("Press the ANY key to continue")
        return tag_delete_by_regex(creds, my_regex)
    if number_of_tags  > LINE_TRESHHOLD:
        ###
        ### DECISION: MANY LINES
        ###
        print(f"\x1b[2J\033[H{cg.color("Temporary Immich Help Scripts","bright_purple")}")
        print(f"There are more than {LINE_TRESHHOLD} lines in the result set: display, abort or retry?")
        print(f"1 - Display result set anyway ({number_of_tags} lines)")
        print("2 - Abort entire process and exit")
        print("3 - Retry and enter different Regex")
        number = recursive_number_input(1, 3)
        if number == 2:
            print("kthxbye, till next time")
            return False
        if number == 3: # do this 255 times and python hates you
            tag_delete_by_regex(creds)
            return False
    for i, key in enumerate(filtered_tags.keys()):
        print(f"{i} - {key}")
        if i and i % 500 == 0:
            print(f"Haltpoint - More entries ({number_of_tags-i}) to come, press ENTER")
            input()
    ###
    ### DECISION: DELETE OR EDIT
    ###
    input("Press the ANY key to continue")
    print(f"\x1b[2J\033[H{cg.color("Temporary Immich Help Scripts","bright_purple")}")
    print(cg.color("Are those hits to your liking?", "bold"))
    print(cg.color("1 - Delete selected tags", "pure_red"))
    print("2 - Enter/Edit Regex")
    number = recursive_number_input(1, 2)
    if number == 2:
        return tag_delete_by_regex(creds, my_regex)
    # if number == 1 GO AHEAD
    saved_tags = {} # * so this is plain text tag to asset uuid
    tag_id_to_asset = {} # + and this is UUID tag to asset uuid
    print("Creating a backup file to make a roll back later possible.")
    tag_len = len(filtered_tags)
    print(cg.color(f"Note: These are {tag_len} API calls, so it takes a while due networking.","grey"))
    for i, (key, value) in enumerate(filtered_tags.items()):
        asset_list = _get_assoc_assets(creds, value)
        progress_number_str = f"{str(i+1)}/{str(tag_len)}"
        simple_progress_bar(i, tag_len, "Save", progress_number_str)
        #print(f"Saves: [{key}:{value}] {len(asset_list)}") # todo: one line ncurse progress bar here
        saved_tags[key] = asset_list
        tag_id_to_asset[value] = asset_list
    simple_progress_bar(0, 0, clear=True) # * Reset line to empty
    file_name = "TagRollback" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
    print("Creating rollback file...")
    with open(file_name, "w") as js_io:
        save_object = {
            'dateCreated': datetime.datetime.now().isoformat(),
            'tags': saved_tags
        }
        json.dump(save_object, js_io, indent=2)
    _actually_delete_tags(creds, filtered_tags)
    return True

if __name__ == "__main__":
    print("This file is part of TemporarImmichHelp, but does nothing in itself. Run main.py")