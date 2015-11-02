B24 и остальные сайты
===

####Правила разработки
 + В конце любой операции по изменению объекта нужно вызывать переиндексацию, а иммено метод reindex.
 + Удалять объекты можно только по одному (bulk нельзя) для переиндексации и вызова callbacks
 + При любом "удалении" объекта пользлвателем нужно просто выставлять флаг is_deleted в true
 + Разрабатывать на Python 3


####Сервера

 + EC2 под проект B24Online.com
 + EC2 под пользовательские сайты
 + 1 EC2 для Elasticsearch
 + Аналитика в NewRelic
 + 1 Elastic Cache Redis для очередей Celery
 + 1 Elastic Cache Redis для очередей Tornado + SockJS
 + RDS Postgres
 + Cloud Front + S3 для файлов (static.tppcenter.com)
 + DNS на Route 53

--

*Внимание!* Модели в b24project/appl/models.py и b24project/core/models.py - Deprecated (Кроме модели User)

Модели бывают могут быть индексируемыми и наследуют от IndexedModelMixin,
а также не удаляемыми(Вместо удаления деактивируем, наследуют от ActiveModelMixing

Используются спец. поля Postgres (HStore, Range).
