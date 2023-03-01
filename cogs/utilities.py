import discord
from discord.ext import commands, tasks

#from discord.commands import slash_command, message_command
# ignore that

from discord import app_commands

from PIL import Image
import pytesseract
import io

import platform
import textblob

import functions


import datetime


import snscrape.modules.twitter as sntwitter


win = (platform.system() == "Windows")
if win:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" # this doesn't actually exist lol

def error(errormsg):
    embed = functions.error("Utilities", errormsg)
    return embed

def botembed(title):
    embed = functions.embed("Utilities - " + title, color=0xffa500)
    return embed

def valid_time(string):
    try:
        datetime.datetime.strptime(string, '%H:%M:%S')
    except:
        try:
            datetime.datetime.strptime(string, '%H:%M')
        except:
            return False
    return True

def valid_date(string):
    try:
        datetime.datetime.strptime(string, '%m/%d/%Y')
    except:
        try:
            datetime.datetime.strptime(string, '%m/%d')
        except Exception as e:
            return False
    return True

def valid_datetime(string):

    duration = [c for c in string]

    now = datetime.timedelta(0)
    intervals = []

    alphabet = "abcdefghijklmnopqrstuvwxyz"
    stop = 0
    for i in range(len(duration)):
        if duration[i] in alphabet:
            interval = duration[stop:i + 1]
            interval = "".join(interval)
            intervals.append(interval)
            stop = i + 1

    for i in intervals:
        try:
            num = int(i[:-1])
        except:
            return datetime.timedelta(0)
        if i.endswith('s'):
            now += datetime.timedelta(seconds=num)
        elif i.endswith('m'):
            now += datetime.timedelta(minutes=num)
        elif i.endswith('h'):
            now += datetime.timedelta(hours=num)
        elif i.endswith('d'):
            now += datetime.timedelta(days=num)
        else:
            continue
    return now

