import requests
import random
import string
import re
import sys
import time
import threading
import argparse
import os
from urllib.parse import quote_plus
from colorama import Fore, Style, init

init(autoreset=True)

__version__ = "2.0.0"
__author__ = "Scayar"

def type_out(text, color=Fore.WHITE, delay=0.01, end="\n"):
    for char in text:
        print(color + char, end="", flush=True)
        time.sleep(delay)
    print(Style.RESET_ALL, end=end)

def print_banner():
    banner = f"""
{Fore.MAGENTA}
                                              ___
                                          ,o88888
                                       ,o8888888'
                 ,:o:o:oooo.        ,8O88Pd8888"
             ,.::.::o:ooooOoOoO. ,oO8O8Pd888'"
           ,.:.::o:ooOoOoOO8O8OOo.8OOPd8O8O"
          , ..:.::o:ooOoOOOO8OOOOo.FdO8O8"
         , ..:.::o:ooOoOO8O888O8O,COCOO"
        , . ..:.::o:ooOoOOOO8OOOOCOCO"
         . ..:.::o:ooOoOoOO8O8OCCCC"o
            . ..:.::o:ooooOoCoCCC"o:o
            . ..:.::o:o:,cooooCo"oo:o:
         `   . . ..:.:cocoooo"'o:o:::'
         .`   . ..::ccccoc"'o:o:o:::'
        :.:.    ,c:cccc"':.:.:.:.:.'
      ..:.:"'`::::c:"'..:.:.:.:.:.'
    ...:.'.:.::::"'    . . . . .'
   .. . ....:."' `   .  . . . ''
 . . . ...."'
 .. . ."'     ScayTor 
.                                
"""
    print(banner)

def hacker_prompt(prompt, color=Fore.LIGHTGREEN_EX):
    type_out(prompt, color=color, delay=0.01, end="")
    return input(Style.RESET_ALL)

def get_user_agent():
    try:
        with open("user-agents.txt", "r", encoding="utf-8") as a:
            agents = [line.strip() for line in a.readlines() if line.strip()]
            if agents:
                return random.choice(agents)
            else:
                return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    except (FileNotFoundError, IOError):
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    except Exception as e:
        type_out(f"[!] Warning: Could not read user-agents.txt: {e}", color=Fore.YELLOW)
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def get_search_query():
    search = hacker_prompt("[?] Enter your search: ")
    if not search.strip():
        type_out("[!] Search query cannot be empty!", color=Fore.RED)
        sys.exit(1)
    return quote_plus(search.strip())

def get_result_limit():
    while True:
        try:
            number = int(hacker_prompt("[?] How many .onion sites do you want? "))
            if number > 0:
                return number
            else:
                type_out("[!] Please enter a positive number.", color=Fore.RED)
        except Exception as err:
            type_out(f"[!] Invalid input: {err}", color=Fore.RED)

def progress_bar(task, total, prefix='', length=30, fill='█'):
    task_completed = threading.Event()
    def animate():
        for i in range(total+1):
            if task_completed.is_set():
                percent = 1.0
                bar = fill * length
                print(f'\r{prefix} |{bar}| 100%', end='', flush=True)
                break
            percent = min(i / total, 1.0)
            bar = fill * int(length * percent) + '-' * (length - int(length * percent))
            print(f'\r{prefix} |{bar}| {int(percent*100)}%', end='', flush=True)
            time.sleep(0.03)
        print()
    t = threading.Thread(target=animate, daemon=True)
    t.start()
    try:
        task()
    finally:
        task_completed.set()
        t.join(timeout=1)

