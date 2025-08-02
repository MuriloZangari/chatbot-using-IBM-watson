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

## Por que escolhi o modelo `granite-3-3-8b-instruct`

- Modelo de 8B parâmetros da família Granite, otimizado para seguir instruções e responder perguntas com clareza e precisão.
- Suporte a **português** e mais de 12 idiomas, ideal para o público-alvo.
- Capacidade de manter **conversas com histórico extenso** (até 131.072 tokens).
- Disponível gratuitamente no Watsonx.ai, com integração direta via SDK (sem necessidade de endpoint).
- Projetado para raciocínio lógico, explicações estruturadas e **aplicações em finanças, atendimento e educação**.
- Licença Apache 2.0 e código aberto via Hugging Face, permitindo transparência e futura evolução do PoC.

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

## Mini-RAG com contexto confiável

Para evitar alucinações e garantir respostas baseadas em fatos reais, o PoC implementa uma técnica simples de RAG (Retrieval-Augmented Generation).

---

## Como funciona

- **Fonte confiável** (ex: Resolução CMN nº 4.744) é inserida no início da conversa
- O conteúdo é adicionado ao `chat_history` como se fosse uma interação anterior
- O modelo prioriza esse contexto ao gerar respostas, mesmo sem acesso à internet

---

## Vantagens do mini-RAG

✅ Elimina alucinações jurídicas como leis inexistentes  
✅ Melhora a precisão e confiabilidade do chatbot  
✅ Facilita explicação técnica para o time de IA  
✅ Não exige banco vetorizado nem FAISS — é leve, direto e eficaz  

---

## Exemplo aplicado

```text
Usuário: Contexto sobre prazo legal para financiamento de veículos  
Assistente: Segundo o Banco Central do Brasil e a Resolução CMN nº 4.744/2019, o prazo máximo para financiamento...

Claro! Aqui está o trecho completo em Markdown (formato `.md`) para você colar no final do seu `poc-presentation.md`:

````md
---

## 📉 Problemas com Cálculos Iniciais

Durante os testes com o modelo `granite-3-3-8b-instruct`, observamos inconsistências em cálculos financeiros simples, como:

```text
"Parcela aproximada: R$ 2.435,42"  ❌  
Valor esperado: R$ 1.807,62
````

> Isso indicava que o modelo aplicava a fórmula incorretamente ou cometia erros aritméticos.

---

## 🔬 Testes com o Prompt Lab

Para investigar:

* Usamos o mesmo prompt no Prompt Lab do Watsonx
* Comparamos diferentes modelos sob o mesmo cenário
* Aplicamos a fórmula padrão de financiamento com juros compostos

---

## 🧪 Comparativo de Modelos

| Questão                      | granite-3-3-8b-instruct ❌    | mistral-medium-2505 ✅         |
| ---------------------------- | ---------------------------- | ----------------------------- |
| Cálculo da parcela com juros | Errado por mais de R\$ 500   | Correto com erro < R\$ 10     |
| Etapas numéricas             | Parcial/incompletas          | Claras, passo a passo         |
| Uso de exponenciação         | Alucinação ou arredondamento | Preciso como Python           |
| Aviso de estimativa          | Ausente na maioria das vezes | Presente de forma consistente |

---

## 🔁 Troca para Mistral

Diante da diferença clara de desempenho, o modelo foi trocado:

✅ Novo modelo: `mistral-medium-2505`
✅ Melhor desempenho em cálculos
✅ Respostas mais transparentes e éticas

---

## 🧮 Ensinar o modelo a calcular

Atualizamos o `base_prompt.txt` com:

* Fórmula detalhada da parcela com juros compostos
* Instruções para exibir **todas as etapas**
* Exemplo explícito com resultado validado em Python:

```text
(1 + 0.015) ** -36 = 0.586550  
1 - 0.586550 = 0.413450  
750 / 0.413450 = 1.815,03 ✅
```

---

## ✅ Resultado final após calibragem

```text
Usuário: Quero financiar R$ 50.000 em 36 vezes com 1,5% de juros ao mês. Quanto vou pagar por parcela?
Assistente:

1. Valor × taxa = 50.000 × 0,015 = 750  
2. (1 + 0,015)^-36 ≈ 0,586550  
3. 1 - 0,586550 ≈ 0,413450  
4. Parcela = 750 / 0,413450 ≈ 1.815,03  

Parcela: **R$ 1.815,03**
```

> O modelo agora responde com **precisão matemática**, clareza e segurança jurídica.

```

Se quiser, posso também converter esse trecho direto para PDF com Marp ou testar no VSCode. Deseja isso?
```
