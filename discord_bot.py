import re
import discord
import torch
from hate_speech_classification_model import HateSpeechClassifier

# https://discord.com/api/oauth2/authorize?client_id=823899168942456922&permissions=8258&scope=bot


def get_env(name: str) -> str:
    import os

    try:
        result = os.environ[name]
    except KeyError:
        result = ""

    return result


client = discord.Client()
token = get_env("DISCORD_TOKEN")

MODEL_PATH = get_env("MODEL_PATH")
model: HateSpeechClassifier = torch.load(MODEL_PATH, map_location="cpu")


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

    if len(message.content) >= 5:
        cleaned_msg = clean_discord_markdown(message.content)
        score = model.infer(cleaned_msg)
        print(message.content, float(score[1]))
        await message.add_reaction(f"{int(score[1] * 10)}\uFE0F\u20E3")

        if score[1] >= 0.7:
            await message.add_reaction("🤬")

    else:
        await message.add_reaction("😑")

    return None

client.run(token)


def clean_discord_markdown(txt: str) -> str:
    pattern = re.compile(r"[*_~]+([^*_~]+)[*_~]+")
    codeblock_pattern = re.compile(r"`{1,3}[^`]+`{1,3}")
    quote_pattern = re.compile(r"^>{1,3}\s?", re.MULTILINE)

    txt = pattern.sub(r"\1", txt)
    txt = codeblock_pattern.sub("", txt)
    txt = quote_pattern.sub("", txt)

    return " ".join([x.strip() for x in txt.split("\n") if x != ""]).strip()
