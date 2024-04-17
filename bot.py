#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards. For an in-depth explanation, check out
 https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example.
"""
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, CallbackContext
import requests

  

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
    """Sends a message with three inline buttons attached."""

    # Extract the user's first name. You can also use user.full_name or user.username
    user = update.effective_user
    # username = user.first_name if user.first_name else user.username or "there"
    username = user.username if user.username else user.first_name  or "there"


    ref_id = context.args[0] if context.args else None
    if ref_id:
        referrer_url = f'https://toyback.onrender.com/telegram/all/{ref_id}/'
        referrer_response = requests.get(referrer_url)
        referrer_data = referrer_response.json()
        referrer = referrer_data["id"]
        previous_data = requests.get(f'https://toyback.onrender.com/toycoin/{ref_id}')
        json_data = previous_data.json()
        print(json_data)
        if previous_data:
            response = requests.patch(f'https://toyback.onrender.com/toycoin/{ref_id}', json={"quantity_mined":float(json_data["quantity_mined"]) + 666.00})
            print(response)
    else:
        referrer = None

    




    # Create or update the user in the database

    data={
        'first_name': user.first_name,
        'username': user.username,
        'last_name': user.last_name,
        'full_name': user.full_name,
        'telegram_id': user.id,
        'language_code': user.language_code,  
        'referrer':referrer
    }
    
    get_url = f'https://toyback.onrender.com/telegram/all/{user.id}/'
    
    url = f'https://toyback.onrender.com/telegram/all/'
    

    # Send a greeting message with the user's name and a description
    greeting_message = f"Hello, {username}! 👋 Welcome to our bot!"
    welcome_back_message = f"Welcome Back, {username}! 👋👋 "
    description = "Here's what you can do here:"
    welcome_back_description = "Continue to claim now."
    # await context.bot.send_message(chat_id=update.effective_chat.id, 
    #                                text=f"{greeting_message}\n\n{description}",
    #                                parse_mode=ParseMode.MARKDOWN)
    front_url = f'https://toycoin.netlify.app/home/{user.id}'

    front_response = requests.get(front_url)
    # print(f"front_response: {front_response}") 

    keyboard = [
        # [
        #     InlineKeyboardButton("Option 1", callback_data="1"),
        #     InlineKeyboardButton("Option 2", callback_data="2"),
        # ],
        [
            # Replace 'https://your_mini_app_url.com' with the actual URL of your Mini App
            InlineKeyboardButton("MINE TOY", web_app=WebAppInfo(url=f"https://toycoin.netlify.app/home/{user.id}")),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the inline keyboard in a new message
    # await update.message.reply_text("Please choose:", reply_markup=reply_markup)
    

    try:
        response = requests.get(get_url, json=data)
        if response.status_code == 200:
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                               text=f"{welcome_back_message}\n\n{welcome_back_description}")
            
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text="Continue by clicking on MINE TOY", 
                                   reply_markup=reply_markup)
        elif response.status_code == 404: 
            new_response = requests.post(url, json=data)
            if new_response.status_code == 201:
                await context.bot.send_message(chat_id=update.effective_chat.id, 
                               text=f"{greeting_message}\n\n{description}")
                
                await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text="Please choose an option:", 
                                   reply_markup=reply_markup)
            # await context.bot.send_message(chat_id=update.effective_chat.id, text="Pls Click start again")
    except requests.exceptions.RequestException as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred has occured, pls reload the bot")
        # print(e)



async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")


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

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    print("working")


if __name__ == "__main__":
    main()

