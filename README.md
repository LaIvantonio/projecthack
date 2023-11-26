
<h4>Реализованная функциональность</h4>
<ul>
    <li>Сбор отчёта обо всех устройствах;</li>
    <li>Экспорт отчёта в форматы pdf xlsx html;</li>
    <li>Сбор информации о системе, серийном номере, установленных программ и их версиях;</li>
</ul> 
<h4>Особенность проекта в следующем:</h4>
<ul>
 <li>Кроссплатформенность;</li>
 <li>Возможность определить устройства которые были подключены раннее;</li> 
 </ul>
<h4>Основной стек технологий:</h4>
<ul>
    <li>Python</li>
	<li>FastAPI</li>
	<li>React</li>
	<li>Node.js</li>
  
 </ul>




СРЕДА ЗАПУСКА
------------
1) развертывание сервиса производится на debian-like linux (docker);
2) возможен запуск из среды разработки (visual studio code, pycharm);


УСТАНОВКА
------------
### Установка пакета 

Выполните 
~~~

git clone https://github.com/LaIvantonio/projecthack
cd full-signal/projecthack
sudo docker-compose up -d
pip install reportlab
pip install pandas openpyxl

...
~~~

ЗАПУСК ПРОЕКТА
------------
чтобы запустить бэкэнд нужно ввести в терминал 
uvicorn full-signal.projecthack.main:app --reload

адрес бэкэнда будет доступен на http://localhost:8000

чтобы запустить фронтэнд-часть нужно ввести в терминал 
cd full-signal/signal-frontend/
затем
npm start


РАЗРАБОТЧИКИ

<h4>Бородинов Иван backend https://t.me/la_ivantonio </h4>
<h4>Дробот Илья backend https://t.me/HellaChloe </h4>
<h4>Гуденко Антон frontend https://t.me/rickkich </h4>
<h4>Чёрный Ярослав дизайн https://t.me/ExSiteVicts </h4>
<h4>Паевский Олег https://t.me/Goodle20 </h4>


