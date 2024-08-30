# pdf-reader
PDF-Reader convert your PDF files to html and raw txt, And contain Function for correcting your raw txt.
## How to use
- **Convert** PDF to HTML and RAW text : create 2 dirs 1.html_output 2.raw_txt_output
```bash
python scripts/convert_pdf_to_html.py /path/to/pdf
```

- **Correct** Text in RAW text : create 1 dir "corrected_txt_output"
```bash
python scripts/corrected_text.py
```

- **Convert** PDF to correct text : create 1 dir "corrected_txt_output"
```bash
python scripts/convert_pdf_to_text.py /path/to/pdf

## Setup
1.Clone the repository
```bash
git clone https://github.com/OpenThaiGPT/pdf-reader.git
cd pdf-reader
```
2.Create Virtual Environment
```bash
conda create --name pdf python=3.9 -y
conda activate pdf
```
3.Install Dependencies
```bash
pip install -e .
```
4.Install Java in Conda
```bash
conda install conda-forge::openjdk
```
5.Install PDFBox
```bash
wget https://dlcdn.apache.org/pdfbox/3.0.3/pdfbox-app-3.0.3.jar
```
