start_all:
	 docker compose up -d

create_admin:
	docker-compose exec auth-api python manage.py create-admin admin@mail.ru 123123 Ivan Ivanov
