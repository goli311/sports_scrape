import time
import re
import requests
import scrapy
from sports_subscribe_scrape.pipelines import SportsSubscribeScrapePipeline
from sports_subscribe_scrape.config import *
from scrapy.selector import Selector
from datetime import datetime, timedelta
import os
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]

def user_agent_get():
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent


class BaseballScrape(scrapy.Spider):

    name = 'mycrawler2'
    con = SportsSubscribeScrapePipeline.con
    cur = SportsSubscribeScrapePipeline.cur

    def start_requests(self):


        results = [('https://generalssports.com/sports/baseball/schedule', 'generalssports'),
                   ('https://jmusports.com/sports/baseball/schedule?path=baseball', 'jmusports')]


        for i in results:
            url=i[0]
            site_name=i[1]

            headers = {
                "user-agent": user_agent_get(),
            }
            meta = {
                'url': url,
                'site_name':site_name,
            }
            yield scrapy.FormRequest(url=url, callback=self.parse, headers=headers,meta=meta)



    def parse(self, response):
        try:
            url = response.meta.get('url')
            site_name = response.meta.get('site_name')
            if response.xpath('//main[@id="main-content"]'):
                all_li=response.xpath('//h3[@id="heading_scheduled_games"]/parent::section/ul/li')

                if all_li:
                    for i in all_li:
                        game_result_get=i.xpath('.//div[contains(@class,"game-result")]/span/text()').getall()
                        game_result=''
                        if game_result_get:
                            game_result=''.join([g.strip() for g in game_result_get if g.strip()])
                        box_score_link_get=i.xpath('.//div[contains(@class,"print-el")]//ul/li//a[contains(text(),"Box Score")]/@href').get()

                        if box_score_link_get:
                            mach_date_get=i.xpath('.//div[contains(@class,"sidearm-schedule-game-opponent-date")]/span/text()').get()

                            if mach_date_get:
                                mach_date_get1=mach_date_get.strip()

                                # prev_date_get = datetime.today()
                                prev_date_get = datetime.today() - timedelta(days=1)

                                prev_date_month=prev_date_get.strftime("%b")
                                prev_date_date=prev_date_get.strftime("%#d")
                                mach_date_get1_split=mach_date_get1.split()

                                try:
                                    today_split_month=mach_date_get1_split[0]
                                    today_split_date=mach_date_get1_split[1]
                                    if today_split_month==prev_date_month and today_split_date ==prev_date_date:



                                        if site_name=="generalssports":
                                            box_score_link = 'https://generalssports.com' + box_score_link_get
                                        elif site_name=="jmusports":
                                            box_score_link = 'https://jmusports.com' + box_score_link_get
                                        else:
                                            print('Error : site_name Not Matched.......',site_name)
                                            return None

                                        headers = {
                                            "user-agent": user_agent_get(),
                                        }

                                        # Todo : Box score request Here...
                                        box_req=requests.get(box_score_link,headers=headers)

                                        box_resp = Selector(text=box_req.text)

                                        event_name_get=box_resp.xpath('//article//h2/text()').get()
                                        final_event_name=''
                                        if event_name_get:

                                            final_event_name=re.sub("[\(\[].*?[\)\]]", "", event_name_get)
                                            final_event_name=final_event_name.replace("-vs-","vs").replace("  "," ").strip()
                                        # -----------------------------------
                                        table_get = box_resp.xpath('//section[@aria-label="Team Individual Statistics"]//div[contains(@class,"columns")]//table')
                                        if table_get:

                                            for j in table_get:

                                                school_name_temp=''
                                                school_name_temp = j.xpath('./caption/text()').get()
                                                print("school", school_name_temp)
                                                tr_get = j.xpath('.//tbody//tr')
                                                if tr_get:
                                                    for k in tr_get:

                                                        """30-03-2022"""

                                                        """"""
                                                        player_name_get = k.xpath('./th/a//text()').get()
                                                        player_name_get1 = k.xpath('./th/text()').getall()
                                                        player_name = ''
                                                        if player_name_get:
                                                            player_name = player_name_get
                                                        elif player_name_get1:
                                                            # print('-----------------------')
                                                            for l in player_name_get1:
                                                                name_get1 = l.strip()
                                                                # print('L:',l.strip())
                                                                if name_get1:
                                                                    player_name = name_get1
                                                                    break
                                                            if not player_name:
                                                                print('Player Not Found......:', box_score_link)
                                                                return None


                                                        # Todo: Statistics
                                                        ab_get = k.xpath('./td[contains(@data-label,"AB")]//text()').get()


                                                        r_get = k.xpath('./td[contains(@data-label,"R")]//text()').get()


                                                        h_get = k.xpath('./td[contains(@data-label,"H")]//text()').get()


                                                        rbi_get = k.xpath('./td[contains(@data-label,"RBI")]//text()').get()


                                                        bb_get = k.xpath('./td[contains(@data-label,"BB")]//text()').get()


                                                        so_get = k.xpath('./td[contains(@data-label,"SO")]//text()').get()


                                                        lob_get = k.xpath('./td[contains(@data-label,"LOB")]//text()').get()



                                                        try:
                                                            insert_query = f"""INSERT INTO `{db_data_table}`(`player`, `school`, `result`, `box_score_link`, `match_date`, `event_name`, `game_status`, `AB`, `R`, `H`, `RBI`, `BB`, `SO`, `LOB`, `site_name`) 
                                                            VALUES ("{player_name}","{school_name_temp}","{game_result}","{box_score_link}","{mach_date_get1}","{final_event_name}","","{ab_get}","{r_get}","{h_get}","{rbi_get}","{bb_get}","{so_get}","{lob_get}","{site_name}")"""

                                                            # print(insert_query)
                                                            self.cur.execute(insert_query)
                                                            self.con.commit()
                                                            print("inserted...")
                                                        except Exception as e:
                                                            print('Error In Insert Query....:{}:{}'.format(e,box_score_link))

                                        # Todo : Pitchers Table

                                        pitchers_table_section_get = box_resp.xpath('//section[@aria-label="Team Individual Pitching Statistics"]//table')
                                        if pitchers_table_section_get:
                                            for pt in pitchers_table_section_get:
                                                pitchers_table_check = pt.xpath('./caption')
                                                if pitchers_table_check:
                                                    pitchers_tbody_get = pt.xpath('.//tbody/tr')
                                                    school_name_pitchers = ''
                                                    school_name_pitchers = pt.xpath('./caption/text()').get()
                                                    print("school", school_name_pitchers)
                                                    if pitchers_tbody_get:
                                                        for ptb in pitchers_tbody_get:
                                                            pitchers_player = ''
                                                            pitchers_player_get = ptb.xpath('./th/a/text()')
                                                            if pitchers_player_get:
                                                                pitchers_player1 = pitchers_player_get.get()
                                                                if pitchers_player1:
                                                                    pitchers_player = re.sub("[\(\[].*?[\)\]]", "",pitchers_player1)
                                                                    pitchers_player = pitchers_player.strip()

                                                            elif ptb.xpath('./th/text()'):
                                                                pitchers_player1 = ptb.xpath('./th/text()').get()
                                                                if pitchers_player1:
                                                                    pitchers_player = re.sub("[\(\[].*?[\)\]]", "",pitchers_player1)
                                                                    pitchers_player = pitchers_player.strip()
                                                            # print(pitchers_table_check.get())
                                                            pitchers_ip_get = ptb.xpath('./td[contains(@data-label,"IP")]/text()').get()
                                                            pitchers_h_get = ptb.xpath('./td[contains(@data-label,"H")]/text()').get()
                                                            pitchers_r_get = ptb.xpath('./td[contains(@data-label,"R")]/text()').get()
                                                            pitchers_er_get = ptb.xpath('./td[contains(@data-label,"ER")]/text()').get()
                                                            pitchers_bb_get = ptb.xpath('./td[contains(@data-label,"BB")]/text()').get()
                                                            pitchers_so_get = ptb.xpath('./td[contains(@data-label,"SO")]/text()').get()
                                                            pitchers_wp_get = ptb.xpath('./td[contains(@data-label,"WP")]/text()').get()
                                                            pitchers_bk_get = ptb.xpath('./td[contains(@data-label,"BK")]/text()').get()
                                                            pitchers_hbp_get = ptb.xpath('./td[contains(@data-label,"HBP")]/text()').get()
                                                            pitchers_ibb_get = ptb.xpath('./td[contains(@data-label,"IBB")]/text()').get()
                                                            pitchers_ab_get = ptb.xpath('./td[contains(@data-label,"AB")]/text()').get()
                                                            pitchers_bf_get = ptb.xpath('./td[contains(@data-label,"BF")]/text()').get()
                                                            pitchers_fo_get = ptb.xpath('./td[contains(@data-label,"FO")]/text()').get()
                                                            pitchers_go_get = ptb.xpath('./td[contains(@data-label,"GO")]/text()').get()
                                                            pitchers_np_get = ptb.xpath('./td[contains(@data-label,"NP")]/text()').get()

                                                            try:

                                                                insert_query_pitchers = f"INSERT INTO `{db_data_table_pitcher}` ( `player`, `school`, `result`, `box_score_link`, `match_date`, `event_name`, `game_status`, `site_name`, `IP`, `H`, `R`, `ER`, `BB`, `SO`, `HR`, `WP`, `BK`, `HBP`, `IBB`, `AB`, `BF`, `FO`, `GO`, `NP`) " \
                                                                                        f"""VALUES ("{pitchers_player}","{school_name_pitchers}","{game_result}","{box_score_link}","{mach_date_get1}","{final_event_name}","","{site_name}",{pitchers_ip_get},{pitchers_h_get},{pitchers_r_get},{pitchers_er_get},{pitchers_bb_get},{pitchers_so_get},"0",{pitchers_wp_get},{pitchers_bk_get},{pitchers_hbp_get},{pitchers_ibb_get},{pitchers_ab_get},{pitchers_bf_get},{pitchers_fo_get},{pitchers_go_get},{pitchers_np_get})"""

                                                                # print(insert_query_pitchers)
                                                                self.cur.execute(insert_query_pitchers)
                                                                self.con.commit()
                                                                print("inserted...")

                                                            except Exception as e:
                                                                print('Error In Insert Query....:{}:{}'.format(e, box_score_link))

                                except Exception as e:
                                    print('Error: today_split_month or today_split_date indexing....:',e)
                            else:
                                print('mach_date_get Not Found......:', box_score_link_get)
                                return None
                else:
                    print("Error : all_li not found...")
                    return None
            else:
                print("Error in Parse Method...")
                return None
        except Exception as E:
            print("Error in Parse Method", E)
            return None

from scrapy.cmdline import execute
# execute('scrapy crawl mycrawler2'.split())