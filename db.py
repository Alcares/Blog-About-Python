import psycopg2
from config import config


def select(query, fetch_all=False):
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


def get_comments(post_id):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        query = "SELECT u.email, c.text, u.name FROM comments c LEFT OUTER JOIN blog_posts b ON c.post_id = b.id \
                 LEFT OUTER JOIN users u ON u.id = c.author_id WHERE b.id = %s"
        cur.execute(query, (post_id, ))
        col_names = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        total = []
        for r in rows:
            r = {col_names[i]: r[i] for i in range(len(col_names))}
            total.append(r)
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        return error
    else:
        return total
    finally:
        if conn is not None:
            conn.close()


def get_user(user_id):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        query = "SELECT * FROM users WHERE email=%s"
        cur.execute(query, (user_id,))
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

def get_user_by_id(user_id):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        query = "SELECT * FROM users WHERE id=%s"
        cur.execute(query, (user_id,))
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


def insert_users(id_num, email, hashed_password, name):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        query = "INSERT INTO users VALUES (%s, %s, %s, %s)"
        cur.execute(query, (id_num, email, hashed_password, name))
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


def insert_comment(comment_id, comment_text, user_id, post_id):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        query = "INSERT INTO comments VALUES (%s, %s, %s, %s)"
        cur.execute(query, (comment_id, comment_text, user_id, post_id))

        update_post_comment_count = "UPDATE blog_posts SET num_comments = num_comments+1 WHERE id = %s"
        cur.execute(update_post_comment_count, (post_id, ))
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


def add_user_blog_post(id, user_id, title, subtitle, date, body, img):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        query = "INSERT INTO user_posts VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cur.execute(query, (id, user_id, title, subtitle, date, body, img))
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

def del_post(post_id):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        query = "DELETE FROM blog_posts WHERE id=%s"
        cur.execute(query, (post_id, ))
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


def get_post(post_id):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        query = "SELECT * FROM blog_posts LEFT OUTER JOIN users ON users.id = blog_posts.author_id \
               WHERE blog_posts.id = %s"
        cur.execute(query, (post_id, ))
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


def update_post(title, subtitle, img_url, user_id, body, post_id):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        query = "UPDATE blog_posts SET title=%s, subtitle=%s, img_url=%s, author_id=%s, body=%s WHERE id=%s"
        cur.execute(query, (title, subtitle, img_url, user_id, body, post_id))
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
    current_user = 1
    posts = select(f'SELECT blog_posts.id, blog_posts.num_comments  FROM blog_posts LEFT OUTER JOIN users ON users.id = blog_posts.author_id WHERE users.id = {current_user} ORDER BY date asc', fetch_all=True)
    print(posts)