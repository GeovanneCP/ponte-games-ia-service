import os
import json
import io
import time
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from PIL import Image

app = FastAPI(title="Ponte Games - IA Validator Service", version="1.0.0")

# Libera CORS para testes diretos via Swagger ou front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResultadoAnaliseDescarte(BaseModel):
    valido: bool = Field(description="True se for resíduo reciclável legítimo.")
    categoria: str = Field(description="Categoria detectada.")
    material_detectado: str = Field(description="Descrição curta do item.")
    confianca: float = Field(description="Grau de certeza entre 0.0 e 1.0.")
    pontos_xp: int = Field(description="XP concedido.")
    mensagem_gamificada: str = Field(description="Mensagem educativa gamificada.")
    motivo_rejeicao: str = Field(default="", description="Motivo se for rejeitado.")

@app.get("/")
def health_check():
    return {"status": "online", "service": "Ponte Games IA Validator"}

@app.post("/api/v1/ia/validar", response_model=ResultadoAnaliseDescarte)
async def validar_descarte(foto: UploadFile = File(...)):
    if not foto.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="O arquivo enviado deve ser uma imagem.")

    try:
        conteudo = await foto.read()
        imagem = Image.open(io.BytesIO(conteudo))
        imagem.thumbnail((1024, 1024))

        client = genai.Client()
        prompt_sistema = """
        Você é o motor de visão computacional da plataforma CitizenTech "Ponte Games".
        Sua função é avaliar imagens submetidas por cidadãos em estações de coleta para validar reciclagem e descartes conscientes.
        Diretrizes:
        1. Itens válidos: Lixo eletrônico (fios, cabos, periféricos, placas, pilhas), plásticos, metais e papelão.
        2. Itens inválidos: Restos de comida, fotos escuras, selfies ou sem contexto.
        3. Gamificação de XP: Eletrônico (100 a 200 XP), Metal (50 XP), Plástico (30 XP), Papel (20 XP), Inválido (0 XP).
        """

        modelos = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.1-flash-lite"]
        configuracao = types.GenerateContentConfig(
            system_instruction=prompt_sistema,
            response_mime_type="application/json",
            response_schema=ResultadoAnaliseDescarte,
            temperature=0.2,
        )

        for modelo in modelos:
            try:
                resposta = client.models.generate_content(
                    model=modelo,
                    contents=[imagem, "Analise esta foto de descarte ecológico e preencha os dados do descarte:"],
                    config=configuracao,
                )
                return json.loads(resposta.text)
            except Exception:
                time.sleep(1)
                continue

        raise HTTPException(status_code=503, detail="Modelos de IA indisponíveis no momento.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    porta = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=porta)