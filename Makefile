lint:
	pre-commit run --all-files

update-isort:
	seed-isort-config

install-libs:
    poetry install

install-hooks:
    pre-commit install

run:
    scrapy crawl list
