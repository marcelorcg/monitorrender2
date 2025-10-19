import requests

url = "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024"

# Cabeçalhos simulando um navegador real
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.31 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

res = requests.get(url, headers=headers)

if res.status_code == 200:
    print("✅ Página acessada com sucesso!")
    html = res.text
    # Aqui entra seu código de hash e monitoramento
else:
    print(f"⚠️ Erro {res.status_code} ao acessar {url}")
