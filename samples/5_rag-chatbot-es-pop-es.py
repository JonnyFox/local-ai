import fitz, os, re
from elasticsearch import Elasticsearch

es = Elasticsearch(
    "https://es01:9200",
    ca_certs="/project/http_ca.crt",
    basic_auth=('elastic', 'gy7GcoMzE9YGeAecXS7T'),
)


def extract_text_from_pdf(pdf_path):
    text = ''
    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            cleaned_text = re.sub(r'\n+', ' ', page.get_text())
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

            text += cleaned_text.strip()
    return text


def index_paragraphs_in_elasticsearch(pdf_path, language):
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page_paragraphs = []
        page = doc.load_page(page_num)
        blocks = page.get_text('dict')['blocks']

        last_header_paragraph = None

        for b in blocks:

            if b['type'] == 0:  # 0 = text, 1 = image, 2 = vector, 3 = ruler, 4 = ellipse, 5 = text box
                paragraph = ''
                is_header = False
                for l in b['lines']:
                    for s in l['spans']:
                        is_header = s['font'].find('Bold') != -1
                        paragraph += s['text']
                cleaned_text = re.sub(r'\n+', ' ', paragraph)
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

                item = {
                    'pdf_path': pdf_path,
                    'page_number': page_num + 1,
                    'paragraph_number': b['number'],
                    'content': cleaned_text.strip(),
                    'language': language,
                    'is_header': is_header,
                    'paragraph_header_index': f'{last_header_paragraph['page_number']}_{last_header_paragraph['paragraph_number']}' if last_header_paragraph else None,
                }

                if is_header:
                    last_header_paragraph = item
                page_paragraphs.append(item)

        for p in page_paragraphs:
            res = es.index(index='manuals2', body=p)
            print(f"Indexed paragraph {p['paragraph_number']} on page {p['page_number']}: {res}")

    doc.close()


def clean_text(text):
    # Replace multiple spaces with a single space
    cleaned_text = ' '.join(text.split())
    return cleaned_text


def index_document(language, text):
    doc = {'language': language, 'content': text}
    res = es.index(index="manuals2", body=doc)
    print(res)


# I manuali sono nella cartella data con questo nome manual_en.pdf, manual_it.pdf, manual_es.pdf, ecc
dir_path = f'./data/'
for filename in os.listdir(dir_path):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(dir_path, filename)
        lang = filename.split('_')[1].split('.')[0]
        index_paragraphs_in_elasticsearch(pdf_path, lang)
        # text = extract_text_from_pdf(pdf_path)
        # index_document(lang, text)
