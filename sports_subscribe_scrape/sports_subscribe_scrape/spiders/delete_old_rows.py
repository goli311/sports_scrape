# """
# For Deleting Old Rows
# """
# from sports_subscribe_scrape.config import *
# from sports_subscribe_scrape.pipelines import SportsSubscribeScrapePipeline
# from datetime import datetime, timedelta
#
# con = SportsSubscribeScrapePipeline.con
# cur = SportsSubscribeScrapePipeline.cur
#
# # today_date_get = (datetime.today()-timedelta(days=5)).strftime('%Y-%m-%d')
# today_date_get = (datetime.today()).strftime('%Y-%m-%d')
# print('today_date_get:',today_date_get)
# try:
#     # delete_data_table_rows = f"""DELETE FROM {db_data_table} WHERE scraped_date < '{today_date_get}%'"""
#     delete_data_table_rows = f"""DELETE FROM {db_data_table} WHERE scraped_date like '{today_date_get}%'"""
#
#     print(delete_data_table_rows)
#     cur.execute(delete_data_table_rows)
#     # print("inserted...")
#     # con.commit()
# except Exception as E:
#     print("error in Delete query2", E)
#
# try:
#     delete_pitchers_table_rows = f"""DELETE FROM {db_data_table_pitcher} WHERE scraped_date like '{today_date_get}%'"""
#     # delete_pitchers_table_rows = f"""DELETE FROM {db_data_table_pitcher} WHERE scraped_date < '{today_date_get}%'"""
#
#     print(delete_pitchers_table_rows)
#     cur.execute(delete_pitchers_table_rows)
#     # print("inserted...")
#     # con.commit()
# except Exception as E:
#     print("error in Delete query2", E)
#
# con.commit()
# con.close()