def fetch_results(url, headers, retries=3, show_progress=True):
    result = {}
    def task():
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                result['text'] = response.text
                result['status'] = 'success'
                return
            except requests.exceptions.Timeout:
                type_out(f"[!] Attempt {attempt+1} failed: Request timeout", color=Fore.YELLOW)
                if attempt < retries - 1:
                    time.sleep(2 * (attempt + 1))  # Exponential backoff
            except requests.exceptions.ConnectionError:
                type_out(f"[!] Attempt {attempt+1} failed: Connection error", color=Fore.YELLOW)
                if attempt < retries - 1:
                    time.sleep(2 * (attempt + 1))
            except requests.exceptions.HTTPError as e:
                type_out(f"[!] Attempt {attempt+1} failed: HTTP {e.response.status_code}", color=Fore.YELLOW)
                if attempt < retries - 1:
                    time.sleep(2 * (attempt + 1))
            except Exception as e:
                type_out(f"[!] Attempt {attempt+1} failed: {e}", color=Fore.YELLOW)
                if attempt < retries - 1:
                    time.sleep(2 * (attempt + 1))
        result['status'] = 'failed'
        type_out(f"[!] Failed to fetch results after {retries} attempts.", color=Fore.RED)
    if show_progress:
        progress_bar(task, 40, prefix=f"{Fore.LIGHTCYAN_EX}[*] Fetching from ahmia.fi")
    else:
        task()
    if result.get('status') == 'failed':
        sys.exit(1)
    return result.get('text', '')

def extract_onion_links(html):
    reg = r"\b[a-zA-Z2-7]{16,56}\.onion\b"
    data = re.findall(reg, html)
    return list(dict.fromkeys(data))

def save_results(links, filename, limit):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for i, link in enumerate(links[:limit], 1):
                f.write(link + "\n")
        type_out(f"[+] Completed! {limit} links saved in {filename}", color=Fore.GREEN)
    except IOError as e:
        type_out(f"[!] Error saving file: {e}", color=Fore.RED)
        sys.exit(1)