languages = {'aa': 'Afar', 'ab': 'Abkhazian', 'ae': 'Avestan', 'af': 'Afrikaans', 'ak': 'Akan', 'am': 'Amharic', 'an': 'Aragonese', 'ar': 'Arabic', 'as': 'Assamese', 'av': 'Avaric', 'ay': 'Aymara', 'az': 'Azerbaijani', 'ba': 'Bashkir', 'be': 'Belarusian', 'bg': 'Bulgarian', 'bh': 'Bihari languages', 'bi': 'Bislama', 'bm': 'Bambara', 'bn': 'Bengali', 'bo': 'Tibetan', 'br': 'Breton', 'bs': 'Bosnian', 'ca': 'Catalan; Valencian', 'ce': 'Chechen', 'ch': 'Chamorro', 'co': 'Corsican', 'cr': 'Cree', 'cs': 'Czech', 'cu': 'Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic', 'cv': 'Chuvash', 'cy': 'Welsh', 'da': 'Danish', 'de': 'German', 'dv': 'Divehi; Dhivehi; Maldivian', 'dz': 'Dzongkha', 'ee': 'Ewe', 'el': 'Greek, Modern (1453-)', 'en': 'English', 'eo': 'Esperanto', 'es': 'Spanish', 'et': 'Estonian', 'eu': 'Basque', 'fa': 'Persian', 'ff': 'Fulah', 'fi': 'Finnish', 'fj': 'Fijian', 'fo': 'Faroese', 'fr': 'French', 'fy': 'Western Frisian', 'ga': 'Irish', 'gd': 'Gaelic; Scottish Gaelic', 'gl': 'Galician', 'gn': 'Guarani', 'gu': 'Gujarati', 'gv': 'Manx', 'ha': 'Hausa', 'he': 'Hebrew', 'hi': 'Hindi', 'ho': 'Hiri Motu', 'hr': 'Croatian', 'ht': 'Haitian; Haitian Creole', 'hu': 'Hungarian', 'hy': 'Armenian', 'hz': 'Herero', 'ia': 'Interlingua (International Auxiliary Language Association)', 'id': 'Indonesian', 'ie': 'Interlingue; Occidental', 'ig': 'Igbo', 'ii': 'Sichuan Yi; Nuosu', 'ik': 'Inupiaq', 'io': 'Ido', 'is': 'Icelandic', 'it': 'Italian', 'iu': 'Inuktitut', 'ja': 'Japanese', 'jv': 'Javanese', 'ka': 'Georgian', 'kg': 'Kongo', 'ki': 'Kikuyu; Gikuyu', 'kj': 'Kuanyama; Kwanyama', 'kk': 'Kazakh', 'kl': 'Kalaallisut; Greenlandic', 'km': 'Central Khmer', 'kn': 'Kannada', 'ko': 'Korean', 'kr': 'Kanuri', 'ks': 'Kashmiri', 'ku': 'Kurdish', 'kv': 'Komi', 'kw': 'Cornish', 'ky': 'Kirghiz; Kyrgyz', 'la': 'Latin', 'lb': 'Luxembourgish; Letzeburgesch', 'lg': 'Ganda', 'li': 'Limburgan; Limburger; Limburgish', 'ln': 'Lingala', 'lo': 'Lao', 'lt': 'Lithuanian', 'lu': 'Luba-Katanga', 'lv': 'Latvian', 'mg': 'Malagasy', 'mh': 'Marshallese', 'mi': 'Maori', 'mk': 'Macedonian', 'ml': 'Malayalam', 'mn': 'Mongolian', 'mr': 'Marathi', 'ms': 'Malay', 'mt': 'Maltese', 'my': 'Burmese', 'na': 'Nauru', 'nb': 'Bokmål, Norwegian; Norwegian Bokmål', 'nd': 'Ndebele, North; North Ndebele', 'ne': 'Nepali', 'ng': 'Ndonga', 'nl': 'Dutch; Flemish', 'nn': 'Norwegian Nynorsk; Nynorsk, Norwegian', 'no': 'Norwegian', 'nr': 'Ndebele, South; South Ndebele', 'nv': 'Navajo; Navaho', 'ny': 'Chichewa; Chewa; Nyanja', 'oc': 'Occitan (post 1500)', 'oj': 'Ojibwa', 'om': 'Oromo', 'or': 'Oriya', 'os': 'Ossetian; Ossetic', 'pa': 'Panjabi; Punjabi', 'pi': 'Pali', 'pl': 'Polish', 'ps': 'Pushto; Pashto', 'pt': 'Portuguese', 'qu': 'Quechua', 'rm': 'Romansh', 'rn': 'Rundi', 'ro': 'Romanian; Moldavian; Moldovan', 'ru': 'Russian', 'rw': 'Kinyarwanda', 'sa': 'Sanskrit', 'sc': 'Sardinian', 'sd': 'Sindhi', 'se': 'Northern Sami', 'sg': 'Sango', 'si': 'Sinhala; Sinhalese', 'sk': 'Slovak', 'sl': 'Slovenian', 'sm': 'Samoan', 'sn': 'Shona', 'so': 'Somali', 'sq': 'Albanian', 'sr': 'Serbian', 'ss': 'Swati', 'st': 'Sotho, Southern', 'su': 'Sundanese', 'sv': 'Swedish', 'sw': 'Swahili', 'ta': 'Tamil', 'te': 'Telugu', 'tg': 'Tajik', 'th': 'Thai', 'ti': 'Tigrinya', 'tk': 'Turkmen', 'tl': 'Tagalog', 'tn': 'Tswana', 'to': 'Tonga (Tonga Islands)', 'tr': 'Turkish', 'ts': 'Tsonga', 'tt': 'Tatar', 'tw': 'Twi', 'ty': 'Tahitian', 'ug': 'Uighur; Uyghur', 'uk': 'Ukrainian', 'ur': 'Urdu', 'uz': 'Uzbek', 've': 'Venda', 'vi': 'Vietnamese', 'vo': 'Volapük', 'wa': 'Walloon', 'wo': 'Wolof', 'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba', 'za': 'Zhuang; Chuang', 'zh': 'Chinese', 'zu': 'Zulu'}

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.image_files = ["jpg", "png", "bmp"]
        self.first_time = False
        

    @app_commands.context_menu(name="Translate")
    async def translate_ctx(inter: discord.Interaction, message: discord.Message):
        m = message
        if not m.content:
            embed = functions.error("OCR", "🚫 " + functions.response(2) + " it looks like this message is empty.")
            return await inter.response.send_message(embed=embed)
        content = m.content
        blob = textblob.TextBlob(content)
        lang = blob.detect_language()
        try:
            translated = blob.translate()
        except textblob.exceptions.NotTranslated:
            embed = functions.error("OCR", "🚫 " + functions.response(2) + " it looks like this message cannot be translated.")
            return await inter.response.send_message(embed=embed)
        return await inter.response.send_message(f"{languages[lang]} -> English: **{translated}**")
        

    @app_commands.context_menu(name="OCR")
    async def ocr_ctx(inter: discord.Interaction, message: discord.Message):
        try:
            m = message
            #x = await inter.channel.send("Processing...")
            valid = [a for a in m.attachments if a.filename.split(".")[-1] in self.image_files]
            if len(valid) == 0:
                embed = functions.error("OCR", "🚫 " + functions.response(2) + " it looks like this message is missing a valid image.")
                return await inter.response.send_message(embed=embed)
            text = ""
            for image in m.attachments:
                imbytes = await m.attachments[0].read()
                text = text + pytesseract.image_to_string(Image.open(io.BytesIO(imbytes))) + "\n"
            if text:
                await inter.response.send_message(text)
                #await x.delete()
            else:
                await inter.response.send_message("🚫 " + functions.response(2) + " I couldn't find any text.")
        except Exception as e:
            print(str(e)) # idk why this is here

    @commands.command()
    async def ocr(self, ctx): # ocr is broken
        attachments = ctx.message.attachments
        valid = [a for a in attachments if a.filename.split(".")[-1] in self.image_files]
        if len(valid) == 0:
            embed = error("🚫 " + functions.response(2) + " it looks like your message is missing a valid image.")
            return await ctx.send(embed=embed)
        text = ""
        for image in attachments:
            imbytes = await attachments[0].read()
            text = text + pytesseract.image_to_string(Image.open(io.BytesIO(imbytes))) + "\n"
        if text:
            await ctx.send(text)
        else:
            await ctx.send(embed=error("🚫 " + functions.response(2) + " I couldn't find any text."))

    @commands.command()
    async def translate(self, ctx, language=None, *, message=None):
        if language is None:
            return await ctx.send(embed=error("🚫 " + functions.response(2) + " you need to specify a language to translate to."))
        if message is None:
            return await ctx.send(embed=error("🚫 " + functions.response(2) + " you need to specify a message to translate."))
        language = language.title()
        if language not in languages.values():
            return await ctx.send(embed=error("🚫 " + functions.response(2) + f" I can't find a language called `{language}`."))
        blob = textblob.TextBlob(message)
        lang = blob.detect_language()
        swapped = {languages[k]: k for k in languages}
        try:
            translated = blob.translate(to=swapped[language])
        except textblob.exceptions.NotTranslated:
            return await ctx.send(embed=error("🚫 " + functions.response(2) + f" it looks like this message can't be translated."))
        embed = botembed("Message Translated")
        embed.description = f"🔠 {functions.response(1)} I translated your message to {language}.\n\n```{translated}```"
        await ctx.send(embed=embed)

    


async def setup(bot):
    await bot.add_cog(Utilities(bot))


