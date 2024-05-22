#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards. For an in-depth explanation, check out
 https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example.
"""
import logging
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, CallbackContext, MessageHandler, filters
import requests
import aiohttp

  

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)



def generate_referral_link(bot_username, user_id):
    return f"https://t.me/{bot_username}?start={user_id}"


async def share_referral(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    referral_link = generate_referral_link('Toycoin_bot', user_id)
    await update.message.reply_text(f"Share this link with your friends: {referral_link}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    username = user.username if user.username else user.first_name or "there"

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ref_id = context.args[0] if context.args else None
    referrer = None

    if ref_id:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://toyback.onrender.com/telegram/all/{ref_id}/') as response:
                    referrer_data = await response.json()
                    referrer = referrer_data["id"]

                async with session.get(f'https://toyback.onrender.com/toycoin/{ref_id}') as response:
                    json_data = await response.json()
                    refdata = {
                        'id': json_data['id'],
                        'name': json_data['name'],
                        'quantity_mined': float(json_data['quantity_mined']) + 1000.00,
                        'time_clicked': json_data['time_clicked'],
                        'first_click': json_data['first_click'],
                        'date_joined': json_data['date_joined'],
                        'mineral_extracted': json_data['mineral_extracted'],
                        'launch_date': json_data['launch_date'],
                        'user': json_data['user']
                    }

                async with session.patch(f'https://toyback.onrender.com/toycoin/{ref_id}/', json=refdata) as response:
                    response.raise_for_status()

        except aiohttp.ClientResponseError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except aiohttp.ClientError as req_err:
            print(f'Request exception: {req_err}')
        except ValueError as json_err:
            print(f'JSON error: {json_err}')


    data = {
        'first_name': user.first_name,
        'username': user.username,
        'last_name': user.last_name,
        'full_name': user.full_name,
        'telegram_id': user.id,
        'language_code': user.language_code,
        'referrer': referrer,
        'last_active': current_time  # Adding last active time to the data
    }

    get_url = f'https://toyback.onrender.com/telegram/all/{user.id}/'
    url = f'https://toyback.onrender.com/telegram/all/'

    greeting_message = f"Hello, {username}! 👋 Welcome to our bot!"
    welcome_back_message = f"Welcome Back, {username}! 👋👋 "
    description = "Here's what you can do here:"
    welcome_back_description = "Continue to claim now."
    front_url = f'https://toycoin.netlify.app/home/{user.id}'

    keyboard = [
        [
            InlineKeyboardButton("MINE TOY", web_app=WebAppInfo(url=f"https://toycoin.netlify.app/home/{user.id}")),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(get_url) as response:
                if response.status == 200:
                    await context.bot.send_message(chat_id=update.effective_chat.id,
                                                   text=f"{welcome_back_message}\n\n{welcome_back_description}")

                    await context.bot.send_message(chat_id=update.effective_chat.id,
                                                   text="Continue by clicking on MINE TOY",
                                                   reply_markup=reply_markup)
                elif response.status == 404:
                    async with session.post(url, json=data) as new_response:
                        if new_response.status == 201:
                            new_user_data = await new_response.json()
                            print(f'New user data: {new_user_data}')

                            await context.bot.send_message(chat_id=update.effective_chat.id,
                                                           text=f"{greeting_message}\n\n{description}")

                            await context.bot.send_message(chat_id=update.effective_chat.id,
                                                           text="Please choose an option:",
                                                           reply_markup=reply_markup)
    except aiohttp.ClientError as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred, please reload the bot")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    print("help just now")
    await update.message.reply_text("Use /start to test this bot.")


async def welcome_new_member(update: Update, context: CallbackContext) -> None:
    """Sends a welcome message to new members of a group."""
    print("Chat ID: -1002124838209")
    print("Welcome New member just joined")
    logger.info("Welcome New member just joined")
    user = update.effective_user
    user_id = user.id

    print(f"Welcome user: {user}")
    chat_id = update.message.chat_id
    chat_title = update.message.chat.title
    print(f"Chat ID: {chat_id}, Chat Title: {chat_title}")
 
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://toyback.onrender.com/telegram/all/{user_id}/') as response:
                if response.status == 200:
                    print(f'User {user_id} exist in Toy Database')
                    user_data = {
                        'telegram_id': user_id,
                    }
                    async with session.patch(f'https://toyback.onrender.com/task/all/{chat_id}/', json=user_data) as j_response:
                        a=j_response.json()
                        print(f'joined successfully {a}')


    except aiohttp.ClientResponseError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except aiohttp.ClientError as req_err:
        print(f'Request exception: {req_err}')
    except ValueError as json_err:
        print(f'JSON error: {json_err}')



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    chat_title = update.message.chat.title
    print(f"Echo Chat ID: {chat_id}, Chat Title: {chat_title}")
    # await update.message.reply_text(f"Echo Chat ID: {chat_id}")



def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.

    TOKEN = '7158898737:AAGLq9zyV15zJcA7Wzlvp5M2u4YykUQKVs8'
    print("Running Main")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("referral", share_referral))

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))



    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES, timeout=30)  # Timeout set to 30 seconds
    print("working")


if __name__ == "__main__":
    main()

