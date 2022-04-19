"""
Discord Bot to display Stock, Commodity, Crypto etc prices.
Data taken from Yahoo Finance

By SiriusBrightstar
"""

import pytz
import discord
import logging
import yfinance as yf
from datetime import datetime
from discord.ext import tasks


logging.basicConfig(filename='bot.log',
                    format='%(asctime)s -> %(levelname)s: %(message)s\n-----', level=logging.INFO)

# YAHOO FINANCE DETAILS
TICKER = '^NSEI'
REFRESH_RATE = 60       # In Seconds


# DISCORD DETAILS
TOKEN = ''   # Bot Token
GUILD_ID = 456                                           # Server ID
BOT_ID = 123                                             # Bot ID
# [ROLE_ID, COLOR_ROLE_ID]
GREEN_ID = [123, 456]
# [ROLE_ID, COLOR_ROLE_ID]
RED_ID = [123, 456]


OPEN = datetime(2022, 3, 23, 9, 00, 00)
CLOSE = datetime(2022, 3, 23, 16, 00, 00)


def Holiday():
    timeZ_Ny = datetime.now(pytz.timezone('Asia/Kolkata'))
    TODAY = timeZ_Ny.strftime('%d %b')

    Holiday_List = {
    "Date": [
        "26 Jan",
        "01 Mar",
        "10 Apr",
        "14 Apr",
        "15 Apr",
        "3 May",
        "10 Jul",
        "09 Aug",
        "31 Aug",
        "02 Oct",
        "05 Oct",
        "24 Oct",
        "24 Oct",
        "08 Nov",
        "25 Dec",
    ],
    "Holiday": [
        "Republic Day",
        "Maha Shivaratri",
        "Ram Navami",
        "Ambedkar Jayanti",
        "Good Friday",
        "Eid Al Fitr",
        "Bakri Id / Eid Ul-Adha",
        "Muharram",
        "Ganesh Chaturthi",
        "Mathatma Gandhi Jayanti",
        "Dussehra",
        "Diwali",
        "Diwali",
        "Guru Nanak's Birthday",
        "Christmas",
    ],
}

    return TODAY in Holiday_List['Date']


def isMarketopen():
    NYC_NOW = datetime.now(pytz.timezone('America/New_York'))
    isWeekday = NYC_NOW.weekday() in [0, 1, 2, 3, 4]
    return (Holiday() == False) and (OPEN.time() < NYC_NOW.time() < CLOSE.time() and (isWeekday))


client = discord.Client()


def price():
    Title = 'Nifty50'
    DATA = yf.Ticker(TICKER)
    DF = DATA.get_info()
    previousClose = DF['previousClose']
    close = DF['regularMarketPrice']
    Change = close - previousClose
    pChange = (Change/previousClose) * 100
    if pChange >= 0:
        retString = [f'{Title}: ₹{close:.4f}',
                     f'{Change:.4f}({pChange:.2f}%)', GREEN_ID]
    else:
        retString = [f'{Title}: ₹{close:.4f}',
                     f'{Change:.4f}({pChange:.2f}%)', RED_ID]
    logging.info(retString, exc_info=True)
    return retString


@tasks.loop(seconds=REFRESH_RATE)
async def updateData():
    try:
        guild = client.get_guild(GUILD_ID)
        bot_account = guild.get_member(BOT_ID)
        ltp = price()
        botRoles = [discord.Object(ltp[2][0]), discord.Object(ltp[2][1])]
        if (isMarketopen() == True):
            await bot_account.edit(nick=ltp[0], roles=botRoles)
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=ltp[1]), status=discord.Status.online)
            logging.info('MARKET is Open', exc_info=True)
        else:
            await bot_account.edit(nick=ltp[0], roles=botRoles)
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=ltp[1]), status=discord.Status.idle)
            logging.info('MARKET is Closed', exc_info=True)

    except RuntimeError:
        logging.error(
            'Failed to run updateData(): Runtime Error', exc_info=True)
    else:
        logging.info('Some other issue', exc_info=True)


@client.event
async def on_ready():
    logging.info('Logging in as {0.user}'.format(client))
    if not updateData.is_running():
        updateData.start()


client.run(TOKEN)
