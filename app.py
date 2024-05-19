from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
	ApiClient, Configuration, MessagingApi,
	ReplyMessageRequest, PushMessageRequest,
	TextMessage, PostbackAction, ImageMessage
)
from linebot.v3.webhooks import (
	FollowEvent, MessageEvent, PostbackEvent, TextMessageContent
)
from imgurpython import ImgurClient
from config import client_id, client_secret, album_id, access_token, refresh_token
import os, random
from PIL import Image
import numpy as np

from dotenv import load_dotenv
load_dotenv()

CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

app = Flask(__name__)

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

#所有從LINE平台傳來的事件都會先經過callback再轉到 handler 進行處理
@app.route("/callback", methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']
	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)
	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
		abort(400)
	return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
	with ApiClient(configuration) as api_client:
		line_bot_api = MessagingApi(api_client)

	line_bot_api.reply_message(ReplyMessageRequest(
		replyToken=event.reply_token,
		messages=[TextMessage(text='Thank You!')]
	))

#文字訊息處理
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
	with ApiClient(configuration) as api_client:
		line_bot_api = MessagingApi(api_client)

	#取得傳入訊息
	received_message = event.message.text
	#關鍵字apple
	if received_message == 'apple':
		line_bot_api.reply_message(ReplyMessageRequest(
			replyToken=event.reply_token,
			messages=[TextMessage(text='This is keyword for apple!')]))
	#關鍵字image
	elif received_message == 'image':
		client = ImgurClient(client_id, client_secret)
		images = client.get_album_images(album_id)
		index = random.randint(0, len(images) - 1)
		url = images[index].link
		line_bot_api.reply_message(ReplyMessageRequest(
			replyToken=event.reply_token,
			messages=[ImageMessage(original_content_url=url,preview_image_url=url)]))	
	#預設回聲
	else:
		line_bot_api.reply_message(ReplyMessageRequest(
			replyToken=event.reply_token,
			messages=[TextMessage(text=received_message)]))
	
@app.route('/', methods=['GET'])
def toppage():
	return 'Hello world!'

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8000, debug=True)