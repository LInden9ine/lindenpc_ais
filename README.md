  1) Вообшем, API реализовано, авторизация проходит по токену, что было успешно протестировано с помощью POSTMAN, где и получается токен.
Авторизация происходит на сервере через API и даже защищено хешированием пароля, реализовано слегка топорно, но минимальная защита данных есть. 
  2) Интерфейс варится, уже несколько вариантов было, но оказались неэффективны.
  3) БД ссоздана, заполнена сущностями с полями, но пока не заполнена записями. БД спокойно открывается в SQLBrowser и так же гибко редактируется.
Там же создавался и редактировался admin, как первая учетная запись.
  4) Приступаю к реализации самого приложения! ╰(▔∀▔)╯ 
Была до ума доделана БД, все сделано для конечного комфорта пользователя в приложении.
  5) Реализованы главное окно с пунктом "Управление комплектующими" и окно авторизации с полями для ввода.
В процессе пришлось менять реализацию интерфейса с PyQt6 на Tkinter, потому что первый 'глубоко под капотом' с чем-то конфликтует, потому, спустя 4 часа был казнен 
и заменен ранее упомянутым Tkinter-ом.
  6) Долго не мог пофиксить отсутствие отображения комплектующих во вкладке "Управление комплектующими", но в итоге все отображается, для чего были заранее
созданы 3 пробные записи. Теперь комплектующие видны!
  7) Добавил кнопки "Добавить запись", "Редактировать запись","Удалить запись", к ним же реализовал функционал-форму с вводными полями для добавления/редактирования 
записей в сущности Component, оно же "Комплектующие". По сути, базовый функционал готов
  8) В меню управления комплектующими все записи, при взаимодействии с ними, будь это это добавление или удаление, дублировались, по типу: 
  Запись 1
  Запись 2
  Запись 3
Какое либо из трех действий (допустим добавление записи 4)*
  Запись 1 --I
  Запись 2   I
  Запись 3 --I
  Запись 1>>>>>^
  Запись 2     ^
  Запись 3     ^
  Запись 4>>>>>^
Эта проблема была связана с тем, что функция load_components добавляла записи в Treeview, не очищая его предварительно. Прикрутил очистку Treeview перед каждой загрузкой данных.