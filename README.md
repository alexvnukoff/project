B24 и остальные сайты
===

####Система изнутри

#####Модели 

Основные модели находятся в [core/models.py](https://github.com/migirov/tpp/blob/master/core/models.py)
и представляют собой модель хранения данных под названием [Entity–attribute–value](http://en.wikipedia.org/wiki/Entity%E2%80%93attribute%E2%80%93value_model)

Все данные(Название описание) о каком либо обьекте(Продукт, компания) находятся в таблице(Моделе) Value 
а и привязана она к таблице Attribute. А все обьекты в системе расширяют модель(класс) Item и находлятся в файле [appl/models.py](https://github.com/migirov/tpp/blob/master/appl/models.py). 

Связи обьектов определяются в модели Relationship, через эту модоль обьект(Item) ссылается сам на себя как многое ко многим что позволяет создавать любые связи.

Все начальные значнния для моделей в файле [/appl/management/__init__.py](https://github.com/migirov/tpp/blob/master/appl/management/__init__.py) и подгружаются **ТОЛЬКО при ПЕРВОМ** suncdb 

#####Логика
При выводе всех детальныъ и списковых страниц( кроме главной и стены ) на B2B используетсе [Class Based Views](https://github.com/migirov/tpp/blob/master/tppcenter/cbv.py), при выводе остальных страгниц (формы и вкладки) используются обычные views которые в дальнейшем надо переделать табкже под CBV.

Cайт B2C также частично [перешел](https://github.com/migirov/tpp/blob/master/centerpokupok/cbv.py) на CBV но его нужно доработать.


#####Темплейты
При верстке темплейтов использовались старые техники, стоит подумать об обновлении вёрстки и спользование современых UI фреймворков.

Все кастомные теги ноходятся в папке [appl/templatetags/](https://github.com/migirov/tpp/tree/master/appl/templatetags).

######Статика 

Статика находится в папке [/appl/Static](https://github.com/migirov/tpp/tree/master/appl/Static).
Статика не сжимается ни чем , а стоило бы.

#####Аналитика

Вся аналитика посещейний делается через google analytics использую ихние именованные метрики:

    <script>
        {% getOwner item_id as owner %}

        {% if owner %}
            {% if owner.type == 'tpp' %}
                ga('set', 'dimension1', {{ owner.pk }});
            {% else %}
                ga('set', 'dimension3', {{ owner.pk }});
            {% endif %}
        {% endif %}
        ga('set', 'dimension2', 'product');
    </script>

Потом эти метрики выводятся с помощью AJAX через функцию [getAnalytic](https://github.com/migirov/tpp/blob/master/appl/func.py#L489)

#####Индексация
Мы используем "Entity–attribute–value" и храним все данные в Text field (Потом с этим надо чтото сделать) по этой причине мы не можем выводить отсортированные данные или фильтровать по ним( Можем но это капец ), для этого нам нужна второй слой БД.
Мы используем elasticsearch для хранения, фильтрации(включая поиск) и вывода данных, без этого слоя системы ничего не выводит.

Система хранит мультиязычные данные и для каждого языка мы используем разные индексы, файл индекса находится [ТУТ](https://github.com/migirov/tpp/blob/master/appl/search_indexes.py) а мультиязычный backend [ТУТ](https://github.com/migirov/tpp/blob/master/tpp/backend.py)


####Правила при разработке
 + В конце любой операции по изменению обьекта (кроме удаления) нужно бызывать переиндексацию, а иммено метод [reindexItem](https://github.com/migirov/tpp/blob/master/core/models.py#L425)
 + Удалять обьекты можно только по одному (bulk нельзя) для переиндексации
 + При любом "удалении" обьекта пользлвателем нужно его просто деактивировать использую метов [activation](https://github.com/migirov/tpp/blob/master/core/models.py#L410) а также нужно переиндексировать обьект
 + При любом выводе обьекта нужно проверять активен ли он
 
####Используемые модули:

#####celery

Используется для добавления обьектов в базу данных ассинхороно и их индексации.
[Таски](https://github.com/migirov/tpp/blob/master/core/tasks.py) и [Коннект](https://github.com/migirov/tpp/blob/master/tpp/celery.py)

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


#####elasticsearch

Драйвер на питоне для elasticsearch используется в django-haystack

#####google-api-python-client, rauth

[Форк python 3.x](https://github.com/fatal10110/GoogleApiPython3x) клиента на питоне для гугла скоро будет [официальный](https://github.com/google/google-api-python-client)

Выводим с его помощью [аналитику](https://github.com/migirov/tpp/tree/master/appl/analytic) вот [ТУТ](https://github.com/migirov/tpp/blob/master/tppcenter/Analytic/views.py)

#####lxml
Зашита (хоть какая) от XSS при выводе текста

#####psutil, pygeoipб python-dateutil, Pillow, pytz, recaptcha-client, django-registration

Просто нужно

#####South

Миграция, пока что не используем Django 1.7 да и не известно поддерживает ли он миграцию Oracle

#####sockjs-tornado, tornado-redis

Serverside sockjs это замена websocket.io , работает вместе с Tornado и Redis для нотификаций в реальном времени как на Facebook управляется всё [ТУТ](https://github.com/migirov/tpp/blob/master/appl/realtime.py) и [ТУТ](https://github.com/migirov/tpp/blob/master/appl/management/commands/async_server.py)

#####Unidecode
Создаем SEO slug для ссылок конвертируюя UTF в URL символы в методе  [createItemSlug](https://github.com/migirov/tpp/blob/master/core/models.py#L697)


#####tinys3

Заливка изображений на Amazon S3, вся логика [ТУТ](https://github.com/migirov/tpp/blob/master/core/amazonMethods.py) .

Используется форк












