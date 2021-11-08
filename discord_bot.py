import os
import hikari
import torch
import util
import db
import logging
from hate_speech_classification_model import HateSpeechClassifier


bot = hikari.GatewayBot(token=os.environ["DISCORD_TOKEN"])
model: HateSpeechClassifier = torch.load(os.environ["MODEL_PATH"], map_location="cpu")
eosa_db = db.EosaDatabase()
model.freeze()
THRESHOLD = os.environ["THRESHOLD"] if ("THRESHOLD" in os.environ) else 0.725


@bot.listen(hikari.GuildMessageCreateEvent)
async def get_message(event: hikari.GuildMessageCreateEvent) -> None:
    if not event.is_human or event.content is None or len(event.content) < 5:
        return None

    cleaned_msg = util.clean_discord_markdown(event.content)
    score = model.infer(cleaned_msg)
    logging.info(f"{model.tokenizer.tokenize(cleaned_msg)} {score}")

    # 점수가 THRESHOLD 이상일 경우 리액션 후 DB에 등록
    if score[1] >= THRESHOLD:
        await event.message.add_reaction("🤬")

        if eosa_db.get_user_detected_count(event.author_id, event.guild_id) >= 2:
            # 등록된 악플 횟수가 2회일 경우 추방 후 기록 삭제
            try:
                await event.get_guild().kick(event.author_id)
            except hikari.ForbiddenError:
                pass

            eosa_db.delete_log_by_user_id(event.author_id, event.guild_id)
        else:
            # 2회 이상이 아닐 경우 DB에 등록
            eosa_db.add_detect_log(event.author_id, event.guild_id, event.content, score[1])


@bot.listen(hikari.InteractionCreateEvent)
async def ping(event: hikari.InteractionCreateEvent) -> None:
    if event.interaction.command_name == "ping":
        await event.interaction.create_initial_response(4, "pong!")
        return None


@bot.listen(hikari.InteractionCreateEvent)
async def log(event: hikari.InteractionCreateEvent) -> None:
    if event.interaction.command_name == "log":
        logs = eosa_db.get_user_detected_log(event.interaction.user.id, event.interaction.guild_id)
        await event.interaction.create_initial_response(4, logs)

    return None


@bot.listen(hikari.InteractionCreateEvent)
async def user_log(event: hikari.InteractionCreateEvent) -> None:
    if event.interaction.command_name == "user-log":
        logs = eosa_db.get_user_detected_log(event.interaction.options[0].value, event.interaction.guild_id)
        await event.interaction.create_initial_response(4, logs)

    return None


bot.run()
