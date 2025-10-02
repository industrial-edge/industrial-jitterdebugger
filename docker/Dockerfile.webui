FROM debian:bullseye-slim
RUN apt-get update && apt-get install -y python3-pip && apt-get clean
RUN pip3 install poetry==1.8.4
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
WORKDIR /work
COPY app.py favicon.ico sie-logo-white-rgb.png pyproject.toml poetry.lock ./
RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR 
EXPOSE 8501
CMD poetry run streamlit run /work/app.py --server.address="0.0.0.0"  --client.toolbarMode="minimal" --theme.base="dark" --theme.backgroundColor="#000028" --theme.primaryColor="#029402"  
