import pymysql

class Database:
    def __init__(self, host, user, password, db,port):
        self.connection_params = {
            'host': host,
            'user': user,
            'password': password,
            'database': db,
            'charset': 'utf8mb4',
            'port': port,
            'cursorclass': pymysql.cursors.DictCursor  # 使用字典形式的游标
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = pymysql.connect(**self.connection_params)
            print("Connection established")
        except pymysql.MySQLError as e:
            print(f"Error connecting to MySQL Platform: {e}")

    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                self.connection.commit()
        except pymysql.MySQLError as e:
            print(f"Error executing query: {e}")

    def execute_read_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                result = cursor.fetchall()
            return result
        except pymysql.MySQLError as e:
            print(f"Error executing read query: {e}")
            return None

    def close_connection(self):
        if self.connection and self.connection.open:
            self.connection.close()
            print("Connection closed")

# 使用示例
if __name__ == "__main__":

    db = Database('121.37.97.10', 'root', '123456', 'oms',3307)
    db.connect()

    # 执行写操作
    # db.execute_query("INSERT INTO tb_monitor_product_log (column1, column2) VALUES (%s, %s)", ('value1', 'value2'))

    # 执行读操作
    result = db.execute_read_query("SELECT * FROM tb_monitor_product_log")
    print(result)
    for row in result:
        print(row)

    # 关闭连接
    db.close_connection()