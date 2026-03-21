# ═══════════════════════════════════════════════
#  Makefile — Comandos de desarrollo frecuentes
# ═══════════════════════════════════════════════

.PHONY: help install test lint docker-up docker-down docker-logs clean

# Mostrar ayuda por defecto
help:
	@echo ""
	@echo "  Comandos disponibles:"
	@echo ""
	@echo "  make install      Instalar dependencias en el virtualenv"
	@echo "  make test         Ejecutar tests con cobertura"
	@echo "  make lint         Ejecutar Pylint"
	@echo "  make docker-up    Levantar app + postgres con Docker Compose"
	@echo "  make docker-down  Detener y eliminar contenedores"
	@echo "  make docker-logs  Ver logs de la app en tiempo real"
	@echo "  make clean        Limpiar archivos temporales de Python"
	@echo ""

install:
	pip install --upgrade pip
	pip install -r requirements.txt

test:
	pytest --cov=app --cov-report=term-missing --cov-fail-under=70 -v

lint:
	pylint app/ wsgi.py --fail-under=7.0 --rcfile=.pylintrc

docker-up:
	docker compose up --build -d
	@echo ""
	@echo "  API disponible en: http://localhost:5000/api/health"
	@echo ""

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f app

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov coverage.xml .coverage 2>/dev/null || true
	@echo "Limpieza completada."
