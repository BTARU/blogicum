# Проект Blogicum

## Описание

Блогикум это блог, где пользователи могут публиковать посты и оставлять комментарии к ним. Для каждого поста нужно указать категорию — например «путешествия», «кулинария», а также опционально локацию, с которой связан пост, например «Остров отчаянья» или «Караганда». 
Пользователь может перейти на страницу любой категории и увидеть все посты, которые к ней относятся.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/BTARU/blogicum.git
```

```
cd blogicum
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

## Автор

[Bulat Ayupov](https://github.com/BTARU)
