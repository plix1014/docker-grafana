ARG GRAFANA_VERSION

FROM grafana/grafana:latest
COPY dashboards /var/lib/grafana/dashboards
COPY provisioning /etc/grafana/provisioning

