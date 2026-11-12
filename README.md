# 🌱 Ponte Games / EcoDrop — Microsserviço de Validação por IA

Microsserviço REST desenvolvido em **Python (FastAPI)** integrado aos modelos multimodais **Google Gemini** para validação automática de descartes recicláveis, filtro anti-fraude e cálculo de recompensas gamificadas (XP).

Este serviço compõe a arquitetura desacoplada da plataforma **Ponte Games / EcoDrop** (projeto acadêmico FIAP), atuando como motor de visão computacional consumido pelo backend principal em Java (Spring Boot) e integrado às estações físicas de coleta IoT.

---

## 👥 Integrantes do Grupo

* **Geovanne Coneglian Passos** — RM 562673
* **Guilherme Soares de Almeida** — RM 563143
* **Lucas Silva Gastão Pinheiro** — RM 563960

---

## 🔗 Links da Entrega

* **🌐 Aplicação Workwi:** https://wokwi.com/projects/480263756551656449
* **📄 Documentação Interativa (Swagger UI):** https://ponte-games-ia-service.onrender.com/docs
* **🎥 Vídeo Explicativo (YouTube):** *Insira aqui o link do vídeo no YouTube*

---


## 🌐 Ambiente em Produção (Render)

* **Base URL:** `https://ponte-games-ia-service.onrender.com`
* **Documentação Interativa (Swagger UI):** `https://ponte-games-ia-service.onrender.com/docs`
* **Health Check:** `GET /`

> **Nota sobre Cold Start:** Hospedado no plano gratuito do Render. Após 15 minutos de inatividade, a primeira requisição pode levar entre 30 e 50 segundos para reativar o container. Recomenda-se configurar o *timeout* de cliente HTTP para **60 segundos**.

---

## 🚀 Funcionalidades

* **Classificação Multimodal de Resíduos:** Identifica materiais a partir de imagens (`Lixo Eletrônico`, `Plástico`, `Metal` e `Papel/Papelão`).
* **Filtro Anti-Fraude:** Rejeita imagens sem contexto de descarte, fotos escuras/ilegíveis, selfies ou resíduos orgânicos/hospitalares, zerando a pontuação e detalhando o motivo da recusa.
* **Gamificação Dinâmica (XP):** Atribui pontos conforme o tipo de resíduo:
  * **Lixo Eletrônico:** 100 a 200 XP
  * **Metal:** 50 XP
  * **Plástico:** 30 XP
  * **Papel/Papelão:** 20 XP
  * **Inválido:** 0 XP
* **Resiliência e Fallback Automático:** Alterna automaticamente entre modelos da família Gemini (`gemini-3.5-flash-lite`, `gemini-3.8-flash` e `gemini-3.1-flash-lite`) em caso de pico de demanda e redimensiona imagens (`max 1024x1024`) antes da inferência.
* **Contrato JSON Estrito:** Respostas validadas via Pydantic (`Structured Outputs`).

---

## 🛠️ Stack Tecnológica

* **Linguagem:** Python 3.11
* **Framework Web:** FastAPI & Uvicorn
* **IA Generativa / Visão Computacional:** Google GenAI SDK (`google-genai`)
* **Validação de Dados:** Pydantic v2
* **Processamento de Imagem:** Pillow (PIL)

---

## 📡 Contrato da API

### `POST /api/v1/ia/validar`

Recebe uma imagem via `multipart/form-data` e retorna o veredito da classificação.

* **Content-Type:** `multipart/form-data`
* **Campo obrigatório:** `foto` (`file` — JPG, PNG ou WEBP)

#### Exemplo de Resposta (`200 OK` — Descarte Válido)
```
{
  "valido": true,
  "categoria": "Lixo Eletrônico",
  "material_detectado": "Cabos coaxiais com conectores",
  "confianca": 0.98,
  "pontos_xp": 150,
  "mensagem_gamificada": "Excelente descarte, Player! Mais lixo eletrônico redirecionado corretamente para a reciclagem. Você ganhou +150 XP no Ponte Games!",
  "motivo_rejeicao": ""
}
```

