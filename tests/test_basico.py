import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from coletar_urls import (
    janela_datas, normalizar_url, parse_data, resolver_bing,
    deduplicar_candidatas, nova_noticia, pontuar_relevancia,
)


def test_janela_d2():
    assert janela_datas(2, 1, date(2026, 10, 13)) == (date(2026, 10, 11), date(2026, 10, 11))


def test_datas_fuso():
    assert parse_data("Sun, 11 Oct 2026 23:00:00 GMT") == date(2026, 10, 11)
    assert parse_data("2026-10-11") == date(2026, 10, 11)
    assert parse_data("20261012T020000Z") == date(2026, 10, 11)


def test_url_sem_rastreamento():
    assert normalizar_url("https://Site.com/a/?utm_source=x&ref=1#abc") == "https://site.com/a?ref=1"


def test_bing_redirect():
    url = "https://www.bing.com/news/apiclick.aspx?ref=foo&url=https%3A%2F%2Fexemplo.com%2Fa"
    assert resolver_bing(url) == "https://exemplo.com/a"


def test_duplicidade():
    a = nova_noticia("Notícia A", "https://exemplo.com/a?utm_source=google", "Google News")
    b = nova_noticia("Notícia A", "https://exemplo.com/a", "GDELT")
    unicas = deduplicar_candidatas([a, b])
    assert len(unicas) == 1
    assert set(unicas[0]["origens"]) == {"Google News", "GDELT"}


def test_filtro_sem_contexto_esportivo():
    noticias = [
        {"titulo": "Indústria pesqueira", "descricao": "mercado de pesca", "texto": "Peixes e indústria. " * 40, "tamanho_texto": 800, "status": "aprovada"},
        {"titulo": "Indústria esportiva e inovação", "descricao": "setor esportivo", "texto": "Tecnologia esportiva. " * 40, "tamanho_texto": 800, "status": "aprovada"},
    ]
    aprovadas, rejeitadas = pontuar_relevancia(noticias, "indústria esportiva")
    assert len(aprovadas) == 1
    assert len(rejeitadas) == 1
    assert rejeitadas[0]["motivo"] == "sem_contexto_esportivo"
