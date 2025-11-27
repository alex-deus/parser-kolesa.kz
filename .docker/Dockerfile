FROM python:3.11.5-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV WORK_DIR "/application/src"
ENV USER kolesa
ENV GROUP kolesa

EXPOSE 5555
EXPOSE 8000

WORKDIR ${WORK_DIR}

RUN addgroup --system ${GROUP} \
    && adduser --system --home ${WORK_DIR}/../user --ingroup ${GROUP} ${USER} --shell /bin/bash \
    && chown -R ${USER}:${GROUP} ${WORK_DIR}/..

RUN pip install --no-cache-dir poetry &&\
    poetry config virtualenvs.create false
ADD poetry.lock .
ADD pyproject.toml .
RUN poetry install --no-interaction --no-ansi --no-root

ADD . .

ENTRYPOINT ["/application/src/docker-entrypoint.sh"]
