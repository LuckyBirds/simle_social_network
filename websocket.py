import asyncio
import json
import logging
import websockets
import random
from furl import furl
import pika
import json
import pymysql


credentials = pika.PlainCredentials('admin', 'admin')


mysql_master = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "socialuser",
    "passwd": "socialpass",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "database": "social"
}


conn = pymysql.connect(**mysql_master)
cursor = conn.cursor()
logging.basicConfig()
WS = dict()

#import pdb; pdb.set_trace()

async def check_queue():
    pika_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672,'/',credentials))
    channel = pika_connection.channel()
    method_frame, header_frame, body = channel.basic_get('news')
    if method_frame:
        message = json.loads(body)
        print(body)
        print(message)
        channel.basic_ack(method_frame.delivery_tag)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM accounts LEFT JOIN friends  ON accounts.id =  friends.friend_id WHERE friends.account_id = %s', (message['author_id'],))
        accounts = cursor.fetchall()
        cursor.close()
        for user in accounts:
            if user['id'] in WS:
                await WS[user['id']].send(message['news_date'] + " " + message['author_name']  + " " + message['news_text'] )
    else:
        print('No messages')
    

async def register(websocket, path):
    url =  furl(path)
    user_id= int(url.args['user_id'])
    user_socket = { user_id: websocket }
    WS.update(user_socket)
    await asyncio.sleep(1)


async def unregister(websocket,id):
    del WS[id]
    await notify_users()




async def counter(websocket, path):
    await register(websocket, path)
    while True:

        await check_queue()
        await asyncio.sleep(1)
        print("#########################################")
        
    # finally:
    #     await unregister(websocket, id)
 
            
start_server = websockets.serve(counter, "172.29.44.74", 5001)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()