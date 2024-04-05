FROM mysterysd/wzmlx:heroku
RUN apt update && apt upgrade -y
RUN apt-get install git curl python3-pip ffmpeg -y
RUN apt-get -y install git
RUN apt-get install -y wget python3-pip curl bash neofetch ffmpeg aria2
COPY requirements.txt .

RUN pip3 install --no-cache-dir -U -r requirements.txt
COPY . .
CMD ["python3", "bot.py"]
