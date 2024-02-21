import os, json, requests, random, time, base64 # to decode the identifier
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

_identifier_ = os.path.join("data", "identifier.txt")
_sites_ = os.path.join("data", "sites.txt")

if os.path.exists(_identifier_):
    print("Welcome back!")
    with open(_identifier_, "r") as i:
        identifier = i.read()
    print("Loaded DeaFed Identifier.\n")
else:
    print("Welcome, for setup instructions please read the README.md file.")
    identifier = input("DeaFed Identifier: ")
    
    try:
        with open(_identifier_, "w") as i:
            i.write(identifier)
    except OSError:
        print("Error: \"data\" directory missing"); exit(1)
    print("Saved.\n")

identifier += '=' * ((4 - len(identifier) % 4) % 4) # idk why it needed padding, thanks stacksoverflow <3
identifier = base64.b64decode(identifier).decode('utf-8')
with open(_sites_) as i:
    sites = [line.strip() for line in i.readlines()]
identifier_dict = json.loads(identifier)

def getLinks(url):
    headers = {key: value.replace("^target-site^", url) for key, value in identifier_dict.items()}

    try:
        response = requests.get(f"https://{url}", headers=headers, allow_redirects=False)
    except requests.exceptions.HTTPError:
        return set()
    except requests.exceptions.InvalidURL:
        print(f"Invalid URL encountered: {url}")
        return set()

    print("REQUESTING", url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = set()

    for link in soup.find_all("link", href=True): #css
        link_url = link.get("href")
        if link_url and not link_url.startswith(('http://', 'https://')):  # Check if URL is properly formed
            link_url = urljoin(url, link_url)
        links.add(link_url)
    for link in soup.find_all("script", src=True): #javascript
        link_url = link.get("src")
        if link_url and not link_url.startswith(('http://', 'https://')):  # Check if URL is properly formed
            link_url = urljoin(url, link_url)
        links.add(link_url)

    # Handle redirects
    if response.status_code // 100 == 3 and 'Location' in response.headers:
        redirect_url = response.headers['Location']
        print(f"Redirected to: {redirect_url}")
        links.add(redirect_url)

    return links


while True:
    random.shuffle(sites) # Sort the list randomly each loop
    remaining_links = {}
    visited_links = set()

    for i in sites:
        remaining_links = {i}
        visited_links = set()

        while remaining_links: 
            url = remaining_links.pop()
            visited_links.add(url)

            print(f"Visiting {url}...")

            links = getLinks(url)
            for link in links:
                if link not in visited_links and urlparse(link).netloc == urlparse(i).netloc:
                    remaining_links.add(link)

        sleeptime = random.randint(10, 60)
        print(f"Sleeping for {sleeptime} seconds...\n")
        time.sleep(sleeptime)
