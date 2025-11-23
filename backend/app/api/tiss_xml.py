from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from app.core.database import get_db
from app.schemas.tiss_xml import XMLTISSGenerateRequest, XMLTISSGenerateResponse
from app.services.tiss_xml_generator import TISSXMLGenerator
from app.models.tiss import TISSLote, TISSGuia, TISSOperadora, TISSProcedimento
from fastapi.responses import Response
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tiss-xml", tags=["TISS XML"])

@router.post("/gerar/{lote_id}", response_model=XMLTISSGenerateResponse)
async def gerar_xml_lote(
    lote_id: str,
    db: Session = Depends(get_db)
):
    """
    Gera arquivo XML TISS padrão ANS para um lote específico
    """
    try:
        lote = db.query(TISSLote).filter(TISSLote.id == lote_id).first()
        if not lote:
            raise HTTPException(status_code=404, detail="Lote não encontrado")
        
        operadora = db.query(TISSOperadora).filter(
            TISSOperadora.id == lote.operadora_id
        ).first()
        if not operadora:
            raise HTTPException(status_code=404, detail="Operadora não encontrada")
        
        guias = db.query(TISSGuia).filter(
            TISSGuia.lote_id == lote_id,
            TISSGuia.deleted_at == None
        ).all()
        
        if not guias:
            raise HTTPException(status_code=400, detail="Lote sem guias válidas")
        
        lote_data = {
            "numero_lote": lote.numero_lote,
            "data_criacao": lote.created_at.strftime("%Y-%m-%d"),
            "operadora_codigo": operadora.registro_ans,
            "operadora_nome": operadora.razao_social,
            "prestador_codigo": "000000",
            "prestador_nome": "Clínica Sanaris",
            "guias": [],
            "valor_total_lote": float(lote.valor_total_informado or 0),
            "quantidade_guias": len(guias)
        }
        
        for guia in guias:
            procedimentos = db.query(TISSProcedimento).filter(
                TISSProcedimento.guia_id == guia.id
            ).all()
            
            codigo_proc = procedimentos[0].codigo_procedimento if procedimentos else ""
            descricao_proc = procedimentos[0].descricao_procedimento if procedimentos else ""
            valor_proc = float(procedimentos[0].valor_unitario_informado or 0) if procedimentos else 0
            
            guia_data = {
                "numero_guia": guia.numero_guia_prestador,
                "data_emissao": guia.created_at.strftime("%Y-%m-%d"),
                "codigo_operadora": operadora.registro_ans,
                "numero_carteira": guia.numero_carteira or "",
                "nome_beneficiario": guia.nome_beneficiario or "",
                "codigo_prestador": guia.codigo_prestador_na_operadora or "000000",
                "nome_prestador": guia.nome_contratado or "Clínica Sanaris",
                "codigo_procedimento": codigo_proc,
                "descricao_procedimento": descricao_proc,
                "data_realizacao": guia.data_atendimento.strftime("%Y-%m-%d") if guia.data_atendimento else "",
                "valor_procedimento": valor_proc,
                "valor_total": float(guia.valor_total_informado or 0)
            }
            lote_data["guias"].append(guia_data)
        
        generator = TISSXMLGenerator()
        xml_content = generator.gerar_xml_lote(lote_data)
        filename = generator.gerar_nome_arquivo(operadora.registro_ans, lote.numero_lote)
        
        return XMLTISSGenerateResponse(
            success=True,
            filename=filename,
            xml_content=xml_content,
            message=f"XML gerado com sucesso: {len(guias)} guias"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar XML TISS: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar XML: {str(e)}")

@router.get("/download/{lote_id}")
async def download_xml_lote(
    lote_id: str,
    db: Session = Depends(get_db)
):
    """
    Faz download direto do arquivo XML do lote
    """
    try:
        result = await gerar_xml_lote(lote_id, db)
        
        return Response(
            content=result.xml_content.encode('utf-8'),
            media_type="application/xml",
            headers={
                "Content-Disposition": f"attachment; filename={result.filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Erro ao fazer download do XML: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao fazer download: {str(e)}")

@router.get("/validar/{lote_id}")
async def validar_xml_lote(
    lote_id: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Valida se o lote está pronto para gerar XML
    """
    try:
        lote = db.query(TISSLote).filter(TISSLote.id == lote_id).first()
        if not lote:
            raise HTTPException(status_code=404, detail="Lote não encontrado")
        
        guias = db.query(TISSGuia).filter(
            TISSGuia.lote_id == lote_id,
            TISSGuia.deleted_at == None
        ).all()
        
        erros = []
        avisos = []
        
        if not guias:
            erros.append("Lote sem guias")
        
        if not lote.operadora_id:
            erros.append("Operadora não definida")
        
        for idx, guia in enumerate(guias):
            if not guia.numero_guia_prestador:
                erros.append(f"Guia {idx+1}: Número da guia não definido")
            
            procedimentos = db.query(TISSProcedimento).filter(
                TISSProcedimento.guia_id == guia.id
            ).all()
            
            if not procedimentos:
                avisos.append(f"Guia {idx+1}: Sem procedimentos cadastrados")
            if not guia.valor_total_informado or guia.valor_total_informado == 0:
                avisos.append(f"Guia {idx+1}: Valor total zerado")
        
        return {
            "valido": len(erros) == 0,
            "erros": erros,
            "avisos": avisos,
            "total_guias": len(guias),
            "pode_gerar": len(erros) == 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao validar lote: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro na validação: {str(e)}")

@router.get("/relatorios/dashboard")
async def relatorios_dashboard(
    data_inicio: str = None,
    data_fim: str = None,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Dashboard de relatórios TISS com estatísticas gerais
    """
    try:
        from datetime import datetime
        
        # Query base
        query = db.query(TISSLote)
        
        # Filtros de data
        if data_inicio:
            query = query.filter(TISSLote.created_at >= datetime.fromisoformat(data_inicio))
        if data_fim:
            query = query.filter(TISSLote.created_at <= datetime.fromisoformat(data_fim))
        
        lotes = query.all()
        
        # Estatísticas gerais
        total_lotes = len(lotes)
        total_guias = sum(lote.quantidade_guias or 0 for lote in lotes)
        valor_total = sum(float(lote.valor_total_informado or 0) for lote in lotes)
        
        # Por operadora
        operadoras_stats = {}
        for lote in lotes:
            operadora = db.query(TISSOperadora).filter(
                TISSOperadora.id == lote.operadora_id
            ).first()
            
            if operadora:
                op_nome = operadora.razao_social
                if op_nome not in operadoras_stats:
                    operadoras_stats[op_nome] = {
                        "nome": op_nome,
                        "quantidade_lotes": 0,
                        "quantidade_guias": 0,
                        "valor_total": 0
                    }
                
                operadoras_stats[op_nome]["quantidade_lotes"] += 1
                operadoras_stats[op_nome]["quantidade_guias"] += lote.quantidade_guias or 0
                operadoras_stats[op_nome]["valor_total"] += float(lote.valor_total_informado or 0)
        
        # Por status
        status_stats = {}
        for lote in lotes:
            status = lote.status
            if status not in status_stats:
                status_stats[status] = {
                    "status": status,
                    "quantidade": 0,
                    "valor": 0
                }
            status_stats[status]["quantidade"] += 1
            status_stats[status]["valor"] += float(lote.valor_total_informado or 0)
        
        return {
            "resumo": {
                "total_lotes": total_lotes,
                "total_guias": total_guias,
                "valor_total": valor_total
            },
            "por_operadora": list(operadoras_stats.values()),
            "por_status": list(status_stats.values())
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatórios: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatórios: {str(e)}")
