# Watson Assistant, Watson Orchestrate e PoC “híbrido”

Documento de apoio aos estudos: **árvore de decisão / fluxo transacional** (Watson Assistant) + **LLM com RAG** (watsonx.ai nesta PoC), e como isso se relaciona com **watsonx Orchestrate**.

---

## 1. O que a PoC usa hoje (`WATSON_AI`)

| Camada | Tecnologia |
|--------|------------|
| **Geração (LLM)** | **watsonx.ai** via SDK Python `ibm-watsonx-ai` (`ModelInference`) — **não** é o motor de diálogo do Watson Assistant. |
| **RAG** | Embeddings locais (`sentence-transformers`) + corpus JSON. |
| **“Roteador” leve** | Python (`response_router`): calculadora determinística → senão LLM. **Simula** um ramo transacional vs. informativo **sem** desenhar Actions no Assistant. |

Ou seja: a PoC **já simula** um híbrido **no código**, mas **não** executa os **Actions/Steps** desenhados na UI do Watson Assistant.

---

## 2. Watson Assistant (watsonx Assistant): fluxos e SDK

### O que você descreveu (Actions, steps, `next_step`, subações)

- No **Assistant**, o desenho do fluxo é **authoring** (interface de **Actions** / passos, transições, integrações).
- O **SDK oficial** (`ibm-watson` / Assistant v2 em Node, Python, Java, etc.) é, em geral, focado em **tempo de execução**:
  - criar sessão,
  - enviar **mensagem** do usuário,
  - receber respostas e **opções** geradas pelo assistente já configurado.

**Não** há, na prática, um substituto completo de “desenhar toda a árvore só em Python” como se fosse código-fonte do fluxo — o **desenho** continua sendo feito na **experiência de construção** do Assistant (ou via **export/import** de conteúdo).

### Authoring “como código” (indireto)

- **Export/import** de skills / backup em **JSON** (e APIs relacionadas a export de rascunho, conforme documentação vigente da IBM) permitem **versionar** o conteúdo no Git e **reimportar** ambientes.
- Isso é **automação do artefato**, não necessariamente “uma API `create_step(...)`” para cada linha do diálogo.

**Conclusão:** use o **SDK** para **integrar** o seu orquestrador (ou a PoC) **ao Assistant em runtime**; use **UI + export JSON** (e políticas de release) para **evoluir** o fluxo transacional como produto.

---

## 3. Watson Orchestrate (watsonx Orchestrate)

Produto **diferente** do “editor de Actions” do Assistant, embora possa **conectar** componentes do ecossistema.

- Foco em **orquestração de agentes** (multi-agente), **ferramentas** (tools), chamadas a **APIs**, integração com **watsonx.ai**, e possibilidade de envolver **instâncias do Watson Assistant** como **colaboradores**.
- Há **ADK** (CLI/APIs) para **criar/importar agentes** (YAML/JSON/Python), registrar agentes, canais (ex.: web chat), etc.
- **Não** é o mesmo que “redesenhar a árvore clássica de Actions passo a passo” na tela do Assistant: é uma camada de **agentes e orquestração** em cima de **habilidades**, **LLMs** e **integrações**.

Para o objetivo “**árvore transacional + fallback LLM**”:

- **Assistant** continua forte para **fluxos guiados** e integrações já amarradas ao **Portal** via extensões.
- **Orchestrate** pode ser o lugar onde um **agente** decide **quando** chamar o Assistant, **quando** chamar uma API, **quando** delegar a um modelo generativo — dependendo da **arquitetura** que o time IBM/empresa adotar.

---

## 4. Como enriquecer a PoC atual (caminhos práticos)

| Abordagem | O que adiciona | Esforço |
|-----------|----------------|---------|
| **A. Simulador no código (Python/Node)** | Máquina de estados simples: menus fictícios → “slot” preenchido → só então LLM/RAG. Amplia o que já existe com `response_router` + `calculadora`. | Baixo; sem custo Assistant extra. |
| **B. Watson Assistant real** | Instância no IBM Cloud; orquestrador chama **message API** com `session_id`; fluxo transacional **real** no Assistant; ramo “dúvida aberta” pode ser **action** que chama seu **backend** (como hoje o orquestrador chama integrações). | Médio; alinhado ao produto fase 2. |
| **C. watsonx Orchestrate** | Piloto: um **agente** com **tools** (HTTP Portal), opcionalmente **Assistant** como colaborador, **LLM** para tarefas abertas. | Médio/alto; depende de licença, ADK e desenho IBM. |

A PoC **não precisa** trocar o LLM atual por Orchestrate **só** para ter “árvore”: a árvore pode continuar no **Assistant** (B) e o Orchestrate entra se o desenho for **multi-agente + APIs** (C).

---

## 5. Respostas diretas às suas perguntas

| Pergunta | Resposta curta |
|----------|------------------|
| **Existe SDK para codar o fluxo do Assistant em vez da UI?** | O SDK cobre sobretudo **runtime** (mensagens/sessão). O **fluxo** em si é **authoring** na ferramenta + **export/import** de artefatos; não espere um DSL completo “só código” equivalente a cada clique da UI em todos os cenários. |
| **Orchestrate substitui a árvore do Assistant?** | **Não** 1:1. É camada de **agentes e orquestração**; pode **usar** Assistant e APIs junto. |
| **Como usar Orchestrate para árvores de diálogo?** | Modelar como **agente(s)** com **instruções**, **tools** e **passagem de contexto**, e/ou **Assistant** embutido — não como clone pixel-a-pixel do editor de Steps. |

---

## 6. Referências oficiais (consultar versão atual)

- **watsonx Assistant** — API v2: [IBM Cloud API Docs — Assistant](https://cloud.ibm.com/apidocs/assistant-v2)  
- **Backup / export / import** — documentação `assistant` na IBM (tópicos de backup e skills).  
- **watsonx Orchestrate** — documentação e ADK: [IBM Documentation — watsonx Orchestrate](https://www.ibm.com/docs/en/watsonx/watson-orchestrate) e [developer.watson-orchestrate.ibm.com](https://developer.watson-orchestrate.ibm.com)  

Produtos e endpoints mudam; validar sempre na documentação da sua região/conta.

---

## 7. Relação com o orquestrador (NestJS)

O **orquestrador** que vocês têm hoje já é o padrão **B**: chama o **Assistant** via API e integra **Portal**. Para **LLM + RAG**, o desenho pode ser: **Assistant** trata intenção/menu; um **action** ou **webhook** encaminha ao **serviço** que chama watsonx (como na PoC Python), sem obrigar o fluxo transacional a viver dentro do mesmo processo do LLM.

Este arquivo **não** substitui decisão de arquitetura com o time IBM — consolida o vocabulário e as opções para os estudos da PoC.
