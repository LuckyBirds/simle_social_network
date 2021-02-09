import pymysql
import pika
import json
credentials = pika.PlainCredentials('admin', 'admin')

while True:
    connection = pymysql.connect(
    host =  "127.0.0.1",
    port =  3306,
    user = "socialuser",
    passwd = "socialpass",
    charset = "utf8mb4",
    cursorclass = pymysql.cursors.DictCursor,
    database = "social")

    #connection.autocommit = True
    try:
        #import pdb; pdb.set_trace()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM counteroutbox  WHERE id =  (  SELECT MIN(id) FROM counteroutbox where status = 0 or status = 3)' )
        counter_data = cursor.fetchone()
        if counter_data:
            id = counter_data['id']
            if counter_data['status'] == 0:
                with connection.cursor() as cursor:
                    cursor.execute('UPDATE  counteroutbox set status = 1 where id = %s' , ( id ),)    
            if counter_data['status'] == 3:
                with connection.cursor() as cursor:
                    cursor.execute('UPDATE  counteroutbox set status = 4 where id = %s' , ( id ),)    
            pika_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672,'/',credentials))
            channel = pika_connection.channel()
            channel.queue_declare(queue='counter')
            counter_message =  {'message_from': counter_data['message_from'], 'message_to': counter_data['message_to'], 'request_id': counter_data['request_id'], 'message_id': counter_data['id'], 'status': counter_data['status'] }
            channel.basic_publish(exchange='', routing_key='counter',  body=json.dumps(counter_message))
            pika_connection.close()  
                    
    finally:
        connection.commit()
        connection.close()
    
     
 