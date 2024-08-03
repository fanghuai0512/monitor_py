import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from Mysql_data import Database
from get_response import get_response
from async_detail_paser import DetailParse
import re

items = []

def get_biz_product(item):
    db = item
    db.connect()
    try:
        result = db.execute_read_query("SELECT * FROM tb_biz_product where monitor = 1")
        return result
    except Exception as e:
        return None
    finally:
        db.close_connection()


def fetch_url(item):
    try:
        url = "https://www.amazon.com/dp/"+item["data"]["asin"]+"/ref=olp-opf-redir?aod=1&condition=new"
        response = get_response(url)
        return item["data"]["asin"], response,1
    except requests.RequestException as e:
        return item["data"]["asin"], e,0


def worker_thread(db):
    items = get_biz_product(db)
    lists = []
    for item in items:
        lists.append({"db": db, "data": item})
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
                    db.execute_query("INSERT INTO tb_monitor_product_log (product_id,sell_price,collect_status,collect_msg,sync_status) VALUES (%s, %s, %s, %s, %s)", (item["data"]["id"], data[0]["data"]["finalPurchasePrice"],1,"",0))
                elif result[2]==2:
                    db.execute_query("INSERT INTO tb_monitor_product_log (product_id,sell_price,collect_status,collect_msg,sync_status) VALUES (%s, %s, %s, %s, %s)",(item["data"]["id"], "", 2, result[1], 0))
            except Exception as exc:
                # print(f'ASIN: {item} generated an exception: {exc}')
                db.execute_query(
                    "INSERT INTO tb_monitor_product_log (product_id,sell_price,collect_status,collect_msg,sync_status) VALUES (%s, %s, %s, %s, %s)",
                    (item["data"]["id"], "", 2, exc, 0))
            finally:
                db.close_connection()

if __name__ == '__main__':
    db = Database('121.37.97.10', 'root', '123456', 'oms', 3307)
    worker_thread(db)
