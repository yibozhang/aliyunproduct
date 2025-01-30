#-*-coding:utf8-*-
import pika

config = pika.ConnectionParameters(
    host='amqp-cn-2r42a2eku009.mq-amqp.cn-hangzhou-249959-a.aliyuncs.com',
    credentials=pika.PlainCredentials('amqp-cn-2r42a2eku009', 'Qjc2QjFEMjU4OTc4Q0Q1RjoxNjI3MzQ5NTUwNDk4'),
)

conn = pika.BlockingConnection(config)
channel = conn.channel()

# 修改 type 为 topic
channel.exchange_declare(exchange='amq.topic', type='topic')

channel.basic_publish(
    exchange='amq.topic',
    routing_key='hanli_key',
    body='Hello World!'
)

conn.close()
