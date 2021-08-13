# Парсер объявлений n1.ru #

## Установка

1. Скачайте код и перейдите в папку проекта.
    ```bash
    git clone https://github.com/n1k0din/n1-parser.git
    ```  
    ```bash
    cd n1-parser
    ```
2. Установите вирт. окружение.
    ```bash
    python -m venv venv
    ```
3. Активируйте.
    ```bash
    venv\Scripts\activate.bat
    ```
    или
    ```bash
    source venv/bin/activate
    ```
4. Установите необходимые пакеты.
    ```bash
    pip install -r requirements.txt
    ```
5. Составьте список идентификаторов зданий в файле `buildings.txt` (например `12660030` это идентификатор: https://novosibirsk.n1.ru/building/1266030/)

6. Создайте таблицы в БД.
    ```sql
    CREATE TABLE public.building
    (
        building_id integer NOT NULL,
        search_url character varying(300) COLLATE pg_catalog."default",
        year smallint,
        address character varying(200) COLLATE pg_catalog."default",
        lon real,
        lat real,
        CONSTRAINT building_pkey PRIMARY KEY (building_id)
    );
    CREATE TABLE public.flat_record
    (
        flat_record_id integer NOT NULL DEFAULT nextval('flat_record_flat_record_id_seq'::regclass),
        flat_id integer NOT NULL,
        record_date timestamp without time zone NOT NULL,
        building integer NOT NULL,
        url character varying(300) COLLATE pg_catalog."default",
        area real,
        apartment_floor smallint,
        max_floor smallint,
        material character varying(50) COLLATE pg_catalog."default",
        price money,
        CONSTRAINT flat_record_pkey PRIMARY KEY (flat_record_id),
        CONSTRAINT flat_record_flat_id_record_date_key UNIQUE (flat_id, record_date),
        CONSTRAINT flat_record_building_fkey FOREIGN KEY (building)
            REFERENCES public.building (building_id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
            NOT VALID
    )
    ```

6. Запустите скрипт сбора данных.
    ```bash
    python3 buildings_parser.py
    ```
7. Запустите скрипт отправки данных в БД.
    ```bash
    python3 send_to_postgresql.py
    ```

### Цель проекта

Код написан в образовательных целях.
