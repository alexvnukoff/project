B24 и остальные сайты
===

#Правила разработки
 + Пишем всё в рамках PEP 0008, а что не соответсвует, по возможности корректируем.
 + В конце любой операции по изменению объекта нужно вызывать переиндексацию, а иммено метод reindex.
 + Удалять объекты можно только по одному (bulk нельзя) для переиндексации и вызова callbacks
 + При любом "удалении" объекта пользлвателем нужно просто выставлять флаг is_deleted в true
 + Разрабатывать на Python 3


#Сервера

 + EC2 под проект B24online.com (Docker)
 + 1 EC2 для Elasticsearch
 + Аналитика в NewRelic
 + 1 Elastic Cache Redis для очередей Celery
 + 1 Elastic Cache Redis для очередей Tornado + SockJS
 + RDS Postgres
 + Cloud Front + S3 для файлов (static.tppcenter.com)
 + DNS на Route 53

--


#Развёртывание Docker на локальном стенде

 + cp ./b24project/local_settings.py.sample ./b24project/local_settings.py
 + docker-compose -f docker-compose.local.yml up -d
 + ./postinstall.sh CONTAINER_ID

--

Добавляем записи в /etc/hosts:

    # b24onlie

    127.0.0.1 nexus.dev
    127.0.0.1 en.nexus.dev
    127.0.0.1 ru.nexus.dev
    127.0.0.1 he.nexus.dev
    127.0.0.1 es.nexus.dev
    127.0.0.1 zh.nexus.dev
    127.0.0.1 ar.nexus.dev

    127.0.0.1 mysite.nexus.dev
    127.0.0.1 en.mysite.nexus.dev
    127.0.0.1 ru.mysite.nexus.dev
    127.0.0.1 he.mysite.nexus.dev
    127.0.0.1 es.mysite.nexus.dev
    127.0.0.1 zh.mysite.nexus.dev
    127.0.0.1 ar.mysite.nexus.dev

    127.0.0.1 ruorg.nexus.dev
    127.0.0.1 en.ruorg.nexus.dev
    127.0.0.1 ru.ruorg.nexus.dev
    127.0.0.1 he.ruorg.nexus.dev
    127.0.0.1 es.ruorg.nexus.dev
    127.0.0.1 zh.ruorg.nexus.dev
    127.0.0.1 ar.ruorg.nexus.dev

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

