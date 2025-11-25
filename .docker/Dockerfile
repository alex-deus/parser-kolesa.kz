FROM python:3.11.5-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV DISPLAY :99
ENV WDM_LOG_LEVEL 30
ENV WORK_DIR "/application/src"
ENV USER kolesa
ENV GROUP kolesa

EXPOSE 5555
EXPOSE 8000

WORKDIR ${WORK_DIR}

RUN apt update \
    && apt install -y xvfb fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libnss3 \
        libnss3 libgconf-2-4 libxi6 libxrender1 libxtst6 libxcomposite1 libasound2 libxdamage1 \
        libxrandr2 libatk1.0-0 libgtk-3-0 libx11-xcb1 wget curl unzip gnupg ca-certificates \
        libnspr4 libnss3 libxss1 libxtst6 libgtk-3-0 libu2f-udev libvulkan1 libgbm1 libxshmfence1 \
    && apt clean \
    && apt autoclean \
    && apt autoremove --yes \
    && rm -rf /var/cache/apt/lists \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

RUN wget -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y /tmp/google-chrome.deb \
    && google-chrome --version \
    && rm -rf  /var/lib/apt/lists/* \
    && apt clean \
    && apt autoclean \
    && apt autoremove --yes \
    && rm -rf /tmp/google-chrome.deb /var/cache/apt/lists \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

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
