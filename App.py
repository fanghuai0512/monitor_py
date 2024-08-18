import logging

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from Mysql_data import Database
from get_response import get_response
from async_detail_paser import DetailParse
import time
import traceback

items = []

def get_biz_product(item):
    db = item
    db.connect()
    try:
        result = db.execute_read_query("select DISTINCT asin from tb_biz_product where monitor = 1")
        return result
    except Exception as e:
        return None
    finally:
        db.close_connection()


def fetch_url(item):
    url = "https://www.amazon.com/dp/"+item["data"]["asin"]+"/ref=olp-opf-redir?aod=1&condition=new"
    response = get_response(url)
    if type(response) == str:
        return item["data"]["asin"], response, 0
    else:
        return item["data"]["asin"], response, 1

def worker_thread(db):
    items = get_biz_product(db)
    lists = []
    for item in items:
        lists.append({"db": db, "data": item})
    # 记录开始时间
    start_time = time.time()
    # 使用with语句创建线程池
    with ThreadPoolExecutor(max_workers=10) as executor:
        # 将任务分配给线程池
        future_to_url = {executor.submit(fetch_url, item): item for item in lists}
        # 收集结果
        for future in as_completed(future_to_url):
            item = future_to_url[future]
            db.connect()
            try:
                result = future.result()
                # print(f'ASIN: {result[0]} rep {result[1]}')
                url = "https://www.amazon.com/dp/" + item["data"]["asin"] + "/ref=olp-opf-redir?aod=1&condition=new"
                if result[2]==1:
                    data = DetailParse(url=url, response=result[1].text).run_parse()
                    db.execute_query("INSERT INTO tb_monitor_product_log (sell_price,collect_status,collect_msg,sync_status,asin) VALUES (%s, %s, %s, %s, %s)", (data[0]["data"]["finalPurchasePrice"],1,"",0,item["data"]["asin"]))
                elif result[2]==0:
                    db.execute_query("INSERT INTO tb_monitor_product_log (collect_status,collect_msg,sync_status,asin) VALUES (%s, %s, %s, %s)",(2, item["data"]["asin"]+":"+str(result[1]), 0,item["data"]["asin"]))
            except Exception as exc:
                # print(f'ASIN: {item} generated an exception: {exc}')
                traceback.print_exc()
                db.execute_query(
                    "INSERT INTO tb_monitor_product_log (collect_status,collect_msg,sync_status,asin) VALUES (%s, %s, %s, %s)",
                    (2, item["data"]["asin"]+":"+str(traceback.print_exc()), 0,item["data"]["asin"]))
            finally:
                db.close_connection()
        # 记录结束时间
        end_time = time.time()
        # 计算执行时间
        execution_time = end_time - start_time
        logging.info(f"总采集时长：{execution_time}秒")


if __name__ == '__main__':
    db = Database('121.37.97.10', 'oms', 'iXZ2mKcz7abMiS7M', 'oms', 3306)
    worker_thread(db)
