import os
import requests
import threading
import queue
from colorama import Fore, Style

print_lock = threading.Lock()
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
def validate_api_key(apikey):
    url = f"https://eclipsesec.tech/api/?apikey={apikey}&validate=true"
    try:
        response = requests.get(url)
        response.raise_for_status()
        body = response.json()
        
        if body.get('status') == "valid":
            return body.get('user'), True
        else:
            print(f"{Fore.RED}Invalid API key: {body.get('message', 'Unknown error')}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please register for a valid API key at: https://eclipsesec.tech/register{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}API key validation failed: {e}{Style.RESET_ALL}")
    
    return "", False
def process_domain(domain, api_key):
    url = f"https://eclipsesec.tech/api/?domain={domain}&apikey={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("data", {})
            if data:
                output = (
                    "========================\n"
                    f"[+] DOMAIN : {data.get('domain', domain)}\n"
                    f">> DA : {data.get('da', 'N/A')}\n"
                    f">> PA : {data.get('pa', 'N/A')}\n"
                    f">> ss : {data.get('ss', 'N/A')}\n"
                    f">> AGE : {data.get('domain_age', 'N/A')}\n"
                    f">> IP : {data.get('ip', 'N/A')}\n"
                    "========================"
                )
                with print_lock:
                    print(output)
            else:
                with print_lock:
                    print(f"No data returned for domain {domain}")
        else:
            with print_lock:
                print(f"Error retrieving data for {domain}, Status Code: {response.status_code}")
    except Exception as e:
        with print_lock:
            print(f"Exception for {domain}: {e}")
def worker(domain_queue, api_key):
    while not domain_queue.empty():
        domain = domain_queue.get()
        process_domain(domain, api_key)
        domain_queue.task_done()
def main(input_file, api_key, num_threads=5):
    domain_queue = queue.Queue()

    with open(input_file, 'r') as file:
        domains = file.read().splitlines()
    for domain in domains:
        domain_queue.put(domain)
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(domain_queue, api_key), daemon=True)
        thread.start()
        threads.append(thread)
    domain_queue.join()
if __name__ == "__main__":
    clear_console()
    print("""█▀▄ ▄▀█ ▄▄ █▀█ ▄▀█   █▀▀ █░█ █▀▀ █▀▀ █▄▀ █▀▀ █▀█
█▄▀ █▀█ ░░ █▀▀ █▀█   █▄▄ █▀█ ██▄ █▄▄ █░█ ██▄ █▀▄
          """)
    print(Fore.WHITE + " - developed by Eclipse Security Labs")
    print(Fore.WHITE + " - website : https://eclipsesec.tech/\n")
    api_key = input("$ Enter your API key: ")
    user, valid = validate_api_key(api_key)
    if not valid:
        print(f"{Fore.YELLOW}Redirecting to registration page...{Style.RESET_ALL}")
        print("Visit: https://eclipsesec.tech/register")
        exit(1)
    
    input_file = input("$ Enter your file list: ")
    
    main(input_file, api_key)
