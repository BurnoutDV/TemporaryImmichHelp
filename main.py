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
import console_garnish as cg
import json

from tag_delete_by_regex import tag_delete_by_regex
from reused_tools import recursive_number_input

def save_credentials_to_json(creds: dict) -> bool:
    """
    Saves credits into hard coded file in run time folder. Holy boilderplate batman.
    :param creds: credentials in std format { "api_key": <>, "instance": <>}
    :return: Always True, always. Catch some exceptions here Alan
    """
    with open('api_key.json', 'w') as api_json:
        json.dump(creds, api_json, indent=4)
    return True

def retrieve_api_key(test_only=False, skip_file=False) -> bool | dict:
    """
    Helper function to get the API key either from a json or by manual input

    :param test_only: if True it does not forward to the manual input
    :param skip_file: Skips the loading from file
    :return:
    """
    if skip_file:
        return manual_api_input()
    try:
        with open('api_key.json', "r") as api_json:
            try:
                key_file = json.load(api_json)
                return key_file
            except json.JSONDecodeError:
                print("Reading file failed, proceeding to manual input")
                if test_only:
                    return False
                return manual_api_input()
    except FileNotFoundError:
        print("No key file located, proceeding to manual input")
        if test_only:
            return False
        return manual_api_input()

def manual_api_input():
    print("[Instance] Copy & Paste (or enter) the path to the Instance API Endpoint")
    print(cg.color("Usually its https://<instances/api/", "grey"))
    instance = input("Instance: ")
    print("Copy & Paste (or enter) the API Key")
    api_key = input("API Key: ")
    return {'api_key': api_key, 'instance': instance}

def check_api_key_rights(cred: dict, *permissions) -> list | bool | None:
    API_KEY = cred['api_key']
    INSTANCE = cred['instance']
    url = INSTANCE + "api-keys/me"
    payload = {}
    headers = {
        'Accept': 'application/json',
        'x-api-key': API_KEY
    }
    try:
        resp = requests.request("GET", url, headers=headers, data=payload)
    except requests.exceptions.ConnectionError:
        return None # endpoint entirely wrong
    if resp.status_code == 404: # site not found / url exists but not correct
        return None # endpoint wrong
    if resp.status_code == 401: # wrong / false API key
        return False
    if resp.status_code == 200: # might have accidentally hit a page that works but is no endpoint:
        if resp.text[:15] == "<!doctype html>":
            return False
    resp_dict = resp.json()
    missing_perm = []
    for perm in permissions: # TODO: there is a better way to probe for list overlap
        if not perm in resp_dict['permissions']:
            missing_perm.append(perm)
    if missing_perm:
        return missing_perm
    return True # this is stupid, but if its None its good because nothing is missing

def recursive_api_key_retrieval(skip_file:bool=False) -> dict | bool:
    """
    Another recursive function that loops itself if something is amiss.

    :return: either False if the process is aborted or the 'creds' dictionary
    """
    creds = retrieve_api_key(skip_file=skip_file)
    check_res = check_api_key_rights(creds, *[])  # empty list should work if API endpoint is correct
    if check_res is None:
        print("The supplied API endpoint seems to not work. Abort or reenter?")
        print("1 - Reenter another API key and endpoint")
        print("2 - Abort process")
        number = recursive_number_input(1, 2)
        if number == 2:
            return False
        return recursive_api_key_retrieval(True)
    if not check_res: # endpoint correct (hopefully) but key false
        print("Endpoint seems okay, but key isnt accepted. Abort or reenter?")
        print("1 - Reenter another API key and endpoint")
        print("2 - Abort process")
        number = recursive_number_input(1, 2)
        if number == 2:
            return False
        return recursive_api_key_retrieval(True)
    if (other_creds := retrieve_api_key(True)) is False:
        print("Do you want to save the credentials in a file for later use?")
        print("1 - Save to file ('api_key.json')")
        print("2 - No, use only this session")
        number = recursive_number_input(1, 2)
        if number == 1:
            save_credentials_to_json(creds)
    else:
        if other_creds != creds:
            print("The new credentials seem to be different than before. Overwrite old key file?")
            print("1 - Save to file ('api_key.json')")
            print("2 - No, Keep it")
            number = recursive_number_input(1, 2)
            if number == 1:
                save_credentials_to_json(creds)
    return creds

PROCESSES = {
    1: {'name': "Delete Tags by Regex", 'active': True},
    2: {'name': "ReTime Whatsapp Pictures", 'active': False},
    3: {'name': "Rollback Tag Deletion", 'active': False}
}

if __name__ == "__main__":
    print(f"\x1b[2J\033[H{cg.color("Temporary Immich Help Scripts","bright_purple")}")
    print(f"Hello, Welcome to {cg.strike("Aperture Science Enrichment Center")}")
    print(f"...{cg.color("Temporary Immich Help Scripts", "pure_red")}")
    print("Checking for API Key")
    creds = recursive_api_key_retrieval()
    if not creds:
        print(cg.color("No work possible without API key, aborting...", "pure_red"))
        input("Press the mighty ANY key to exit()")
        exit(1)
    print("Looks good, proceeding...")
    print(f"\x1b[2J\033[H{cg.color("Temporary Immich Help Scripts","bright_purple")}")
    print(cg.color("Choose a scripted process:", "bold"))
    for i, each in PROCESSES.items():
        if each['active']:
            print(f"{i} {each['name']}")
        else:
            print(cg.strike(f"{i} {each['name']}"))
    print("\n0 - Exit")
    print(cg.color("Choose process by Number", "dull_white"))
    number = recursive_number_input(0, 1)
    if number == 0:
        exit(0)

    # and at this point it is not parametric anymore because the processes are all so different, anyway, for now
    # there is only one anyway

    print(f"Congratulations, your chosen process is {cg.color(PROCESSES[number]['name'], "bold")}")

    print("Checking if the provided API key got the correct permissions.")  # actually I would need to this after I choose a process
    needed_perm = ["asset.read", "tag.read", "tag.delete"]  # search for affected assets, find all tags, delete selected tags
    if missing := check_api_key_rights(creds, *needed_perm):
        if isinstance(missing, list):
            print(f"Permissions are missing: {", ".join(missing)}")
            print("Aborting, see ya next time")
            input("Press the ANY key to exit()")
    tag_delete_by_regex(creds)

