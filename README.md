# Andrey-Daniil-45
Коллективная разработка приложений

### main

Основной функционал расположен в файле main.py.  
Он запускает процесс преобразования XDB -> RAM -> DBD -> RAM - > XDB2  

Файл test1.py выполняет преобразование XDB -> RAM -> DBD с выводом в консоль ram-представления.  
Файл test2.py выполняет преобразование DBD -> RAM - > XDB2 с выводом в консоль ram-представления.  

В папке modules расположены модули преобразования:  
xmlParser - модуль преобразования xml таблиц из xdb файлов в ram-представление.  
xmlMaker - модуль преобразования ram представления в xml таблицы в xdb файл.  
ram_dbd - модуль преобразования ram представления в sql таблицы в db файл.  
dbd_ram - модуль преобразования sql таблиц из db файла в ram представление.  

Файлы исходных .xdb файлов (tasks.xdb и prjadm.xdb) расположены в папке materials.

Модуль sql_requests содержит sql-запросы и расположен в папке modules.  

### Модуль minidom

Стандартная библиотека языка Python содержит готовый XML анализатор (парсер) Доступ к нему осуществляется через пакет xml: import xml.dom.minidom. В проекте он импортируется из файла order_plugin, который также осуществялет заполнение xml-файла в нужном порядке.

### Модуль argparse

Для обработки параметров командной строки использовался модуль argparse:

https://docs.python.org/2/howto/argparse.html

Модуль может автоматически генерировать сообщения справки или ошибки, когда пользователи вводят неверные опции программы в консоль.
