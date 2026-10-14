# FutureAI Radar — Coletor V2

Protótipo acadêmico em Python para descobrir notícias relacionadas à **indústria esportiva**, extrair o conteúdo e selecionar resultados relevantes. **Não classifica as notícias em categorias**: clustering/LLM são etapas posteriores.

## O que mudou da V1

- **Janela D-2 configurável**: por padrão, considera notícias publicadas *anteontem*, no horário de Brasília. Datas ausentes ou fora da janela são rejeitadas; o campo `seendate` do GDELT não é confundido com data de publicação.
- **Fontes independentes**: Google News (biblioteca `gnews`), Bing News RSS e GDELT DOC API. Também aceita RSS de portais informados em `feeds.txt`.
- **URLs originais**: links intermediários do Google News são decodificados quando possível. Falhas são registradas, não disfarçadas.
- **Texto integral**: usa Trafilatura para extrair o corpo da matéria, sem menus e comentários. Não contorna paywalls nem proteções anti-bot.
- **Deduplicação**: por URL/título e similaridade do texto extraído.
- **Relevância**: pontuação heurística (TF-IDF do título e do conteúdo + completude), com filtro amplo de contexto esportivo e tentativa de diversificar os domínios. **Não é uma avaliação humana nem um modelo semântico treinado.**
- **Auditoria**: gera `rejeitadas.csv` e `relatorio.json` para identificar o que não foi possível aproveitar.

## Instalação (Windows, Git Bash no VS Code)

No diretório do projeto:

```bash
python --version
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

Não copie a pasta `.venv` entre computadores; recrie-a em cada máquina.

## Executar

Primeiro teste com poucos candidatos (pode levar alguns minutos por causa da extração):

```bash
python coletar_urls.py --candidatas 10 --limite 5
```

Executar coleta maior:

```bash
python coletar_urls.py --tema "indústria esportiva" --candidatas 40 --limite 20
```

O parâmetro `--candidatas 40` é **por fonte**, não o total geral. O Bing RSS pode retornar menos do que o solicitado.

### Como interpretar D-2

A implementação inicial assume que **D-2 significa o dia de anteontem**. Ex.: execução em 13/10/2026 coleta publicações datadas de **11/10/2026**.

```bash
# Notícias de ontem (D-1)
python coletar_urls.py --dias-atras 1

# Hoje e ontem (dois dias corridos, incluindo hoje)
python coletar_urls.py --dias-atras 0 --janela-dias 2

# Janela de três dias terminando anteontem (D-4 até D-2)
python coletar_urls.py --dias-atras 2 --janela-dias 3
```

Se a equipe quis dizer outra coisa com “D-2” (por exemplo, atraso mínimo de dois dias), a regra precisa ser ajustada.

## Saída

O programa cria `data/` com:

- `noticias.csv` — notícias finais, com texto e pontuação (abre no Excel).
- `noticias.json` — mesmo conjunto, estruturado para o pipeline posterior.
- `candidatas.json` — URLs descobertas antes de baixar as páginas.
- `rejeitadas.csv` — registros descartados e motivo (data, falha de extração, duplicidade, etc.).
- `relatorio.json` — quantidades por etapa e erros das fontes.

**Não existe garantia de retornar 20 notícias**: se a janela for estreita ou os portais bloquearem a extração, o programa retorna menos e avisa. A pontuação de relevância é relativa e precisa ser validada manualmente com uma amostra.

## Observações técnicas

- Google News pode retornar URLs intermediárias que não podem ser decodificadas em alguns casos.
- Bing News RSS é uma interface pública, não uma API contratual estável: pode mudar ou limitar resultados.
- GDELT registra quando viu uma matéria, o que não garante a data original de publicação. Para entrar na seleção, precisa ser possível confirmar a data no artigo.
- Sites com paywall, bloqueio anti-bot ou conteúdo renderizado só com JavaScript podem não permitir extração.
- Respeite as políticas e termos das fontes; faça coleta moderada e não redistribua os textos completos sem verificar os direitos.
- Como o objetivo do desafio é descobrir tendências não antecipadas, não usamos categorias predefinidas por modalidade esportiva.
- Os scores são **heurísticos**: antes de apresentar como qualidade validada, revise uma amostra das 20 notícias mais bem colocadas e das descartadas.

## Melhorias futuras

- Embeddings multilíngues para reranking semântico (testar contra a heurística atual).
- Histórico persistente em SQLite para não baixar novamente matérias já processadas.
- Métricas de precisão da relevância com avaliação humana e diversidade por veículo/tema.
- Agendamento diário e exportação para a etapa de clustering.
