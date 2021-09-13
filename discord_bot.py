import os
import discord
import torch
from hate_speech_classification_model import HateSpeechClassifier

import util
import db

# https://discord.com/api/oauth2/authorize?client_id=823899168942456922&permissions=8258&scope=bot

client = discord.Client()
token = os.environ["DISCORD_TOKEN"]

MODEL_PATH = os.environ["MODEL_PATH"]
model: HateSpeechClassifier = torch.load(MODEL_PATH, map_location="cpu")
eosa_db = db.EosaDatabase()


@client.event
async def on_ready():
    print("login")


@client.event
async def on_message(message):
    if message.author.bot:
        return None

    if message.content.startswith("!"):
        await message.add_reaction("⏭️")
        return None

    if message.content.startswith("?"):
        log = eosa_db.get_guild_detected_log(message.guild.id)
        await message.reply(log)

    if len(message.content) >= 5:
        cleaned_msg = util.clean_discord_markdown(message.content)
        score = model.infer(cleaned_msg)
        print(message.content, float(score[1]))
        await message.add_reaction(f"{int(score[1] * 10)}\uFE0F\u20E3")

        if score[1] >= 0.7:
            eosa_db.add_detect_log(message.author.id, message.guild.id, cleaned_msg, score[1])
            await message.add_reaction("🤬")

    else:
        await message.add_reaction("😑")

    return None

client.run(token)