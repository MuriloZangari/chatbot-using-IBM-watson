# Parâmetros de geração (watsonx.ai / `ModelInference`)

Este documento descreve os parâmetros usados em **`get_default_params()`** em `cli_chatbot/watson_client.py` e como eles influenciam a saída do modelo no contexto desta PoC (RAG + tom institucional).

Implementação de referência:

```82:91:/home/murilo-zangari/WATSON_AI/cli_chatbot/watson_client.py
def get_default_params():
    return {
        "decoding_method": "greedy",        # Obrigatório
        "max_new_tokens": 1000,             # Obrigatório
        "stop_sequences": ["Usuário:"],     # Recomendado

        # Parâmetros opcionais:
        "temperature": 0.2,                 # Menor temperatura = mais determinístico
        "repetition_penalty": 1.1           # Evita repetições excessivas
    }
```

Os nomes exatos e o comportamento podem seguir a documentação atual do SDK **`ibm-watsonx-ai`** e do modelo escolhido (`WATSONX_MODEL_ID`).

---

## `decoding_method`: `"greedy"`

- **Efeito:** em cada passo de geração, escolhe o token de **maior probabilidade** (decodificação gulosa), sem amostragem aleatória.
- **Consequência:** respostas mais **estáveis e reproduzíveis**; favorece **aderência** ao prompt e ao contexto RAG, com menos “criatividade” imprevisível.
- **Risco:** em alguns modelos, greedy pode favorecer **repetição** de frases; por isso costuma combinar com `repetition_penalty`.

Para chatbot com texto recuperado de acervo, greedy é em geral **adequado**.

---

## `max_new_tokens`: `1000`

- **Efeito:** limite superior de tokens **novos** gerados na continuação (não inclui o prompt).
- **1000** é **generoso** para respostas em parágrafos ou listas; reduz risco de cortar a resposta no meio em fluxos explicativos.
- **Ajuste:** diminuir (ex.: 400–600) se a política for respostas mais curtas, menor latência ou menor custo por chamada; aumentar apenas se houver cortes frequentes no fim.

---

## `stop_sequences`: `["Usuário:"]`

- **Efeito:** a geração **para** quando o modelo emitiria essa sequência — aqui usada para evitar que o modelo **simule** um novo turno do usuário após responder.
- **Contexto do projeto:** o prompt montado em `ask_watson` inclui `Usuário: {pergunta}`; sem `stop_sequences`, modelos costumam continuar o diálogo fictício (`Usuário: ...`).

É uma proteção **importante** para o formato de prompt atual.

---

## `temperature`: `0.2`

- **Efeito típico (em modos com amostragem):** valores **baixos** reduzem aleatoriedade e deixam a saída mais **determinística**.
- **Com `decoding_method: greedy`:** em muitas stacks, a temperatura **pouco ou nada altera** o resultado, porque não há amostragem — a escolha já é argmax. A intenção no código é documentar preferência por **comportamento previsível**; validar no SDK/modelo se o parâmetro é ignorado em greedy.
- **Se no futuro** mudarem para decodificação com amostragem (ex.: sampling), `temperature` passa a ser um **alavanca real** para variar criatividade vs. consistência.

---

## `repetition_penalty`: `1.1`

- **Efeito:** penaliza a repetição dos mesmos tokens (valor **1.0** = neutro; **> 1** reduz repetição).
- **1.1** é **moderado:** ajuda contra loops verbais sem ser tão agressivo a ponto de atrapalhar listas ou nomes que naturalmente repetem termos.

Experimentos na PoC: testar **1.05–1.2** se notar repetição excessiva ou, no extremo oposto, estranheza na lista de marcas/dados.

---

## Tabela rápida (cenário RAG + institucional)

| Parâmetro | Papel neste projeto |
|-----------|---------------------|
| Greedy | Estabilidade e fidelidade ao contexto. |
| `max_new_tokens` | Teto de tamanho da resposta; tunar por custo/comprimento desejado. |
| `stop_sequences` | Evita continuação como “Usuário:”. |
| `temperature` | Intenção de baixa aleatoriedade; efeito prático depende do modo de decodificação. |
| `repetition_penalty` | Reduz repetições irritantes sem ser extremo. |

---

## Como experimentar na PoC

1. Manter pergunta e corpus **fixos**; variar **um** parâmetro de cada vez.
2. Comparar: **fidelidade ao RAG**, **repetição**, **comprimento**, **cortes** no final.
3. Documentar o `model_id` e a data — comportamento pode mudar entre versões do modelo.

---

## Ver também

- `docs/montagem-do-prompt-llm.md` — montagem do prompt enviado ao modelo  
- `cli_chatbot/watson_client.py` — `get_default_params`, `ask_watson`  
