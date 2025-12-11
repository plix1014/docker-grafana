# Datei: grafana/telegraf/Dockerfile (docbuc/telegraf)
FROM telegraf:latest

COPY --chown=telegraf:root --chmod=0644 telegraf.conf /etc/telegraf
COPY --chown=telegraf:root --chmod=0644 telegraf-openweathermap.conf /etc/telegraf/telegraf.d

RUN chown -R telegraf:root /etc/telegraf

COPY entrypoint.sh /

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
CMD ["telegraf"]

