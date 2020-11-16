# intermediate image for dependencies and user "cosifer" setup
FROM tsenit/cosifer
RUN pip install --no-cache-dir notebook==5.*
ENV HOME /home/cosifer
COPY examples/ ${HOME}/examples/
RUN chown -R cosifer ${HOME}
# run jupyter
USER cosifer
WORKDIR ${HOME}
EXPOSE 8888
ENTRYPOINT []
CMD [ "jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0"]
