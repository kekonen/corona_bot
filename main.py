from bs4 import BeautifulSoup
import requests, re, time, slack, html2text
import os, dotenv
dotenv.load_dotenv()
import telegram
from telegram import ParseMode
from telegram.error import NetworkError, Unauthorized
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import hashlib
from googletrans import Translator
from lib.Users import UsersDB

translator = Translator()

def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

class SourceFetcher:
    def __init__(self, parse_function):
        self.parse_function = parse_function
        # self.history = [md5(item) for item in self.get_all_items()]
        self.history = self.get_all_items()

    def get_all_items(self):
        return self.parse_function()[::-1]
    
    def get_new_items(self):
        result = []
        for item in self.get_all_items():
            # md5_item = md5(item)
            # if md5_item not in self.history:
            #     self.history.append(md5_item)
            #     result.append(item)
            if item not in self.history:
                self.history.append(item)
                result.append(item)
        return result
    
    def get_history(self):
        return self.history
    
    def get_last(self):
        print(len(self.history))
        if len(self.history) > 0:
            return self.history[-1]


def parse_source_1():
    url = 'https://www.merkur.de/welt/coronavirus-deutschland-merkel-china-bayern-was-ist-symptome-infektion-news-muenchen-zr-13500123.html'
    # https://www.merkur.de/welt/coronavirus-gegenmittel-heilung-china-symptome-deutschland-krankheit-australien-homoeopathie-zr-13507549.html

    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    article_html = soup.find(id='id-js-DocumentDetail').prettify(formatter="html")
    md = html2text.html2text(article_html)

    md = md.split('\n\n')
    results = []
    ree = re.compile(r'\*\*.+[\d\.]+ Uhr:\*\* .+')
    for part in md:
        part = part.replace('\n', ' ')
        if ree.match(part):
            if part not in results:
                results.append(part)
    return results

source_1 = SourceFetcher(parse_source_1)

class CoronaBot:
    def __init__(self, token):
        self.updater = Updater(token, use_context=True)
        self.job_queue = self.updater.job_queue

        # self.users = []# 218135295
        self.users = UsersDB('./users.pkl')

        self.dp = self.updater.dispatcher

        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("stop", self.stop))
        self.dp.add_handler(CommandHandler("help", self.help))
        self.dp.add_handler(CommandHandler("u", self.get_update))
        self.dp.add_handler(CommandHandler("history", self.get_history))
        self.dp.add_handler(CommandHandler("latest", self.get_latest))

        self.dp.add_handler(MessageHandler(Filters.text, self.echo))

        self.dp.add_error_handler(self.error)

        self.jobs = []
        self.jobs.append(self.job_queue.run_repeating(self.send_updates2users, 60)) # , context=update


    def run(self):
        self.updater.start_polling()
        self.updater.idle()
        
    def send_updates2users(self, job_context):
        # print('LOLS', context.job.context)
        new_items = source_1.get_new_items()
        for new_item in new_items:
            translated_item = translator.translate(new_item, dest='en', src='de').text
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
        # logger.warning('Update "%s" caused error "%s"', update, context.error)
        print(f'Update "{update}" caused error "{context.error}"')

    def get_update(self, update, context):
        """Get update on the virus."""
        for item in source_1.get_new_items():
            translated_item = translator.translate(item, dest='en', src='de').text
            update.message.reply_text(translated_item)
        # update.message.reply_markdown(md)
        
    def get_latest(self, update, context):
        """Get latest update on the virus."""
        print('Something')
        item = source_1.get_last()
        print('Got item', ParseMode.MARKDOWN)
        if (item):
            translated_item = translator.translate(item, dest='en', src='de').text
            context.bot.send_message(update.message.chat.id, text=translated_item, parse_mode=ParseMode.MARKDOWN)
            # update.message.reply_text(translated_item)
        else:
            update.message.reply_text("Sorry, updates are temporary unavailable")
    
    def get_history(self, update, context):
        """Get history on the virus."""
        for item in source_1.get_history():
            update.message.reply_text(item)


CoronaBot(os.environ.get('TELEGRAM_TOKEN')).run()

# def get_last_update():
#     r = requests.get(url)
#     soup = BeautifulSoup(r.text, features="html.parser")
#     return list(filter(lambda x: re.match(r'\d{2}\.\d{2} Uhr\:', x.strip()), [x.replace('\xa0', '') for x in soup.findAll(text=True)]))[0]