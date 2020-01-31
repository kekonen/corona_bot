import os, dotenv
import telegram
from telegram import ParseMode
from telegram.error import NetworkError, Unauthorized
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from googletrans import Translator
from lib.Users import UsersDB
from collections import deque
from lib.Sources import SourceFetcher, parse_source_1, parse_source_2
dotenv.load_dotenv()

translator = Translator()

source_1 = SourceFetcher(parse_source_1)
source_2 = SourceFetcher(parse_source_2)

class CoronaBot:
    def __init__(self, token):
        self.updater = Updater(token, use_context=True)
        self.job_queue = self.updater.job_queue

        self.users = UsersDB('./users.pkl')

        self.last_news = deque(maxlen=5)

        self.dp = self.updater.dispatcher

        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("stop", self.stop))
        self.dp.add_handler(CommandHandler("help", self.help))
        self.dp.add_handler(CommandHandler("u", self.get_update))
        self.dp.add_handler(CommandHandler("latest", self.get_latest))

        self.dp.add_handler(MessageHandler(Filters.text, self.echo))

        self.dp.add_error_handler(self.error)
        
        self.jobs = []
        self.jobs.append(self.job_queue.run_repeating(self.send_updates2users, 60)) # , context=update

    def run(self):
        self.updater.start_polling()
        self.updater.idle()
        
    def send_updates2users(self, job_context):
        new_items = source_1.get_new_items() + source_2.get_new_items()
        for new_item in new_items:
            translated_item = translator.translate(new_item, dest='en', src='de').text
            self.last_news.append(translated_item)
            for chat_it in self.users.db:
                job_context.bot.send_message(chat_id=chat_it, text=translated_item, parse_mode=ParseMode.MARKDOWN)
        # job_context.bot.send_message(chat_id=job_context.job.context.message.chat.id, text='Alarm') WORKS!
        # job_context.job.context.message.reply_text('Alarm2')WORKS!

    def start(self, update, context):
        """Send a message when the command /start is issued."""
        chat_id = update.effective_chat.id
        if self.users.add(chat_id):
            update.message.reply_text('Hi!')
            context.bot.send_message(218135295, text=f'New user: {chat_id}, {update.message.chat}')
        else:
            update.message.reply_text('Hello again!')
    
    def stop(self, update, context):
        """Send a message when the command /start is issued."""
        chat_id = update.effective_chat.id
        if self.users.delete(chat_id):
            update.message.reply_text('May the God be with you!')
            context.bot.send_message(218135295, text=f'deleted user: {chat_id}')
        else:
            update.message.reply_text('Byyyyeeee!')

    def help(self, update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!')
        if update.effective_chat.id == 218135295:
            print(self.users.db)
            update.message.reply_text(str(self.users.db))

    def echo(self, update, context):
        """Echo the user message."""
        update.message.reply_text(update.message.text)

    def error(self, update, context):
        """Log Errors caused by Updates."""
        print(f'Update "{update}" caused error "{context.error}"')
        context.bot.send_message(218135295, text=f'error: {context.error}')

    def get_update(self, update, context):
        """Get update on the virus."""
        new_items = source_1.get_all_items() + source_2.get_all_items()
        for item in new_items:
            update.message.reply_text(item)
        
    def get_latest(self, update, context):
        """Get latest update on the virus."""
        for item in self.last_news:
            context.bot.send_message(update.message.chat.id, text=item, parse_mode=ParseMode.MARKDOWN)
    
CoronaBot(os.environ.get('TELEGRAM_TOKEN')).run()