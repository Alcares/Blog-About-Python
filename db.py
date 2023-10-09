import psycopg2
from config import config


def select(query, fetch_all=False):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(query)
        if fetch_all:
            col_names = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            total = []
            for r in rows:
                r = {col_names[i]: r[i] for i in range(len(col_names))}
                total.append(r)
        else:
            result = cur.fetchone()
            col_names = [desc[0] for desc in cur.description]
            total = {col_names[i]: result[i] for i in range(len(col_names))}
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        return error
    else:
        return total
    finally:
        if conn is not None:
            conn.close()


def insert_row(query: str):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return error
    else:
        print('Success')
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    row_count = select(
        """select 
	        u.email,
	        c.text,
	        u.name
            from comments c
            left outer join blog_posts b
	            on c.post_id = b.id
            left outer join users u
	            on u.id = c.author_id""", fetch_all=True
    )
    print(row_count)
