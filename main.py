import os
from dotenv import load_dotenv
from paho.mqtt import client as mqtt_client
from flask import Flask
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage

load_dotenv()

app = Flask(__name__)

# 環境変数の読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
USER_ID = os.getenv('USER_ID')
MQTT_TOPIC_TEMP = os.getenv('MQTT_TOPIC_TEMP')
MQTT_TOPIC_HUMID = os.getenv('MQTT_TOPIC_HUMID')

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
        if msg.topic == MQTT_TOPIC_TEMP:
            text = f"今の気温は {msg.payload.decode()} 度です"
        elif msg.topic == MQTT_TOPIC_HUMID:
            text = f"今の湿度は {msg.payload.decode()} %です"

        line_bot_api.push_message(USER_ID, TextSendMessage(text=text))
        print('Message sent to LINE')
    
    client.subscribe([(MQTT_TOPIC_TEMP, 0), (MQTT_TOPIC_HUMID, 0)])
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

@app.route('/')
def home():
    return 'Hello, World!'

if __name__ == '__main__':
    # Start Flask app
    # app.run(port=3000)
    # Start MQTT loop
    run()
