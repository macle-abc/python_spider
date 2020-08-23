from scrapy.utils.project import get_project_settings

import sqlite3


def main():
    """
    创建报告数据库及其数据表
    :return: None
    """
    DB_Name = get_project_settings()['DBNAME']
    print("数据库连接成功", DB_Name)

    Table_Name = 'REPORT'
    conn = sqlite3.connect(DB_Name)
    try:
        cursor = conn.cursor()
        SQL = '''
        CREATE TABLE IF NOT EXISTS "REPORT"(
          "detail_link" TEXT NOT NULL,
          "title" TEXT,
          "speaker" TEXT,
          "holding_time" TEXT,
          "release_time" TEXT,
          "address" TEXT,
          "university" TEXT,
          PRIMARY KEY ("detail_link")
        );
        '''

        cursor.execute(SQL)
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()
        print('创建数据库表%s失败' % Table_Name)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
