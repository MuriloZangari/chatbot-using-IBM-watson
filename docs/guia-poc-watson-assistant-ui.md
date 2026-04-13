# Guia — primeiro fluxo no watsonx Assistant (PoC)

Este guia apoia a **Fase 2** do `plano-de-acao-poc-hibrida.md`: criar um assistente de **laboratório** com um **fluxo transacional mínimo** na interface do **watsonx Assistant**.

**O que este documento não faz:** substituir a documentação oficial IBM (menus, nomes de botões e telas mudam). Use-o como **checklist** e **escopo mínimo**.

---

## 1. O que você precisa antes

- Conta IBM com **watsonx Assistant** (ou Watson Assistant) habilitado para criação de assistentes.
- Navegador; tempo para ~30–60 min na primeira vez.
- Decisão de **nome** do assistente de teste (ex.: `poc-hibrido-seu-nome`).

---

## 2. Criar o assistente de laboratório

1. Acesse o **IBM Cloud** / console do **watsonx Assistant** conforme o caminho da sua organização.
2. **Criar assistant** novo (não use o assistente de produção da empresa).
3. Escolha idioma **pt-BR** se disponível.
4. Anote **sem colar em repositório público**:
   - **Assistant ID** (ou equivalente na URL / tela de configuração).
   - **Região** / URL base da API (ex.: `https://api.us-south.assistant.watson.cloud.ibm.com` — confirme na documentação da sua instância).

---

## 3. Um fluxo mínimo sugerido (Actions)

Objetivo: aprender **Actions**, **steps** e **transições**, sem integrar Portal ainda.

**Cenário fictício:** “Menu Pagamentos (simulado)”

| Step | Comportamento |
|------|----------------|
| 1 | Mensagem de boas-vindas + pergunta: “O que você quer fazer?” com opções **botões** ou entradas fixas: `Emitir boleto (simulado)` / `Ver ajuda sobre pagamentos` / `Voltar` |
| 2a (se Emitir)** | Mensagem fixa: “Em produção aqui chamaria a API do Portal. PoC: simulação concluída com sucesso.” |
| 2b (se Ajuda)** | Mensagem: “Na próxima fase, você colocará aqui um step de **conversational search** ou encaminhará para outra Action.” + botão “Voltar ao menu” |
| 3 | Opcional: confirmação “Posso ajudar em algo mais?” com `Sim` → volta ao step 1 / `Não` → encerra |

**Regras de aprendizado:**

- Use **uma Action** principal ou **subactions** — o importante é **percorrer** o editor de passos.
- **Publique** a versão draft (ou equivalente) para o **preview** funcionar.

---

## 4. Testar no Preview

1. Abra o **Preview** do assistente.
2. Percorra: cada opção do menu até ver as mensagens simuladas.
3. Anote **comportamentos estranhos** (loops, intents não capturadas) para ajustar depois.

---

## 5. O que guardar para a Fase 4 (SDK)

Quando for integrar por código, você vai precisar (valores **não** vão no Git):

- `WATSON_ASSISTANT_API_KEY` ou IAM API key do serviço.
- URL da API (região).
- `assistant_id` (ID do assistente).
- Opcional: `environment_id` (draft vs. publicado), conforme a API v2 que usar.

Crie um **`.env.example`** na PoC com nomes das variáveis e **placeholders** — sem chaves reais.

---

## 6. Como eu posso te ajudar daqui (sem acessar o IBM)

1. **Refinar o roteiro** do fluxo (mais simples ou mais próximo do “Ajuda pagamentos” + CTA).
2. **Revisar** o que você colar aqui (textos de steps, **sem** credenciais) — coerência com `proposta-arquitetura-hibrida-poc.md`.
3. **Depois de publicado:** escrever o **script Python** (`ibm-watson`) que chama `create_session` / `message` com as variáveis do seu `.env`.
4. **Troubleshooting** de erros de API (mensagens de erro, versão da API, formato do body).

---

## 7. Próximo passo imediato (sua sessão de trabalho)

1. Criar assistente de lab.
2. Implementar o **menu de 3 opções** + ramos **2a** e **2b** como acima.
3. Publicar e testar no Preview.
4. Copiar **só** `assistant_id` e **região** para um bloco de notas; gerar credencial de API para **Fase 4** quando for integrar.

Quando o fluxo estiver no ar, diga “preview OK” e seguimos para o **SDK** ou para o **step de conversational search** (Fase 3).

---

## Referências IBM (consultar versão atual)

- Documentação **watsonx Assistant** — *Building actions*, *Preview*, *API*.
- **API Reference** Assistant v2 (sessão, mensagem): [IBM Cloud API Docs — Assistant](https://cloud.ibm.com/apidocs/assistant-v2).
