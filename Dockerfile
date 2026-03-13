FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD sh -c "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0"