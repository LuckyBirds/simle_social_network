import pymysql
import pika
import json
import time
credentials = pika.PlainCredentials('admin', 'admin')

while True:
    time.sleep(1)
    connection = pymysql.connect(
    host =  "127.0.0.1",
    port =  3306,
    user = "socialuser",
    passwd = "socialpass",
    charset = "utf8mb4",
    cursorclass = pymysql.cursors.DictCursor,
    database = "social")

    pika_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672,'/',credentials))
    channel = pika_connection.channel()
    method_frame, header_frame, body = channel.basic_get('counter')
    if method_frame:
        #import pdb; pdb.set_trace()
        message = json.loads(body)
        print(body)
        print(message)
        channel.basic_ack(method_frame.delivery_tag)
        if message['status'] == 0:
            with connection.cursor() as cursor:
                cursor.execute('SELECT  new_messages from messagecounter  WHERE account_id = %s and friend_id =%s ',(message['message_to'], message['message_from']), )
            counter_data = cursor.fetchone()
            if counter_data:
                counter = counter_data['new_messages']
                counter += 1
                with connection.cursor() as cursor:
                    cursor.execute('UPDATE  messagecounter set new_messages = %s where account_id = %s and friend_id = %s ' , ( counter,  message['message_to'],message['message_from'] ),)    
        
            else:
                 with connection.cursor() as cursor:
                    cursor.execute('INSERT INTO messagecounter ( new_messages, account_id, friend_id )   VALUES(1, %s, %s)  ' , ( message['message_to'], message['message_from'] ),)   
            with connection.cursor() as cursor:       
                cursor.execute('DELETE FROM   counteroutbox  where id = %s' , ( message['message_id'] ),)    
            connection.commit()
            connection.close()

        #import pdb; pdb.set_trace()
        if message['status'] == 3:
            with connection.cursor() as cursor:
                cursor.execute('SELECT  new_messages from messagecounter  WHERE account_id = %s and friend_id =%s ',(message['message_from'], message['message_to']), )
            counter_data = cursor.fetchone()
            if counter_data:
                with connection.cursor() as cursor:
                    cursor.execute('UPDATE  messagecounter set new_messages = 0  where account_id = %s and friend_id = %s ' , ( message['message_from'],message['message_to'] ),)    
        
            with connection.cursor() as cursor:       
                cursor.execute('DELETE FROM   counteroutbox  where id = %s' , ( message['message_id'] ),)    
            connection.commit()
            connection.close()
        
    else:
        print('No messages')