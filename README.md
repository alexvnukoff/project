B24 и остальные сайты
===


####Используемые модули:

#####celery

Используется для добавления обьектов в базу данных ассинхороно и их индексации.
[Таски тут](https://github.com/migirov/tpp/blob/master/core/tasks.py)

#####django-celery
Нужно включить celerycam в supervisorctl для просмотра лога тасков 

#####django-celery-with-redis
Для очередей задач в Redis

#####cx-Oracle

Драйвер питона к базе Oracle 

В случае если надо будет использовать другую базу, меняйте запросы [в менеджере иерархий](https://github.com/migirov/tpp/blob/master/core/hierarchy.py) и [в методе получения самых продаваемых товаров getTopSales класса Product](https://github.com/migirov/tpp/blob/master/appl/models.py#L418) (Желаиельно медот переделать)
а также в функциях [sortByAttr](https://github.com/migirov/tpp/blob/master/appl/func.py#L142) и [sortQuerySetByAttr](https://github.com/migirov/tpp/blob/master/appl/func.py#L168) которые желательно удалить

#####django-debug-toolbar
Смотрим полезные логи на странице настраивается в [settings.py](https://github.com/migirov/tpp/blob/master/tpp/settings.py) , [в фукции show_toolbar](https://github.com/migirov/tpp/blob/master/appl/func.py#L1349) и в [urls.py](https://github.com/migirov/tpp/blob/master/tppcenter/urls.py#L145)

#####django-haystack

Используется [форк](https://github.com/fatal10110/django-haystack) с переделоным [backend'om для elasticsearch 1.x](https://github.com/fatal10110/django-haystack/blob/master/haystack/backends/elasticsearch_backend.py). Когда будет готов стабильный релиз [elasticsearch-dsl-py](https://github.com/elasticsearch/elasticsearch-dsl-py) стоит использовать его для более вменяемого использования elasticsearch и вообще переделать механизм поиска и вывода данных, т.к на данный момент иммено он отвечает за вывод любых данных (и даже больше)


#####django-loginas
Логинимся как другой пользователь, единственная настройка находится в [urls.py](https://github.com/migirov/tpp/blob/master/tppcenter/urls.py#L57) используется в админке Django и нашей кастомной

#####django-modeltranslation 
Используем для многоязычности в моделях [Values](https://github.com/migirov/tpp/blob/master/core/models.py#L923) и [Slots](https://github.com/migirov/tpp/blob/master/core/models.py#L221)
и настраевается в файле [tanslation.py](https://github.com/migirov/tpp/blob/master/core/translation.py)


#####django-registration
Регистрация , восстановление пароля и отправка имейлов

#####elasticsearch

Драйвер на питоне для elasticsearch используется в django-haystack

#####google-api-python-client

[Форк python 3.x](https://github.com/fatal10110/GoogleApiPython3x) клиента на питоне для гугла скоро будет [официальный](https://github.com/google/google-api-python-client)

Выводим с его помощью [аналитику](https://github.com/migirov/tpp/tree/master/appl/analytic) вот [ТУТ]()

#####lxml
Зашита (хоть какая) от XSS при выводе текста

#####psutil, pygeoipб python-dateutil, Pillow

Просто нужно

#####python-dateutil











