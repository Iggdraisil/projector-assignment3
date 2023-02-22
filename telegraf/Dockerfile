FROM telegraf:1.24

LABEL author="Alexis Le Provost <alexis.leprovost@outlook.com>"
LABEL version="1.0.0"
LABEL description="Telegraf docker image"

USER root


RUN apt-get update && apt-get -y install build-essential hddtemp

ADD run.sh /run.sh

ADD telegraf.conf.template /telegraf.conf.template
COPY *.conf /etc/telegraf/telegraf.d/

ENTRYPOINT ["bash", "/run.sh"]
