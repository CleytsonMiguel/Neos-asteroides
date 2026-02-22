import requests

API_KEY = "DEMO_KEY"  # substitua pela sua chave se quiser
URL = f"https://api.nasa.gov/neo/rest/v1/neo/browse?api_key={API_KEY}"

def obter_asteroides(paginas=3):
    """Busca asteroides do catálogo da NASA em várias páginas"""
    asteroides = []
    url = URL
    for _ in range(paginas):
        resposta = requests.get(url).json()
        for neo in resposta["near_earth_objects"]:
            dados = {
                "nome": neo["name"],
                "id": neo["id"],
                "diametro_min": neo["estimated_diameter"]["meters"]["estimated_diameter_min"],
                "diametro_max": neo["estimated_diameter"]["meters"]["estimated_diameter_max"],
                "perigoso": neo["is_potentially_hazardous_asteroid"]
            }
            asteroides.append(dados)
        # ir para próxima página se existir
        if "next" in resposta["links"]:
            url = resposta["links"]["next"]
        else:
            break
    return asteroides

lista = obter_asteroides(5)  # pega 3 páginas (≈100 asteroides)
for a in lista:
    print(f"🌑 {a['nome']} (ID: {a['id']})")
    print(f"   - Tamanho: {a['diametro_min']:.1f}m – {a['diametro_max']:.1f}m")
    print(f"   - Potencialmente perigoso: {'Sim' if a['perigoso'] else 'Não'}\n")

import os, sys, argparse, requests
from datetime import datetime
from rich.console import Console
from rich.table import Table
import pandas as pd

console = Console()

API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
BASE = "https://api.nasa.gov/neo/rest/v1/feed"

def fetch_neo_feed(start_date: str, end_date: str, api_key: str):
    params = {"start_date": start_date, "end_date": end_date, "api_key": api_key}
    r = requests.get(BASE, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def parse_neo_data(payload):
    """Achata todas as datas do dicionário near_earth_objects em uma lista única."""
    items = []
    neo = payload.get("near_earth_objects", {})
    for date_key, arr in neo.items():
        for a in arr:
            # alguns objetos têm múltiplas aproximações; pegamos a primeira do intervalo
            cad = a.get("close_approach_data", [])
            if not cad:
                continue
            approach = cad[0]
            try:
                vel_kmh = float(approach["relative_velocity"]["kilometers_per_hour"])
                miss_km = float(approach["miss_distance"]["kilometers"])
                ld = miss_km / 384400.0
                dmin = a["estimated_diameter"]["meters"]["estimated_diameter_min"]
                dmax = a["estimated_diameter"]["meters"]["estimated_diameter_max"]
                dmed = (dmin + dmax) / 2
            except Exception:
                continue

            items.append({
                "name": a.get("name", "—"),
                "date": approach.get("close_approach_date", date_key),
                "pha": bool(a.get("is_potentially_hazardous_asteroid", False)),
                "vel_kmh": vel_kmh,
                "miss_ld": ld,
                "miss_km": miss_km,
                "diam_m": dmed
            })
    # ordena por distância mínima (LD)
    items.sort(key=lambda x: x["miss_ld"])
    return items

def print_table(rows, start_date, end_date):
    title = f"🌍️ NEOs {start_date} → {end_date} (ordenado por distância mínima)"
    table = Table(title=title)
    table.add_column("Nome", style="cyan")                                                                                                       table.add_column("Data", style="yellow")
    table.add_column("PHA", style="bold red")
    table.add_column("Distância (LD)", justify="right", style="green")
    table.add_column("Veloc. (km/h)", justify="right", style="red")
    table.add_column("Diâmetro méd. (m)", justify="right", style="magenta")

    if not rows:
        console.print("[bold yellow]Nenhum NEO no intervalo informado.[/bold yellow]")
        return

    for r in rows:
        pha = "⚠️" if r["pha"] else ""
        table.add_row(
            r["name"],
            r["date"],
            pha,
            f"{r['miss_ld']:.2f}",
            f"{r['vel_kmh']:,.0f}",
            f"{r['diam_m']:,.0f}"
        )
    console.print(table)
    
    def save_csv(rows, path):
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    console.print(f"[green]CSV salvo:[/green] {path}")

def valid_date(s):
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        raise argparse.ArgumentTypeError("Use o formato YYYY-MM-DD.")

def main():
    parser = argparse.ArgumentParser(description="Rastreador de NEOs (NASA NeoWs).")
    parser.add_argument("--start", type=valid_date, default=datetime.now().strftime("%Y-%m-%d"),
                        help="Data inicial (YYYY-MM-DD). Padrão: hoje.")
    parser.add_argument("--end", type=valid_date, default=None,
                        help="Data final (YYYY-MM-DD). Padrão: igual à inicial.")
    parser.add_argument("--csv", type=str, default=None, help="Salvar resultados em CSV (caminho).")
    args = parser.parse_args()
    end = args.end or args.start

    try:
        data = fetch_neo_feed(args.start, end, API_KEY)
        rows = parse_neo_data(data)
        print_table(rows, args.start, end)
        if args.csv:
            save_csv(rows, args.csv)
    except requests.HTTPError as e:
        status = getattr(e.response, "status_code", "—")
        console.print(f"[red]Erro HTTP {status} ao acessar a API.[/red]")
        if status == 429:
            console.print("[yellow]Limite de requisições atingido. Tente novamente mais tarde ou use sua própria API key (defina NASA_API_KE>
    except requests.RequestException as e:
        console.print(f"[red]Erro de rede: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Erro inesperado: {e}[/red]")

if __name__ == "__main__":
    main()
import requests

API_KEY = "DEMO_KEY"  # substitua pela sua chave se quiser
URL = f"https://api.nasa.gov/neo/rest/v1/neo/browse?api_key={API_KEY}"

def obter_asteroides(paginas=3):
    """Busca asteroides do catálogo da NASA em várias páginas"""
    asteroides = []
    url = URL
    for _ in range(paginas):
        resposta = requests.get(url).json()
        for neo in resposta["near_earth_objects"]:
            dados = {
                "nome": neo["name"],
                "id": neo["id"],
                "diametro_min": neo["estimated_diameter"]["meters"]["estimated_diameter_min"],
                "diametro_max": neo["estimated_diameter"]["meters"]["estimated_diameter_max"],
                "perigoso": neo["is_potentially_hazardous_asteroid"]
            }
            asteroides.append(dados)
        # ir para próxima página se existir
        if "next" in resposta["links"]:
            url = resposta["links"]["next"]
        else:
            break
    return asteroides

lista = obter_asteroides(5)  # pega 5 páginas (≈100 asteroides)
for a in lista:
    print(f"🌑 {a['nome']} (ID: {a['id']})")
    print(f"   - Tamanho: {a['diametro_min']:.1f}m – {a['diametro_max']:.1f}m")
    print(f"   - Potencialmente perigoso: {'Sim' if a['perigoso'] else 'Não'}\n")