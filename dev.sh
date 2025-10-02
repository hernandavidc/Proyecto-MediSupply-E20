#!/bin/bash
# dev.sh - Script para desarrollo con Docker Compose

set -e

function build() {
    echo "🔨 Building services..."
    docker-compose build --no-cache
}

function up() {
    echo "🚀 Starting services..."
    docker-compose up -d
}

function down() {
    echo "🛑 Stopping services..."
    docker-compose down
}

function logs() {
    echo "📋 Showing logs..."
    docker-compose logs -f user-service
}

function restart() {
    echo "🔄 Restarting user service..."
    docker-compose restart user-service
}

function shell() {
    echo "🐚 Opening shell in user-service container..."
    docker-compose exec user-service bash
}

function db-shell() {
    echo "🗄️ Opening database shell..."
    docker-compose exec user-db psql -U user -d users_db
}

function status() {
    echo "📊 Services status:"
    docker-compose ps
}

function clean() {
    echo "🧹 Cleaning up..."
    docker-compose down -v
    docker system prune -f
}

case $1 in
    build)
        build
        ;;
    up)
        up
        ;;
    down)
        down
        ;;
    logs)
        logs
        ;;
    restart)
        restart
        ;;
    shell)
        shell
        ;;
    db-shell)
        db-shell
        ;;
    status)
        status
        ;;
    clean)
        clean
        ;;
    *)
        echo "Usage: $0 {build|up|down|logs|restart|shell|db-shell|status|clean}"
        echo ""
        echo "Commands:"
        echo "  build     - Build all services"
        echo "  up        - Start all services"
        echo "  down      - Stop all services"
        echo "  logs      - Show user-service logs"
        echo "  restart   - Restart user-service"
        echo "  shell     - Open shell in user-service container"
        echo "  db-shell  - Open database shell"
        echo "  status    - Show services status"
        echo "  clean     - Clean up containers and volumes"
        exit 1
        ;;
esac
