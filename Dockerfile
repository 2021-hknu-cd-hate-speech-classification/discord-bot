FROM python:3.8-slim
WORKDIR /opt
COPY . .
RUN apt-get -y update
RUN apt-get -y install git
RUN pip install -r requirements.txt
CMD [ "python", "discord_bot.py" ]
