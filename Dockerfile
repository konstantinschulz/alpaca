FROM python:3.9-slim
RUN apt-get update
RUN apt-get install -y gnupg2 wget git g++
RUN wget -qO - https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | apt-key add -
RUN apt-get install -y software-properties-common
RUN add-apt-repository --yes https://adoptopenjdk.jfrog.io/adoptopenjdk/deb/
RUN apt-get update
# avoid https://github.com/debuerreotype/debuerreotype/issues/10
RUN mkdir -p /usr/share/man/man1
RUN apt-get install -y adoptopenjdk-8-hotspot
# Install tini and create an unprivileged user
ADD https://github.com/krallin/tini/releases/download/v0.19.0/tini /sbin/tini
RUN addgroup --gid 1001 "elg" && adduser --disabled-password --gecos "ELG User,,," --home /elg --ingroup elg --uid 1001 elg && chmod +x /sbin/tini

# Copy in our app, its requirements file and the entrypoint script
COPY --chown=elg:elg requirements.txt docker-entrypoint.sh elg_service.py /elg/
COPY --chown=elg:elg language_tool_python /elg/.cache/language_tool_python
# Everything from here down runs as the unprivileged user account
USER elg:elg
WORKDIR /elg
ENV WORKERS=1
# Create a Python virtual environment for the dependencies
RUN python -m venv venv
RUN /elg/venv/bin/pip --no-cache-dir install -r requirements.txt
RUN /elg/venv/bin/python -c "import nltk; nltk.download('punkt')"
COPY --chown=elg:elg . .
RUN chmod +x ./docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
