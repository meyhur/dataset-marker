# Используйте виртуальное окружение с развернутым проектом Django
***

## Создайте виртуальное окружение

```console
virtualenv venv -p python3
source venv/bin/activate
```

## Склонируйте проект

```console
git clone https://github.com/meyhur/dataset-marker.git
cd dataset_gen
pip install -r requirements.txt
```

## Сделайте миграции

```console
python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser

*Username (leave blank to use 'yourname'):*
*Email address:*
*Password:*
*Password (again):*
```

# Наполнение БД не размеченным датасетом

Образец демоданных неразмечееного датасета файл data/phrase_data.csv

Для наполнения БД требуется в файле load_data.py в функции main исправить имя файла filedata на имя вашего файла

Файл entities.csv содержит перечень базовых сущностей

```console
python load_data.py
```

# Запуск сервера

В корне проекта

```console
python manage.py runserver
```