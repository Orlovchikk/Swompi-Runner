FROM alpine/openssl:3.5.4 AS build

COPY ./init_config.sh /usr/local/bin
RUN chmod +x /usr/local/bin/init_config.sh && ./usr/local/bin/init_config.sh

FROM debian:11-slim

COPY --from=build /etc/garage.toml /etc/
COPY ./garage /
COPY ./init_garage.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/init_garage.sh && chmod +x /garage

CMD [ "/garage", "server"]