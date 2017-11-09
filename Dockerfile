FROM frolvlad/alpine-python3

# Install all required dependencies
RUN apk add --no-cache gcc yaml-dev libev-dev git gcc g++ make libffi-dev openssl-dev
RUN apk add --no-cache python3-dev

# Create the directories where you are going to store the configs, logs and Amon itself
RUN mkdir -p /opt/amon
RUN mkdir -p /var/log/amon
RUN mkdir -p /etc/opt/amon

# Clone repo into app directory
RUN git clone https://github.com/amonapp/amon.git /opt/amon

# Install Python deps
RUN pip install -r /opt/amon/requirements.txt

# Setup Unicorn
COPY gunicorn.conf /opt/amon/gunicorn.conf

# Copy defaults and setup working directroy
COPY amon-defaults.yml /etc/opt/amon/amon.yml
WORKDIR /opt/amon

# Run the database migrations and cron install tasks
RUN python3 manage.py migrate
RUN python3 manage.py installtasks

# Setup external volumes
VOLUME ["/opts/amon", "/var/log/amon", "/etc/opt/amon"]

# Setup Ports
EXPOSE 8000

# Start webserver
CMD gunicorn wsgi -c /opt/amon/gunicorn.conf