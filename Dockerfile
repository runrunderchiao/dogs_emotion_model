# 使用官方的 Python 基礎映像檔
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 進入容器中
COPY requirements.txt .

# 安裝所需的系統依賴（如需要，可加入更多）
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安裝依賴
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 將 TensorFlow 設為可選 (如果您的應用需要特定版本，請明確指定)
RUN pip install tensorflow

# 複製所有 FastAPI 應用程式檔案
COPY . .

# 設定 FastAPI 的埠號 (例如 8000)
EXPOSE 8080

# 啟動 FastAPI 伺服器 (使用 uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]