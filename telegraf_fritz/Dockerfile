#------------------------------------------------------------------------------------------
# checkout git
FROM alpine/git:latest
WORKDIR /addon
RUN git clone https://github.com/kbr/fritzconnection.git
RUN git clone https://github.com/blackw1ng/FritzBox-monitor.git

#------------------------------------------------------------------------------------------
# build image
# Datei: grafana/telegraf/Dockerfile (docbuc/telegraf)
FROM telegraf:1.27 AS base

COPY --from=0 /addon/fritzconnection /src/fritzconnection
COPY --from=0 /addon/FritzBox-monitor /src/FritzBox-monitor

# os config
RUN apt update && \
  apt-get install -y --no-install-recommends coreutils locales python3 pip python3-requests python3-idna python3-urllib3 python3-charset-normalizer python3-certifi sudo && \
  pip install --no-cache-dir --break-system-packages  fritzconnection && \
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
COPY --chown=telegraf:root --chmod=0644 telegraf-fritzbox.conf /etc/telegraf/telegraf.d

RUN chown -R telegraf:root /etc/telegraf

COPY entrypoint.sh /
COPY --chmod=0755 checkfritz.py /usr/local/bin

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
CMD ["telegraf"]

