import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from bs4 import BeautifulSoup
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

console = Console()
MAX_REPOS_TO_SAVE = 15
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "daily_trends.md"

# --- Translations Dictionary ---
LANGUAGES = {
    "1": "en",
    "2": "es",
    "3": "pt"
}

TEXTS = {
    "en": {
        "banner_sub": "» Created to find rough diamonds 💎",
        "lang_prompt": "Select Language",
        "interval_title": "⏱️  Scanning Configuration",
        "opt_fast": "[1] Fast       (Every 10 mins)",
        "opt_normal": "[2] Normal     (Every 1 hour) [Recommended]",
        "opt_slow": "[3] Slow       (Every 12 hours)",
        "opt_custom": "[4] Custom     (Define seconds)",
        "opt_once": "[5] Once       (Run and exit)",
        "prompt_choice": "Choose an option",
        "prompt_custom": "Enter wait time in seconds",
        "err_obscura_not_found": "Error: Obscura executable not found at",
        "err_obscura_not_file": "Error: Obscura path exists but is not a file:",
        "err_obscura_not_executable": "Error: Obscura file is not executable. Use chmod +x if needed.",
        "err_obscura_failed": "Error: Obscura failed to run.",
        "err_obscura_invalid_output": "Error: Obscura returned no valid HTML.",
        "status_scraping": "Stealthily navigating GitHub (Obscura Stealth)...",
        "err_critical": "Critical error:",
        "err_no_repos": "No repositories found.",
        "err_html_schema": "Warning: GitHub HTML structure may have changed.",
        "table_title": "📈 Top RepoHunter Finds",
        "col_repo": "Repository",
        "col_lang": "Language",
        "col_stars": "⭐ Today",
        "col_desc": "Description",
        "report_title": "# 🚀 RepoHunter - Exclusive Report\n\n",
        "report_update": "> *Last updated: {}*\n\n",
        "report_intro": "Here is the cream of the crop for today. Analyze the descriptions and pick the best gem for your audience.\n\n",
        "md_desc": "**📝 Description:**",
        "md_lang": "**💻 Language:**",
        "md_stars": "**⭐ Stars (today):**",
        "success_saved": "Report successfully saved to:",
        "sleep_active": "💤 Sleep mode active. Next scan in: ",
        "sleep_exit": " (Ctrl+C to exit)",
        "scan_start": "Starting Scan",
        "mode_once_done": "👋 'Once' mode completed. See you soon!",
        "user_interrupt": "🛑 Program interrupted by user. Exiting...",
        "no_desc": "No description provided.",
        "unknown_lang": "Unknown"
    },
    "es": {
        "banner_sub": "» Creado para encontrar diamantes en bruto 💎",
        "lang_prompt": "Selecciona un Idioma",
        "interval_title": "⏱️  Configuración de Escaneo",
        "opt_fast": "[1] Rápido     (Cada 10 minutos)",
        "opt_normal": "[2] Normal     (Cada 1 hora) [Recomendado]",
        "opt_slow": "[3] Lento      (Cada 12 horas)",
        "opt_custom": "[4] Personal   (Definir segundos)",
        "opt_once": "[5] Una vez    (Ejecutar y salir)",
        "prompt_choice": "Elige una opción",
        "prompt_custom": "Ingresa los segundos de espera",
        "err_obscura_not_found": "Error: No se encontró el ejecutable de Obscura en",
        "err_obscura_not_file": "Error: La ruta de Obscura existe pero no es un archivo:",
        "err_obscura_not_executable": "Error: El archivo de Obscura no es ejecutable. Usa chmod +x si es necesario.",
        "err_obscura_failed": "Error: Obscura no pudo ejecutarse.",
        "err_obscura_invalid_output": "Error: Obscura no devolvió HTML válido.",
        "status_scraping": "Navegando sigilosamente por GitHub (Obscura Stealth)...",
        "err_critical": "Error crítico:",
        "err_no_repos": "No se encontraron repositorios.",
        "err_html_schema": "Advertencia: la estructura HTML de GitHub puede haber cambiado.",
        "table_title": "📈 Top RepoHunter Tendencias",
        "col_repo": "Repositorio",
        "col_lang": "Lenguaje",
        "col_stars": "⭐ Hoy",
        "col_desc": "Descripción",
        "report_title": "# 🚀 RepoHunter - Reporte Exclusivo\n\n",
        "report_update": "> *Última actualización: {}*\n\n",
        "report_intro": "Aquí tienes la crema y nata de los repositorios de hoy. Analiza las descripciones y elige la mejor gema para tu audiencia.\n\n",
        "md_desc": "**📝 Descripción:**",
        "md_lang": "**💻 Lenguaje:**",
        "md_stars": "**⭐ Estrellas (hoy):**",
        "success_saved": "Reporte guardado exitosamente en:",
        "sleep_active": "💤 Modo Reposo activo. Próximo escaneo en: ",
        "sleep_exit": " (Ctrl+C para salir)",
        "scan_start": "Iniciando Escaneo",
        "mode_once_done": "👋 Modo 'Una vez' completado. ¡Hasta pronto!",
        "user_interrupt": "🛑 Programa interrumpido por el usuario. Saliendo...",
        "no_desc": "Sin descripción.",
        "unknown_lang": "Desconocido"
    },
    "pt": {
        "banner_sub": "» Criado para encontrar diamantes brutos 💎",
        "lang_prompt": "Selecione o Idioma",
        "interval_title": "⏱️  Configuração de Verificação",
        "opt_fast": "[1] Rápido     (A cada 10 minutos)",
        "opt_normal": "[2] Normal     (A cada 1 hora) [Recomendado]",
        "opt_slow": "[3] Lento      (A cada 12 horas)",
        "opt_custom": "[4] Pessoal    (Definir segundos)",
        "opt_once": "[5] Uma vez    (Executar e sair)",
        "prompt_choice": "Escolha uma opção",
        "prompt_custom": "Insira o tempo de espera em segundos",
        "err_obscura_not_found": "Erro: Executável Obscura não encontrado em",
        "err_obscura_not_file": "Erro: O caminho do Obscura existe mas não é um arquivo:",
        "err_obscura_not_executable": "Erro: O arquivo Obscura não é executável. Use chmod +x se necessário.",
        "err_obscura_failed": "Erro: Obscura não pôde ser executado.",
        "err_obscura_invalid_output": "Erro: Obscura não retornou HTML válido.",
        "status_scraping": "Navegando furtivamente no GitHub (Obscura Stealth)...",
        "err_critical": "Erro crítico:",
        "err_no_repos": "Nenhum repositório encontrado.",
        "err_html_schema": "Aviso: a estrutura HTML do GitHub pode ter mudado.",
        "table_title": "📈 Top RepoHunter Tendências",
        "col_repo": "Repositório",
        "col_lang": "Linguagem",
        "col_stars": "⭐ Hoje",
        "col_desc": "Descrição",
        "report_title": "# 🚀 RepoHunter - Relatório Exclusivo\n\n",
        "report_update": "> *Última atualização: {}*\n\n",
        "report_intro": "Aqui está a nata dos repositórios de hoje. Analise as descrições e escolha a melhor joia para seu público.\n\n",
        "md_desc": "**📝 Descrição:**",
        "md_lang": "**💻 Linguagem:**",
        "md_stars": "**⭐ Estrelas (hoy):**",
        "success_saved": "Relatório salvo com sucesso em:",
        "sleep_active": "💤 Modo de suspensão ativo. Próxima verificação em: ",
        "sleep_exit": " (Ctrl+C para sair)",
        "scan_start": "Iniciando Verificação",
        "mode_once_done": "👋 Modo 'Uma vez' concluído. Até logo!",
        "user_interrupt": "🛑 Programa interrompido pelo usuário. Saindo...",
        "no_desc": "Sem descrição.",
        "unknown_lang": "Desconhecido"
    }
}

