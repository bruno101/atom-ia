# Módulo de conexão com banco de dados MySQL
# Fornece funções para acessar dados do sistema AtoM
import os
import pymysql.cursors
from dotenv import load_dotenv

# Carrega variáveis de ambiente para configuração do banco
load_dotenv()

def get_connection():
    """Cria conexão com o banco de dados MySQL
    
    Returns:
        pymysql.Connection: Conexão configurada com o banco
    """
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),      # Host do banco
        user=os.getenv('DB_USER', 'root'),           # Usuário do banco
        password=os.getenv('DB_PASS', ''),           # Senha do banco
        database=os.getenv('DB_NAME', ''),           # Nome do banco
        cursorclass=pymysql.cursors.DictCursor,      # Retorna resultados como dicionário
        charset='utf8mb4',                           # Charset para suporte completo UTF-8
        autocommit=True,                             # Commit automático das transações
    )
    return connection

def fetch_content():
    """Busca todo o conteúdo dos objetos informacionais do AtoM
    
    Returns:
        list: Lista de dicionários com dados dos documentos
    """
    conn = get_connection()
    with conn.cursor() as cursor:
        # Query complexa que junta informações de várias tabelas do AtoM
        cursor.execute(""" SELECT
            i18n.title,                                                    -- Título do documento
            GROUP_CONCAT(DISTINCT ti18n.name SEPARATOR ', ') AS subjects, -- Assuntos/termos
            MAX(evi.date) AS data_expression,                             -- Data mais recente
            i18n.scope_and_content,                                       -- Âmbito e conteúdo
            i18n.extent_and_medium,                                       -- Dimensão e suporte
            s.slug                                                        -- Identificador único
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
            i18n.title IS NOT NULL    -- Apenas documentos com título
            AND s.slug IS NOT NULL    -- Apenas documentos com slug
            AND s.slug <> ''          -- Slug não pode ser vazio
        GROUP BY
            io.id, s.slug, io.description_identifier, i18n.title, i18n.scope_and_content, i18n.extent_and_medium;
        """)
        results = cursor.fetchall()
    conn.close()
    return results

def fetch_slugs():
    """Busca todos os slugs válidos do sistema
    
    Returns:
        list: Lista de strings com todos os slugs
    """
    conn = get_connection()
    with conn.cursor() as cursor:
        # Busca todos os slugs da tabela slug
        cursor.execute("SELECT slug FROM slug;")
        results = cursor.fetchall()
    conn.close()
    # Extrai apenas os valores dos slugs da lista de dicionários
    return [row['slug'] for row in results]

def traditional_query(expressions: list[str], number_results: int):
    """Executa busca tradicional (lexical) no banco de dados
    
    Args:
        expressions (list[str]): Lista de expressões para buscar
        number_results (int): Número máximo de resultados por expressão
        
    Returns:
        list: Lista combinada de resultados de todas as expressões
    """
    conn = get_connection()
    with conn.cursor() as cursor:
        all_results = []  # Lista para acumular todos os resultados
        
        # Executa uma query para cada expressão
        for expression in expressions:
            # Prepara o padrão de busca (usa apenas a primeira palavra)
            search = f'%{expression.split(" ")[0]}%' 
            
            # Query que busca em todos os campos relevantes do documento
            query = """
            SELECT
                i18n.title,                                                    -- Título principal
                GROUP_CONCAT(DISTINCT ti18n.name SEPARATOR ', ') AS subjects, -- Assuntos
                MAX(evi.date) AS data_expression,                             -- Data
                i18n.scope_and_content,                                       -- Âmbito e conteúdo
                i18n.extent_and_medium,                                       -- Dimensão e suporte
                i18n.alternate_title,                                         -- Título alternativo
                i18n.edition,                                                 -- Edição
                i18n.archival_history,                                        -- Histórico arquivístico
                i18n.acquisition,                                             -- Aquisição
                i18n.appraisal,                                               -- Avaliação
                s.slug                                                        -- Identificador
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
                -- Busca o padrão em todos os campos relevantes
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

            # Parâmetros: padrão de busca repetido 11 vezes + limite de resultados
            params = [search] * 11 + [number_results]
            cursor.execute(query, params)
            results = cursor.fetchall()
            # Adiciona os resultados à lista geral
            all_results = list(all_results) + list(results)
    conn.close()
    return all_results