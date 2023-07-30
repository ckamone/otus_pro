FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /hasker
COPY ./requirements.txt /hasker
RUN pip install -r requirements.txt
COPY . /hasker
COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]