import os
import pymysql.cursors
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASS', ''),
        database=os.getenv('DB_NAME', ''),
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4',
        autocommit=True,
    )
    return connection

def fetch_content():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(""" SELECT
            i18n.title,
            GROUP_CONCAT(DISTINCT ti18n.name SEPARATOR ', ') AS subjects,
            MAX(evi.date) AS data_expression,
            i18n.scope_and_content,
            i18n.extent_and_medium,
            s.slug
        FROM
            information_object io
        LEFT JOIN slug s ON s.object_id = io.id
        LEFT JOIN information_object_i18n i18n ON i18n.id = io.id
        LEFT JOIN object_term_relation otr ON otr.object_id = io.id
        LEFT JOIN term t ON t.id = otr.term_id
        LEFT JOIN term_i18n ti18n ON ti18n.id = t.id AND ti18n.culture = i18n.culture
        LEFT JOIN event ev ON ev.object_id = io.id
        LEFT JOIN event_i18n evi ON evi.id = ev.id AND evi.culture = i18n.culture
        WHERE
            i18n.title IS NOT NULL
            AND s.slug IS NOT NULL
            AND s.slug <> ''
        GROUP BY
            io.id, s.slug, io.description_identifier, i18n.title, i18n.scope_and_content, i18n.extent_and_medium;
        """)
        results = cursor.fetchall()
    conn.close()
    return results

def fetch_slugs():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT slug FROM slug;")
        results = cursor.fetchall()
    conn.close()
    return [row['slug'] for row in results]

def traditional_query(expressions: list[str], number_results: int):
    conn = get_connection()
    with conn.cursor() as cursor:
        all_results = []
        for expression in expressions:
            search = f'%{expression.split(" ")[0]}%' 
            query = """
            SELECT
                i18n.title,
                GROUP_CONCAT(DISTINCT ti18n.name SEPARATOR ', ') AS subjects,
                MAX(evi.date) AS data_expression,
                i18n.scope_and_content,
                i18n.extent_and_medium,
                i18n.alternate_title,
                i18n.edition,
                i18n.archival_history,
                i18n.acquisition,
                i18n.appraisal,
                s.slug
            FROM
                information_object io
            LEFT JOIN slug s ON s.object_id = io.id
            LEFT JOIN information_object_i18n i18n ON i18n.id = io.id
            LEFT JOIN object_term_relation otr ON otr.object_id = io.id
            LEFT JOIN term t ON t.id = otr.term_id
            LEFT JOIN term_i18n ti18n ON ti18n.id = t.id AND ti18n.culture = i18n.culture
            LEFT JOIN event ev ON ev.object_id = io.id
            LEFT JOIN event_i18n evi ON evi.id = ev.id AND evi.culture = i18n.culture
            WHERE
                i18n.title IS NOT NULL
                AND s.slug IS NOT NULL
                AND s.slug <> ''
            GROUP BY
                io.id, 
                s.slug, 
                io.description_identifier, 
                i18n.title, 
                i18n.scope_and_content, 
                i18n.extent_and_medium, 
                i18n.alternate_title,
                i18n.edition,
                i18n.archival_history,
                i18n.acquisition,
                i18n.appraisal
            HAVING
                s.slug LIKE %s OR
                i18n.title LIKE %s OR
                subjects LIKE %s OR
                data_expression LIKE %s OR
                i18n.scope_and_content LIKE %s OR
                i18n.extent_and_medium LIKE %s OR
                i18n.alternate_title LIKE %s OR
                i18n.edition LIKE %s OR
                i18n.archival_history LIKE %s OR
                i18n.acquisition LIKE %s OR
                i18n.appraisal LIKE %s 
            LIMIT
                %s
            """

            params = [search] * 11 + [number_results]
            cursor.execute(query, params)
            results = cursor.fetchall()
            all_results = list(all_results) + list(results)
    conn.close()
    return all_results