t = TEXTS["en"]  # Default to English


def print_banner():
    banner = f"""[bold cyan]
 ╦═╗┌─┐┌─┐┌─┐ ╦ ╦┬ ┬┌┐┌┌┬┐┌─┐┬─┐
 ╠╦╝├┤ ├─┘│ │ ╠═╣│ ││││ │ ├┤ ├┬┘
 ╩╚═└─┘┴  └─┘ ╩ ╩└─┘┘└┘ ┴ └─┘┴└─
[/bold cyan]
[bold white]» RepoHunter via Obscura[/bold white]
[bold green]{t['banner_sub']}[/bold green]
"""
    console.print(Panel(Align.center(banner), border_style="cyan"))


def get_language():
    global t
    console.print("\n[bold yellow]🌍 Select Language / Selecciona Idioma / Selecione o Idioma[/bold yellow]")
    console.print("[1] [bold blue]English[/bold blue]")
    console.print("[2] [bold green]Español[/bold green]")
    console.print("[3] [bold magenta]Português[/bold magenta]\n")

    choice = Prompt.ask("Choose / Elige / Escolha", choices=["1", "2", "3"], default="1")
    t = TEXTS[LANGUAGES[choice]]


def get_user_interval():
    console.print(f"\n[bold yellow]{t['interval_title']}[/bold yellow]")
    console.print(f"[bold green]{t['opt_fast']}[/bold green]")
    console.print(f"[bold blue]{t['opt_normal']}[/bold blue]")
    console.print(f"[bold magenta]{t['opt_slow']}[/bold magenta]")
    console.print(f"[bold cyan]{t['opt_custom']}[/bold cyan]")
    console.print(f"[bold red]{t['opt_once']}[/bold red]\n")

    choice = Prompt.ask(t['prompt_choice'], choices=["1", "2", "3", "4", "5"], default="2")

    if choice == "1":
        return 600
    elif choice == "2":
        return 3600
    elif choice == "3":
        return 43200
    elif choice == "4":
        return IntPrompt.ask(t['prompt_custom'])
    elif choice == "5":
        return -1


