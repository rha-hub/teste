"""Testes do verificador (05_ferramentas/verificar_dados.py) com dados FICTÍCIOS isolados.

Cada teste parte de um estado aprovado (todas as validações humanas vigentes, código 0),
muda UMA coisa e confere o efeito exato: o que deve ficar desatualizado, o que NÃO deve
ficar, e se a aprovação do exercício cai ou se mantém.

Executar:  python3 -m unittest discover -s colaboracao-ia/02_testes -v
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "05_ferramentas"))
import dados_ficticios as df  # noqa: E402
import verificar_dados as vd  # noqa: E402

TODAS_DIMS = [("J99-01", "LINGUISTICA"), ("J99-01", "TRADUCAO"), ("J99-01", "PEDAGOGICA"),
              ("J99-02", "LINGUISTICA"), ("J99-02", "TRADUCAO"), ("J99-02", "PEDAGOGICA"),
              ("A99-01", "ROTEIRO"), ("A99-01_v100_r1_t1", "GRAVACAO"), ("A99-01_v080_r1_t1", "GRAVACAO"),
              ("X99-E1", "PEDAGOGICA"), ("X99-E1", "ESCUTA"), ("X99-E2", "PEDAGOGICA"), ("X99-E2", "ESCUTA"),
              ("X99-M1", "PEDAGOGICA")]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="verif_"))
        self.dados, self.audio = df.gerar_aprovado(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # utilidades -------------------------------------------------------------
    def verificar(self, com_audio=True):
        return vd.Verificador(self.dados, self.audio if com_audio else None).executar()

    def mudar(self, tabela, chave, valor_chave, **novos):
        linhas = df.ler(self.dados, tabela)
        alvo = [l for l in linhas if l[chave] == valor_chave]
        self.assertEqual(len(alvo), 1, f"{tabela} {valor_chave}")
        alvo[0].update(novos)
        df.gravar(self.dados, tabela, linhas)

    def status(self, R, item, dim):
        return R.status_validacao[(item, dim)]["status_efetivo"]

    def desatualizadas(self, R):
        return {k for k, v in R.status_validacao.items() if v["status_efetivo"] == "DESATUALIZADA"}

    def assertSoDesatualizadas(self, R, esperadas):
        self.assertEqual(self.desatualizadas(R), set(esperadas))
        for k in TODAS_DIMS:
            if k in R.status_validacao and k not in esperadas:
                self.assertEqual(self.status(R, *k), "APROVADO", k)


class EstadoValido(Base):
    def test_estado_aprovado_sem_achados(self):
        R = self.verificar()
        self.assertEqual(R.achados, [], [a.como_dict() for a in R.achados])
        self.assertEqual(R.codigo_saida, 0)
        self.assertTrue(all(v["aprovado"] for v in R.aprovacao_exercicio.values()))
        self.assertEqual(R.resolucao["X99-E1"], ["A99-01_v100_r1_t1"])  # ATIVO
        self.assertEqual(R.resolucao["X99-E2"], ["A99-01_v080_r1_t1"])  # FIXO

    def test_csvs_oficiais_vazios_sao_validos(self):
        R = vd.Verificador(AQUI.parent / "01_dados").executar()
        self.assertEqual([a.como_dict() for a in R.achados if a.severidade == "ERRO"], [])
        self.assertEqual(R.codigo_saida, 0)

    def test_impressao_e_deterministica_e_normalizada(self):
        a = vd.impressao("japones", "テスト", "")
        self.assertEqual(a, vd.impressao("japones", "テスト", ""))
        self.assertEqual(a, vd.impressao("japones", vd.normalizar("  テスト\r\n"), ""))
        # separador impede colisão por concatenação
        self.assertNotEqual(vd.impressao("x", "ab", "c"), vd.impressao("x", "a", "bc"))
        # NFC: forma decomposta == composta
        self.assertEqual(vd.normalizar("é"), "é")
        self.assertEqual(len(a), 64)

    def test_atualizar_impressoes_nao_muda_nada_no_estado_aprovado(self):
        _, mud = vd.atualizar_impressoes(self.dados)
        self.assertEqual(mud, [])


class CenariosObrigatorios(Base):
    # 1
    def test_01_traducao_nao_invalida_audio(self):
        self.mudar("frases.csv", "id_frase", "J99-01", traducao_ptbr="[fictício] tradução nova")
        _, mud = vd.atualizar_impressoes(self.dados)
        self.assertIn("frases.csv J99-01: imp_traducao atualizada, versao_traducao → 2", mud)
        R = self.verificar()
        self.assertSoDesatualizadas(R, {("J99-01", "TRADUCAO"), ("J99-01", "PEDAGOGICA"),
                                        ("X99-E1", "PEDAGOGICA"), ("X99-M1", "PEDAGOGICA")})
        self.assertFalse(R.tem("GRAVACAO_DESATUALIZADA"))
        self.assertFalse(R.tem("ROTEIRO_DESATUALIZADO"))
        self.assertEqual(self.status(R, "A99-01_v100_r1_t1", "GRAVACAO"), "APROVADO")
        self.assertEqual(self.status(R, "X99-E1", "ESCUTA"), "APROVADO")
        self.assertEqual(df.ler(self.dados, "frases.csv")[0]["versao_japones"], "1")

    # 2
    def test_02_explicacao_nao_invalida_audio_nem_traducao(self):
        self.mudar("frases.csv", "id_frase", "J99-01", explicacao_curta="[fictício] explicação nova")
        vd.atualizar_impressoes(self.dados)
        R = self.verificar()
        self.assertSoDesatualizadas(R, {("J99-01", "PEDAGOGICA"), ("X99-E1", "PEDAGOGICA"), ("X99-M1", "PEDAGOGICA")})
        self.assertFalse(R.tem("GRAVACAO_DESATUALIZADA"))
        self.assertEqual(df.ler(self.dados, "frases.csv")[0]["versao_explicacao"], "2")

    # 3
    def test_03_texto_japones_invalida_roteiro_e_gravacoes(self):
        self.mudar("frases.csv", "id_frase", "J99-01",
                   forma_reduzida="{試験|しけん}の{文|ぶん}、{読|よ}んじゃった")
        vd.atualizar_impressoes(self.dados)
        R = self.verificar()
        self.assertSoDesatualizadas(R, {("J99-01", "LINGUISTICA"), ("J99-01", "TRADUCAO"), ("J99-01", "PEDAGOGICA"),
                                        ("A99-01", "ROTEIRO"), ("X99-E1", "PEDAGOGICA"), ("X99-E2", "PEDAGOGICA"),
                                        ("X99-M1", "PEDAGOGICA")})
        self.assertTrue(R.tem("ROTEIRO_DESATUALIZADO", "A99-01#1"))
        self.assertFalse(R.tem("ROTEIRO_DESATUALIZADO", "A99-01#2"))
        self.assertTrue(R.tem("GRAVACAO_DESATUALIZADA", "A99-01_v100_r1_t1"))
        self.assertTrue(R.tem("GRAVACAO_DESATUALIZADA", "A99-01_v080_r1_t1"))
        # a GRAVACAO (bytes) continua validada, mas o exercício não pode ser aprovado com gravação desatualizada
        self.assertEqual(self.status(R, "A99-01_v100_r1_t1", "GRAVACAO"), "APROVADO")
        self.assertFalse(R.aprovacao_exercicio["X99-E1"]["aprovado"])
        self.assertTrue(any("desatualizada em relação ao roteiro" in b for b in R.aprovacao_exercicio["X99-E1"]["bloqueios"]))
        self.assertEqual(df.ler(self.dados, "audios.csv")[0]["versao_roteiro"], "2")

    # 4
    def test_04_furigana_e_mudanca_no_japones(self):
        self.mudar("frases.csv", "id_frase", "J99-02", forma_completa="{試験|ためし}です")
        vd.atualizar_impressoes(self.dados)
        R = self.verificar()
        self.assertEqual(self.status(R, "J99-02", "LINGUISTICA"), "DESATUALIZADA")
        self.assertEqual(self.status(R, "A99-01", "ROTEIRO"), "DESATUALIZADA")
        self.assertTrue(R.tem("ROTEIRO_DESATUALIZADO", "A99-01#2"))
        self.assertTrue(R.tem("GRAVACAO_DESATUALIZADA"))
        self.assertEqual(self.status(R, "J99-01", "LINGUISTICA"), "APROVADO")

    def test_04b_furigana_malformada_e_erro(self):
        self.mudar("frases.csv", "id_frase", "J99-02", forma_completa="{試験しけん}です")
        R = self.verificar()
        self.assertTrue(R.tem("FURIGANA"))
        self.assertEqual(R.codigo_saida, 1)

    # 5
    def test_05_ordem_dos_segmentos_invalida_roteiro_nao_frases(self):
        segs = df.ler(self.dados, "audio_segmentos.csv")
        segs[0]["ordem"], segs[1]["ordem"] = "2", "1"
        df.gravar(self.dados, "audio_segmentos.csv", segs)
        vd.atualizar_impressoes(self.dados)
        R = self.verificar()
        self.assertSoDesatualizadas(R, {("A99-01", "ROTEIRO"), ("X99-E1", "PEDAGOGICA"), ("X99-E2", "PEDAGOGICA")})
        self.assertTrue(R.tem("GRAVACAO_DESATUALIZADA"))
        self.assertFalse(R.tem("ROTEIRO_DESATUALIZADO"))  # o japonês das frases não mudou

    def test_05b_ordem_das_linhas_no_csv_nao_importa(self):
        """Só o valor de `ordem` define a sequência; reordenar as linhas do CSV não invalida nada."""
        for tabela in ("audio_segmentos.csv", "exercicio_audios.csv", "frases.csv", "respostas.csv", "validacoes.csv"):
            df.gravar(self.dados, tabela, list(reversed(df.ler(self.dados, tabela))))
        R = self.verificar()
        self.assertEqual(R.achados, [], [a.como_dict() for a in R.achados])

    # 6
    def test_06_substituir_gravacao_ativa(self):
        arqs = df.ler(self.dados, "arquivos_audio.csv")
        arqs[0]["situacao"] = "SUBSTITUIDO"  # v100 t1
        arqs.append(df.nova_gravacao(self.tmp, self.dados, "A99-01", "100", "2"))
        df.gravar(self.dados, "arquivos_audio.csv", arqs)
        R = self.verificar()
        self.assertEqual(R.resolucao["X99-E1"], ["A99-01_v100_r1_t2"])
        self.assertSoDesatualizadas(R, {("X99-E1", "PEDAGOGICA"), ("X99-E1", "ESCUTA")})
        self.assertTrue(any("a gravação usada mudou" in a.mensagem for a in R.achados))
        # a gravação nova não herda validação
        self.assertTrue(R.tem("SEM_APROVACAO_FINAL", "A99-01_v100_r1_t2"))
        self.assertFalse(R.aprovacao_exercicio["X99-E1"]["aprovado"])
        # roteiro, FIXO (X99-E2) e a outra velocidade não são afetados
        self.assertEqual(self.status(R, "A99-01", "ROTEIRO"), "APROVADO")
        self.assertTrue(R.aprovacao_exercicio["X99-E2"]["aprovado"])
        self.assertFalse(R.tem("GRAVACAO_DESATUALIZADA"))
        # depois das novas validações, volta a ficar tudo aprovado
        df.validar_tudo(self.dados, so={("A99-01_v100_r1_t2", "GRAVACAO"), ("X99-E1", "PEDAGOGICA"), ("X99-E1", "ESCUTA")})
        R2 = self.verificar()
        self.assertEqual(R2.codigo_saida, 0, [a.como_dict() for a in R2.achados])

    def test_06b_bytes_regravados_no_mesmo_id_invalidam_validacoes(self):
        """Mesmo ID, bytes diferentes registrados: só a impressão (não a lista de IDs) detecta."""
        novo = df._arquivo_audio(self.tmp, "A99-01_v100_r1_t1.ficticio", "FICTICIO regravado")
        self.mudar("arquivos_audio.csv", "id_arquivo_audio", "A99-01_v100_r1_t1", sha256_arquivo=novo)
        R = self.verificar()
        self.assertEqual(R.resolucao["X99-E1"], ["A99-01_v100_r1_t1"])  # mesmo arquivo resolvido
        self.assertSoDesatualizadas(R, {("A99-01_v100_r1_t1", "GRAVACAO"), ("X99-E1", "PEDAGOGICA"), ("X99-E1", "ESCUTA")})
        self.assertFalse(R.tem("AUDIO_SHA_DIVERGENTE"))  # o registro e o disco concordam

    # 7
    def test_07_mudar_velocidade_do_exercicio(self):
        linhas = df.ler(self.dados, "exercicio_audios.csv")
        linhas[0]["velocidade"] = "080"
        df.gravar(self.dados, "exercicio_audios.csv", linhas)
        _, mud = vd.atualizar_impressoes(self.dados)
        self.assertIn("exercicios.csv X99-E1: imp_exercicio atualizada, versao → 2", mud)
        R = self.verificar()
        self.assertEqual(R.resolucao["X99-E1"], ["A99-01_v080_r1_t1"])
        self.assertSoDesatualizadas(R, {("X99-E1", "PEDAGOGICA"), ("X99-E1", "ESCUTA")})
        self.assertEqual(self.status(R, "A99-01_v080_r1_t1", "GRAVACAO"), "APROVADO")

    def test_07b_mudar_velocidade_sem_atualizar_impressao_e_erro(self):
        linhas = df.ler(self.dados, "exercicio_audios.csv")
        linhas[0]["velocidade"] = "080"
        df.gravar(self.dados, "exercicio_audios.csv", linhas)
        R = self.verificar()
        self.assertTrue(R.tem("IMPRESSAO_GRAVADA_DIVERGENTE", "X99-E1"))
        self.assertEqual(R.codigo_saida, 1)

    # 8
    def test_08_fixo_mantem_gravacao_quando_outra_vira_ativa(self):
        arqs = df.ler(self.dados, "arquivos_audio.csv")
        arqs[1]["situacao"] = "SUBSTITUIDO"  # v080 t1
        arqs.append(df.nova_gravacao(self.tmp, self.dados, "A99-01", "080", "2"))
        df.gravar(self.dados, "arquivos_audio.csv", arqs)
        R = self.verificar()
        self.assertEqual(R.resolucao["X99-E2"], ["A99-01_v080_r1_t1"])
        self.assertTrue(R.tem("FIXO_SUBSTITUIDO", "X99-E2"))
        self.assertEqual(self.status(R, "X99-E2", "PEDAGOGICA"), "APROVADO")
        self.assertEqual(self.status(R, "X99-E2", "ESCUTA"), "APROVADO")
        self.assertTrue(R.aprovacao_exercicio["X99-E2"]["aprovado"])

    def test_08b_fixo_para_gravacao_retirada_e_erro(self):
        self.mudar("arquivos_audio.csv", "id_arquivo_audio", "A99-01_v080_r1_t1", situacao="RETIRADO")
        R = self.verificar()
        self.assertTrue(R.tem("FIXO_RETIRADO", "X99-E2"))
        self.assertFalse(R.aprovacao_exercicio["X99-E2"]["aprovado"])
        self.assertEqual(R.codigo_saida, 1)

    def test_08c_fixo_com_velocidade_diferente_e_erro(self):
        self.mudar("exercicio_audios.csv", "id_exercicio", "X99-E2", id_arquivo_audio="A99-01_v100_r1_t1")
        vd.atualizar_impressoes(self.dados)
        R = self.verificar()
        self.assertTrue(R.tem("FIXO_INCOERENTE", "X99-E2"))

    def test_08d_fixo_sem_arquivo_e_ativo_com_arquivo_sao_erros(self):
        linhas = df.ler(self.dados, "exercicio_audios.csv")
        linhas[0]["id_arquivo_audio"] = "A99-01_v100_r1_t1"   # ATIVO com arquivo
        linhas[1]["id_arquivo_audio"] = ""                    # FIXO sem arquivo
        df.gravar(self.dados, "exercicio_audios.csv", linhas)
        R = self.verificar()
        self.assertTrue(R.tem("ATIVO_COM_ARQUIVO"))
        self.assertTrue(R.tem("FIXO_SEM_ARQUIVO"))

    # 9
    def test_09_ativo_sem_gravacao_ativa_e_erro(self):
        self.mudar("arquivos_audio.csv", "id_arquivo_audio", "A99-01_v100_r1_t1", situacao="SUBSTITUIDO")
        R = self.verificar()
        self.assertTrue(R.tem("SEM_GRAVACAO_ATIVA", "X99-E1"))
        self.assertEqual(R.resolucao["X99-E1"], [None])
        self.assertFalse(R.aprovacao_exercicio["X99-E1"]["aprovado"])
        self.assertEqual(R.codigo_saida, 1)

    # 10
    def test_10_gravacao_inexistente(self):
        self.mudar("exercicio_audios.csv", "id_exercicio", "X99-E2", id_arquivo_audio="A99-01_v080_r1_t9")
        vd.atualizar_impressoes(self.dados)
        R = self.verificar()
        self.assertTrue(R.tem("ARQUIVO_INEXISTENTE", "X99-E2"))
        self.assertEqual(R.codigo_saida, 1)

    def test_10b_validacao_de_item_inexistente(self):
        linhas = df.ler(self.dados, "validacoes.csv")
        linhas[0]["id_item"] = "J99-77"
        df.gravar(self.dados, "validacoes.csv", linhas)
        self.assertTrue(self.verificar().tem("REFERENCIA_INEXISTENTE", "validacoes.csv"))

    def test_10c_frase_inexistente_em_exercicio_e_segmento(self):
        self.mudar("exercicios.csv", "id_exercicio", "X99-M1", frases_usadas="J99-01|J99-55")
        segs = df.ler(self.dados, "audio_segmentos.csv")
        segs[1]["id_frase"] = "J99-56"
        df.gravar(self.dados, "audio_segmentos.csv", segs)
        R = self.verificar()
        self.assertTrue(R.tem("REFERENCIA_INEXISTENTE", "exercicios.csv"))
        self.assertTrue(R.tem("REFERENCIA_INEXISTENTE", "audio_segmentos.csv"))

    # 11
    def test_11_identificadores_duplicados(self):
        frases = df.ler(self.dados, "frases.csv")
        frases.append(dict(frases[0]))
        df.gravar(self.dados, "frases.csv", frases)
        arqs = df.ler(self.dados, "arquivos_audio.csv")
        arqs.append(dict(arqs[1], situacao="SUBSTITUIDO"))
        df.gravar(self.dados, "arquivos_audio.csv", arqs)
        R = self.verificar()
        self.assertTrue(R.tem("ID_DUPLICADO", "frases.csv"))
        self.assertTrue(R.tem("ID_DUPLICADO", "arquivos_audio.csv"))
        self.assertEqual(R.codigo_saida, 1)

    def test_11b_identificador_de_arquivo_com_tomada_incoerente(self):
        self.mudar("arquivos_audio.csv", "id_arquivo_audio", "A99-01_v100_r1_t1", tomada="2")
        R = self.verificar()
        self.assertTrue(R.tem("ID_ARQUIVO_INCOERENTE", "A99-01_v100_r1_t1"))

    def test_11c_formato_de_identificador_de_arquivo(self):
        self.mudar("arquivos_audio.csv", "id_arquivo_audio", "A99-01_v100_r1_t1",
                   id_arquivo_audio="A99-01_v100_r01_t1", versao_roteiro="01")
        self.assertTrue(self.verificar().tem("FORMATO", "arquivos_audio.csv"))

    # 12
    def test_12_duas_gravacoes_ativas_mesma_faixa_e_velocidade(self):
        arqs = df.ler(self.dados, "arquivos_audio.csv")
        arqs.append(df.nova_gravacao(self.tmp, self.dados, "A99-01", "100", "2"))
        df.gravar(self.dados, "arquivos_audio.csv", arqs)
        R = self.verificar()
        self.assertTrue(R.tem("MAIS_DE_UM_ATIVO", "A99-01, 100"))
        self.assertEqual(R.codigo_saida, 1)

    # 13
    def test_13_gravacao_com_roteiro_desatualizado(self):
        segs = df.ler(self.dados, "audio_segmentos.csv")
        segs[1]["voz"] = "voz-ficticia-3"
        df.gravar(self.dados, "audio_segmentos.csv", segs)
        vd.atualizar_impressoes(self.dados)
        R = self.verificar()
        self.assertTrue(R.tem("GRAVACAO_DESATUALIZADA", "A99-01_v100_r1_t1"))
        self.assertTrue(R.tem("GRAVACAO_DESATUALIZADA", "A99-01_v080_r1_t1"))
        self.assertEqual(R.codigo_saida, 2)
        for ex in ("X99-E1", "X99-E2"):
            self.assertFalse(R.aprovacao_exercicio[ex]["aprovado"])
        self.assertTrue(R.aprovacao_exercicio["X99-M1"]["aprovado"])  # sem áudio

    def test_13b_gravacao_futura_e_erro(self):
        self.mudar("arquivos_audio.csv", "id_arquivo_audio", "A99-01_v100_r1_t1",
                   id_arquivo_audio="A99-01_v100_r5_t1", versao_roteiro="5")
        self.assertTrue(self.verificar().tem("VERSAO_FUTURA"))

    # 14
    def test_14_exercicio_sem_resposta_correta(self):
        self.mudar("respostas.csv", "id_resposta", "X99-M1-a", tipo="ERRADA")
        vd.atualizar_impressoes(self.dados)
        R = self.verificar()
        self.assertTrue(R.tem("SEM_RESPOSTA_CORRETA", "X99-M1"))
        self.assertEqual(self.status(R, "X99-M1", "PEDAGOGICA"), "DESATUALIZADA")

    # 15
    def test_15_validacao_antiga_nao_continua_aprovada(self):
        self.mudar("frases.csv", "id_frase", "J99-01", traducao_ptbr="[fictício] outra tradução")
        vd.atualizar_impressoes(self.dados)
        R = self.verificar()
        self.assertEqual(self.status(R, "J99-01", "TRADUCAO"), "DESATUALIZADA")
        self.assertTrue(R.tem("VALIDACAO_DESATUALIZADA", "J99-01, TRADUCAO"))
        self.assertFalse(R.aprovacao_exercicio["X99-E1"]["aprovado"])
        # a validação antiga continua no arquivo (histórico), só não vale mais
        self.assertEqual(len(df.ler(self.dados, "validacoes.csv")), len(TODAS_DIMS))
        # nova validação com a impressão atual restaura a aprovação
        df.validar_tudo(self.dados, so={("J99-01", "TRADUCAO"), ("J99-01", "PEDAGOGICA"),
                                        ("X99-E1", "PEDAGOGICA"), ("X99-M1", "PEDAGOGICA")})
        self.assertEqual(self.verificar().codigo_saida, 0)

    def test_15b_reverter_conteudo_reativa_validacao_antiga_com_aviso(self):
        original = df.ler(self.dados, "frases.csv")[0]["traducao_ptbr"]
        self.mudar("frases.csv", "id_frase", "J99-01", traducao_ptbr="[fictício] temporária")
        vd.atualizar_impressoes(self.dados)
        df.validar_tudo(self.dados, status="AJUSTAR", so={("J99-01", "TRADUCAO")})
        self.mudar("frases.csv", "id_frase", "J99-01", traducao_ptbr=original)
        vd.atualizar_impressoes(self.dados)
        R = self.verificar()
        self.assertEqual(self.status(R, "J99-01", "TRADUCAO"), "APROVADO")
        self.assertTrue(R.tem("VALIDACAO_RECENTE_DE_OUTRA_VERSAO"))


class RevisoresEValidacoes(Base):
    def test_aprovacao_de_ia_e_apenas_auxiliar(self):
        df.validar_tudo(self.dados, revisor="IA_CHATGPT", so={("J99-01", "LINGUISTICA")})
        R = self.verificar()
        self.assertEqual(self.status(R, "J99-01", "LINGUISTICA"), "APROVADO_AUXILIAR")
        self.assertTrue(R.tem("SEM_APROVACAO_FINAL", "J99-01"))
        self.assertFalse(R.aprovacao_exercicio["X99-E1"]["aprovado"])

    def test_humano_responsavel_nao_aprova_linguistica(self):
        df.validar_tudo(self.dados, revisor="HUMANO_RESPONSAVEL", so={("J99-02", "LINGUISTICA")})
        self.assertEqual(self.status(self.verificar(), "J99-02", "LINGUISTICA"), "APROVADO_AUXILIAR")

    def test_humano_responsavel_aprova_pedagogica(self):
        df.validar_tudo(self.dados, revisor="HUMANO_RESPONSAVEL", so={("X99-M1", "PEDAGOGICA")})
        self.assertEqual(self.status(self.verificar(), "X99-M1", "PEDAGOGICA"), "APROVADO")

    def test_problema_apontado_por_ia_bloqueia(self):
        df.validar_tudo(self.dados, revisor="IA_CHATGPT", status="NAO_USAR", so={("X99-M1", "PEDAGOGICA")})
        R = self.verificar()
        self.assertEqual(self.status(R, "X99-M1", "PEDAGOGICA"), "NAO_USAR")
        self.assertFalse(R.aprovacao_exercicio["X99-M1"]["aprovado"])

    def test_humano_sem_identificacao_e_erro(self):
        linhas = df.ler(self.dados, "validacoes.csv")
        linhas[0]["revisor_identificacao"] = ""
        df.gravar(self.dados, "validacoes.csv", linhas)
        self.assertTrue(self.verificar().tem("REVISOR_SEM_IDENTIFICACAO"))

    def test_dimensao_incompativel_com_item(self):
        linhas = df.ler(self.dados, "validacoes.csv")
        linhas[0]["dimensao"] = "ESCUTA"  # linha 0 é de frase
        df.gravar(self.dados, "validacoes.csv", linhas)
        self.assertTrue(self.verificar().tem("DIMENSAO_INCOMPATIVEL"))

    def test_lista_de_gravacoes_resolvidas_obrigatoria(self):
        linhas = df.ler(self.dados, "validacoes.csv")
        alvo = [l for l in linhas if l["id_item"] == "X99-E1" and l["dimensao"] == "ESCUTA"][0]
        alvo["arquivos_audio_resolvidos"] = ""
        df.gravar(self.dados, "validacoes.csv", linhas)
        self.assertTrue(self.verificar().tem("RESOLVIDOS_INCOMPLETO"))


class EstruturaEArquivos(Base):
    def test_cabecalho_errado(self):
        p = self.dados / "frases.csv"
        p.write_text(p.read_text(encoding="utf-8").replace("traducao_ptbr", "traducao", 1), encoding="utf-8")
        R = self.verificar()
        self.assertTrue(R.tem("CABECALHO", "frases.csv"))
        self.assertEqual(R.codigo_saida, 1)

    def test_bom_e_crlf(self):
        p = self.dados / "audios.csv"
        p.write_bytes(b"\xef\xbb\xbf" + p.read_bytes().replace(b"\n", b"\r\n"))
        R = self.verificar()
        self.assertTrue(R.tem("CODIFICACAO", "audios.csv"))
        self.assertTrue(R.tem("FIM_DE_LINHA", "audios.csv"))

    def test_lista_com_separador_errado(self):
        self.mudar("exercicios.csv", "id_exercicio", "X99-M1", frases_usadas="J99-01;J99-02")
        self.assertTrue(self.verificar().tem("FORMATO", "X99-M1"))

    def test_frase_de_capitulo_posterior(self):
        frases = df.ler(self.dados, "frases.csv")
        frases.append(dict(frases[1], id_frase="J98-01", capitulo="98"))
        df.gravar(self.dados, "frases.csv", frases)
        exs = df.ler(self.dados, "exercicios.csv")
        exs.append(dict(exs[2], id_exercicio="X98-M1", capitulo="98", frases_usadas="J99-02"))
        df.gravar(self.dados, "exercicios.csv", exs)
        R = self.verificar()
        self.assertTrue(R.tem("CAPITULO_POSTERIOR", "X98-M1"))

    def test_capitulo_do_id_coerente(self):
        self.mudar("frases.csv", "id_frase", "J99-02", capitulo="98")
        self.assertTrue(self.verificar().tem("CAPITULO_ID", "J99-02"))

    def test_segmento_reduzido_de_frase_sem_reducao(self):
        segs = df.ler(self.dados, "audio_segmentos.csv")
        segs[1]["forma_falada"] = "REDUZIDA"
        df.gravar(self.dados, "audio_segmentos.csv", segs)
        self.assertTrue(self.verificar().tem("FORMA_INEXISTENTE"))

    def test_buraco_na_ordem_dos_segmentos(self):
        segs = df.ler(self.dados, "audio_segmentos.csv")
        segs[1]["ordem"] = "3"
        df.gravar(self.dados, "audio_segmentos.csv", segs)
        self.assertTrue(self.verificar().tem("ORDEM_COM_BURACO", "A99-01"))

    def test_escuta_sem_audio(self):
        df.gravar(self.dados, "exercicio_audios.csv",
                  [l for l in df.ler(self.dados, "exercicio_audios.csv") if l["id_exercicio"] != "X99-E2"])
        vd.atualizar_impressoes(self.dados)
        self.assertTrue(self.verificar().tem("ESCUTA_SEM_AUDIO", "X99-E2"))

    def test_referencia_a_item_retirado(self):
        self.mudar("frases.csv", "id_frase", "J99-02", situacao="RETIRADA")
        R = self.verificar()
        self.assertTrue(R.tem("REFERENCIA_RETIRADA", "X99-E2"))
        self.assertTrue(R.tem("REFERENCIA_RETIRADA", "audio_segmentos.csv"))

    def test_velocidade_fora_do_piloto_e_aviso(self):
        arqs = df.ler(self.dados, "arquivos_audio.csv")
        arqs.append(df.nova_gravacao(self.tmp, self.dados, "A99-01", "070", "1"))
        df.gravar(self.dados, "arquivos_audio.csv", arqs)
        R = self.verificar()
        self.assertTrue(R.tem("VELOCIDADE_FORA_DO_PILOTO"))
        self.assertFalse(any(a.severidade == "ERRO" for a in R.achados))

    def test_bytes_do_audio_trocados_sem_registro(self):
        (self.audio / "A99-01_v100_r1_t1.ficticio").write_bytes(b"conteudo trocado")
        R = self.verificar()
        self.assertTrue(R.tem("AUDIO_SHA_DIVERGENTE", "A99-01_v100_r1_t1"))
        self.assertEqual(R.codigo_saida, 1)

    def test_audio_ausente_ou_nao_conferido_e_aviso(self):
        (self.audio / "A99-01_v080_r1_t1.ficticio").unlink()
        R = self.verificar()
        self.assertTrue(R.tem("AUDIO_AUSENTE", "A99-01_v080_r1_t1"))
        R2 = self.verificar(com_audio=False)
        self.assertTrue(R2.tem("AUDIO_NAO_CONFERIDO"))
        self.assertEqual(R2.codigo_saida, 0)

    def test_roteiro_nao_fechado(self):
        segs = df.ler(self.dados, "audio_segmentos.csv")
        segs[0]["imp_japones_usada"] = ""
        df.gravar(self.dados, "audio_segmentos.csv", segs)
        R = self.verificar()
        self.assertTrue(R.tem("ROTEIRO_NAO_FECHADO", "A99-01#1"))
        vd.fechar_roteiro(self.dados, "A99-01")
        self.assertFalse(self.verificar().tem("ROTEIRO_NAO_FECHADO"))

    def test_impressao_nao_gravada(self):
        self.mudar("frases.csv", "id_frase", "J99-01", imp_traducao="")
        self.assertTrue(self.verificar().tem("IMPRESSAO_NAO_GRAVADA", "J99-01"))


class CodigosRestantes(Base):
    """Garante que todo código de achado do verificador tem ao menos um teste."""

    def test_arquivo_ausente(self):
        (self.dados / "respostas.csv").unlink()
        self.assertTrue(self.verificar().tem("ARQUIVO_AUSENTE", "respostas.csv"))

    def test_campo_vazio_e_valor_invalido(self):
        self.mudar("frases.csv", "id_frase", "J99-02", traducao_ptbr="", registro="INFORMAL")
        R = self.verificar()
        self.assertTrue(R.tem("CAMPO_VAZIO", "J99-02"))
        self.assertTrue(R.tem("VALOR_INVALIDO", "J99-02"))

    def test_numero_de_colunas(self):
        p = self.dados / "audios.csv"
        p.write_text(p.read_text(encoding="utf-8").rstrip("\n") + ",coluna-a-mais\n", encoding="utf-8")
        self.assertTrue(self.verificar().tem("COLUNAS", "audios.csv"))

    def test_faixa_sem_segmentos(self):
        df.gravar(self.dados, "audio_segmentos.csv", [])
        self.assertTrue(self.verificar().tem("FAIXA_SEM_SEGMENTOS", "A99-01"))

    def test_prefixo_da_resposta(self):
        self.mudar("respostas.csv", "id_resposta", "X99-M1-b", id_resposta="X99-E1-z")
        self.assertTrue(self.verificar().tem("ID_INCOERENTE", "X99-E1-z"))

    def test_lista_repetida(self):
        self.mudar("exercicios.csv", "id_exercicio", "X99-M1", frases_usadas="J99-01|J99-01")
        self.assertTrue(self.verificar().tem("LISTA_REPETIDA", "X99-M1"))

    def test_resolvidos_indevido(self):
        linhas = df.ler(self.dados, "validacoes.csv")
        alvo = [l for l in linhas if l["id_item"] == "X99-M1"][0]  # exercício sem áudio
        alvo["arquivos_audio_resolvidos"] = "A99-01_v100_r1_t1"
        df.gravar(self.dados, "validacoes.csv", linhas)
        self.assertTrue(self.verificar().tem("RESOLVIDOS_INDEVIDO"))

    def test_velocidade_fora_da_faixa_e_caminho_absoluto(self):
        self.mudar("arquivos_audio.csv", "id_arquivo_audio", "A99-01_v080_r1_t1",
                   id_arquivo_audio="A99-01_v300_r1_t1", velocidade="300", arquivo="/tmp/x.mp3", transcricao_confere="TALVEZ")
        R = self.verificar()
        self.assertTrue(R.tem("VELOCIDADE", "A99-01_v300_r1_t1"))
        self.assertTrue(R.tem("CAMINHO", "A99-01_v300_r1_t1"))
        self.assertTrue(R.tem("VALOR_INVALIDO", "A99-01_v300_r1_t1"))

    def test_exercicio_nao_aprovado_lista_bloqueios(self):
        df.validar_tudo(self.dados, status="AJUSTAR", so={("J99-02", "LINGUISTICA")})
        R = self.verificar()
        self.assertTrue(R.tem("EXERCICIO_NAO_APROVADO", "X99-E2"))
        self.assertTrue(R.tem("EXERCICIO_NAO_APROVADO", "X99-M1"))
        self.assertFalse(R.tem("EXERCICIO_NAO_APROVADO", "X99-E1"))
        self.assertIn("frase usada J99-02 LINGUISTICA: AJUSTAR", R.aprovacao_exercicio["X99-E2"]["bloqueios"])


class CoberturaDosCodigos(unittest.TestCase):
    def test_todo_codigo_de_achado_tem_teste(self):
        import re
        codigo = (AQUI.parent / "05_ferramentas" / "verificar_dados.py").read_text(encoding="utf-8")
        testes = Path(__file__).read_text(encoding="utf-8")
        cods = set(re.findall(r'"(?:ERRO|PENDENCIA|AVISO)",\s*"([A-Z_]+)"', codigo))
        cods |= set(re.findall(r'_exige\([^,]+,\s*"([A-Z_]+)"', codigo, re.S))
        cods |= {"CAMPO_VAZIO", "FORMATO", "VALOR_INVALIDO", "ID_DUPLICADO"}  # emitidos por funções auxiliares
        cods -= {"ERRO", "PENDENCIA", "AVISO"}  # severidades, não códigos (aparecem numa tupla do relatório)
        self.assertGreater(len(cods), 40)
        self.assertEqual(sorted(c for c in cods if f'"{c}"' not in testes), [])


class SincroniaEsquemaCodigo(unittest.TestCase):
    """Esquema, CSVs oficiais e código descrevem as mesmas colunas e valores."""

    def setUp(self):
        self.esquema = (AQUI.parent / "01_dados" / "ESQUEMA.md").read_text(encoding="utf-8")

    def test_csvs_oficiais_tem_os_cabecalhos_do_codigo(self):
        for nome, cab in vd.CABECALHOS.items():
            primeira = (AQUI.parent / "01_dados" / nome).read_text(encoding="utf-8").splitlines()[0]
            self.assertEqual(primeira.split(","), cab, nome)

    def test_esquema_documenta_cada_arquivo_e_coluna(self):
        import re
        for nome, cab in vd.CABECALHOS.items():
            self.assertIn(f"`{nome}`", self.esquema)
            # a seção 4 lista as colunas de cada arquivo logo após o título "### <arquivo>"
            m = re.search(rf"### {re.escape(nome)}[^\n]*\n(.*?)(?=\n### |\n## )", self.esquema, re.S)
            self.assertIsNotNone(m, nome)
            faltam = [c for c in cab if f"`{c}`" not in m.group(1)]
            self.assertEqual(faltam, [], f"{nome}: colunas sem documentação na seção 4")

    def test_esquema_documenta_valores_fixos(self):
        for chave in ("registro", "dimensao", "status", "revisor", "modo_selecao", "situacao_arquivo", "tipo_resposta"):
            for valor in vd.ENUM[chave]:
                self.assertIn(f"`{valor}`", self.esquema, f"{chave}={valor}")
        for dim, aprovadores in vd.APROVADORES_FINAIS.items():
            self.assertIn(f"`{dim}`", self.esquema)
        self.assertEqual(vd.VELOCIDADES_PILOTO, {"100", "080"})
        self.assertIn("Versão do esquema: **5**", self.esquema)
        self.assertEqual(vd.VERSAO_ESQUEMA, 5)


class LinhaDeComando(Base):
    SCRIPT = AQUI.parent / "05_ferramentas" / "verificar_dados.py"

    def rodar(self, *args):
        return subprocess.run([sys.executable, str(self.SCRIPT), *args], capture_output=True, text=True)

    def test_codigos_de_saida(self):
        self.assertEqual(self.rodar("verificar", "--dados", str(self.dados), "--raiz-audio", str(self.audio)).returncode, 0)
        self.mudar("frases.csv", "id_frase", "J99-01", traducao_ptbr="[fictício] x")
        self.rodar("atualizar-impressoes", "--dados", str(self.dados))
        self.assertEqual(self.rodar("verificar", "--dados", str(self.dados)).returncode, 2)
        self.mudar("frases.csv", "id_frase", "J99-01", registro="INVALIDO")
        self.assertEqual(self.rodar("verificar", "--dados", str(self.dados)).returncode, 1)
        self.assertEqual(self.rodar("verificar", "--dados", str(self.tmp / "nao-existe")).returncode, 3)

    def test_impressao_validacao(self):
        r = self.rodar("impressao-validacao", "X99-E1", "ESCUTA", "--dados", str(self.dados))
        self.assertEqual(r.returncode, 0)
        self.assertIn("arquivos_audio_resolvidos=A99-01_v100_r1_t1", r.stdout)
        linhas = df.ler(self.dados, "validacoes.csv")
        esperado = [l for l in linhas if l["id_item"] == "X99-E1" and l["dimensao"] == "ESCUTA"][0]["imp_validada"]
        self.assertIn(f"imp_validada={esperado}", r.stdout)

    def test_relatorio_json(self):
        saida = self.tmp / "r.json"
        self.rodar("verificar", "--dados", str(self.dados), "--json", str(saida))
        import json
        d = json.loads(saida.read_text(encoding="utf-8"))
        self.assertEqual(d["esquema"], vd.VERSAO_ESQUEMA)
        self.assertIn("X99-E1", d["exercicios"])


class Apontamentos(unittest.TestCase):
    C = "1" * 40

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="apont_"))
        self.p = self.tmp / "apontamentos.csv"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def gravar(self, **mud):
        base = dict(id_apontamento="P99", origem="IA_CHATGPT", rodada="99", data=df.DATA, commit_revisado=self.C,
                    area="DADOS", gravidade="MEDIA", descricao="[fictício]", status="ABERTO", commit_correcao="",
                    evidencia="", verificado_por="", commit_verificado="", documento="", observacoes="")
        base.update(mud)
        import csv
        with open(self.p, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(vd.CAB_APONTAMENTOS)
            w.writerow([base[c] for c in vd.CAB_APONTAMENTOS])

    def test_valido(self):
        self.gravar(status="VERIFICADO", commit_correcao=self.C, evidencia="teste X", verificado_por="IA_CHATGPT",
                    commit_verificado=self.C)
        self.assertEqual(vd.verificar_apontamentos(self.p).achados, [])

    def test_claude_nao_verifica_a_propria_correcao(self):
        self.gravar(status="VERIFICADO", commit_correcao=self.C, evidencia="teste X", verificado_por="IA_CLAUDE",
                    commit_verificado=self.C)
        self.assertTrue(vd.verificar_apontamentos(self.p).tem("VERIFICACAO_INVALIDA"))

    def test_corrigido_exige_commit_e_evidencia(self):
        self.gravar(status="CORRIGIDO_AGUARDA_VERIFICACAO")
        R = vd.verificar_apontamentos(self.p)
        self.assertEqual(sum(a.codigo == "SEM_EVIDENCIA" for a in R.achados), 2)

    def test_rejeicao_exige_justificativa(self):
        self.gravar(status="REJEITADO_COM_JUSTIFICATIVA")
        self.assertTrue(vd.verificar_apontamentos(self.p).tem("SEM_JUSTIFICATIVA"))

    def test_registro_oficial_e_valido(self):
        R = vd.verificar_apontamentos(AQUI.parent / "03_revisao" / "apontamentos.csv")
        self.assertEqual([a.como_dict() for a in R.achados], [])


class Originais(unittest.TestCase):
    def test_quatro_originais_intactos(self):
        script = AQUI.parent / "05_ferramentas" / "verificar_originais.py"
        r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        if r.returncode == 3:
            self.skipTest("fora de um repositório git com a base disponível")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ÍNTEGRO", r.stdout)


if __name__ == "__main__":
    unittest.main()
