import os
from io import BytesIO
import requests
import numpy as np
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
from PIL import Image
from keras.models import load_model
from dotenv import load_dotenv

# 載入 .env 文件
load_dotenv()

# 初始化 FastAPI 應用程式
app = FastAPI()

# 從 .env 文件中讀取 Channel Access Token 和 Channel Secret
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

# 設定 LINE Messaging API 配置和 WebhookHandler
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 載入訓練好的模型
model = load_model("your_model.h5")
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# 定義類別名稱
class_names = ["不要碰我 除非你有肉肉", "啦啦啦啦開心(⁠⁠˘⁠⁠³⁠˘⁠)", "歐歐睏", "QQ快來給我惜惜"]  # 根據您的分類類別更新

# 圖片處理與預測函數
def predict_image(img):
    # 調整圖片大小與預處理
    img = img.resize((150, 150))  # 假設模型需要 150x150 大小
    img_array = np.array(img) / 255.0  # 正規化
    img_array = np.expand_dims(img_array, axis=0)  # 增加批次維度
    
    # 使用模型進行預測
    predictions = model.predict(img_array)
    predicted_class = class_names[np.argmax(predictions)]
    confidence = np.max(predictions)
    return predicted_class, confidence

# 根路徑測試
@app.get("/")
def root():
    return {"message": "LINE Chatbot is running"}

# LINE Webhook 路徑
@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()

    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return JSONResponse(content={"message": "OK"})

# 處理訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 回傳固定文字「開心」
    reply_text = "傳送你家狗狗的表情照片"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    # 取得圖片訊息 ID
    image_id = event.message.id

    # 使用 LINE Messaging API 下載圖片內容
    message_content = line_bot_api.get_message_content(image_id)
    
    # 將圖片內容儲存至記憶體
    image_data = BytesIO(message_content.content)
    img = Image.open(image_data)

    # 您可以在此處對圖片執行進一步操作，例如儲存檔案、執行模型預測等
    # 使用模型進行分類
    predicted_class, confidence = predict_image(img)

    # 回應預測結果
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"辨識結果: {predicted_class}，信心值: {confidence:.2f}")
    )