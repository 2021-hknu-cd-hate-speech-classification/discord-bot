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
        score = model.infer(message.content)
        print(message.content, float(score[1]))
        await message.add_reaction(f"{int(score[1] * 10)}\uFE0F\u20E3")

        if score[1] >= 0.7:
            await message.add_reaction("🤬")

    else:
        await message.add_reaction("😑")

    return None

    # if score[0][1] > threshold_score:
    #     # 메시지를 삭제한 후 안내
    #     noti = discord.Embed()
    #     noti.title = "메시지 삭제 안내"
    #     noti.description = f"메시지가 삭제되었습니다. 점수가 {threshold_score}점 이상일 경우 삭제됩니다."
    #     noti.colour = 0xd32f2f
    #     noti.add_field(name="메시지 내용", value=message.content, inline=False)
    #     noti.add_field(name="점수", value=str(score.tolist()), inline=False)
    #     noti.add_field(name="작성 시간(UTC)", value=message.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    #     noti.add_field(name="작성자", value=message.author.display_name)
    #     await message.delete()
    #     await message.channel.send(embed=noti)
    # elif score[0][1] > threshold_score - 0.1:
    #     await message.add_reaction("🤬")
    #     return None

client.run(token)
