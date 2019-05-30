# Jetpack - Development Environment Quickstarts

## Why?

...

## Jetpacks

### Docker-Compose + Go (Routing with Gin) + React (TypeScript)

First thing you are going to need to do is install Create-React-App (note you need version 2.1.0 or higher):

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

Add in the files from the repo (`https://github.com/the-rileyj/Jetpacks`) in `./Go-React-TypeScript` into the root of your project directory, then adjust the following variables in the files as described in the following sections; these adjustments are the minimal nessesary for you to get up and going, any other changes are up to you.

***Note*** - If you are testing building the environment locally after developing and already have all of the front-end dependencies, you can speed up the build time significantly by adding in a `COPY` directive which copies the `node_modules` directory into the `Front-End-Builder` build context (before the `RUN npm install` line) in the dockerfile that is in the root of the project after copying over the files in `./Go-React-TypeScript`. If you do this, you need to remove the `node_modules/` line from the `.dockerignore` file

#### docker-compose.yml

Under the `api-server`, `file-server`, and `networks` directive, the network is currently called "PROJECT-network", change all of them to whatever you want, so long as they are all the same.

#### dockerfile

At the very end of the file, the lines which would copy the certificate and secret file into the container are commented out. Remove the lines if you aren't going to need HTTPS, or change the source copy paths to where your certificates are located.

#### back-end/dockerfile

Under the first build context called `API-Builder`, the first `WORKDIR` directive is changes to `/go/src/github.com/the-rileyj/PROJECT/`, you will want to change `PROJECT` to the name of where your project resides in the `~/go/src/github.com/the-rileyj/` directory on your host machine or change the path to suit your needs.

Additionally, in the last build context of the dockerfile, the first non-commented line starting immediately after the `FROM scratch` line should have its copy source changed from `/go/src/github.com/the-rileyj/PROJECT/` to whatever you changed the `WORKDIR` destination to in the `API-Builder` build context.

#### Finishing Thoughts

...
