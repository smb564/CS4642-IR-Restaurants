import scrapy


class HotelSpider(scrapy.Spider):
    name = 'hotels'

    start_urls = ['https://www.yamu.lk/place/restaurants?page=1']
    
    def parse(self, response):
        # get the urls form the page corrsponding to each restaurant
        hotel_urls = response.css('ul.media-list.search-results div.row a::attr(href)').extract()

        for url in hotel_urls:
            yield scrapy.Request(url=url, callback=self.parse_hotel_page)
        
        # check whether next page exits
        # if len(response.css('ul.pagination li.disabled span').extract()) != 2 or response.url.split('?')[-1]=='page=1':

        # check the page number, if exceeds the maximum number of pages, then stop
        if int(response.url.split('=')[-1]) < 45:
            # next page exits (disabled one is the middle ... part , other is the next part in the last page)
            next_url = response.css('ul.pagination li a::attr(href)').extract()[-1]
            with open('log.txt','a+') as f:
                f.write(next_url + '\n')

            yield scrapy.Request(url=next_url, callback=self.parse)


    def parse_hotel_page(self, response):
        title = response.css('div.place-title-box h2::text').extract_first()
        excerpt = response.css('p.excerpt::text').extract_first()

        content = response.css('div.bodycopy p::text').extract()
        # there are additional unwanted <p> tags in the footer of the article, remove them from the content
        unwanted_footer_size = len(response.css('div.bodycopy div p::text').extract())

        content = content[:len(content) - unwanted_footer_size]
        content = ' '.join(map(lambda x: ' '.join(x.split()), content))

        # let's get some additional information about the hotel as well
        # get the tags
        tags = response.css('div.panel.panel-default.place-info-box div.label-yamu div.inner::text').extract()
        tags = map(lambda x: ' '.join(x.split()), tags)

        telephone = response.css('div.panel.panel-default.place-info-box div.time-range a.closed::text').extract_first()
        # this contains 'Call ' remove and add a starting zero
        if telephone!=None:
            telephone = '0' + telephone[len('Call '):]

        info_tab = response.css('div.panel.panel-default.place-info-box div.text-center.info p::text').extract()

        address = info_tab[1]
        directions = info_tab[3]

        ratings = response.css('div.panel.panel-default.place-info-box dl.dl-horizontal dd span::text').extract()
        rating_category = response.css('div.panel.panel-default.place-info-box dl.dl-horizontal dt a::text').extract()
        rating = {}

        for cat, rat in zip(rating_category, ratings):
            rating[cat] = rat
        
        operating_hours = response.css('div.panel.panel-default.place-info-box p.open::text').extract_first()

        # now create the object to be saved
        yield {
            'titile' : title,
            'excerpt' : excerpt,
            'content' : content,
            'tags' : tags,
            'telephone' : telephone,
            'address' : address,
            'directions' : directions,
            'ratings' : rating,
            'operating_hourse' : operating_hours
        }