def save_html_report(links, filename, limit, search):
    html_filename = filename.replace('.txt', '.html')
    # Ensure banner images exist, use placeholder if not
    banner_light = 'CuteCat.png' if os.path.exists('CuteCat.png') else ''
    banner_dark = 'Scarycat.png' if os.path.exists('Scarycat.png') else ''
    html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ScayTor Report</title>
    <style>
        :root {{
            --light-bg: #FBEDE2;
            --light-text: #5A2516;
            --light-accent1: #745F5D;
            --light-accent2: #DCB6A3;
            --light-accent3: #D9AC92;
            --dark-bg: #181a20;
            --dark-container: #23272e;
            --dark-text: #e6e6e6;
            --dark-accent1: #00ffd0;
            --dark-accent2: #ff26a6;
            --dark-accent3: #22262e;
        }}
        body {{
            background: var(--light-bg);
            color: var(--light-text);
            font-family: 'Fira Mono', 'Consolas', monospace;
            margin: 0;
            padding: 0;
            transition: background 0.3s, color 0.3s;
        }}
        .container {{
            max-width: 700px;
            margin: 40px auto;
            background: var(--light-accent2);
            border-radius: 18px;
            box-shadow: 0 0 32px var(--light-accent1)55, 0 0 8px var(--light-accent3)55;
            padding: 36px 44px 44px 44px;
            border: 2px solid var(--light-accent3);
            transition: background 0.3s, border 0.3s, box-shadow 0.3s;
        }}
        .banner-img {{
            display: block;
            margin: 0 auto 28px auto;
            max-width: 100%;
            max-height: 260px;
            width: auto;
            height: auto;
            border-radius: 18px;
            box-shadow: 0 0 32px var(--light-accent1)88, 0 0 8px var(--light-accent3)55;
            object-fit: contain;
            background: var(--light-bg);
            transition: box-shadow 0.3s;
        }}
        h1 {{
            color: var(--light-text);
            font-size: 2.3em;
            margin-bottom: 0.2em;
            letter-spacing: 2px;
            text-shadow: 0 0 8px var(--light-accent3), 0 0 2px #fff;
            transition: color 0.3s, text-shadow 0.3s;
        }}
        .subtitle {{
            color: var(--light-accent1);
            font-size: 1.15em;
            margin-bottom: 1.7em;
            text-shadow: 0 0 4px var(--light-accent2);
            transition: color 0.3s, text-shadow 0.3s;
        }}
        .onion-list {{
            list-style: none;
            padding: 0;
        }}
        .onion-list li {{
            background: var(--light-bg);
            margin: 0.5em 0;
            padding: 0.8em 1.1em;
            border-radius: 8px;
            font-size: 1.13em;
            transition: background 0.2s, color 0.2s, border 0.2s;
            border-left: 4px solid var(--light-accent1);
            box-shadow: 0 0 8px var(--light-accent3)55;
            color: var(--light-text);
        }}
        .onion-list li:hover {{
            background: var(--light-accent3);
            color: var(--light-text);
            border-left: 4px solid var(--light-text);
        }}
        a {{
            color: var(--light-text);
            text-decoration: none;
            font-weight: bold;
            transition: color 0.2s, text-shadow 0.2s;
        }}
        a:hover {{
            color: var(--light-accent1);
            text-shadow: 0 0 8px var(--light-accent2), 0 0 2px #fff;
        }}
        .footer {{
            margin-top: 2em;
            color: var(--light-accent1);
            font-size: 1em;
            text-align: center;
            opacity: 0.85;
            text-shadow: 0 0 4px var(--light-accent2);
            transition: color 0.3s, text-shadow 0.3s;
        }}
        .toggle-btn {{
            position: absolute;
            top: 24px;
            right: 24px;
            background: var(--light-accent1);
            color: var(--light-bg);
            border: none;
            border-radius: 8px;
            padding: 8px 18px;
            font-size: 1em;
            font-family: inherit;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 0 8px var(--light-accent1)55;
            transition: background 0.3s, color 0.3s;
            z-index: 10;
        }}
        .toggle-btn:hover {{
            background: var(--light-accent3);
            color: var(--light-text);
        }}
        body.dark {{
            background: var(--dark-bg);
            color: var(--dark-text);
        }}
        body.dark .container {{
            background: var(--dark-container);
            border: 2px solid var(--dark-accent1);
            box-shadow: 0 0 32px var(--dark-accent1)55, 0 0 8px #000a;
        }}
        body.dark .banner-img {{
            background: var(--dark-bg);
            box-shadow: 0 0 32px var(--dark-accent1)88, 0 0 8px #000a;
        }}
        body.dark h1 {{
            color: var(--dark-accent1);
            text-shadow: 0 0 8px var(--dark-accent1), 0 0 2px #fff;
        }}
        body.dark .subtitle {{
            color: var(--dark-accent2);
            text-shadow: 0 0 4px var(--dark-accent2);
        }}
        body.dark .onion-list li {{
            background: var(--dark-accent3);
            border-left: 4px solid var(--dark-accent1);
            box-shadow: 0 0 8px var(--dark-accent1)55;
            color: var(--dark-text);
        }}
        body.dark .onion-list li:hover {{
            background: var(--dark-accent1);
            color: var(--dark-bg);
            border-left: 4px solid var(--dark-accent2);
        }}
        body.dark a {{
            color: var(--dark-accent1);
        }}
        body.dark a:hover {{
            color: var(--dark-accent2);
            text-shadow: 0 0 8px var(--dark-accent2), 0 0 2px #fff;
        }}
        body.dark .footer {{
            color: var(--dark-accent1);
            text-shadow: 0 0 4px var(--dark-accent1);
        }}
        body.dark .toggle-btn {{
            background: var(--dark-accent1);
            color: var(--dark-bg);
            box-shadow: 0 0 8px var(--dark-accent1)55;
        }}
        body.dark .toggle-btn:hover {{
            background: var(--dark-accent2);
            color: var(--dark-bg);
        }}
    </style>
    <script>
        var bannerLight = '{banner_light}';
        var bannerDark = '{banner_dark}';
        function toggleMode() {{
            document.body.classList.toggle('dark');
            var btn = document.getElementById('toggle-btn');
            var img = document.getElementById('banner-img');
            if(document.body.classList.contains('dark')) {{
                btn.textContent = '☀️ Light Mode';
                if (bannerDark) {{
                    img.src = bannerDark;
                    img.style.display = 'block';
                }} else {{
                    img.style.display = 'none';
                }}
            }} else {{
                btn.textContent = '🌙 Dark Mode';
                if (bannerLight) {{
                    img.src = bannerLight;
                    img.style.display = 'block';
                }} else {{
                    img.style.display = 'none';
                }}
            }}
        }}
        window.onload = function() {{
            var btn = document.getElementById('toggle-btn');
            var img = document.getElementById('banner-img');
            btn.textContent = '🌙 Dark Mode';
            if (bannerLight) {{
                img.src = bannerLight;
                img.style.display = 'block';
            }} else {{
                img.style.display = 'none';
            }}
        }}
    </script>
