import json
import PyPDF2
from datetime import datetime
from io import BytesIO
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def show_progress(current, total, step):
    """Exibe barra de progresso no terminal"""
    percentage = round((current / total) * 100)
    bar = '█' * (percentage // 5) + '░' * (20 - percentage // 5)
    print(f"\r[{bar}] {percentage}% - {step}", end='', flush=True)

def extract_text_from_pdf(pdf_file):
    """Extrai texto do arquivo PDF"""
    show_progress(1, 5, 'Extraindo texto do PDF...')
    
    pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file))
    text = ""
    
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    
    if len(text.strip()) < 50:
        raise ValueError("O arquivo PDF contém apenas imagens. Por favor, anexe um arquivo que contenha texto.")
    
    return text

def analyze_pdf_with_llm(text):
    """Analisa o texto do PDF usando LLM para extrair metadados"""
    show_progress(2, 5, 'Analisando conteúdo com IA...')
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        prompt = f"""
        Analise o seguinte texto de um documento PDF e extraia as informações solicitadas:

        TEXTO DO DOCUMENTO:
        {text[:4000]}  # Limita para evitar excesso de tokens

        Extraia e formate as seguintes informações em JSON:
        1. Assunto Principal: Área principal
        2. Termos-Chave: 3-5 termos essenciais para a busca de arquivos relacionados
        3. Resumo: Resumo detalhado com introdução sobre os assuntos tratados (5-7 frases)

        Responda APENAS com um JSON válido no seguinte formato:
        {{
            "assunto_principal": "área de estudo",
            "termos_chave": ["termo1", "termo2", "termo3"],
            "resumo": "Este documento aborda [assunto principal] e apresenta [principais tópicos]."
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Extrai JSON da resposta
        json_text = response.text.strip()
        if json_text.startswith('```json'):
            json_text = json_text[7:-3]
        elif json_text.startswith('```'):
            json_text = json_text[3:-3]
        
        return json.loads(json_text)
        
    except Exception as e:
        print(f"Erro na análise LLM: {e}")
        # Fallback se não conseguir usar LLM
        lines = text.split('\n')[:20]
        titulo = next((line.strip() for line in lines if len(line.strip()) > 10 and len(line.strip()) < 100), "Documento PDF")
        
        words = text.lower().split()
        word_count = {}
        for word in words:
            if len(word) > 4:
                word_count[word] = word_count.get(word, 0) + 1
        
        top_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:5]
        termos_chave = [word for word, count in top_words]
        
        return {
            "assunto_principal": titulo,
            "termos_chave": termos_chave,
            "resumo": f"Este documento aborda {titulo} e apresenta informações relevantes sobre o tema. O trabalho explora conceitos fundamentais e discute aspectos importantes da área. Os autores analisam diferentes perspectivas e propõem contribuições para o campo de estudo. O documento é relevante para pesquisadores e profissionais interessados no assunto. Oferece insights valiosos sobre {', '.join(termos_chave[:3])} e temas relacionados."
        }

def create_search_json(metadata):
    """Cria JSON estruturado para busca"""
    show_progress(3, 5, 'Gerando JSON de busca...')
    
    current_date = datetime.now().strftime("%Y%m%d")
    
    # Cria input de busca baseado nos metadados
    input_busca = f"Procure informações sobre {metadata['assunto_principal']} relacionadas aos termos {', '.join(metadata['termos_chave'])}."
    
    search_json = {
        "query_id": f"AUTO_AUDIT_QUERY-{current_date}",
        "resumo": metadata["resumo"],
        "input_busca": input_busca,
        "assunto_principal": metadata["assunto_principal"],
        "termos_chave": metadata["termos_chave"]
    }
    
    return search_json

def processPDFBackend(pdf_file):
    """Processa arquivo PDF e retorna JSON estruturado para busca"""
    print("\n🔄 Iniciando processamento do PDF no backend...")
    
    try:
        # Etapa 1: Extrair texto
        text = extract_text_from_pdf(pdf_file)
        
        # Etapa 2: Analisar com LLM
        metadata = analyze_pdf_with_llm(text)
        
        # Etapa 3: Criar JSON de busca
        search_json = create_search_json(metadata)
        
        show_progress(4, 5, 'Finalizando processamento...')
        
        # Log do JSON gerado
        print(f"\n\n=== JSON GERADO ===")
        print(json.dumps(search_json, ensure_ascii=False, indent=2))
        print("==================\n")
        
        show_progress(5, 5, 'Processamento concluído!')
        print("\n✅ PDF processado com sucesso\n")
        
        return search_json
        
    except Exception as error:
        print(f"\n❌ Erro ao processar PDF: {str(error)}")
        # Retorna JSON básico em caso de erro
        return {
            "query_id": f"ERROR_QUERY-{datetime.now().strftime('%Y%m%d')}",
            "resumo": "Erro no processamento do PDF",
            "input_busca": "Pesquise sobre o documento anexado",
            "assunto_principal": "Documento PDF",
            "termos_chave": ["documento", "pdf", "pesquisa"]
        }