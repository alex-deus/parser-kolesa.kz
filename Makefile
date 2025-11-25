lint:
	pre-commit run --all-files

update-isort:
	seed-isort-config

cp:
	rsync -avz \
 		--exclude 'tmp' \
 		--exclude '.env' \
 		--exclude '.idea' \
 		--exclude '.DS_Store' \
 		--exclude '.git' \
 		--exclude '*.pyc' \
 		--exclude '__pycache__' \
 		--exclude 'settings_local.py' \
 		--exclude 'bandit-report.html' \
 		. kolesa:/opt/scraper/

deploy:
	ssh k 'cd /opt/kolesa ; docker compose -f .docker/compose.yml up -d --build'
