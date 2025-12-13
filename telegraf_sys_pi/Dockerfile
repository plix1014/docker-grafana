# Datei: grafana/telegraf/Dockerfile (docbuc/telegraf)
FROM telegraf:latest

ARG TELEGRAF_VERSION

ENV TELEGRAF_VERSION=${TELEGRAF_VERSION}

# os config
RUN apt update && \
  apt-get install -y --no-install-recommends sudo && \
  apt-get -y clean && \
  rm -r /var/cache/apt /var/lib/apt/lists/* /var/log/*log

#------------------------------------------------------------------------------------------
COPY 010_telegraf-nopasswd /etc/sudoers.d

COPY --chown=telegraf:root --chmod=0644 telegraf.conf /etc/telegraf

RUN chown -R telegraf:root /etc/telegraf
RUN usermod -aG video telegraf


ADD raspi.libs.tar.gz /
COPY entrypoint.sh /
COPY vcgencmd.sh /usr/local/bin

USER telegraf

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
CMD ["telegraf"]

