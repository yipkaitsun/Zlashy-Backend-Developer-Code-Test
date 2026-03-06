FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=run:app
ENV DATABASE_URL=mysql+pymysql://root:password@flask-app-mysql/flask_app
ENV AUTH_USERNAME=admin
ENV AUTH_PASSWORD=admin
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
