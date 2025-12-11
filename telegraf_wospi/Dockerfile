#------------------------------------------------------------------------------------------
# build image
# Datei: grafana/telegraf/Dockerfile (docbuc/telegraf)
FROM telegraf:latest AS base


# os config
RUN apt update && \
  apt-get install -y --no-install-recommends coreutils locales python3 python3-requests python3-idna python3-urllib3 python3-charset-normalizer python3-certifi python3-pytzdata python3-bs4 python3-lxml sudo && \
  sed -i -e 's,^# en_US,en_US,g' -e 's,^# de_AT,de_AT,g' /etc/locale.gen && \
  locale-gen && \
  update-locale && \
  apt-get -y clean && \
  rm -r /var/cache/apt /var/lib/apt/lists/* /var/log/*log

COPY 010_telegraf-nopasswd /etc/sudoers.d


#------------------------------------------------------------------------------------------
# build vanilla image
FROM base AS image-vanilla


# config telegraf
COPY --chown=telegraf:root --chmod=0644 telegraf.conf /etc/telegraf
COPY --chown=telegraf:root --chmod=0644 telegraf-wospi.conf /etc/telegraf/telegraf.d

RUN chown -R telegraf:root /etc/telegraf

COPY entrypoint.sh /
COPY --chmod=0755 wxdata2json.py /usr/local/bin

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
CMD ["telegraf"]

