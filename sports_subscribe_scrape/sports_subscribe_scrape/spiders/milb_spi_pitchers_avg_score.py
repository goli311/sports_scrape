# """
# With Win And Lose Score With Pitchers AVG Score (W,1-0)
# """
# import json
# import scrapy
# import requests
# from sports_subscribe_scrape.pipelines import SportsSubscribeScrapePipeline
# from sports_subscribe_scrape.config import *
# from datetime import datetime, timedelta
# from random_user_agent.user_agent import UserAgent
# from random_user_agent.params import SoftwareName, OperatingSystem
#
# software_names = [SoftwareName.CHROME.value]
# operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
#
# def user_agent_get():
#     user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
#     user_agent = user_agent_rotator.get_random_user_agent()
#     return user_agent
#
#
# class BaseballScrape(scrapy.Spider):
#
#     name = 'mycrawler3'
#     con = SportsSubscribeScrapePipeline.con
#     cur = SportsSubscribeScrapePipeline.cur
#     headers = {
#         "user-agent": user_agent_get(),
#     }
#     def start_requests(self):
#
#         today_date_get = (datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d')
#         # today_date_get = (datetime.today()).strftime('%Y-%m-%d')
#         url=f'https://statsapi.mlb.com/api/v1/schedule?sportId=14&date={today_date_get}'
#         site_name='milb'
#
#         meta = {
#             'url': url,
#             'site_name':site_name,
#             'today_date_get':today_date_get,
#         }
#         yield scrapy.FormRequest(url=url, callback=self.parse, headers=self.headers,meta=meta)
#
#
#
#     def parse(self, response):
#         try:
#             url = response.meta.get('url')
#             site_name = response.meta.get('site_name')
#             today_date_get = response.meta.get('today_date_get')
#
#
#             try:
#                 main_json=json.loads(response.text)
#
#             except Exception as e:
#                 print("Error in Json Load:", e)
#                 return None
#             page_json_dates_get=main_json.get('dates')
#             if page_json_dates_get:
#                 page_json_dates_get=page_json_dates_get[0]
#                 page_json_date=page_json_dates_get.get('date')
#
#                 if page_json_date == today_date_get:
#                     print(today_date_get)
#                     games_get=page_json_dates_get.get('games')
#                     if games_get:
#
#                         for i in games_get:
#                             gamepk_get= i.get('gamePk')
#
#                             link_get='https://statsapi.mlb.com'+i.get('link')+'?language=en' if i.get('link') else None
#
#                             box_score_link=f'https://www.milb.com/gameday/{gamepk_get}/final/box'
#                             if link_get:
#                                 box_score_res=requests.get(link_get,headers=self.headers)
#                                 box_score_data=box_score_res.text
#
#
#                                 try:
#                                     box_score_json=json.loads(box_score_data)
#
#                                 except Exception as E:
#                                     print("Error in: Box Score Json Load...:", E)
#                                     continue
#
#
#                                 # TODO : Away Team Data scrape------------------
#                                 teams_list=['away','home']
#                                 for k in teams_list:
#                                     try:
#                                         away_data_get=box_score_json.get('liveData').get('boxscore').get('teams').get(k)
#                                     except Exception as E:
#                                         print("Error in: away_data_get...:", E)
#                                         break
#                                         # return None
#                                     # TODO : Probable Pitchers For W OR L Score data-------------------
#                                     try:
#                                         win_pitcher_id_get=box_score_json.get('liveData').get('decisions').get('winner').get('id')
#                                         print('win_pitcher_id_get:',win_pitcher_id_get)
#                                     except:
#                                         win_pitcher_id_get=''
#
#                                     try:
#                                         loser_pitcher_id_get=box_score_json.get('liveData').get('decisions').get('loser').get('id')
#                                     except:
#                                         loser_pitcher_id_get=''
#
#                                     # TODO : (Pitchers AVG Score) match decisions id in home or away players data For : Winer result-------------------
#                                     try:
#                                         result_get = ''
#                                         pitchers_ids_get = away_data_get.get('pitchers')
#                                         if win_pitcher_id_get:
#                                             if win_pitcher_id_get in pitchers_ids_get:
#                                                 result_get = away_data_get.get('players').get(f'ID{win_pitcher_id_get}').get('stats').get('pitching').get('note')
#
#                                         if result_get == '':
#                                             if loser_pitcher_id_get in pitchers_ids_get:
#                                                 result_get = away_data_get.get('players').get(f'ID{loser_pitcher_id_get}').get('stats').get('pitching').get('note')
#
#
#                                     except:
#                                         result_get = ''
#
#                                     if result_get == '':
#                                         result_get='-'
#
#                                     # TODO : Scrape Batters data-------------------
#                                     batters_ids_get=away_data_get.get('batters')
#                                     if batters_ids_get:
#
#                                         # TODO : ----------------------------------
#                                         for j in batters_ids_get:
#
#                                             try:
#
#                                                 player_name_get = box_score_json.get('gameData').get('players').get(f'ID{j}').get('boxscoreName')
#                                                 player_name =player_name_get.strip() if player_name_get else ""
#
#                                                 try:
#                                                     #  TODO : K = away or home --------------------
#                                                     school_name_get=box_score_json.get('gameData').get('teams').get(k).get('locationName')
#                                                     school_name=school_name_get.strip() if school_name_get else ""
#
#                                                 except:
#                                                     school_name=''
#                                                 try:
#                                                     school_name_away_get=box_score_json.get('gameData').get('teams').get('away').get('name')
#                                                     school_name_away=school_name_away_get.strip() if school_name_away_get else ""
#
#                                                     school_name_home_get=box_score_json.get('gameData').get('teams').get('home').get('name')
#                                                     school_name_home=school_name_home_get.strip() if school_name_home_get else ""
#
#                                                     event_name=f'{school_name_home},{school_name_away}'
#                                                 except:
#                                                     event_name=''
#                                                 try:
#                                                     batting_json_get=away_data_get.get('players').get(f'ID{j}').get('stats').get('batting')
#                                                 except:
#                                                     batting_json_get={}
#
#                                                 if batting_json_get:
#
#                                                     ab_get=batting_json_get.get('atBats')
#                                                     ab_get=ab_get if ab_get or ab_get == 0 else ""
#
#                                                     r_get = batting_json_get.get('runs')
#                                                     r_get = r_get if r_get or r_get == 0 else ""
#
#                                                     h_get = batting_json_get.get('hits')
#                                                     h_get = h_get if h_get or h_get == 0 else ""
#
#                                                     rbi_get = batting_json_get.get('rbi')
#                                                     rbi_get = rbi_get if rbi_get or rbi_get == 0 else ""
#
#                                                     bb_get = batting_json_get.get('baseOnBalls')
#                                                     bb_get = bb_get if bb_get or bb_get == 0 else ""
#
#                                                     so_get = batting_json_get.get('strikeOuts')
#                                                     so_get = so_get if so_get or so_get == 0 else ""
#
#                                                     lob_get = batting_json_get.get('leftOnBase')
#                                                     lob_get = lob_get if lob_get or lob_get == 0 else ""
#
#                                                     try:
#                                                         avg_get=away_data_get.get('players').get(f'ID{j}').get('seasonStats').get('batting').get('avg')
#                                                         avg_get=avg_get if avg_get else ""
#                                                     except:
#                                                         avg_get=''
#
#
#                                                     try:
#                                                         ops_get=away_data_get.get('players').get(f'ID{j}').get('seasonStats').get('batting').get('ops')
#                                                         ops_get=ops_get if ops_get else ""
#                                                     except:
#                                                         ops_get=''
#
#
#                                                     try:
#                                                         insert_query = f"""INSERT INTO `{db_data_table}`(`player`, `school`, `result`, `box_score_link`, `match_date`, `event_name`, `game_status`, `AB`, `R`, `H`, `RBI`, `BB`, `SO`, `LOB`, `AVG`, `OPS`, `site_name`)
#                                                         VALUES ("{player_name}","{school_name}","{result_get}","{box_score_link}","{today_date_get}","{event_name}","",{ab_get},{r_get},{h_get},{rbi_get},{bb_get},{so_get},{lob_get},{avg_get},{ops_get},"{site_name}")"""
#
#                                                         print(insert_query)
#                                                         self.cur.execute(insert_query)
#                                                         print("inserted...")
#                                                         self.con.commit()
#
#                                                     except Exception as E:
#                                                         print("error in insert query2", E)
#                                                         return None
#
#                                                     # break
#
#
#                                             except Exception as E:
#                                                 print("Error in: batting_json_get...:", E)
#                                                 return None
#
#                                     # TODO : Scrape Pitchers data-------------------
#                                     pitchers_ids_get = away_data_get.get('pitchers')
#                                     if pitchers_ids_get:
#                                         for m in pitchers_ids_get:
#                                             try:
#
#                                                 p_player_name_get = box_score_json.get('gameData').get('players').get(f'ID{m}').get('boxscoreName')
#                                                 p_player_name = p_player_name_get.strip() if p_player_name_get else ""
#
#
#
#                                                 try:
#                                                     #  TODO : K = away or home --------------------
#                                                     p_school_name_get = box_score_json.get('gameData').get('teams').get(k).get('locationName')
#                                                     p_school_name = p_school_name_get.strip() if p_school_name_get else ""
#
#                                                 except:
#                                                     p_school_name = ''
#                                                 try:
#                                                     p_school_name_away_get = box_score_json.get('gameData').get('teams').get('away').get('name')
#                                                     p_school_name_away = p_school_name_away_get.strip() if p_school_name_away_get else ""
#
#
#                                                     p_school_name_home_get = box_score_json.get('gameData').get('teams').get('home').get('name')
#                                                     p_school_name_home = p_school_name_home_get.strip() if p_school_name_home_get else ""
#
#                                                     p_event_name = f'{p_school_name_home} , {p_school_name_away}'
#                                                 except:
#                                                     p_event_name = ''
#                                                 try:
#                                                     p_pitching_json_get = away_data_get.get('players').get(f'ID{m}').get('stats').get('pitching')
#
#                                                 except:
#                                                     p_pitching_json_get = {}
#
#                                                 if p_pitching_json_get:
#
#                                                     p_ip_get = p_pitching_json_get.get('inningsPitched')
#                                                     p_ip_get = p_ip_get if p_ip_get or p_ip_get == 0 else ""
#
#                                                     p_h_get = p_pitching_json_get.get('hits')
#                                                     p_h_get = p_h_get if p_h_get or p_h_get == 0 else ""
#
#                                                     p_r_get = p_pitching_json_get.get('runs')
#                                                     p_r_get = p_r_get if p_r_get or p_r_get == 0 else ""
#
#                                                     p_er_get = p_pitching_json_get.get('earnedRuns')
#                                                     p_er_get = p_er_get if p_er_get or p_er_get == 0 else ""
#
#                                                     p_bb_get = p_pitching_json_get.get('baseOnBalls')
#                                                     p_bb_get = p_bb_get if p_bb_get or p_bb_get == 0 else ""
#
#                                                     p_so_get = p_pitching_json_get.get('strikeOuts')
#                                                     p_so_get = p_so_get if p_so_get or p_so_get == 0 else ""
#
#                                                     p_hr_get = p_pitching_json_get.get('homeRuns')
#                                                     p_hr_get = p_hr_get if p_hr_get or p_hr_get == 0 else ""
#
#                                                     try:
#                                                         p_era_get = away_data_get.get('players').get(f'ID{m}').get('seasonStats').get('pitching').get('era')
#                                                         p_era_get = p_era_get if p_era_get else ""
#                                                     except:
#                                                         p_era_get = ''
#
#
#                                                     try:
#                                                         p_insert_query = f"""INSERT INTO `{db_data_table_pitcher}`(`player`, `school`, `result`, `box_score_link`, `match_date`, `event_name`, `game_status`, `site_name`, `IP`, `H`, `R`, `ER`, `BB`, `SO`, `HR`, `WP`, `BK`, `HBP`, `IBB`, `AB`, `BF`, `FO`, `GO`, `NP`,`ERA`)
#                                                         VALUES ("{p_player_name}","{p_school_name}","{result_get}","{box_score_link}","{today_date_get}","{p_event_name}","","{site_name}",{p_ip_get},{p_h_get},{p_r_get},{p_er_get},{p_bb_get},{p_so_get},{p_hr_get},0,0,0,0,0,0,0,0,0,{p_era_get})"""
#
#                                                         print(p_insert_query)
#                                                         self.cur.execute(p_insert_query)
#                                                         print("Pitcher inserted...")
#                                                         self.con.commit()
#
#                                                     except Exception as E:
#                                                         print("error in insert query pitcher", E)
#                                                         return None
#
#                                                     # break
#
#                                             except Exception as E:
#                                                 print("Error in: batting_json_get...:", E)
#                                                 return None
#
#
#                                 # break # games boxscore links for loop
#
#                 else:
#                     print("Main Page Content: Date Not Matched...:")
#                     return None
#             else:
#                 print("Main Page Content Not Found (Date Key)...:")
#                 return None
#         except Exception as E:
#             print("Error in Parse Method", E)
#             return None
#
# from scrapy.cmdline import execute
# # execute('scrapy crawl mycrawler3'.split())