</head>
<body>
    <button class="toggle-btn" id="toggle-btn" onclick="toggleMode()"></button>
    <div class="container">
        <img src="{banner_light}" alt="ScayTor Banner" class="banner-img" id="banner-img" style="display: {'block' if banner_light else 'none'};" />
        <h1>ScayTor Report</h1>
        <p class="subtitle">Search Results for: <strong>{search}</strong></p>
        <ul class="onion-list">
'''
    for i, link in enumerate(links[:limit], 1):
        html_content += f'            <li><a href="{link}" target="_blank">{link}</a></li>\n'
    html_content += f'''
        </ul>
        <p class="footer">Made With Love By Scayar {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
</body>
</html>
'''
    try:
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        type_out(f"[+] HTML report generated: {html_filename}", color=Fore.GREEN)
    except IOError as e:
        type_out(f"[!] Error generating HTML report: {e}", color=Fore.RED)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="ScayTor - A Modern Tool for Searching .onion Sites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python TorSearch.py
  python TorSearch.py --query "marketplace" --limit 20
  python TorSearch.py --query "security" --limit 10 --output results.txt

Version: {__version__}
Author: {__author__}
        """
    )
    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Search query (if not provided, will prompt interactively)'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help='Number of results to retrieve (if not provided, will prompt interactively)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output filename (default: random 5-character name)'
    )
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'ScayTor {__version__}'
    )
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Disable progress bar animation'
    )
    return parser.parse_args()

def main():
    try:
        args = parse_arguments()
        print_banner()
        
        # Get search query
        if args.query:
            search_query = args.query
            if not search_query.strip():
                type_out("[!] Search query cannot be empty!", color=Fore.RED)
                sys.exit(1)
        else:
            search_query = hacker_prompt("[?] Enter your search: ")
            if not search_query.strip():
                type_out("[!] Search query cannot be empty!", color=Fore.RED)
                sys.exit(1)
        
        search = quote_plus(search_query.strip())
        
        # Get result limit
        if args.limit:
            if args.limit > 0:
                number = args.limit
            else:
                type_out("[!] Limit must be a positive number.", color=Fore.RED)
                sys.exit(1)
        else:
            number = get_result_limit()
        
        # Build URL and headers
        url = f"https://ahmia.fi/search/?q={search}"
        user_agent = get_user_agent()
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
        
        # Fetch results
        html = fetch_results(url, headers, show_progress=not args.no_progress)
        
        # Extract links
        links = extract_onion_links(html)
        if not links:
            type_out("[!] No .onion links found for your search.", color=Fore.RED)
            sys.exit(0)
        
        actual_limit = min(number, len(links))
        type_out(f"[+] Found {len(links)} .onion links. Displaying up to {actual_limit}...", color=Fore.CYAN)
        
        # Display results
        for i, link in enumerate(links[:actual_limit], 1):
            type_out(f"[{i:02}] {link}", color=Fore.LIGHTGREEN_EX, delay=0.002)
        
        # Generate filename
        if args.output:
            filename = args.output
            if not filename.endswith('.txt'):
                filename += '.txt'
        else:
            filename = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + ".txt"
        
        # Save results
        save_results(links, filename, actual_limit)
        save_html_report(links, filename, actual_limit, search_query.strip())
        type_out(f"[=] Session complete. Stay anonymous, hacker.\n", color=Fore.LIGHTMAGENTA_EX)
        
    except KeyboardInterrupt:
        type_out("\n[!] Interrupted by user.", color=Fore.RED)
        sys.exit(1)
    except Exception as e:
        type_out(f"[!] Unexpected error: {e}", color=Fore.RED)
        import traceback
        if '--debug' in sys.argv:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
