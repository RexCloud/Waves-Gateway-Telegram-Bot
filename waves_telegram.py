import waves_bot
import waves_database
import waves_payments
import re
from waves_config import BOT_TOKEN
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext import filters
from telegram.constants import ParseMode
from time import time
from random import randint
from threading import Thread

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    username = update.effective_chat.username
    if username != "your_telegram_username":
        print("[INFO] New user:", username)

    text = "<b>GM! This is a private bot.</b>\n\n<b>Current features:</b>\n- Monitor USDC/USDT/BUSD balances of gateway\n- Check for withdrawal availability of these stablecoins\n- Notify when arbitrage opportunity occurs and withdrawal is available\n\n<b>Commands:</b>\n- Help — Displays this message\n- Configure notifications — Set notifications mode\n- Info — Show latest info"
    
    keyboard = [
        ["Info", "Configure notifications"],
        ["Account", "Help"]
    ]

    markup = ReplyKeyboardMarkup(keyboard, True)

    await context.bot.send_message(update.effective_chat.id, text, ParseMode.HTML, reply_markup=markup)

async def account(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = await waves_database.get_user(update.effective_chat.username)

    keyboard = [
            [InlineKeyboardButton("Buy subscription — $10 (1 month)", callback_data="Buy")]
    ]

    markup = InlineKeyboardMarkup(keyboard)
    
    text = f"<b>Account:</b>\n{update.effective_user.full_name} (@{update.effective_chat.username})\n\n<b>Subscriptions:</b>\n"

    if not user:
        text = text + "No active subscription"
        await context.bot.send_message(update.effective_chat.id, text, ParseMode.HTML, reply_markup=markup)
        return
    
    expiration = user[1]
    current_time = int(time())
    if expiration > current_time:
        days_count = round((expiration-current_time)/60/60/24)
        text = text + f"{days_count} day left" if days_count == 1 else text + f"{days_count} days left"
        if days_count <= 2:
            await context.bot.send_message(update.effective_chat.id, text, ParseMode.HTML, reply_markup=markup)
            return
        await context.bot.send_message(update.effective_chat.id, text, ParseMode.HTML)
        return
    if expiration == 0:
        text = text + "Lifetime subscription"
        await context.bot.send_message(update.effective_chat.id, text, ParseMode.HTML)
        return

    text = text + "No active subscription"
    await context.bot.send_message(update.effective_chat.id, text, ParseMode.HTML, reply_markup=markup)

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = await waves_database.get_user(update.effective_chat.username)
    
    if not user:
        keyboard = [
            [InlineKeyboardButton("Get free trial (1 day)", callback_data="Trial")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(update.effective_chat.id, "You're not allowed to use this command", reply_markup=markup)
        return False

    expiration = user[1]
    if expiration > int(time()):
        return True
    if expiration == 0:
        return True
    
    await context.bot.send_message(update.effective_chat.id, "Your subscription/trial has expired")
    return False

async def give_trial(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if await waves_database.get_user(update.effective_chat.username):
        await update.callback_query.answer("You have already used trial or have active subscription")
        return

    await waves_database.add_user(update.effective_chat.username)
    await waves_database.set_user_expiration(update.effective_chat.username, int(time())+86400)
    
    await update.callback_query.answer("Your trial period has started!")

async def process_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tx_hash = update.effective_message.text

    random_num = context.user_data.get("random_num")
    if not random_num:
        return

    amount = float("10."+str(random_num))

    if not waves_payments.check_tx(tx_hash, amount):
        await context.bot.send_message(update.effective_chat.id, "Failed to process this transaction:\nTransaction doesn't exist or tx hash is invalid")
        return

    current_time = int(time())
    user = await waves_database.get_user(update.effective_chat.username)
    if user:
        expiration = user[1]
        if expiration == 0 or expiration < current_time:
            context.user_data.clear()
            await waves_database.set_user_expiration(update.effective_chat.username, current_time+60*60*24*30)
            await context.bot.send_message(update.effective_chat.id, "Your 30 day subscription period has started!")
            return
        offset = expiration - current_time
        context.user_data.clear()
        await waves_database.set_user_expiration(update.effective_chat.username, current_time+offset+60*60*24*30)
        await context.bot.send_message(update.effective_chat.id, "Added 30 days to your current subscription!")
        return
    context.user_data.clear()
    await waves_database.add_user(update.effective_chat.username)
    await waves_database.set_user_expiration(update.effective_chat.username, current_time+60*60*24*30)
    await context.bot.send_message(update.effective_chat.id, "Your 30 day subscription period has started!")
    return

async def buy_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):

    random_num = context.user_data.get("random_num")
    
    if not random_num:
        random_num = randint(100000, 999999)
        context.user_data.update({"random_num": random_num})

    text = f"Send <b>exactly</b> 10.{random_num} USDT/BUSD/USDC to {waves_payments.RECEIVER_ADDRESS}\n\nAccepted chains:\nEthereum, BSC, Polygon\n\nEnter the tx hash:"

    await update.callback_query.answer("")
    await context.bot.send_message(update.effective_chat.id, text, ParseMode.HTML)

async def configure(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_subscription(update, context):
        return

    keyboard = [
        [InlineKeyboardButton("Standard", callback_data="Standard"), InlineKeyboardButton("Silent", callback_data="Silent")],
        [InlineKeyboardButton("Disable", callback_data="Disable")]
    ]

    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(update.effective_chat.id, "Choose notification mode:", reply_markup=markup)

async def bot_runner(context: ContextTypes.DEFAULT_TYPE):
    
    if not waves_bot.msg:
        return

    mode = context.job.data[0]
    expiration = context.job.data[1]
    if int(time()) > expiration and expiration != 0:
        jobs = context.job_queue.jobs()
        for job in jobs:
            if job.chat_id == context.job.chat_id:
                job.schedule_removal()

    if mode == 1:
        await context.bot.send_message(context.job.chat_id, f"```\n{waves_bot.msg}```", ParseMode.MARKDOWN_V2)
    if mode == 2 and "arb" in waves_bot.msg:
        await context.bot.send_message(context.job.chat_id, f"```\n{waves_bot.msg}```", ParseMode.MARKDOWN_V2)

async def bot_standard(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_subscription(update, context):
        return
    
    jobs = context.job_queue.jobs()

    for job in jobs:
        if job.chat_id == update.effective_chat.id:
            job.schedule_removal()
    
    await update.callback_query.answer("Started sending notifications every 30 seconds")

    await waves_database.set_mode(update.effective_chat.username, update.effective_chat.id, 1)
    expiration = (await waves_database.get_user(update.effective_chat.username))[1]
    context.job_queue.run_repeating(bot_runner, 30, chat_id=update.effective_chat.id, data=(1, expiration))

async def bot_silent(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_subscription(update, context):
        return

    jobs = context.job_queue.jobs()

    for job in jobs:
        if job.chat_id == update.effective_chat.id:
            job.schedule_removal()
    
    await update.callback_query.answer("Started sending notifications for arbitrage opportunities")
    
    await waves_database.set_mode(update.effective_chat.username, update.effective_chat.id, 2)
    expiration = (await waves_database.get_user(update.effective_chat.username))[1]
    context.job_queue.run_repeating(bot_runner, 30, chat_id=update.effective_chat.id, data=(2, expiration))

async def bot_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):

    jobs = context.job_queue.jobs()

    if not jobs:
        await update.callback_query.answer("Notifications are already disabled")
        return
    
    for job in jobs:
        if job.chat_id == update.effective_chat.id:
            job.schedule_removal()
            await waves_database.set_mode(update.effective_chat.username, update.effective_chat.id, 0)
            await update.callback_query.answer("Notifications disabled")
        else:
            await update.callback_query.answer("Notifications are already disabled")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_subscription(update, context):
        return
    
    if not waves_bot.msg:
        return

    await context.bot.send_message(update.effective_chat.id, f"```\n{waves_bot.msg}```", ParseMode.MARKDOWN_V2)

class AdminCommands:

    async def try_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):

        if update.effective_chat.username != "rexcloud":
            await context.bot.send_message(update.effective_chat.id, "You're not allowed to use this command")
            return
        
        if waves_bot.try_withdraw_running:
            await context.bot.send_message(update.effective_chat.id, "Already running. Use /stop_try_withdraw first")
            return

        if len(context.args) != 2:
            await context.bot.send_message(update.effective_chat.id, "Invalid command params:\n/try_withdraw TOKEN AMOUNT\nExample:\n/try_withdraw USDT 5000")
            return
        
        token = context.args[0].upper()
        if token not in ("USDT", "USDC", "BUSD"):
            await context.bot.send_message(update.effective_chat.id, "Invalid token (USDT, USDC, BUSD)")
            return

        amount = context.args[1]
        try:
            if "." in amount:
                amount = float(amount)
            elif "," in amount:
                await context.bot.send_message(update.effective_chat.id, "Invalid amount format (1000 or 1000.77)")
                return
            else:
                amount = int(amount)
        except ValueError:
            await context.bot.send_message(update.effective_chat.id, "Invalid amount format (1000 or 1000.77)")
            return
        
        waves_bot.try_withdraw_running = True
        Thread(target=waves_bot.try_withdraw_loop, args=(token, amount), daemon=True).start()

        await context.bot.send_message(update.effective_chat.id, f"Started trying to withdraw {amount} {token}")

    async def stop_try_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):

        if update.effective_chat.username != "rexcloud":
            await context.bot.send_message(update.effective_chat.id, "You're not allowed to use this command")
            return
        
        if waves_bot.try_withdraw_running:
            waves_bot.try_withdraw_running = False
            await context.bot.send_message(update.effective_chat.id, "Stopped trying to withdraw")

        else:
            await context.bot.send_message(update.effective_chat.id, "Use /try_withdraw TOKEN AMOUNT first")

    async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        if update.effective_chat.username != "rexcloud":
            await context.bot.send_message(update.effective_chat.id, "You're not allowed to use this command")
            return
        
        if len(context.args) != 1:
            await context.bot.send_message(update.effective_chat.id, "Invalid command params:\n/add_user @username")
            return

        username = context.args[0].replace("@", "")
        
        await waves_database.add_user(username)
        await context.bot.send_message(update.effective_chat.id, f"Added {username}")

    async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        if update.effective_chat.username != "rexcloud":
            await context.bot.send_message(update.effective_chat.id, "You're not allowed to use this command")
            return
        
        if len(context.args) != 1:
            await context.bot.send_message(update.effective_chat.id, "Invalid command params:\n/remove_user @username")
            return

        username = context.args[0].replace("@", "")

        jobs = context.job_queue.jobs()
        if jobs:
            for job in jobs:
                if job.chat_id == update.effective_chat.id:
                    job.schedule_removal()
        
        await waves_database.remove_user(username)
        await context.bot.send_message(update.effective_chat.id, f"Removed {username}")

    async def get_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        if update.effective_chat.username != "rexcloud":
            await context.bot.send_message(update.effective_chat.id, "You're not allowed to use this command")
            return

        text = "Username, mode, period:\n\n"

        users = await waves_database.get_all_users()
        for user in users:
            text = text + user[0] + ", " + str(user[1]) + ", " + str(user[2]) + "\n"

        await context.bot.send_message(update.effective_chat.id, text)

if __name__ == "__main__":

#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    Thread(target=waves_bot.run_parser, daemon=True).start()

    bot = ApplicationBuilder().token(BOT_TOKEN).build()
    
    bot.add_handler(CommandHandler(("start", "help"), start))
    bot.add_handler(MessageHandler(filters.Regex(re.compile("^(start|help)$", re.IGNORECASE)), start))
    bot.add_handler(MessageHandler(filters.Regex(re.compile("^Info$", re.IGNORECASE)), info))
    bot.add_handler(MessageHandler(filters.Regex(re.compile("^Configure notifications$", re.IGNORECASE)), configure))
    bot.add_handler(MessageHandler(filters.Regex(re.compile("^Account$", re.IGNORECASE)), account))
    bot.add_handler(MessageHandler(filters.Regex(re.compile("^0x", re.IGNORECASE)), process_subscription))
    bot.add_handler(CallbackQueryHandler(buy_subscription, "Buy"))
    bot.add_handler(CallbackQueryHandler(give_trial, "Trial"))
    bot.add_handler(CallbackQueryHandler(bot_standard, "Standard"))
    bot.add_handler(CallbackQueryHandler(bot_silent, "Silent"))
    bot.add_handler(CallbackQueryHandler(bot_stop, "Disable"))
    bot.add_handler(CommandHandler("try_withdraw", AdminCommands.try_withdraw))
    bot.add_handler(CommandHandler("stop_try_withdraw", AdminCommands.stop_try_withdraw))
    bot.add_handler(CommandHandler("add_user", AdminCommands.add_user))
    bot.add_handler(CommandHandler("remove_user", AdminCommands.remove_user))
    bot.add_handler(CommandHandler("get_users", AdminCommands.get_users))
    
    while True:
        try:
            active_jobs = waves_database._get_active_modes()
            for job in active_jobs:
                bot.job_queue.run_repeating(bot_runner, 30, chat_id=job[0], data=(job[1], job[2]))
            bot.run_polling(drop_pending_updates=True)
        except:
            continue
