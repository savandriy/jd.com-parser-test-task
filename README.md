jd.com-parser-test-task
======
#### Test task for Bintime

Task:

> Create a scraper to get requested product data in CSV file.  
> One product – one line in file.  
> Link to scrape all products: https://search.jd.com/Search?keyword=qnap&enc=utf-8&wq=qnap&pvid=yhzxfuxi.4ocx0a00n52av  
> Output file should contain such columns - ['Brand', 'MPN', 'URL', 'Name', 'Price', 'Stock'].  

Jd.com uses a lot of Javascipt to load content, so I used Selenium & Firefox to load pages. It works slowly(took me almost 3 hours to parse all products), but eventually you get a nice .csv file.

##### Note:
In order to run this scraper, you need to have:
- Python3 
- Selenium 
- Firefox

Script was tested on Python 3.4, Selenium 2.53.6 & Firefox 44.0, Ubuntu 15.04 (x64).
