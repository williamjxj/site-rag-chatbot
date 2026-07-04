PROJECT_NAME := site-chatbot-rag
BACKEND_DIR := backend
FRONTEND_DIR := frontend

.PHONY: help backend frontend backend-db-up backend-db-down install test clean

help:
	@printf "%s\n" "$(PROJECT_NAME) commands:"
	@printf "%s\n" "  make backend        Start the backend on port 8088"
	@printf "%s\n" "  make frontend       Start the frontend on port 8080"
	@printf "%s\n" "  make backend-db-up  Start the Postgres container"
	@printf "%s\n" "  make backend-db-down Stop the Postgres container"
	@printf "%s\n" "  make install        Install backend and frontend dependencies"
	@printf "%s\n" "  make test           Run backend and frontend tests"
	@printf "%s\n" "  make clean          Remove frontend node_modules and backend venv"

backend:
	cd $(BACKEND_DIR) && ./scripts/start-server.sh

frontend:
	cd $(FRONTEND_DIR) && pnpm dev

backend-db-up:
	cd $(BACKEND_DIR) && docker compose up -d

backend-db-down:
	cd $(BACKEND_DIR) && docker compose down

install:
	cd $(BACKEND_DIR) && pip install -e .[dev]
	cd $(FRONTEND_DIR) && pnpm install

test:
	cd $(BACKEND_DIR) && pytest
	cd $(FRONTEND_DIR) && pnpm test

clean:
	rm -rf $(FRONTEND_DIR)/node_modules $(BACKEND_DIR)/venv