import requests
import random
import string
import re
import sys
import time
import threading
from colorama import Fore, Style, init

init(autoreset=True)

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
        with open("user-agents.txt", "r") as a:
            return random.choice(a.readlines()).strip()
    except Exception:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

def get_search_query():
    search = hacker_prompt("[?] Enter your search: ")
    if not search.strip():
        type_out("[!] Search query cannot be empty!", color=Fore.RED)
        sys.exit(1)
    return search.replace(" ", "+")

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
    def animate():
        for i in range(total+1):
            percent = (i / total)
            bar = fill * int(length * percent) + '-' * (length - int(length * percent))
            print(f'\r{prefix} |{bar}| {int(percent*100)}%', end='', flush=True)
            time.sleep(0.03)
        print()
    t = threading.Thread(target=animate)
    t.start()
    task()
    t.join()

def fetch_results(url, headers, retries=3):
    result = {}
    def task():
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                result['text'] = response.text
                return
            except Exception as e:
                type_out(f"[!] Attempt {attempt+1} failed: {e}", color=Fore.YELLOW)
                time.sleep(2)
        type_out(f"[!] Failed to fetch results after {retries} attempts.", color=Fore.RED)
        sys.exit(1)
    progress_bar(task, 40, prefix=f"{Fore.LIGHTCYAN_EX}[*] Fetching from ahmia.fi")
    return result.get('text', '')

def extract_onion_links(html):
    reg = r"[a-zA-Z2-7]{16,56}\.onion"
    data = re.findall(reg, html)
    return list(dict.fromkeys(data))

def save_results(links, filename, limit):
    with open(filename, "w", encoding="utf-8") as f:
        for i, link in enumerate(links[:limit], 1):
            f.write(link + "\n")
    type_out(f"[+] Completed! {limit} links saved in {filename}", color=Fore.GREEN)

def save_html_report(links, filename, limit, search):
    html_filename = filename.replace('.txt', '.html')
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
        function toggleMode() {{
            document.body.classList.toggle('dark');
            var btn = document.getElementById('toggle-btn');
            var img = document.getElementById('banner-img');
            if(document.body.classList.contains('dark')) {{
                btn.textContent = '☀️ Light Mode';
                img.src = 'Scarycat.png';
            }} else {{
                btn.textContent = '🌙 Dark Mode';
                img.src = 'cuteCat.png';
            }}
        }}
        window.onload = function() {{
            var btn = document.getElementById('toggle-btn');
            var img = document.getElementById('banner-img');
            btn.textContent = '🌙 Dark Mode';
            img.src = 'cuteCat.png';
        }}
    </script>
</head>
<body>
    <button class="toggle-btn" id="toggle-btn" onclick="toggleMode()"></button>
    <div class="container">
        <img src="cuteCat.png" alt="ScayTor Banner" class="banner-img" id="banner-img" />
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
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    type_out(f"[+] HTML report generated: {html_filename}", color=Fore.GREEN)

def main():
    print_banner()
    search = get_search_query()
    number = get_result_limit()
    url = f"https://ahmia.fi/search/?q={search}"
    user_agent = get_user_agent()
    headers = {"User-Agent": user_agent}
    html = fetch_results(url, headers)
    links = extract_onion_links(html)
    if not links:
        type_out("[!] No .onion links found for your search.", color=Fore.RED)
        sys.exit(0)
    type_out(f"[+] Found {len(links)} .onion links. Displaying up to {number}...", color=Fore.CYAN)
    for i, link in enumerate(links[:number], 1):
        type_out(f"[{i:02}] {link}", color=Fore.LIGHTGREEN_EX, delay=0.002)
    filename = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + ".txt"
    save_results(links, filename, number)
    type_out(f"[=] Session complete. Stay anonymous, hacker.\n", color=Fore.LIGHTMAGENTA_EX)
    save_html_report(links, filename, number, search)

if __name__ == "__main__":
    main()
