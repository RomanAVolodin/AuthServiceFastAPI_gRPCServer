#echo "extra variant of awaiting"
#echo "Waiting for postgres..."
#while ! nc -z $POSTGRES_ADMIN_HOST $POSTGRES_PORT; do
#  sleep 0.1
#done
#echo "PostgreSQL started"



python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000