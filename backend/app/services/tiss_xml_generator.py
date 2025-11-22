from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from typing import List
from decimal import Decimal
from datetime import date
import uuid

class TISSXMLGenerator:
    """Gerador de arquivos XML padrão TISS ANS"""
    
    def __init__(self):
        self.versao_tiss = "4.03.00"
        
    def gerar_xml_lote(self, lote_data: dict) -> str:
        """Gera XML completo do lote TISS"""
        
        # Elemento raiz
        root = Element("ans:mensagemTISS", {
            "xmlns:ans": "http://www.ans.gov.br/padroes/tiss/schemas",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.ans.gov.br/padroes/tiss/schemas mensagem.xsd"
        })
        
        # Cabeçalho
        header = SubElement(root, "ans:cabecalho")
        SubElement(header, "ans:identificacaoTransacao").text = str(uuid.uuid4())
        SubElement(header, "ans:tipoTransacao").text = "ENVIO_LOTE_GUIAS"
        SubElement(header, "ans:sequencialTransacao").text = lote_data.get("numero_lote", "1")
        SubElement(header, "ans:dataRegistroTransacao").text = date.today().strftime("%Y-%m-%d")
        SubElement(header, "ans:horaRegistroTransacao").text = date.today().strftime("%H:%M:%S")
        
        # Identificação do prestador
        prestador = SubElement(header, "ans:prestador")
        SubElement(prestador, "ans:codigoPrestadorNaOperadora").text = lote_data.get("prestador_codigo", "")
        SubElement(prestador, "ans:nomeContratado").text = lote_data.get("prestador_nome", "")
        
        # Versão TISS
        SubElement(header, "ans:Padrao").text = self.versao_tiss
        
        # Corpo do lote
        corpo = SubElement(root, "ans:prestadorParaOperadora")
        lote_guias = SubElement(corpo, "ans:loteGuias")
        
        # Número do lote
        SubElement(lote_guias, "ans:numeroLote").text = lote_data.get("numero_lote", "")
        
        # Operadora
        operadora = SubElement(lote_guias, "ans:dadosOperadora")
        SubElement(operadora, "ans:codigoOperadoraNaANS").text = lote_data.get("operadora_codigo", "")
        SubElement(operadora, "ans:nomeOperadora").text = lote_data.get("operadora_nome", "")
        
        # Guias
        guias_element = SubElement(lote_guias, "ans:guias")
        
        for guia in lote_data.get("guias", []):
            self._adicionar_guia_consulta(guias_element, guia)
        
        # Totalizadores
        SubElement(lote_guias, "ans:valorTotalLote").text = str(lote_data.get("valor_total_lote", "0.00"))
        SubElement(lote_guias, "ans:quantidadeGuias").text = str(lote_data.get("quantidade_guias", "0"))
        
        # Hash do lote
        SubElement(lote_guias, "ans:hashLote").text = self._gerar_hash_lote(lote_data)
        
        # Converter para string XML formatada
        xml_string = self._prettify_xml(root)
        return xml_string
    
    def _adicionar_guia_consulta(self, parent: Element, guia: dict):
        """Adiciona guia de consulta ao XML"""
        guia_consulta = SubElement(parent, "ans:guiaConsulta")
        
        # Cabeçalho da guia
        cabecalho = SubElement(guia_consulta, "ans:cabecalhoGuia")
        SubElement(cabecalho, "ans:registroANS").text = guia.get("codigo_operadora", "")
        SubElement(cabecalho, "ans:numeroGuiaPrestador").text = guia.get("numero_guia", "")
        
        # Dados do beneficiário
        beneficiario = SubElement(guia_consulta, "ans:dadosBeneficiario")
        SubElement(beneficiario, "ans:numeroCarteira").text = guia.get("numero_carteira", "")
        SubElement(beneficiario, "ans:nomeBeneficiario").text = guia.get("nome_beneficiario", "")
        
        # Dados do contratado executante
        contratado = SubElement(guia_consulta, "ans:dadosContratadoExecutante")
        SubElement(contratado, "ans:codigoPrestadorNaOperadora").text = guia.get("codigo_prestador", "")
        SubElement(contratado, "ans:nomeContratado").text = guia.get("nome_prestador", "")
        
        # Dados do atendimento
        atendimento = SubElement(guia_consulta, "ans:dadosAtendimento")
        SubElement(atendimento, "ans:tipoConsulta").text = "1"  # 1=Primeira Consulta
        SubElement(atendimento, "ans:dataAtendimento").text = guia.get("data_realizacao", "")
        
        # Procedimentos
        procedimentos = SubElement(guia_consulta, "ans:procedimentosExecutados")
        proc = SubElement(procedimentos, "ans:procedimento")
        SubElement(proc, "ans:codigoProcedimento").text = guia.get("codigo_procedimento", "")
        SubElement(proc, "ans:descricaoProcedimento").text = guia.get("descricao_procedimento", "")
        SubElement(proc, "ans:valorProcedimento").text = str(guia.get("valor_procedimento", "0.00"))
        
        # Valor total
        SubElement(guia_consulta, "ans:valorTotal").text = str(guia.get("valor_total", "0.00"))
        SubElement(guia_consulta, "ans:dataEmissao").text = guia.get("data_emissao", "")
    
    def _gerar_hash_lote(self, lote_data: dict) -> str:
        """Gera hash do lote para validação"""
        import hashlib
        conteudo = f"{lote_data.get('numero_lote', '')}{lote_data.get('valor_total_lote', '')}"
        return hashlib.md5(conteudo.encode()).hexdigest()[:16]
    
    def _prettify_xml(self, elem: Element) -> str:
        """Formata XML de forma legível"""
        rough_string = tostring(elem, encoding='unicode', method='xml')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode('utf-8')
    
    def gerar_nome_arquivo(self, operadora_codigo: str, numero_lote: str) -> str:
        """Gera nome padrão do arquivo XML"""
        data_str = date.today().strftime("%Y%m%d")
        return f"TISS_{operadora_codigo}_{numero_lote}_{data_str}.xml"
