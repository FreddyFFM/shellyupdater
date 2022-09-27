FROM python:3.8.14
ENV PYTHONUNBUFFERED 1
ENV TERM xterm

# Install dependencies
RUN \
  apt-get -y update && \
  apt-get -y install libssl-dev libffi-dev libcairo2 net-tools nano && \
  apt-get -y install python3-psycopg2 python3-pip python3-dev gunicorn

# Install Supervisor
RUN apt-get -y update && \
    apt-get -y install curl rsyslog supervisor procps
RUN mkdir -p /var/log/supervisor

# PIP Install
ADD shellyupdater/requirements.txt /home/updater/requirements.txt
RUN pip3 install --upgrade pip
RUN cd /home/updater && pip3 install -r requirements.txt

# Add Code
COPY shellyupdater /home/updater/shellyupdater
RUN mkdir -p /home/updater/logs

WORKDIR /home/updater/shellyupdater

EXPOSE 28080

# Copy Scripts
COPY config/scripts/migrate_load.sh /home/updater/shellyupdater/migrate_load.sh

# Start Supervisor
COPY config/supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