def get_obscura_path() -> Path:
    system = platform.system().lower()
    if system == "windows":
        return BASE_DIR / "obscura-windows" / "obscura.exe"
    if system == "darwin":
        return BASE_DIR / "obscura-macos" / "obscura"
    if system == "linux":
        return BASE_DIR / "obscura-linux" / "obscura"
    return BASE_DIR / "obscura"


def validate_obscura_executable(obscura_path: Path) -> bool:
    if not obscura_path.exists():
        console.print(f"\n[bold red]❌ {t['err_obscura_not_found']}[/bold red] [yellow]{obscura_path}[/yellow]")
        return False

    if not obscura_path.is_file():
        console.print(f"\n[bold red]❌ {t['err_obscura_not_file']}[/bold red] [yellow]{obscura_path}[/yellow]")
        return False

    if obscura_path.suffix != ".exe" and os.name != "nt":
        if not os.access(obscura_path, os.X_OK):
            console.print(f"\n[bold red]❌ {t['err_obscura_not_executable']}[/bold red] [yellow]{obscura_path}[/yellow]")
            return False

    return True


def extract_repo_info(article):
    for selector in ["h2 a", "h1 a", "a"]:
        for link in article.select(selector):
            href = link.get("href")
            if not href or not href.startswith("/"):
                continue
            parts = href.strip("/").split("/")
            if len(parts) >= 2:
                title = " ".join(link.get_text(strip=True).split())
                return title, f"https://github.com{href.strip()}"
    return None, None


def extract_description(article):
    description = article.find("p")
    if description:
        return description.get_text(strip=True)

    alt_description = article.select_one("div[class*='color-fg-muted'], div[class*='text-gray']")
    if alt_description:
        return alt_description.get_text(strip=True)

    return t["no_desc"]


def extract_language(article):
    lang_span = article.find(attrs={"itemprop": "programmingLanguage"})
    if lang_span:
        return lang_span.get_text(strip=True)

    alt_lang = article.select_one("span[class*='programmingLanguage'], span[class*='color-fg-muted']")
    if alt_lang:
        return alt_lang.get_text(strip=True)

    return t["unknown_lang"]


def extract_stars_today(article):
    for node in article.select("span.float-sm-right, span[class*='float-sm-right'], span[class*='stars']"):
        text = node.get_text(" ", strip=True)
        if "stars today" in text.lower():
            return text.lower().replace("stars today", "").strip()

    all_text = article.get_text(" ", strip=True)
    import re
    match = re.search(r"([0-9,]+)\s*stars\s*today", all_text, re.I)
    if match:
        return match.group(1)

    return "N/A"


