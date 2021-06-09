# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
"""
   Heroku manager for your userbot
"""

import math

import aiohttp
import heroku3

from SaitamaRobot import HEROKU_API_KEY, HEROKU_APP_NAME
from SaitamaRobot.events import dispatcher
from SaitamaRobot.modules.disable import DisableAbleCommandHandler
from telegram import Update
from telegram.ext import CallbackContext, run_async

heroku_api = "https://api.heroku.com"
if HEROKU_APP_NAME is not None and HEROKU_API_KEY is not None:
    Heroku = heroku3.from_key(HEROKU_API_KEY)
    app = Heroku.app(HEROKU_APP_NAME)
    heroku_var = app.config()
else:
    app = None


"""
    Check account quota, remaining quota, used quota, used app quota
"""


@run_async
def usage(update: Update, context: CallbackContext):
    """Get your account Dyno Usage."""
    if app is None:
        return await dyno.edit(
            "`[HEROKU]\nPlease setup your`  "
            "**HEROKU_APP_NAME** and ***HEROKU_API_KEY**."
        )
    await dyno.edit("`Getting Information...`")
    useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/81.0.4044.117 Mobile Safari/537.36"
    )
    user_id = Heroku.account().id
    headers = {
        "User-Agent": useragent,
        "Authorization": f"Bearer {HEROKU_API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    path = "/accounts/" + user_id + "/actions/get-quota"
    async with aiohttp.ClientSession() as session:
        async with session.get(heroku_api + path, headers=headers) as r:
            if r.status != 200:
                await dyno.client.send_message(
                    dyno.chat_id, f"`{r.reason}`", reply_to=dyno.id
                )
                await dyno.edit("`Can't get information...`")
                return False
            result = await r.json()
            quota = result["account_quota"]
            quota_used = result["quota_used"]

            """ - User Quota Limit and Used - """
            remaining_quota = quota - quota_used
            percentage = math.floor(remaining_quota / quota * 100)
            minutes_remaining = remaining_quota / 60
            hours = math.floor(minutes_remaining / 60)
            minutes = math.floor(minutes_remaining % 60)
            day = math.floor(hours / 24)

            """ - User App Used Quota - """
            Apps = result["apps"]
            for apps in Apps:
                if apps.get("app_uuid") == app.id:
                    AppQuotaUsed = apps.get("quota_used") / 60
                    AppPercentage = math.floor(apps.get("quota_used") * 100 / quota)
                    break
            else:
                AppQuotaUsed = 0
                AppPercentage = 0

            AppHours = math.floor(AppQuotaUsed / 60)
            AppMinutes = math.floor(AppQuotaUsed % 60)

            await dyno.edit(
                "**Dyno Usage**:\n\n"
                f"-> `Dyno usage for`  **{app.name}**:\n"
                f"     •  **{AppHours} hour(s), "
                f"{AppMinutes} minute(s)  -  {AppPercentage}%**"
                "\n\n"
                "-> `Dyno hours quota remaining this month`:\n"
                f"     •  **{hours} hour(s), {minutes} minute(s)  "
                f"-  {percentage}%**\n\n"
                f" `Estimated Heroku Expired`:  **{day}** day(s)"
            )
            return True

WEEBIFY_HANDLER = DisableAbleCommandHandler("usage", usage)

dispatcher.add_handler(USAGE_HANDLER)

__help__ = """
/usage
"""

__mod_name__ = "USAGE"
__command_list__ = [
    "alive"
]
__handlers__ = [
    USAGE_HANDLER
]

