from dataclasses import dataclass
from lxml import html
import requests

_BASE_URL: str = "https://www.rtp.pt"

@dataclass
class Class:
    class_name: str
    url: str

@dataclass
class Episode:
    class_name: str
    url: str
    title: str
    number: str
    duration: str
    date: str


def full_url(path: str):
    return f"{_BASE_URL}{path}"

def get_classes(main_url: str):
    page = requests.get(main_url)
    tree = html.fromstring(page.content)
    classes = []
    for elem in tree.xpath("""//a[contains(@href,'/play/estudoemcasa/p')]"""):
        classes.append(
            Class(
                class_name = elem.attrib["title"],
                url = elem.attrib["href"]
            )
        )
    return classes

def get_class_episodes(class_url: str, class_name):
    page = requests.get(class_url)
    tree = html.fromstring(page.content)

    episodes = []
    for article in tree.xpath("/html/body/div[2]/div/div/div/div[3]/article"):

        try:
            ep_url = "{base}{path}".format(base=_BASE_URL, path=article.xpath("a")[0].attrib['href'])
        except:
            ep_url = ""
        
        try:
            ep_title = article.xpath("a/div[2]/h4")[0].text.strip()
        except:
            ep_title = ""
            

        try:
            meta = article.xpath("a/div[2]")[0].text_content().strip().split("|")
        except:
            meta = ["","",""]

        try:
            ep_number = article.xpath("a/div[2]/span[@class='episode']")[0].text.replace("|","").strip()
        except:
            ep_number = ""

        try:
            ep_date = article.xpath("a/div[2]/span[@class='episode-date']")[0].text.strip()
        except:
            ep_date = ""

        try:
            ep_duration = (
                article.xpath("a/div[2]")[0].text_content()
                .replace(ep_title,"")
                .replace(ep_number, "")
                .replace(ep_date, "")
                .replace("|", "")
                .strip())
        except:
            ep_duration = ""

        episodes.append(
            Episode(
                class_name = class_name,
                url = ep_url,
                title = ep_title,
                number = ep_number,
                date = ep_date,
                duration = ep_duration
            )
        )
    return episodes

if __name__ == "__main__":
    classes = get_classes(full_url("/play/estudoemcasa/"))

    episodes = []
    for loaded_class in classes:
        episodes.extend(get_class_episodes(full_url(loaded_class.url), loaded_class.class_name))

    for episode in episodes:
        print(episode)