Exemplo de Resposta (200 OK — Descarte Inválido)
```
{
  "valido": false,
  "categoria": "Inválido",
  "material_detectado": "Restos de alimentos orgânicos",
  "confianca": 0.95,
  "pontos_xp": 0,
  "mensagem_gamificada": "Ops! Esse item não pode ser pontuado nesta estação de coleta.",
  "motivo_rejeicao": "Resíduos orgânicos não são aceitos nos pontos de coleta reciclável."
}
```

### 🔑 Como obter sua chave de API (`GEMINI_API_KEY`)

Para rodar o microsserviço localmente, você precisará de uma chave gratuita do Google AI Studio:

1. Acesse o **[Google AI Studio](https://aistudio.google.com/)** e faça login com sua conta Google.
2. No menu lateral esquerdo, clique em **Get API key** (ou acesse diretamente [aistudio.google.com/apikey](https://aistudio.google.com/apikey)).
3. Clique no botão **Create API key**.
4. Selecione um projeto existente no Google Cloud ou clique em **Create API key in new project** para gerar um novo automaticamente.
5. Copie a chave gerada (ela começa com `AIza...`) e guarde-a em local seguro — **nunca suba essa chave diretamente no código ou no GitHub**.

## ⚙️ Execução Local

Instale as dependências:

pip install -r requirements.txt

Configure a variável de ambiente com a chave do Google AI Studio:

$env:GEMINI_API_KEY="SUA_CHAVE_AQUI"

Inicie o servidor:

python main.py

## 🧠 Como a Inteligência Artificial Foi Utilizada

Em vez de treinar um modelo tradicional de classificação de imagens do zero (que exigiria milhares de fotos rotuladas e alto custo computacional), o projeto utiliza **IA Generativa Multimodal (Vision-Language Models)** através do SDK oficial **Google GenAI** (`google-genai`).

### 1. Visão Computacional Multimodal (Análise de Imagem)
Quando o cidadão registra uma foto do resíduo, o microsserviço pré-processa a imagem em memória (redimensionando para no máximo `1024x1024` pixels via Pillow para reduzir latência e consumo de banda) e a envia junto a um *System Prompt* especializado para os modelos da família **Google Gemini**. A IA interpreta o contexto visual da cena para identificar o material predominante (`Lixo Eletrônico`, `Plástico`, `Metal` ou `Papel/Papelão`).

### 2. Engenharia de Prompt e Filtro Anti-Fraude
O comportamento do modelo foi calibrado com temperatura baixa (`temperature = 0.2`) para garantir respostas determinísticas e rigorosas na auditoria:
* **Validação de Legitimidade:** A IA diferencia resíduos recicláveis reais de tentativas de fraude (como selfies, fotos totalmente escuras/borradas, telas de computador ou restos de comida orgânica), marcando `valido: false` e preenchendo automaticamente o campo `motivo_rejeicao` para orientar o usuário.
* **Cálculo Dinâmico de Gamificação (XP):** Com base na complexidade e no impacto ambiental do material identificado na imagem, a própria IA atribui a pontuação correspondente (100 a 200 XP para lixo eletrônico, 50 XP para metal, 30 XP para plástico e 20 XP para papel) e redige uma mensagem personalizada de engajamento.

### 3. Saídas Estruturadas (Structured Outputs com Pydantic)
Para permitir que o backend em **Java (Spring Boot)** consuma o resultado sem falhas de *parsing*, a IA é forçada a responder estritamente dentro de um contrato JSON definido via **Pydantic** (`ResultadoAnaliseDescarte`), eliminando textos soltos ou alucinações de formato.

### 4. Resiliência com Fallback Automático de Modelos
Para garantir alta disponibilidade durante testes e apresentações, o código implementa uma fila de contingência (*fallback*): se o modelo principal (`gemini-3.5-flash-lite`) sofrer limitação de taxa ou indisponibilidade momentânea, a API alterna automaticamente para `gemini-3.8-flash` ou `gemini-3.1-flash-lite`.

---





