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
        cursor.execute("""SELECT s.slug, io.description_identifier, i18n.*
            FROM information_object io
            LEFT JOIN slug s ON s.object_id = io.id
            LEFT JOIN information_object_i18n i18n ON i18n.id = io.id
            WHERE i18n.title IS NOT NULL
            AND s.slug IS NOT NULL
            AND s.slug <> '';""")
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