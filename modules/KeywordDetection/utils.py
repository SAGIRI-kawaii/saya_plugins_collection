from .Sqlite3Manager import Sqlite3Manager


async def get_group_switch(group_id: int) -> bool:
    conn = Sqlite3Manager.get_instance().get_conn()
    sql = f"SELECT switch FROM setting WHERE groupId={group_id}"
    print(sql)
    cursor = conn.cursor()
    cursor.execute(sql)
    if result := cursor.fetchall():
        cursor.close()
        print(result[0][0])
        return True if result[0][0] else False
    sql = f"INSERT INTO setting (groupId, switch) VALUES (?, ?)"
    cursor.execute(sql, (group_id, 1))
    conn.commit()
    cursor.close()
    return True


async def set_group_switch(group_id: int, new_status: int) -> None:
    conn = Sqlite3Manager.get_instance().get_conn()
    cursor = conn.cursor()
    sql = f"UPDATE setting SET switch={new_status} WHERE groupId={group_id}"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
