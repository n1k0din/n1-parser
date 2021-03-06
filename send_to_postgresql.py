import json
from datetime import datetime

import psycopg2


def buildings_to_pgsql(buildings, date):
    conn = psycopg2.connect('dbname=n1 user=postgres password=postgres')
    #
    cur = conn.cursor()

    for building_id, metadata in buildings.items():
        cur.execute(
            "INSERT INTO building (building_id, search_url, year, address, lon, lat)\
            VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT(building_id)\
            DO UPDATE SET (lat, lon) = (EXCLUDED.lat, EXCLUDED.lon)", (
                building_id,
                metadata['search_url'],
                metadata['year'],
                metadata['address'],
                metadata['lat'],
                metadata['lon'],
            )
        )

        flats = metadata['flats']
        for flat_id, flat_data in flats.items():
            sql = """INSERT INTO flat_record (
                    flat_id,
                    record_date,
                    building,
                    url,
                    area,
                    apartment_floor,
                    max_floor,
                    material,
                    price
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT(flat_id,record_date) DO UPDATE SET price = EXCLUDED.price
            """

            data = (
                flat_id,
                date,
                building_id,
                flat_data['url'],
                flat_data['area'],
                flat_data['apartment_floor'],
                flat_data['max_floor'],
                flat_data['material'],
                flat_data['price'],
            )

            cur.execute(sql, data)

    conn.commit()
    cur.close()
    conn.close()


def main():
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    filename = f'{today.strftime("%Y%m%d")}_buildings.json'

    with open(filename) as f:
        buildings = json.load(f)

    buildings_to_pgsql(buildings, today)


if __name__ == '__main__':
    main()
