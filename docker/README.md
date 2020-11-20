# cosifer via Docker
cosifer depends on both python and R. Via docker we provide an platform
independent environment to use the command line interface, and an additional 
image to use  cosifer as a library via jupyter notebooks.  

If you have a clone of the repo, you can quickly download both images from
DockerHub with
```
docker-compose -f docker/docker-compose.yml pull
```


## CLI
The cosifer image could be run like this:
```console
docker --rm run tsenit/cosifer --help
```
However, as cosifer reads and writes files, you will have to make sure the 
docker container has appropriate access. This boils down to bind mounting the 
source and target directories, which can be done modifying the `docker` call, 
adding the `--volume` flag and arguments.  

We recommend using a small docker-compose.yml, like it can be found in the
[GitHub repo](https://github.com/PhosphorylatedRabbits/cosifer/docker/docker-compose.yml).


For example this docker-compose.yml:
```
version: "3"
services:
  cosifer:
    image: tsenit/cosifer
    container_name: "cosifer-cli-container"
    volumes:
    - your/local/path/to/data:/data
    # more mounts here
```
can run with:
```
docker-compose -f docker-compose.yml run --rm cosifer -i /data/input.tsv -o /data/output_directory/
```
and compares to:
```
docker --rm -v "absolute/local/path/to/data:/data" run tsenit/cosifer cosifer -i /data/input.tsv -o /data/output_directory/
```
so you will find the results under `your/local/path/to/data/output_directory/`


## Jupyter Notebook
<!-- TODO Binder badge -->
you might want use cosifer directly in python, and for that we provide an image 
running cosifer in a jupyter notebook. This allows more control over your 
workflow/pipeline. Try out an example interactively via binder!
<!-- TODO Binder link -->

Moreover, the Dockerfile might serve as an example to build your 
own image where you can add your dependencies.

Compared to run the [cli image](#cli), make sure to export the jupyter port 
when starting a container.

For example with such a docker-compose.yml:
```
version: "3"
services:
  notebook:
    image: tsenit/cosifer_notebook
    container_name: "cosifer-notebook-container"
    ports:
    - "8888:8888"
    volumes:
    - your/local/path/to/data:/data
    - ./notebooks:/home/cosifer/notebooks
```

Start the jupyter notebook server with
```
docker-compose -f docker-compose.yml up notebook
```
and use the url in the logs to open the notebook in the browser.