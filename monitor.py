"""Checa a página uma vez e avisa no celular (ntfy) se a venda abriu."""
import json
import os
import sys

import requests

URL = os.environ["URL"]
TOPICO = os.environ["TOPICO"]
PALAVRAS = ["comprar", "ingressos disponíveis", "selecione o setor", "adicionar ao carrinho"]
ARQUIVO = "estado.json"


def carregar():
    try:
        with open(ARQUIVO) as f:
            return set(json.load(f))
    except (FileNotFoundError, ValueError):
        return set()


def main():
    try:
        r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        r.raise_for_status()
    except requests.RequestException as e:
        print("Erro ao acessar a página:", e)
        sys.exit(0)

    texto = r.text.lower()
    achou = {p for p in PALAVRAS if p in texto}
    novas = achou - carregar()
    print("Palavras encontradas:", sorted(achou))

    if novas:
        requests.post(
            f"https://ntfy.sh/{TOPICO}",
            data=f"Possível abertura de vendas! Detectei: {', '.join(sorted(novas))}. Abra agora.".encode("utf-8"),
            headers={"Title": "Ingresso Corinthians", "Priority": "urgent", "Click": URL},
            timeout=10,
        )

    with open(ARQUIVO, "w") as f:
        json.dump(sorted(achou), f)


if __name__ == "__main__":
    main()
