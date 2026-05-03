# Tase Personal Notifier Makefile

.PHONY: build up down restart sync logs shell db-shell clean backup

# Build the docker images
build:
	sg docker -c "docker compose build"

# Start the services in the background
up:
	sg docker -c "docker compose up -d"

# Stop the services
down:
	sg docker -c "docker compose down"

# Restart the services
restart: down up

# Run the data sync script (Fetches companies and exports SQL)
sync:
	sg docker -c "docker compose run --rm app"

# View logs for all services
logs:
	sg docker -c "docker compose logs -f"

# Open a shell in the app container
shell:
	sg docker -c "docker compose run --rm app bash"

# Open a psql shell in the database container
db-shell:
	sg docker -c "docker compose exec db psql -U postgres -d tase_notifier"

# Remove all containers, networks, and the database volume (CAUTION: Data will be lost if not backed up)
clean:
	sg docker -c "docker compose down -v"

# Manually trigger a backup (Runs the sync script)
backup: sync

# List all companies currently in the database
list-companies:
	sg docker -c "docker compose exec db psql -U postgres -d tase_notifier -c 'SELECT count(*) FROM company;'"
