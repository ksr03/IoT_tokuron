import os
from dotenv import load_dotenv
from paho.mqtt import client as mqtt_client
from flask import Flask
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
import datetime

load_dotenv()

app = Flask(__name__)

# 環境変数の読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
USER_ID = os.getenv('USER_ID')
MQTT_TOPIC = os.getenv('MQTT_TOPIC')

# LINE Botの設定
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# MQTTブローカーへの接続
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect('broker.hivemq.com', 1883)
    return client

# MQTTトピックの購読
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        data = msg.payload.decode()

        # 気温と湿度を取得
        temp, humid = data.split(',')
        temp = float(temp)
        humid = float(humid)

        # テキストの作成
        dt_now = datetime.datetime.now()
        text = f"{dt_now.strftime('%Y/%m/%d %H:%M:%S')}\n気温は {temp} 度、湿度は {humid} %です。"
        if temp > 28:

            text += "\n注意: 室温が28度以上です。熱中症対策のため、冷房を付けましょう"
        if humid > 65:
            text += "\n注意: 湿度が65%以上です。湿度が高いため、水分補給を忘れずに"

        # LINEにメッセージを送信
        line_bot_api.push_message(USER_ID, TextSendMessage(text=text))
        print(f"Message sent to LINE: {text}")
    
    client.subscribe(MQTT_TOPIC)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

@app.route('/')
def home():
    return 'Hello, World!'

if __name__ == '__main__':
    run()
