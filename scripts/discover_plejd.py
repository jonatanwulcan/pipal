#!/usr/bin/env python3
"""List Plejd sites and devices for the configured account."""
import asyncio
import json

from pyplejd import PlejdManager

CREDENTIALS_FILE = "plejd_credentials.json"


async def main():
    with open(CREDENTIALS_FILE) as f:
        creds = json.load(f)

    username = creds["username"]
    password = creds["password"]

    sites = await PlejdManager.get_sites(username, password)
    if not sites:
        print("No sites found.")
        return

    for site in sites:
        print(f"\nSite: {site['title']}  (id: {site['siteId']})")
        manager = PlejdManager(credentials={"username": username, "password": password}, sitedata={"siteId": site["siteId"]})
        await manager.init()
        for addr, device in manager.devices.items():
            print(f"  [{addr}] {device.name}  (dimmable: {device.dimmable})")


asyncio.run(main())
