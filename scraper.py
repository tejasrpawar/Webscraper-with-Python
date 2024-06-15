import requests
from bs4 import BeautifulSoup
import csv


def initialize_csv(filename='output-DS.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['Class Code', '-', 'Class name', 'Class link', 'Class details link', 'Instructor', 'Instructor page', 'Units', 'Enrollment Cap', 'Enrolled'])


def append_to_csv(data, filename='output-DS.csv'):
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)


# Function to fetch the content of the URL
def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def handle_links(link_a, link_b):
    prefix = 'https://student.apps.utah.edu/uofu/stu/ClassSchedules/main/1248/'
    link_a = prefix + link_a
    link_b = prefix + link_b
    return link_a, link_b


def parse_class_size_page(html_content, sub_name):
    soup = BeautifulSoup(html_content, 'html.parser')
    target_section = soup.find('tbody').find_all('tr')

    enrollment_cap, currently_enrolled = 0, 0
    for i in target_section:
        if sub_name in i.get_text():
            list_of_vals = [j.get_text() for j in i.find_all('td')]
            enrollment_cap, currently_enrolled = list_of_vals[5], list_of_vals[7]

    return enrollment_cap, currently_enrolled


def get_class_size_info(class_url, sub_name):
    html_content = fetch_page(class_url)
    cap, enrolled = 0, 0
    if html_content:
        cap, enrolled = parse_class_size_page(html_content, sub_name)
    return cap, enrolled


def handle_class_tab(class_tab):
    info = class_tab.find('div', class_='card-body row d-none d-md-block')

    h3_tab = info.find('h3')
    buttons = info.find('div', class_='buttons')

    class_code, class_name = h3_tab.find('a'), h3_tab.find_all('span')

    sub_name, prim_name = '', ''
    class_code_text = class_code.get_text()
    class_code_href = class_code['href']

    if class_name:
        sub_name = class_name[0].get_text()

    try:
        prim_name = class_name[1].get_text()
    except IndexError:
        prim_name = ''

    class_details_link = buttons.find('a')['href']

    instructor_name, instructor_page, number_of_units = '', '', ''
    instructor_div = info.find_all('div', class_='col-12 p-0')[1]
    ul = instructor_div.find('ul')
    for i in ul:
        if 'Instructor' in i.get_text():
            instructor_name, instructor_page = i.find('a').get_text(), i.find('a')['href']
        if 'Units' in i.get_text():
            number_of_units = i.find('span').get_text()
    class_code_href, class_details_link = handle_links(class_code_href, class_details_link)

    enrollment_cap, enrolled = get_class_size_info(class_code_href, sub_name)

    return class_code_text, sub_name, prim_name, class_code_href, class_details_link, instructor_name, instructor_page, number_of_units, enrollment_cap, enrolled


def parse_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    target_section = soup.find('div', class_='container-fluid mb-auto mt-0 mx-0 p-0').find('section',
                                                                                           class_='container-fluid px-2 px-sm-4 px-md-5 flex-grow-1')

    main_class = target_section.find('main').find('div', id='class-details')

    classes = main_class.find_all('div', class_='class-info card mt-3')

    if classes:
        for c in classes:
            print(handle_class_tab(c))
            append_to_csv(handle_class_tab(c))
    else:
        print("No main class found")


def scrape(url):
    html_content = fetch_page(url)
    if html_content:
        parse_page(html_content)


# URL to scrape
url = ('https://student.apps.utah.edu/uofu/stu/ClassSchedules/main/1248/class_list.html?subject=DS')
initialize_csv()
scrape(url)
