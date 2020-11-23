# intermediate image for dependencies
FROM rocker/r-ver:3.6.3 as intermediate
# system dependencies
RUN apt-get -y update && apt-get -y install git libgraphviz-dev pkg-config \
        python3-dev python3-pip libcurl4-openssl-dev libssl-dev libxml2-dev \
        && rm -rf /var/lib/apt/lists/*
# get requirements
COPY requirements.txt /
WORKDIR /pip-packages/
RUN pip3 install wheel
RUN pip3 wheel -w /pip-packages/ -r /requirements.txt
# main image
FROM rocker/r-ver:3.6.3
# system dependencies
RUN apt-get -y update && apt-get -y install git libgraphviz-dev pkg-config \
        python3-dev python3-pip libcurl4-openssl-dev libssl-dev libxml2-dev \
        locales curl libssh2-1-dev cmake gosu libgit2-dev build-essential
        # && rm -rf /var/lib/apt/lists/*
# update pip
RUN pip3 install --upgrade pip
# setting locale to UTF-8
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
# get dependencies from the intermediate container
WORKDIR /pip-packages/
COPY --from=intermediate /pip-packages/ /pip-packages/
# installation
WORKDIR /app/
# install requirements
RUN pip3 install --no-index -f /pip-packages/ /pip-packages/*
# install app
COPY . .
RUN pip3 install -v --no-deps -e .
# add user to run the app
RUN adduser --disabled-password --gecos '' cosifer --uid 1000
RUN chown -R cosifer:cosifer /app
# make R libraries visible to the app user
RUN find /root -type d -exec chmod 777 {} \; && find /root -type f -exec chmod 666 {} \;
ENV R_LIBS_USER /usr/local/lib/R/site-library
ENV LD_LIBRARY_PATH /usr/local/lib/R/lib
# run cosifer
WORKDIR /
COPY docker/entrypoint_cli.sh .
ENTRYPOINT ["./entrypoint_cli.sh"]
CMD [ "--help" ]
