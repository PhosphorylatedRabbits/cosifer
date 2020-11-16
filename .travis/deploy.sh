 #!/bin/sh

echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin
docker tag tsenit/cosifer:latest tsenit/cosifer:${TRAVIS_COMMIT}
docker tag tsenit/cosifer_notebook:latest tsenit/cosifer_notebook:${TRAVIS_COMMIT}
docker push tsenit/mimkl:${TRAVIS_COMMIT}
docker push tsenit/mimkl:latest