import nbformat as nbf
import os
import re

py_file = r'D:\File\file\Fauzan Lubada\PIJAK\Behaviour_Workspace\02_Notebooks\behaviour_training_script.py'
ipynb_file = r'D:\File\file\Fauzan Lubada\PIJAK\Behaviour_Workspace\02_Notebooks\Behaviour_Model_Training.ipynb'

with open(py_file, 'r', encoding='utf-8') as f:
    content = f.read()

chunks = re.split(r'(print\("\n=== TAHAP.*?|print\("=== TAHAP.*?)', content)

nb = nbf.v4.new_notebook()
cells = []

if chunks[0].strip():
    cells.append(nbf.v4.new_code_cell(chunks[0].strip()))

for i in range(1, len(chunks), 2):
    header = chunks[i]
    body = chunks[i+1]
    cell_content = (header + body).strip()
    if cell_content:
        cells.append(nbf.v4.new_code_cell(cell_content))

nb.cells = cells

with open(ipynb_file, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print('Berhasil membuat file .ipynb!')

# Menghapus file .py yang lama
if os.path.exists(py_file):
    os.remove(py_file)
    print(f'File {py_file} berhasil dihapus.')
