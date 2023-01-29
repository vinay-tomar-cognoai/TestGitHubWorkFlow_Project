FROM python:3.9.1

COPY entrypoint_daphne.sh /
#COPY entrypoint_scheduler.sh /Cognoai/
#COPY entrypoint_daphne.sh /Cognoai/
COPY requirements.txt /
COPY nltk_setup.py /
WORKDIR /Cognoai
RUN pip install -r /requirements.txt
RUN rm /requirements.txt
RUN apt update
RUN apt install libenchant1c2a -y
#RUN apt-get install cron -y
#RUN pip install -U Twisted[tls,http2]
RUN python -m spacy download en_core_web_sm
RUN python /nltk_setup.py
RUN rm /nltk_setup.py
#RUN apt install nodejs -y
#RUN apt install npm -y
#EXPOSE 8002
EXPOSE 8010
# npm entrypoint only for livechat
#ENTRYPOINT ["cd /Cognoai/LiveChatApp/ && npm install && npm run build"]
ENTRYPOINT ["sh", "/entrypoint_daphne.sh"]
