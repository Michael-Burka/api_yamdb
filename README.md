### YaMDb

## Описание

- Проект YaMDb представляет собой онлайн-платформу, собирающую отзывы пользователей на произведения.
- Произведения делятся на категории: Книги, Фильмы, Музыка. Произведению может быть также выбран жанр.

#### Функционал

- Управление пользователями.
- Получение списка всех категорий и жанров, добавление и удаление.
- Получение списка всех произведений. Получение, обновление и удаление конкретного произведения.
- Получение списка всех отзывов. Получение, обновление и удаление конкретного отзыва.  
- Получение списка всех комментариев. Получение, обновление и удаление конкретного комментария.
- Возможность получения подробной информации о своем аккаунте.
- Возможность импорта данных в из csv.

_Полная документация к API находится по эндпоинту /redoc_

## Стек:
-   Python
-   Django
-   Django REST Framework
-   REST API
-   Simple JWT

## Установка

Клонировать репозиторий и перейти в него в командной строке.
```
git clone https://github.com/EvgVol/api_yamdb.git
```

Обновить систему управления пакетами.

Установить зависимости из файла requirements.txt.
```
pip install -r requirements.txt
```

Выполнить миграции.
```
python manage.py migrate
```

При необходимости импортировать данные из csv файлов.
```
python manage.py csv_import
```

Запустить проект.
```
python manage.py runserver
```

Подробная документация доступна по эндпоинту /redoc/

### Примеры работы с API для авторизованных пользователей

Регистрация пользователя:  
``` POST /api/v1/auth/signup/ ```  
Получение данных своей учетной записи:  
``` GET /api/v1/users/me/ ```  
Добавление новой категории:  
``` POST /api/v1/categories/ ```  
Удаление жанра:  
``` DELETE /api/v1/genres/{slug} ```  
Частичное обновление информации о произведении:  
``` PATCH /api/v1/titles/{titles_id} ```  
Получение списка всех отзывов:  
``` GET /api/v1/titles/{title_id}/reviews/ ```   
Добавление комментария к отзыву:  
``` POST /api/v1/titles/{title_id}/reviews/{review_id}/comments/ ```  
