import requests
import scrapy
from datetime import date, timedelta
from sports_subscribe_scrape.pipelines import SportsSubscribeScrapePipeline
from sports_subscribe_scrape.config import *
import scrapy.selector
import os
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
#test git

def user_agent_get():
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent
#test git

class MainScrape(scrapy.Spider):
    name = 'mycrawler1_d'
    h1 = {
        'authority': 'www.rbcathletics.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'

    }

    con = SportsSubscribeScrapePipeline.con
    cur = SportsSubscribeScrapePipeline.cur

    def start_requests(self):

        results = [('https://www.rbcathletics.com/sports/bsb/2021-22/schedule', 'rbcathletics')]

        for i in results:
            url = i[0]
            site_name = i[1]

            headers = {
                "user-agent": user_agent_get(),
            }

            yield scrapy.FormRequest(url=url, callback=self.parse, headers=headers,
                                     meta={'url': url, 'site_name': site_name,
                                           })

    def parse(self, response):
        try:
            site_name = response.meta.get('site_name')
            if response.xpath('//div[@class="links"]//ul//li//a[contains(@aria-label,"Box Score")][not(contains(@target,"_blank"))]'):  # check if box score link is available or not

                main_loop = response.xpath('//div[@class="links"]//ul//li//a[contains(@aria-label,"Box Score")][not(contains(@target,"_blank"))]')
                for i in main_loop:

                    box_score_link = i.xpath('.//@href').get()
                    final_box_score_link = f"https://www.rbcathletics.com{box_score_link}"


                    match_date = final_box_score_link.split("/")[-1].split("_")[0]

                    yesterday_date = (date.today() - timedelta(days=1)).strftime('%Y%m%d')
                    # yesterday_date = date.today().strftime('%Y%m%d')

                    if match_date == yesterday_date:
                        print("...MATCH AVAILABLE...")

                        event_name = i.xpath('.//@aria-label').get()

                        final_event_get=event_name.split('Baseball event:')[1].split(': Box Score')[0].strip()

                        final_event=final_event_get.split(": ")[1].strip()


                        opponent = i.xpath('.//ancestor::div[@class="links"]//ancestor::div[@class="event-info clearfix"]//div[@class="opponent"]//span[@class="team-name"]//text()').get()
                        opponent_final=opponent.strip()

                        match_date_get = i.xpath('.//ancestor::div[@class="links"]//ancestor::div[@class="event-info clearfix"]//div[@class="date"]//@title').get()
                        final_match_date=match_date_get.strip()


                        status = i.xpath('.//ancestor::div[@class="links"]//ancestor::div[@class="event-info clearfix"]//div[@class="status"]//text()').get()

                        final_game_status=status.strip()

                        result = i.xpath('.//ancestor::div[@class="links"]//ancestor::div[@class="event-info clearfix"]//div[@class="result"]//text()').get()
                        final_result=result.strip()


                        """------Request to the box score link------"""
                        try:
                            box_response = requests.get(final_box_score_link, headers=self.h1)

                            main_response = scrapy.Selector(text=box_response.text)

                            tab_loop = main_response.xpath('//span[@class="offscreen"][contains(text(),"Batters")]/ancestor::table//tr')
                            for i in tab_loop:
                                if i.xpath('.//span[contains(@class,"player-name")]'):

                                    school_name=i.xpath('.//span[contains(@class,"player-name")]//ancestor::table//span[@class="team-name"]//text()').get()
                                    final_school_name=school_name.strip()
                                    player = i.xpath('.//span[contains(@class,"player-name")]//text()').get()
                                    ab = i.xpath('.//span[contains(@class,"player-name")]//following::td[1]//text()').get()
                                    r = i.xpath('.//span[contains(@class,"player-name")]//following::td[2]//text()').get()
                                    h = i.xpath('.//span[contains(@class,"player-name")]//following::td[3]//text()').get()
                                    rbi = i.xpath('.//span[contains(@class,"player-name")]//following::td[4]//text()').get()
                                    bb = i.xpath('.//span[contains(@class,"player-name")]//following::td[5]//text()').get()
                                    so = i.xpath('.//span[contains(@class,"player-name")]//following::td[6]//text()').get()
                                    lob = i.xpath('.//span[contains(@class,"player-name")]//following::td[7]//text()').get()


                                    try:
                                        insert_query=f"INSERT INTO {db_data_table}" \
                                                     f"(`player`, `school`, `result`, `box_score_link`, `match_date`, `event_name`, `game_status`, `AB`, `R`, `H`, `RBI`, `BB`, `SO`, `LOB`, `site_name`) " \
                                                     f"VALUES ('{player}','{final_school_name}','{final_result}','{final_box_score_link}','{final_match_date}','{final_event}','{final_game_status}','{ab}','{r}','{h}','{rbi}','{bb}','{so}','{lob}','{site_name}')"


                                        self.cur.execute(insert_query)
                                        self.con.commit()
                                        print("inserted...")

                                    except Exception as E:
                                        print("error in insert query1",E)
                                        return None


                                elif i.xpath('.//a[contains(@class,"player-name")]'):

                                    school_name = i.xpath('.//a[contains(@class,"player-name")]//ancestor::table//a[@class="team-name"]//text()').get()
                                    final_school_name = school_name.strip()
                                    player = i.xpath('.//a[contains(@class,"player-name")]//text()').get()
                                    ab = i.xpath('.//a[contains(@class,"player-name")]//following::td[1]//text()').get()
                                    r = i.xpath('.//a[contains(@class,"player-name")]//following::td[2]//text()').get()
                                    h = i.xpath('.//a[contains(@class,"player-name")]//following::td[3]//text()').get()
                                    rbi = i.xpath('.//a[contains(@class,"player-name")]//following::td[4]//text()').get()
                                    bb = i.xpath('.//a[contains(@class,"player-name")]//following::td[5]//text()').get()
                                    so = i.xpath('.//a[contains(@class,"player-name")]//following::td[6]//text()').get()
                                    lob = i.xpath('.//a[contains(@class,"player-name")]//following::td[7]//text()').get()
                                    try:
                                        insert_query = f"INSERT INTO {db_data_table}" \
                                                       f"(`player`, `school`, `result`, `box_score_link`, `match_date`, `event_name`, `game_status`, `AB`, `R`, `H`, `RBI`, `BB`, `SO`, `LOB`, `site_name`) " \
                                                       f"VALUES ('{player}','{final_school_name}','{final_result}','{final_box_score_link}','{final_match_date}','{final_event}','{final_game_status}','{ab}','{r}','{h}','{rbi}','{bb}','{so}','{lob}','{site_name}')"
                                        print(insert_query)
                                        self.cur.execute(insert_query)
                                        print("inserted...")
                                        self.con.commit()

                                    except Exception as E:
                                        print("error in insert query2", E)
                                        return None


                            """ ....pitchers data..."""
                            tab_loop_pitcher=main_response.xpath('//span[@class="offscreen"][contains(text(),"Pitchers")]/ancestor::table//tr')
                            for j in tab_loop_pitcher:
                                if j.xpath('.//span[contains(@class,"player-name")]'):

                                    school_name = j.xpath( './/span[contains(@class,"player-name")]//ancestor::table//span[@class="team-name"]//text()').get()
                                    final_school_name = school_name.strip()

                                    player = j.xpath('.//span[contains(@class,"player-name")]//text()').get()
                                    ip = j.xpath('.//span[contains(@class,"player-name")]//following::td[1]//text()').get()
                                    h = j.xpath('.//span[contains(@class,"player-name")]//following::td[2]//text()').get()
                                    r = j.xpath('.//span[contains(@class,"player-name")]//following::td[3]//text()').get()
                                    er = j.xpath('.//span[contains(@class,"player-name")]//following::td[4]//text()').get()
                                    bb = j.xpath('.//span[contains(@class,"player-name")]//following::td[5]//text()').get()
                                    so = j.xpath('.//span[contains(@class,"player-name")]//following::td[6]//text()').get()
                                    hr = j.xpath('.//span[contains(@class,"player-name")]//following::td[7]//text()').get()


                                    try:
                                        insert_query = f"INSERT INTO {db_data_table_pitcher}" \
                                                       f"(`player`, `school`, `result`, `box_score_link`, `match_date`, `event_name`, `game_status`, `IP`, `H`, `R`, `ER`, `BB`, `SO`, `HR`, `site_name`) " \
                                                       f"VALUES ('{player}','{final_school_name}','{final_result}','{final_box_score_link}','{final_match_date}','{final_event}','{final_game_status}','{ip}','{h}','{r}','{er}','{bb}','{so}','{hr}','{site_name}')"

                                        print(insert_query)
                                        self.cur.execute(insert_query)
                                        self.con.commit()
                                        print("inserted...")

                                    except Exception as E:
                                        print("error in insert query1", E)
                                        return None


                                elif j.xpath('.//a[contains(@class,"player-name")]'):

                                    school_name = j.xpath(
                                        './/a[contains(@class,"player-name")]//ancestor::table//a[@class="team-name"]//text()').get()
                                    final_school_name = school_name.strip()
                                    player = j.xpath('.//a[contains(@class,"player-name")]//text()').get()
                                    ip = j.xpath('.//a[contains(@class,"player-name")]//following::td[1]//text()').get()
                                    h = j.xpath('.//a[contains(@class,"player-name")]//following::td[2]//text()').get()
                                    r = j.xpath('.//a[contains(@class,"player-name")]//following::td[3]//text()').get()
                                    er = j.xpath('.//a[contains(@class,"player-name")]//following::td[4]//text()').get()
                                    bb = j.xpath('.//a[contains(@class,"player-name")]//following::td[5]//text()').get()
                                    so = j.xpath('.//a[contains(@class,"player-name")]//following::td[6]//text()').get()
                                    hr = j.xpath('.//a[contains(@class,"player-name")]//following::td[7]//text()').get()

                                    try:
                                        insert_query = f"INSERT INTO {db_data_table_pitcher}" \
                                                       f"(`player`, `school`, `result`, `box_score_link`, `match_date`, `event_name`, `game_status`, `IP`, `H`, `R`, `ER`, `BB`, `SO`, `HR`, `site_name`) " \
                                                       f"VALUES ('{player}','{final_school_name}','{final_result}','{final_box_score_link}','{final_match_date}','{final_event}','{final_game_status}','{ip}','{h}','{r}','{er}','{bb}','{so}','{hr}','{site_name}')"

                                        print(insert_query)
                                        self.cur.execute(insert_query)
                                        print("inserted...")
                                        self.con.commit()

                                    except Exception as E:
                                        print("error in insert query2", E)
                                        return None

                        except Exception as E:
                            print("error in player request", E)

                        """-------------------------"""

                    else:
                        print(".....no match available.....")

        except Exception as E:
            print("Error in Main Parse Method", E)
            return None


# from scrapy.cmdline import execute
# execute('scrapy crawl mycrawler1_d'.split())
#new
