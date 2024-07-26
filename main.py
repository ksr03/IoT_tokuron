import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from flask import Flask
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage

load_dotenv()

app = Flask(__name__)

# 環境変数の読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
USER_ID = os.getenv('USER_ID')
MQTT_TOPIC = os.getenv('MQTT_TOPIC')

# Initialize LINE bot API and handler
# line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
# handler = WebhookHandler(LINE_CHANNEL_SECRET)

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Received message: {message} on topic {msg.topic}")
    # line_bot_api.push_message(USER_ID, TextSendMessage(text=message))
    print('Message sent to LINE')

# MQTTクライアントの作成
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to MQTT broker
mqtt_client.connect('broker.hivemq.com', 1883, 60)

@app.route('/')
def home():
    return MQTT_TOPIC

if __name__ == '__main__':
    # Start Flask app
    app.run(port=3000)
    # Start MQTT loop
    mqtt_client.loop_start()
