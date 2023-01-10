import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import re
from pprint import pprint
import json

def find_true_info(text):
    pattern = r"(.*django.*flask.*)|(.*flask.*django.*)"
    result = re.findall(pattern, text, flags=re.I)
    return result

def find_usd(salary):
    pattern = r"usd"
    result = re.findall(pattern, salary, flags=re.I)
    return result

def city(text):
    pattern = r"([А-ё-]+),| .*"
    result = re.sub(pattern, r"\1", text)
    return result

def get_headers():
    return Headers(browser="chrome", os="win").generate()

def find_count_pages(url):
    html = requests.get(url + "0", headers=get_headers()).text
    soup2 = BeautifulSoup(html, features="lxml")
    count_results = soup2.find('h1', class_="bloko-header-section-3").text
    num = count_results.split()[0]
    return (int(num) // 20)

if __name__ == '__main__':
    id_ = 0
    info = []
    HOST = r"https://spb.hh.ru/search/vacancy?no_magic=true&L_save_area=true&text=Python&excluded_text=&area=2&area=1&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=1&items_on_page=20&page="
    count_pages = find_count_pages(HOST)
    print(count_pages + 1)
    for el in range(count_pages + 1):
        print(f"{int(el) + 1} страница")
        head_main_html = requests.get(f"{HOST}{el}", headers=get_headers()).text
        soup = BeautifulSoup(head_main_html, features="lxml")
        vak_list = soup.find_all('div', class_="serp-item")
        for tag in vak_list:
            link = tag.find('a', class_="serp-item__title")['href']        
            description_html = requests.get(link, headers=get_headers()).text
            soup1 = BeautifulSoup(description_html, features="lxml")
            description_body = soup1.find('div', class_="vacancy-section").text
            tag_salary = soup1.find(class_="bloko-header-section-2 bloko-header-section-2_lite").text
            if len(find_usd(tag_salary)) > 0:
                if len(find_true_info(description_body)) > 0:
                    city_name = tag.select_one('.bloko-text[data-qa=vacancy-serp__vacancy-address]').text
                    job_name = tag.find('a', class_="bloko-link bloko-link_kind-tertiary").text 
                    id_ += 1
                    info.append( {id_: {
                            "Link": link,
                            "Salary": tag_salary.replace(u"\xa0", ""),
                            "Name": job_name.replace(u"\xa0", " "),
                            "City": city(city_name)
                        }})
    pprint(info)
     
    with open(r"info.json", 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False,  indent=2)