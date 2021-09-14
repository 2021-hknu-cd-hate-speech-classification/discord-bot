import os
import hikari
import torch
import util
import db
from hate_speech_classification_model import HateSpeechClassifier


bot = hikari.GatewayBot(token=os.environ["DISCORD_TOKEN"])
model: HateSpeechClassifier = torch.load(os.environ["MODEL_PATH"], map_location="cpu")
eosa_db = db.EosaDatabase()


@bot.listen(hikari.GuildMessageCreateEvent)
async def get_message(event: hikari.GuildMessageCreateEvent) -> None:
    if not event.is_human or len(event.content) < 5:
        return None

    cleaned_msg = util.clean_discord_markdown(event.content)
    score = model.infer(cleaned_msg)
    await event.message.add_reaction(f"{int(score[1] * 10)}\uFE0F\u20E3")

    if score[1] >= 0.7:
        eosa_db.add_detect_log(event.author_id, event.guild_id, event.content, score[1])
        await event.message.add_reaction("🤬")


@bot.listen(hikari.InteractionCreateEvent)
async def ping(event: hikari.InteractionCreateEvent) -> None:
    if event.interaction.command_name == "ping":
        await event.interaction.create_initial_response(4, "pong!")
        return None


@bot.listen(hikari.InteractionCreateEvent)
async def log(event: hikari.InteractionCreateEvent) -> None:
    if event.interaction.command_name == "log":
        logs = eosa_db.get_guild_detected_log(event.interaction.guild_id)
        await event.interaction.create_initial_response(4, logs)
        return None


bot.run()
