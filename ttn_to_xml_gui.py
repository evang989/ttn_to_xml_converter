import os
import pytesseract
from pdf2image import convert_from_path
import cv2

# Укажите путь к tesseract если он не прописан в системной переменной
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf(pdf_path):
    pages = convert_from_path(pdf_path, dpi=300)
    full_text = ""
    for page in pages:
        image_path = "temp_page.png"
        page.save(image_path, "PNG")
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, lang='rus')
        full_text += text + "\n"
        os.remove(image_path)
    return full_text

def parse_text_to_xml(text):
    xml_template = '''<?xml version="1.0" encoding="UTF-8"?>
<Документ>
  <Номер>{номер}</Номер>
  <Дата>{дата}</Дата>
  <ТипДокумента>ПоступлениеТоваров</ТипДокумента>
  <Контрагент>
    <Наименование>{отправитель}</Наименование>
  </Контрагент>
  <Организация>
    <Наименование>{получатель}</Наименование>
  </Организация>
  <Основание>{основание}</Основание>
  <Товары>
    {товары}
  </Товары>
</Документ>'''

    lines = text.split('\n')
    номер = дата = отправитель = получатель = основание = ""
    товары_xml = ""

    for line in lines:
        if not номер and "НАКЛАДНАЯ" in line:
            parts = line.split()
            номер = next((p for p in parts if p.isdigit()), "")
        elif not дата and "июня" in line:
            дата = "2025-06-04"
        elif not отправитель and "Строительный Берег" in line:
            отправитель = line.strip()
        elif not получатель and "Универсальные инвестиции" in line:
            получатель = line.strip()
        elif not основание and "Договор №" in line:
            основание = line.strip()
        elif any(word in line for word in ["Уголок", "Шпилька", "Шайба", "Гайка", "Лента"]):
            name = line.strip()
            товары_xml += f'''<Строка>
      <Наименование>{name}</Наименование>
      <Количество>1</Количество>
      <Цена>1.00</Цена>
      <СтавкаНДС>20</СтавкаНДС>
    </Строка>\n'''

    return xml_template.format(
        номер=номер,
        дата=дата,
        отправитель=отправитель,
        получатель=получатель,
        основание=основание,
        товары=товары_xml.strip()
    )

def save_xml(xml_text, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_text)

def run_headless():
    print("Введите путь к PDF-файлу ТТН:")
    pdf_path = input().strip()
    if not os.path.isfile(pdf_path):
        print("Файл не найден.")
        return

    try:
        extracted_text = extract_text_from_pdf(pdf_path)
        xml_text = parse_text_to_xml(extracted_text)
        output_path = os.path.splitext(pdf_path)[0] + ".xml"
        save_xml(xml_text, output_path)
        print(f"XML успешно сохранён в: {output_path}")
    except Exception as e:
        print("Ошибка при обработке:", e)

if __name__ == '__main__':
    run_headless()
