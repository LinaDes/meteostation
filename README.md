# Проект **Метеостанция**
Опрашивает датчики, подключенные к Arduino, и сохраняет показания в базе данных SQLite.

## Структура проекта:
**weatherstation/weatherstation.ino**
Скетч для Arduino

**www/webserver.py**
Web-сервер для отладки

**www/cgi-bin/sensors.py**
cgi-скрипт для манипуляции со справочником датчиков в БД

**www/cgi-bin/ws.py**
cgi-скрипт для запроса данных из БД

**dbhelper.py**
Библиотера для работы с БД

**getweather.py**
Скрипт для получения данных от Arduino

**protocol.py**
Библиотека для опроса Arduino

**slip.py**
Библиотека для slip-преобразования

## Протокол обмена с прибором:
#### Формат сообщения:
адрес_прибора(1 байт) класс(1 байт) метод(1 байт) данные(N байт)

#### Формат ответа:
адрес_прибора(1 байт) данные(N байт)

адрес_прибора = 0

класс 0 (PING)
методы:
0   возвращает 0x55 0xAA 0x55 0xAA

класс 1 (INFO)
методы:
0   запрос количества датчиков температуры
возвращает: (unsigned char)количество
1   запрос показания и серийного номера с датчика темературы N
данные: (unsigned char)N
возвращает: (float)температура (8 bytes)sernum
2   запрос показания с датчика давления
возвращает: (int32_t)давление (char)sernum
3   запрос показания с датчика влажности
возвращает: (float)влажность (byte)sernum

#### API службы cgi:
http://host:port/ws.py
Возвращает html-страницу с последней записью из БД

http://host:port/ws.py?mtd=last
Возвращает последнюю запись в формате json-строки

http://host:port/ws.py?mtd=interval&min=XX&max=YY
Возвращает диапазон записей между датами min и max в формате json-строки

http://host:port/ws.py?mtd=all
Возвращает все записи в формате json-строки

http://host:port/ws.py?mtd=version
Возвращает версию API в формате json-строки

http://host:port/sensors.py
Возвращает html-страницу с перечнем датчиков



## License

* [Apache Version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html)