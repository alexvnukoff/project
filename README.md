B24 и остальные сайты
===

####Правила разработки
 + Запомнить, что проект делали конченые мудаки. Всё что можно сделать проще и удобнее сделано, через заднее отверстие человеческой особи. В любом непонятном случае возвращаться к этому пункту.
 + В конце любой операции по изменению объекта (кроме удаления) нужно вызывать переиндексацию, а иммено метод [reindexItem](https://github.com/migirov/tpp/blob/master/core/models.py#L425)
 + Удалять объекты можно только по одному (bulk нельзя) для переиндексации и удаления связаных объектов
 + При любом "удалении" объекта пользлвателем нужно его просто деактивировать использую метов [activation](https://github.com/migirov/tpp/blob/master/core/models.py#L410) а также нужно переиндексировать объект
 + При любом выводе объекта нужно проверять активен ли он
 + Разрабатывать на Python 3

--

####Amazon и Dynect

 + EC2 на котором балансер HAproxy (ELB когда перейдем на Route 53)
 + N x EC2 на котор развёрнут Django
 + 1 Elastic Cache Redis для очередей Celery
 + 1 Elastic Cache Redis для очередей Tornado + SockJS
 + 1 Elastic Cache Memcached для кэширования и сессий
 + RDS Oracle + License
 + 1 EC2 для Elasticsearch
 + Cloud Front + S3 для файлов (static.tppcenter.com)
 + DNS у компании Dynect (Надо перейти на Route 53)

--

####Система изнутри

#####Модели 

Основные модели находяться в [core/models.py](https://github.com/migirov/tpp/blob/master/core/models.py)
и представляют собой модель хранения данных под названием [Entity–attribute–value](http://en.wikipedia.org/wiki/Entity%E2%80%93attribute%E2%80%93value_model)

Все данные(Название, описание, цена и т.д) о каком-либо объекте(Продукт, компания) находяться в таблице(Моделе) Value и которая в свою очередь связана с таблицей Attribute. Все объекты в системе расширяют модель(класс) Item и находяться в файле [appl/models.py](https://github.com/migirov/tpp/blob/master/appl/models.py). 

Также присутствуют модели Slot и Dictionary которые хранят список заданных значений для определенных атрибутов,
при выборе значения для атрибута значение **дублируется**(Копируется) в модель Value.

Связи объектов определяются в моделе Relationship, через эту модоль объект(Item) ссылается сам на себя как многое ко многим что позволяет создавать любые связи.

Все начальные значнния для моделей заданы в файле [/appl/management/__ init __.py](https://github.com/migirov/tpp/blob/master/appl/management/__init__.py) и подгружаются **ТОЛЬКО при ПЕРВОМ** syncdb 

#####Логика
При выводе всех детальных и списковых страниц( кроме главной и стены ) на B2B, используется [Class Based Views](https://github.com/migirov/tpp/blob/master/tppcenter/cbv.py), при выводе остальных страниц (формы и вкладки) используются обычные views которые в дальнейшем надо переделать также под CBV.

Cайт B2C также частично [перешёл](https://github.com/migirov/tpp/blob/master/centerpokupok/cbv.py) на CBV но его нужно доработать.

#####Формы
Т.к мы используем в базе модель EAV, мы не можем использовать стандартный функционал Django для форм, для этого мы определили для каждого атрибута его тип соостветсвующий типам полей Djnago и изменили немного процесс обработки форм, дополненый класс находится [ТУТ](https://github.com/migirov/tpp/blob/master/tppcenter/forms.py).

Поля нужные поля для каждой модели отмечаются в админке в ContentType каждой модели.


#####Темплейты
При верстке темплейтов использовались старые техники верстки, стоит подумать об обновлении вёрстки и использовании современных UI фреймворков(Angular.js, Bootstrap) и технологий(HTML 5).

Все кастомные теги находяться в папке [appl/templatetags/](https://github.com/migirov/tpp/tree/master/appl/templatetags).

######Статика 

Статика находиться в папке [/appl/Static](https://github.com/migirov/tpp/tree/master/appl/Static).
Статика не сжимается ни чем , а стоило бы.

#####Аналитика

Вся аналитика посещейний делается через google analytics используя их именованные метрики:

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
Мы используем "Entity–attribute–value" и храним все данные в Text field (Потом с этим надо что-то сделать) по этой причине мы не можем выводить отсортированные данные или фильтровать по ним( Можем но это капец ), для этого нам нужен второй слой БД.
Мы используем elasticsearch для хранения, фильтрации(включая поиск) и вывода данных, без этого слоя система ничего не выводит.

Система хранит мультиязычные данные,  для каждого языка мы используем разные индексы. 
Файл индекса находится [ТУТ](https://github.com/migirov/tpp/blob/master/appl/search_indexes.py) а мультиязычный backend [ТУТ](https://github.com/migirov/tpp/blob/master/tpp/backend.py)

#####Мультиязычность
Система хранит все значения в мультиязычном виде в моделе Value, также там хранятся значения которые не являются мультиязычными(Цены, пути, цифры) но хранятся в том же виде, для этого введён флаг "multilingual" в моделе Attribute если его значение для атрибута установлено в False(Default: Ture), при записи Value значение дублируется на все поля (Еще не использовался). 

#####Безопасность и иерархия связей

######Группы, Permissions и Флаги

Группы

 + Redactor - Модератор системы может добовлять ТВ новости и новости на главную.
 + TPP Creator - Модератор системы может создавать новые ТПП.
 + Staff - Дефолтные права работников.
 + Owner - Дефолтные права владельца.
 + Admin - Дефолтные права администратора.
 + Company Creator - Может создавать компании.

Permissions

У каждой модели есть 3 вида разрешений

 + Add (напр. add_company для модели Company) - Пользователь может добовлять объекты модели
 + Change  (напр. change_ business _proposal для модели BusinessProposal) - Пользователь может изменять объекты модели
 + Delete - Пользователь может удалять объекты модели
 

Флаги

у каждого пользователя есть 5 флагов

 + is_admin - не используется (только в методе is_staff в моделе User)
 + is_manager - Модератор нашей системы
 + is_active - Пользователь активен
 + is_superuser - Супер пользователь(Для Django). Нету в админке
 + is_commando - Тоже что и супер пользователь но не имеет прав в Django admin. Нету в админке

######Типы связей

Иерархия связей в системе немного запутана, есть 3 основных типа начальных точек

 + Dependence - Объект принадлежит другому объекту и зависит от него во всех отношениях (компания - продукт) могут иметь только одну связь к родителю.
 + Relation - Объект просто связан с другим объектом (продукт - категория) и могут иметь много связий.
 + Hierarchy - У объекта могут быть иерархические связи (категория - под-категория) могут иметь только одну связь к родителю.
 
######Организации \ компании

Также существуют разные типы организаций \ компаний и обьеденены они в одну модель Organization

 + Международная организация (Деловой центр СНГ) в которую входят несколько государств - Модель Tpp
 + Торгово промышленная палата (Принадлежит стране) - Модель Tpp
 + Компания принадлежит любой ТПП или международной оргинизации и стране - Модель Company
 + Компания не пренадлежит не к какой ТПП или оргинизации и привязана только к стране - Модель Company
 
Модель безопасности позволяет модераторам (работникам) ТПП управлять компаниями которые связаны с этой ТПП и их объектами,
Сотрудники компаний в свою очередь могут управлять только компанией и её объектами(Продукты, предложения и т.д).

######Новости

Раздел новостей разделен на 2 раздела, ТВ(Модель TppTV) и Новости(Модель News), ТВ новости могут добовлять и редактировать только участники группы  "Redactor" у которых есть Permissions для класса TppTv.

В раздел новостей могут добовлять новости все работники, но выводиться на главной будут только те новости которые были добавлены чланами группы "Redactor" остольные новости будут видны после применения фильтра.

--

####Используемые модули:

#####celery

Используется для добавления объектов в базу данных ассинхороно и их индексации.
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

#####psutil, pygeoip, python-dateutil, Pillow, pytz, python3-memcached

Просто нужно

#####South

Миграция, пока что не используем Django 1.7 да и не известно поддерживает ли он миграцию Oracle

**Не использовать версию 1.0 она не работает с Py3**

#####sockjs-tornado, tornado-redis

Serverside sockjs это замена websocket.io , работает вместе с Tornado и Redis для нотификаций в реальном времени как на Facebook управляется всё [ТУТ](https://github.com/migirov/tpp/blob/master/appl/realtime.py) и [ТУТ](https://github.com/migirov/tpp/blob/master/appl/management/commands/async_server.py)

#####Unidecode
Создаем SEO slug для ссылок конвертируюя UTF в URL символы в методе  [createItemSlug](https://github.com/migirov/tpp/blob/master/core/models.py#L697)


#####tinys3

Заливка изображений на Amazon S3, вся логика [ТУТ](https://github.com/migirov/tpp/blob/master/core/amazonMethods.py) .

Используется [форк](https://github.com/fatal10110/tinys3).

#####recaptcha-client
используется [форк](https://github.com/dave-gallagher/recaptcha-client-1.0.6-ssl-Python3) стоит подумать о [django-recaptcha](https://github.com/praekelt/django-recaptcha)

#####django-registration

Используется [форк](https://github.com/fatal10110/django-registration), стоит подумать о [django-registration-redux](https://github.com/macropin/django-registration)
