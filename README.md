B24 и остальные сайты
===

####Правила разработки
 + Пишем всё в рамках PEP 0008, а что не соответсвует, по возможности корректируем.
 + В конце любой операции по изменению объекта нужно вызывать переиндексацию, а иммено метод reindex.
 + Удалять объекты можно только по одному (bulk нельзя) для переиндексации и вызова callbacks
 + При любом "удалении" объекта пользлвателем нужно просто выставлять флаг is_deleted в true
 + Разрабатывать на Python 3


####Сервера

 + EC2 под проект B24online.com (Docker)
 + 1 EC2 для Elasticsearch
 + Аналитика в NewRelic
 + 1 Elastic Cache Redis для очередей Celery
 + 1 Elastic Cache Redis для очередей Tornado + SockJS
 + RDS Postgres
 + Cloud Front + S3 для файлов (static.tppcenter.com)
 + DNS на Route 53

--


####Развёртывание Docker на локальном стенде

 + docker-compose build
 + docker-compose -f docker-compose.local.yml create
 + docker-compose start

--

Далее:

 + docker ps -a
 + docker start <id> # ID для db контейнера
 + docker exec -ti <id> psql -U postgres -d postgres -c 'create extension hstore;'
 + docker ps # Все контейнеры должны быть в статусе Up (подробнее команда 'docker-compose top')

Далее:

 + docker-compose -f docker-compose.local.yml run --rm web ./install.sh
 + docker-compose restart

--

Добавляем записи в /etc/hosts:

    # b24onlie

    127.0.0.1 b24online.dev
    127.0.0.1 en.b24online.dev
    127.0.0.1 ru.b24online.dev
    127.0.0.1 he.b24online.dev
    127.0.0.1 es.b24online.dev
    127.0.0.1 zh.b24online.dev
    127.0.0.1 ar.b24online.dev

    127.0.0.1 mysite.b24online.dev
    127.0.0.1 en.mysite.b24online.dev
    127.0.0.1 ru.mysite.b24online.dev
    127.0.0.1 he.mysite.b24online.dev
    127.0.0.1 es.mysite.b24online.dev
    127.0.0.1 zh.mysite.b24online.dev
    127.0.0.1 ar.mysite.b24online.dev

 Готово!

 --


 Выполнеие разовых команд:

 # CREATESUPERUSER
 + docker exec -ti <id> python3 manage.py createsuperuser

# COLLECTSTATIC
 + docker exec -ti <id> python3 manage.py collectstatic

# COMPILEMESSAGES
 + docker exec -ti <id> python3 manage.py compilemessages -f

 и так далее..

