---
marp: true
theme: default
class: lead
paginate: true
---

# Escolha Tecnológica para o PoC  
**Watsonx.ai vs Watson Assistant**

---

## Plataformas Consideradas

- **Watson Assistant**  
  Chatbot com fluxos estruturados, baseado em intents e entidades.

- **Watsonx.ai**  
  Plataforma de IA generativa com foundation models e prompts.

---

## O Desafio do PoC

- Criar um chatbot simples sobre:
  - Financiamento de veículos
  - Parcelamento
  - Taxas de juros
  - Cálculos financeiros

- Precisava responder perguntas **diversas e abertas**, com linguagem natural.

---

## Por que escolhi o Watsonx.ai?

✅ Maior flexibilidade com linguagem natural  
✅ Mais alinhado com tendências de IA generativa  
✅ Entrega rápida em menos de 10 horas  
✅ Experiência prévia com Ollama e LLMs

---

## Resultado

- Chatbot funcional via linha de comando (CLI)
- Respostas naturais e contextuais
- Código limpo, leve e facilmente adaptável

---

## Passo a passo do desenvolvimento

1. ✅ Criei conta na IBM Cloud e acessei o Watsonx.ai Studio
2. ✅ Explorei o Prompt Lab com o modelo gratuito `granite-3-3-8b-instruct`
3. ✅ Validei um prompt base para perguntas sobre financiamento de veículos
4. ✅ Salvei esse prompt como um **ativo tipo "Modelo de Prompt"** no projeto
5. ✅ Criei estrutura de projeto local com:
   - `prompts/base_prompt.txt`
   - `cli_chatbot/main.py`
   - `cli_chatbot/watson_client.py`
6. ✅ Configurei variáveis de ambiente com `.env` e `python-dotenv`
7. ✅ Integrei o Watsonx via **SDK oficial `ibm-watsonx-ai`** (sem criar endpoint)

---

## Observação sobre o Ativo Criado

- O ativo salvo (`Modelo de Prompt`) no Watsonx Studio **não é um modelo funcional nem um serviço**.
- Ele funciona como um **repositório de referência**, útil para testes no Prompt Lab.
- A execução do PoC é feita localmente via SDK, com chamadas diretas ao modelo Granite.

---

## Conclusão

> A escolha do Watsonx.ai demonstrou domínio de tecnologias emergentes em IA, alinhamento com o propósito do PoC e aproveitamento máximo do tempo disponível.
