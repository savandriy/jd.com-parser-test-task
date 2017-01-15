from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from lxml import html
import time
import csv


def write_csv(items):
    """
    Takes a list of dictionaries, where every dictionary contains information about some product.
    Writes all of given information line-by-line into a csv file.
    """
    with open('items.csv', 'w') as csvfile:
        fieldnames = ['Brand', 'MPN', 'URL', 'Name', 'Price', 'Stock']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for item in items:
            writer.writerow(item)


def parse_items(url):
    """
    Takes a url with all of the items needed to be parsed.
    Returns a list of dictionaries, where every dictionary contains information about some product.
    This function does all the 'dirty' work.
    """
    # initialize the output list
    output_list = []
    # Initialize a webdriver
    browser = webdriver.Firefox()

    # load the page with all of the items
    browser.get(url)

    # every iteration of this cycle represents one page with products
    while True:
        # Scroll the page to load all products(due to javascript "lazy load")
        len_of_page = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match = False
        while match == False:
            last_count = len_of_page
            time.sleep(3)
            len_of_page = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            if last_count == len_of_page:
                match = True

        counter = 1
        # Every iteration of this cycle - parsing one product
        while True:
            # All products are list items - so to find the next product we just need to increment
            xpath = '//*[@id="J_goodsList"]/ul/li[' + str(counter) + ']/div/div[1]/a'
            try:
                # Find the product and it's link on main page
                link = browser.find_element_by_xpath(xpath)
                # Scroll to the found element to make it visible
                browser.execute_script("arguments[0].scrollIntoView(true);", link)
            except:
                # If we didn't find a product - go back to main cycle, probably to go to new page
                break
            # Save the window opener (current window, do not mistaken with tab... not the same)
            main_window = browser.current_window_handle

            # Open the link in a new tab by sending key strokes on the element
            # Use: Keys.CONTROL + Keys.SHIFT + Keys.RETURN to open tab on top of the stack
            link.send_keys(Keys.CONTROL + Keys.RETURN)

            # Switch tab to the new tab, which we will assume is the next one on the right
            browser.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.TAB)

            # Put focus on current window which will, in fact, put focus on the current visible tab
            browser.switch_to.window(main_window)

            # Scroll the page to load all products(due to javascript "lazy load")
            len_of_page = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            match = False
            while match == False:
                last_count = len_of_page
                time.sleep(3)
                len_of_page = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if last_count == len_of_page:
                    match = True

            # Find the url of the product
            item_url = browser.current_url
            # Find Brand of current product
            item_brand = browser.find_element_by_css_selector('#parameter-brand > li > a:nth-child(1)').text
            # Find MPN of current product
            # Create a tree from product page html code
            tree = html.fromstring(browser.page_source)

            # Due to different markdowns of product pages we need to try find information 2 times
            try:
                r = tree.xpath('//*[@id="parameter2"]/li[2]')
                item_mpn = r[0].get('title')
            except:
                r = tree.xpath('//*[@id="detail"]/div[2]/div[1]/div[1]/ul[2]/li[2]')
                item_mpn = r[0].get('title')

            # Find Name of item
            try:
                item_name = tree.xpath('//*[@id="name"]/h1')[0].text_content()
            except:
                item_name = tree.xpath('//div[@class="itemInfo-wrap"]/div[@class="sku-name"]')[0].text_content()

            # Find price of item
            try:
                item_price = tree.xpath('//*[@id="jd-price"]')[0].text_content()[1:]
            except:
                item_price = tree.xpath('//span[@class="p-price"]/span[2]')[0].text_content()

            # Find the Stock status
            stock_text = tree.xpath('//*[@id="store-prompt"]/strong')[0].text_content()

            item_stock = ''
            if stock_text == '无货':
                item_stock = 0
            elif stock_text == '有货':
                item_stock = 1

            output_list.append({'Brand': item_brand, 'MPN': item_mpn, 'URL': item_url, 'Name': item_name,
                                'Price': item_price, 'Stock': item_stock})

            # Close current tab
            browser.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')

            # Put focus on current window which will be the window opener
            browser.switch_to.window(main_window)

            counter += 1

        try:
            # If the next page button is inactive -> we're on the last page -> end the cycle
            browser.find_element_by_css_selector('#J_topPage > a.fp-next.disabled')
            break
        except:
            # Find and press the 'next page' button
            browser.find_element_by_css_selector('#J_topPage > a.fp-next').click()

    return output_list


if __name__ == '__main__':
    start_time = time.time()
    # Url with all of the items
    url = 'https://search.jd.com/Search?keyword=qnap&enc=utf-8&wq=qnap&pvid=yhzxfuxi.4ocx0a00n52av'
    # parse all of the items
    print('Started parsing')
    items = parse_items(url)
    # write all parsed items to a csv file
    print('Writing items to file')
    write_csv(items)
    print("--- %s minutes ---" % ((time.time() - start_time) / 60))
