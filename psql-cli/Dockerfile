FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive

RUN /bin/echo -e '#!/bin/bash\nDEBIAN_FRONTEND=noninteractive\napt-get update && apt-get install -y $@ && apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/apt/lists/*' \
    > /usr/local/sbin/apt_install_clean.sh && \
    chmod a+x /usr/local/sbin/apt_install_clean.sh
RUN /bin/echo -e '#!/bin/bash\nDEBIAN_FRONTEND=noninteractive\napt-get update && apt-get remove -y $@ && apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/apt/lists/*' \
    > /usr/local/sbin/apt_remove_clean.sh && \
    chmod a+x /usr/local/sbin/apt_remove_clean.sh

# install
#RUN /usr/local/sbin/apt_install_clean.sh postgresql-client iputils-ping net-tools curl wget
RUN /usr/local/sbin/apt_install_clean.sh iputils-ping net-tools curl wget gnupg2 nano

# psql 14
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
#RUN apt search postgresql
RUN /usr/local/sbin/apt_install_clean.sh postgresql-client-14

# build validation
RUN which psql
RUN which ping
RUN which netstat
RUN which curl
RUN which wget
RUN which nano

RUN /usr/local/sbin/apt_install_clean.sh openssh-server
#CMD ["/bin/sh", "-c", "sleep infinity"]
# also start up ssh for cases where it's helpful
COPY setup_ssh.sh /
ENTRYPOINT ["/setup_ssh.sh"]
