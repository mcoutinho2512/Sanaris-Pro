from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/cfm-embed-test", response_class=HTMLResponse)
async def cfm_embed_test():
    """Página de teste para embed do CFM"""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Teste CFM Embed - Sanaris Pro</title>
        <style>
            body {
                margin: 0;
                padding: 20px;
                font-family: Arial, sans-serif;
                background: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #1E40AF;
                margin-bottom: 20px;
            }
            .info {
                background: #E0F2FE;
                border-left: 4px solid #0284C7;
                padding: 15px;
                margin-bottom: 20px;
            }
            .test-section {
                margin-bottom: 30px;
            }
            iframe {
                width: 100%;
                height: 600px;
                border: 2px solid #ddd;
                border-radius: 4px;
            }
            .error {
                background: #FEE2E2;
                border-left: 4px solid #EF4444;
                padding: 15px;
                margin-top: 20px;
            }
            .success {
                background: #D1FAE5;
                border-left: 4px solid #10B981;
                padding: 15px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 Teste de Embed do Portal CFM</h1>
            
            <div class="info">
                <strong>ℹ️ Sobre este teste:</strong><br>
                Estamos testando se o portal do CFM (Conselho Federal de Medicina) permite ser incorporado via iframe.
                Muitos sites bloqueiam isso por questões de segurança usando o header X-Frame-Options.
            </div>

            <div class="test-section">
                <h2>Teste 1: Portal CFM Principal</h2>
                <p>Tentando incorporar: <a href="https://portal.cfm.org.br/" target="_blank">https://portal.cfm.org.br/</a></p>
                <iframe src="https://portal.cfm.org.br/" title="Portal CFM"></iframe>
            </div>

            <div class="test-section">
                <h2>Teste 2: Consulta de Médicos CFM</h2>
                <p>Tentando incorporar: <a href="https://portal.cfm.org.br/busca-medicos/" target="_blank">https://portal.cfm.org.br/busca-medicos/</a></p>
                <iframe src="https://portal.cfm.org.br/busca-medicos/" title="Busca Médicos CFM"></iframe>
            </div>

            <div class="success">
                <strong>✅ Se você vê o conteúdo do CFM acima:</strong><br>
                O embed está funcionando! Você pode incorporar o portal CFM no sistema.
            </div>

            <div class="error">
                <strong>❌ Se você vê uma página em branco ou erro:</strong><br>
                O CFM bloqueia incorporação via iframe. Neste caso, as alternativas são:<br>
                • Usar um link que abre em nova aba<br>
                • Criar um proxy reverso (mais complexo)<br>
                • Usar a API do CFM (se disponível)
            </div>

            <div style="margin-top: 30px; padding: 20px; background: #F3F4F6; border-radius: 4px;">
                <h3>📋 Resultado do Teste:</h3>
                <p>Abra o console do navegador (F12) para ver se há erros de X-Frame-Options ou CSP.</p>
                <p><strong>Volte para o Swagger:</strong> <a href="/docs" target="_blank">http://localhost:8888/docs</a></p>
            </div>
        </div>

        <script>
            // Detectar se o iframe carregou
            window.addEventListener('load', function() {
                const iframes = document.querySelectorAll('iframe');
                iframes.forEach((iframe, index) => {
                    iframe.addEventListener('load', function() {
                        console.log(`✅ Iframe ${index + 1} carregou com sucesso`);
                    });
                    iframe.addEventListener('error', function() {
                        console.error(`❌ Iframe ${index + 1} falhou ao carregar`);
                    });
                });
            });
        </script>
    </body>
    </html>
    """
    
    return html_content
