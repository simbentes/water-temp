import os, requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

URL = "https://www.ipma.pt/pt/maritima/costeira/index.jsp?selLocal=205&idLocal=205"
RESP = requests.get(URL, timeout=15)

soup = BeautifulSoup(RESP.content, "html.parser")

tabs = [a.get_text(strip=True).split(",")[0]
        for a in soup.select("ul.simpleTabsNavigation li a")]

leitura_18h = [] # (dia, temp)

for idx, table in enumerate(soup.select("div.simpleTabsContent table.tablelist")):
    dia = tabs[idx] if idx < len(tabs) else f"Dia {idx}"

    linha_18h = next(
        (tr for tr in table.select("tr")[1:]            # ignora cabeçalho
         if tr.td and tr.td.get_text(strip=True) == "18h"),
        None
    )
    if not linha_18h:
        continue

    temp_str = linha_18h.find_all("td")[9].get_text(strip=True) \
                         .replace("°C", "").replace(",", ".")
    try:
        temp = float(temp_str)
    except ValueError:
        continue

    leitura_18h.append((dia, temp))


if leitura_18h:
    linhas = [f"▸ {dia}: {t:.1f} °C às 18 h" for dia, t in leitura_18h]
    mensagem = "🌊 Temperatura da água na Fonte da Telha\n" + "\n".join(linhas)

    print(mensagem)

    if any(t > 19 for _, t in leitura_18h):
        load_dotenv()
        BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": mensagem}
        )
    else:
        print(mensagem)
else:
    print("Não encontrei a linha das 18 h.")
