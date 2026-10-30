import csv, tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "05_ferramentas"))
from verificar_dados import SCHEMA, run, furigana_ok

def write_dataset(root):
    for name, header in SCHEMA.items():
        with (root/name).open("w",encoding="utf-8",newline="") as f:
            csv.writer(f,lineterminator="\n").writerow(header)
    def add(name,row):
        with (root/name).open("a",encoding="utf-8",newline="") as f:
            csv.writer(f,lineterminator="\n").writerow(row)
    add("frases.csv",["J01-01","1","","{食|た}べる","","","CASUAL","comer","forma casual","1","1","1","","","","ATIVA",""])
    add("exercicios.csv",["X01-R1","1","","RECONHECER","MULTIPLA_ESCOLHA","Escolha a forma.","J01-01","Capítulo 1","EXATA","1","","ATIVA",""])
    add("respostas.csv",["X01-R1-a","X01-R1","A","食べる","CORRETA","Forma correta.","1","","ATIVA",""])
    return add

class PDFBookTests(unittest.TestCase):
    def test_furigana_valid(self):
        self.assertTrue(furigana_ok("{昨日|きのう}"))
    def test_furigana_invalid(self):
        self.assertFalse(furigana_ok("{昨日}"))
    def test_valid_pdf_only_dataset(self):
        with tempfile.TemporaryDirectory() as d:
            add=write_dataset(Path(d))
            errors,warnings=run(Path(d))
            self.assertEqual(errors,[])
    def test_missing_reference(self):
        with tempfile.TemporaryDirectory() as d:
            add=write_dataset(Path(d))
            add("exercicios.csv",["X01-R2","1","","RECONHECER","MULTIPLA_ESCOLHA","Escolha.","J01-99","Capítulo 1","EXATA","1","","ATIVA",""])
            errors,_=run(Path(d))
            self.assertTrue(any("REFERENCIA_INEXISTENTE" in x for x in errors))
    def test_active_exercise_requires_correct_answer(self):
        with tempfile.TemporaryDirectory() as d:
            add=write_dataset(Path(d))
            p=Path(d)/"respostas.csv"
            p.write_bytes((",".join(SCHEMA["respostas.csv"])+"\n").encode("utf-8"))
            errors,_=run(Path(d))
            self.assertTrue(any("SEM_RESPOSTA_CORRETA" in x for x in errors))
    def test_duplicate_phrase_id(self):
        with tempfile.TemporaryDirectory() as d:
            add=write_dataset(Path(d))
            add("frases.csv",["J01-01","1","","食べる","","","CASUAL","comer","", "1","1","1","","","","ATIVA",""])
            errors,_=run(Path(d))
            self.assertTrue(any("ID_DUPLICADO" in x for x in errors))
    def test_no_audio_or_interactive_tables(self):
        self.assertEqual(set(SCHEMA),{"frases.csv","exercicios.csv","respostas.csv","validacoes.csv"})
if __name__=="__main__": unittest.main()
