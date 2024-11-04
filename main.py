import asyncio
import datetime

from playwright.async_api import async_playwright


async def fetch_tr_elements(url, xpath):
    async with async_playwright() as p:
        # Launch a browser context
        browser = await p.chromium.launch(headless=True)  # Set headless=False if you want to see the browser
        page = await browser.new_page()

        # Navigate to the URL
        await page.goto(url)

        # Wait for the specified XPath to appear in the DOM
        await page.wait_for_selector(xpath)

        # Evaluate the XPath to get all <tr> elements
        tr_elements = await page.query_selector_all(f'{xpath}/tr')

        # Extract data from each <tr> element
        data = []
        for tr in tr_elements:
            date_element = await tr.query_selector('.date span span')
            date = await date_element.get_attribute('content')
            date_display = await date_element.text_content()
            date_display = date_display.strip()
            date_str = date_display.split(',')[0].strip()

            title_element = await tr.query_selector('.title a')
            title = await title_element.text_content()
            title_link = await title_element.get_attribute('href')

            department_element = await tr.query_selector('.department div')
            department = await department_element.text_content()

            data.append({
                'date': date,
                'date_display': date_display,
                'date_str': date_str,
                'title': title,
                'title_link': r"https://www.shmtu.edu.cn/" + title_link,
                'department': department
            })

        # Close the browser
        await browser.close()

        return data


def handle_url(url):
    print(url)

    xpath = '//*[@id="block-system-main"]/div/div[1]/div/table/tbody'
    data = asyncio.run(fetch_tr_elements(url, xpath))

    print(f"Found {len(data)} <tr> elements:")

    for item in data:
        print(f"Date: {item['date']}")
        print(f"Date Display: {item['date_display']}")
        print(f"Date String: {item['date_str']}")
        print(f"Title: {item['title']}")
        print(f"Title Link: {item['title_link']}")
        print(f"Department: {item['department']}")
        print("-" * 80)

    return data


def main(page_count=20):
    url_list = []

    for i in range(page_count):
        if i == 0:
            url = f"https://www.shmtu.edu.cn/events"
        else:
            url = f"https://www.shmtu.edu.cn/events?page={i}"

        url_list.append(url)

    date_list = []

    for url in url_list:
        date_list.extend(handle_url(url))

    csv_content = ""
    for item in date_list:
        csv_content += f"{item['date_str']},{item['title']},{item['department']},{item['title_link']}\n"

    now = datetime.datetime.now()
    time_str = now.strftime("%Y-%m-%d-%H-%M-%S")

    with open(f'shmtu-event-{time_str}.csv', 'w', encoding='utf-8') as f:
        f.write(csv_content)


if __name__ == "__main__":
    main()