def fetch_trending_repos():
    obscura_path = get_obscura_path()

    if not validate_obscura_executable(obscura_path):
        console.print("[bold red]Please ensure the correct Obscura binary is available for your OS.[/bold red]")
        return []

    command = [
        str(obscura_path),
        "fetch",
        "https://github.com/trending",
        "--stealth",
        "--wait-until",
        "networkidle0",
        "--dump",
        "html",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )

        if result.returncode != 0:
            console.print(f"\n[bold red]❌ {t['err_obscura_failed']}[/bold red]")
            error_text = result.stderr.strip() or result.stdout.strip()
            if error_text:
                console.print(f"[yellow]{error_text}[/yellow]")
            return []

        html_content = result.stdout
        if not html_content or "<html" not in html_content.lower():
            console.print(f"\n[bold red]❌ {t['err_obscura_invalid_output']}[/bold red]")
            return []

        start_html = html_content.find("<html")
        if start_html != -1:
            html_content = html_content[start_html:]

        soup = BeautifulSoup(html_content, "html.parser")
        articles = soup.find_all("article", class_="Box-row")

        if not articles:
            articles = soup.select("article")

        if not articles:
            console.print(f"\n[bold yellow]⚠️ {t['err_html_schema']}[/bold yellow]")
            return []

        repos = []
        for article in articles:
            title, url = extract_repo_info(article)
            if not title or not url:
                continue

            description = extract_description(article)
            language = extract_language(article)
            stars_today = extract_stars_today(article)

            repos.append(
                {
                    "title": title,
                    "url": url,
                    "description": description,
                    "language": language,
                    "stars_today": stars_today,
                }
            )

        if not repos:
            console.print(f"\n[bold yellow]⚠️ {t['err_html_schema']}[/bold yellow]")

        return repos

    except subprocess.TimeoutExpired:
        console.print(f"\n[bold red]❌ {t['err_obscura_failed']}[/bold red] Timeout expired while waiting for Obscura.")
        return []
    except Exception as exc:
        console.print(f"\n[bold red]❌ {t['err_critical']}[/bold red] {exc}")
        return []


def display_and_save(repos, filename: Path = OUTPUT_FILE):
    if not repos:
        console.print(f"[bold red]❌ {t['err_no_repos']}[/bold red]")
        return

    table = Table(title=f"[bold white]{t['table_title']}[/bold white]", show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=3)
    table.add_column(t["col_repo"], style="green", width=30)
    table.add_column(t["col_lang"], style="magenta")
    table.add_column(t["col_stars"], justify="right", style="yellow")
    table.add_column(t["col_desc"], style="white", overflow="fold")

    try:
        with filename.open("w", encoding="utf-8") as f:
            f.write(t["report_title"])
            f.write(t["report_update"].format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            f.write(t["report_intro"])
            f.write("---\n\n")

            for i, repo in enumerate(repos[:MAX_REPOS_TO_SAVE], 1):
                short_desc = repo["description"]
                if len(short_desc) > 70:
                    short_desc = short_desc[:70] + "..."

                table.add_row(
                    str(i),
                    repo["title"],
                    repo["language"],
                    repo["stars_today"],
                    short_desc,
                )

                f.write(f"### {i}. [{repo['title']}]({repo['url']})\n\n")
                f.write(f"{t['md_desc']} {repo['description']}\n\n")
                f.write(f"{t['md_lang']} `{repo['language']}` | {t['md_stars']} `{repo['stars_today']}`\n\n")
                f.write("---\n\n")

    except OSError as exc:
        console.print(f"\n[bold red]❌ {t['err_critical']}[/bold red] {exc}")
        return

    console.print()
    console.print(table)
    console.print(f"\n[bold green]✅ {t['success_saved']}[/bold green] [bold white]{filename}[/bold white]")


def countdown_sleep(seconds: int):
    target_time = datetime.now() + timedelta(seconds=seconds)

    with Live(refresh_per_second=1) as live:
        while True:
            now = datetime.now()
            if now >= target_time:
                break

            remaining = target_time - now
            mins, secs = divmod(remaining.seconds, 60)
            hours, mins = divmod(mins, 60)

            time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"

            status_text = Text()
            status_text.append(t["sleep_active"], style="dim")
            status_text.append(time_str, style="bold yellow")
            status_text.append(t["sleep_exit"], style="dim")

            live.update(Panel(status_text, border_style="dim"))
            time.sleep(1)


def main():
    os.system("cls" if os.name == "nt" else "clear")
    get_language()

    os.system("cls" if os.name == "nt" else "clear")
    print_banner()
    interval = get_user_interval()

    while True:
        console.rule(f"[bold cyan]🔍 {t['scan_start']} - {datetime.now().strftime('%H:%M:%S')}[/bold cyan]")

        with console.status(f"[bold green]{t['status_scraping']}[/bold green]", spinner="dots12"):
            repos = fetch_trending_repos()

        if repos:
            display_and_save(repos)

        if interval == -1:
            console.print(f"\n[bold green]{t['mode_once_done']}[/bold green]")
            break

        try:
            console.print()
            countdown_sleep(interval)
        except KeyboardInterrupt:
            console.print(f"\n[bold red]{t['user_interrupt']}[/bold red]")
            break


if __name__ == "__main__":
    main()
