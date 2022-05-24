import scrapy
from scrapy_selenium import SeleniumRequest
import csv
import dateparser


csv_fields = ["Title", "Text", "Author", "Date", "Url"]
filename = "AspenTimesArticles.csv"


class AspenSpiderSpider(scrapy.Spider):
    name = 'aspen_spider'
    next_page = ""
    new_main_page = ""

    def start_requests(self):
        yield SeleniumRequest(
            url="https://www.aspentimes.com/recent-stories/local/",
            wait_time=5,
            screenshot=False,
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):
        get_urls = response.css("h5 a::attr(href)").extract()
        # get_titles = response.css("h5 a::text").extract()
        # get_dates = response.css(".relative-date::attr(datetime)").extract()
        with open(filename, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile, dialect="excel")
            csvwriter.writerow(csv_fields)

        for url in get_urls:
            AspenSpiderSpider.next_page = url
            next_url = url

            yield response.follow(next_url, callback=self.parse_local)

    def parse_local(self, response):
        # paras = response.css(".oc-body").extract()
        paras = response.css(".oc-body , .lSSlideOuter img, .is-resized img").extract()
        author = response.css("#article-byline h6 a:nth-child(1)")[0].css("::text")[0].extract()
        if author is None:
            author = ""

        final_time = ""
        title = response.css("h1::text")[0].extract()
        time = response.css(".relative-date::attr(datetime)")[0].extract()
        if time is not None:
            date = dateparser.parse(time)
            final_time = date.strftime('%d %B %Y')

        article = ""

        current_url = AspenSpiderSpider.next_page

        for para in paras:
            article += para+" "

        with open(filename, "a+", newline="") as csvfile:
            csvwriter = csv.writer(csvfile, dialect="excel")
            csvwriter.writerow([title, article, author, final_time, current_url])
        pass
