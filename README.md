# Jetpack - Development Quickstarts

Certain tasks like setting up development infrastructure or bootstrapping a development environment quickly can be a challenge, guides about them can help in streamlining the process.

- [Jetpack - Development Quickstarts](#jetpack---development-quickstarts)
  - [Jetpacks](#jetpacks)
  - [Docker-Compose + Flask (Python 3.6) + React (TypeScript)](#docker-compose--flask-python-36--react-typescript)
    - [Overview](#overview)
    - [Guide](#guide)
    - [Finishing Thoughts](#finishing-thoughts)
  - [Docker-Compose + Go (Routing with Gin) + React (TypeScript)](#docker-compose--go-routing-with-gin--react-typescript)
    - [Overview](#overview-1)
    - [Guide](#guide-1)
    - [Go-React-TypeScript Files](#go-react-typescript-files)
      - [`docker-compose.yml`](#docker-composeyml)
      - [`dockerfile`](#dockerfile)
      - [`back-end/dockerfile`](#back-enddockerfile)
    - [Finishing Thoughts](#finishing-thoughts-1)

## Jetpacks

## Docker-Compose + Flask (Python 3.6) + React (TypeScript)

### Overview

The end product is a Flask app that serves a React files and handles API requests. It will be deployable by either docker-compose building locally, or via being built as an image and then handling through a container orchestrator such as Kubernetes. Note, that this is not a "production ready" template due to the tight coupling of the API-Server and File-Server through the Flask app, though this would scale, a much more effective route towards the same solution would likely involve a static file server which also reverse proxies API requests to the Flask Back-End, allowing for independent scaling of the Front-End and Back-End.

### Guide

...

### Finishing Thoughts

...

## Docker-Compose + Go (Routing with Gin) + React (TypeScript)

### Overview

The end product is a composition of two Go web applications: one that serves strictly API requests and another which handles both file serving and proxying requests to the aforementioned API server. It will be deployable by either docker-compose building locally, or via both applications being built into images and then handling through a container orchestrator such as Kubernetes. The API-Server and File-Server are not tightly coupled, as a result this would scale effectively on it's own, though you could very well make adjustments to suite it more towards your liking.

### Guide

First thing you are going to need to do is install Create-React-App:

```bash
$ npm install -g create-react-app
+ create-react-app@3.0.1
added 32 packages from 28 contributors, removed 4 packages and updated 11 packages in 90.445s
```

Then run Create-React-App with the flag for TypeScript to create the boilerplate in a new directory for your react project (note, npx is included in npm with npm 5.2+ and higher, [see these instructions for help with older npm versions](https://gist.github.com/gaearon/4064d3c23a77c74a3614c498a8bb1c5f)):

```bash
$ npx create-react-app my-app --typescript

Creating a new React app in ~/my-app.

Installing packages. This might take a couple of minutes.
Installing react, react-dom, and react-scripts...

...

We suggest that you begin by typing:

  cd my-app
  npm start

Happy hacking!

```

Add in the files (with the same directory structure as in the repo) from the Jetpacks [repo](https://github.com/the-rileyj/Jetpacks) in `./Go-React-TypeScript` into the root of your project directory. You will then need to install [github.com/gin-gonic/gin](github.com/gin-gonic/gin) and [github.com/the-rileyj/serverutils](github.com/the-rileyj/serverutils) via `go get`.

[github.com/the-rileyj/serverutils](github.com/the-rileyj/serverutils) is a package I wrote, it is a small collection of server utilities (password hashing, generating UUIDs, etc), route handlers, and middleware. It is fairly easy to read and comprehend, and though this package is largely geared toward my own needs, I'm always accepting pull requests if there is something you find broken or missing.

Adjust the following variables in the files as described in the following sections; these adjustments are the most minimal nessesary for you to get up and going, any other changes are up to you.

***Note*** - If you are testing building the environment locally after developing and already have all of the front-end dependencies, you can speed up the build time significantly by adding in a `COPY` directive which copies the `node_modules` directory into the `Front-End-Builder` build context (before the `RUN npm install` line) in the dockerfile that is in the root of the project after copying over the files in `./Go-React-TypeScript`. If you do this, you need to remove the `node_modules/` line from the `.dockerignore` file

### Go-React-TypeScript Files

#### `docker-compose.yml`

Note, if you intend for this project to be standalone, as in it won't connect to any other services via a docker network, you can simply remove the top-level network directive and the network attributes for each of the services. Under the `api-server`, `file-server`, and `networks` directive, the "internal" network (the network used by the services in the `docker-compose.yml` file via the `networks` top-level-directive, used in tandem with the "name" field, roughly associates that network name with an external-network docker network, in this case named "PROJECT-network-external) is currently called "PROJECT-network-internal", change all occurances in the file to whatever you want, so long as they are all the same. Then change the "external" network "PROJECT-network-external" to the name of the docker network you want to connect to.

The `networks` top-level-directive (in the `docker-compose.yml` file):

```yml
networks:
  PROJECT-network-internal:
    name: PROJECT-network-external
```

The `file-server` service (in the `docker-compose.yml` file):

```yml
  ...

  file-server:
    build: .
    expose:
      - "80"
    networks:
      - PROJECT-network-internal
    restart: always

  ...
```

#### `dockerfile`

Right after the second build stage (named `File-Server-Builder`), the `WORKDIR` is set to change into `/go/src/github.com/the-rileyj/PROJECT/`, change `PROJECT` and `the-rileyj` to your project name and github name (it should end up looking very similar to the path of your project on your development machine) or change the path to suit your needs, then do the same thing shortly after the last build stage (after the `FROM scratch` line). Note that there isn't any copying of TLS certificates or secrets, so if you are planning to use HTTPS make sure to place them in the container.

Right after the second build stage (in the `dockerfile`):

```dockerfile
...
# Add ca-certificates to get the proper certs for making requests,
# gcc and musl-dev for any cgo dependencies, and
# git for getting dependencies residing on github
RUN apk update && \
    apk add --no-cache ca-certificates gcc git musl-dev

WORKDIR /go/src/github.com/the-rileyj/PROJECT/

COPY ./back-end/file-server/file-server.go .
...
```

After the last build stage (in the `dockerfile`):

```dockerfile
...
# Last stage of build, adding in files and running
# newly compiled webserver
FROM scratch

# Copy the built files into the file-server container
COPY --from=Front-End-Builder /build /static

# Copy the Go program compiled in the second stage
COPY --from=File-Server-Builder /go/src/github.com/the-rileyj/PROJECT/ /

...
```

#### `back-end/dockerfile`

Under the first build context called `API-Builder`, the first `WORKDIR` directive is set to change into `/go/src/github.com/the-rileyj/PROJECT/` change `PROJECT` and `the-rileyj` to your project name and github name (it should end up looking very similar to the path of your project on your development machine) or change the path to suit your needs; then in the last build context of the dockerfile, the first non-commented line starting immediately after the line with the `FROM scratch` directive should have its copy source changed from `/go/src/github.com/the-rileyj/PROJECT/` to whatever you changed the `WORKDIR` destination to in the `API-Builder` build context.

Under the first build context (found in the `dockerfile`):

```dockerfile
...

FROM golang:1.11.3-alpine3.8 AS API-Builder

# Add ca-certificates to get the proper certs for making requests,
# gcc and musl-dev for any cgo dependencies, and
# git for getting dependencies residing on github
RUN apk update && \
    apk add --no-cache ca-certificates gcc git musl-dev

WORKDIR /go/src/github.com/the-rileyj/PROJECT/

...
```

Immediately after the line with the `FROM scratch` directive (found in the `dockerfile`):

```dockerfile
...

# Last stage of build, adding in files and running
# newly compiled webserver
FROM scratch

# Copy the Go program compiled in the second stage
COPY --from=API-Builder /go/src/github.com/the-rileyj/PROJECT/ /

...
```

### Finishing Thoughts

If you are using go modules, make sure to copy over your dependency files and install prior to copying over your Go file (to make the most use of caching the installs). Best of luck, hack away!
