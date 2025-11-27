# Description
Crawler of [kolesa.kz](https://kolesa.kz) which iterates over every region/brand combination, walks paginated listing pages, follows each vehicle card.

## Features
- Save to MongoDB
- Send to Rabbit queue
- Save images to Minio-S3
- Use proxies list if it necessary
- Use search params if it necessary

# Configure
- See [.env](examples/.env) and copy it to the project root when running inside Docker
- Copy the optional config files to project's root if needed:
  - [headers.json](examples/headers.json)
  - [params.json](examples/params.json)
  - [proxies.txt](examples/proxies.txt)

# Run
## Locally
1. Initialize a virtual environment
2. See [.env](examples/.env) and add to envs
3. Install dependencies: `make install-libs`
4. Run the crawler: `make run`

## Docker
1. Review the sample [.env](examples/.env) and copy it to the project's root
2. Run it:
```shell
docker compose -f .docker/compose.services.yml up -d --build
docker compose -f .docker/compose.yml up -d --build
```

# Develop
## Install
1. Initialize a virtual environment
2. Install dependencies: `make install-libs`
3. Install pre-commit hooks: `make install-hooks`

## Develop
- After installing libraries: `make update-isort`
- After each commit: `make lint` or plain `make`
