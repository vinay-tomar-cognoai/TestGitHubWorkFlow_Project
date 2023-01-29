from EasyChat import settings
from kafka import KafkaProducer
import json
import sys
import socket
from EasyChatApp.utils_execute_query import send_bot_break_mail
import threading

kafka_producer = None


def send_broken_mail(text_message, livechat_config_obj):
    
    try:
        from LiveChatApp.utils import logger
        
        EMAIL_LIST_FOR_MAIL = json.loads(livechat_config_obj.kafka_error_email_list)
        
        if len(EMAIL_LIST_FOR_MAIL) == 0:
            return
        
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        text_message += f' IP:{ip_address}'
        to_email_id = EMAIL_LIST_FOR_MAIL[0]
        cc = ",".join(EMAIL_LIST_FOR_MAIL[1:])
    
        thread = threading.Thread(target=send_bot_break_mail, args=(
            to_email_id, "", "", settings.EASYCHAT_DOMAIN, text_message, cc), daemon=True)
        thread.start()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Not able to send mail: " + str(e), extra={"AppName": "LiveChat"})

try:
    from LiveChatApp.utils import logger
    kafka_producer = KafkaProducer(
        bootstrap_servers=settings.KAFKA_CONFIG["bootstrap_servers"],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        max_block_ms=10000,
    )
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    logger.error("Not able to make kafka_producer: " +
                 str(e), extra={"AppName": "LiveChat"})


def send_packet_into_kafka_producer(topic, value, livechat_config_obj):
    
    # we don't have any app for kafka_producer so we use inline import we will fix in future. 
    from LiveChatApp.utils import logger 
    
    is_kafka_enabled = settings.IS_REPORT_GENERATION_VIA_KAFKA_ENABLED
    if not is_kafka_enabled:
        return 
    
    if kafka_producer == None and is_kafka_enabled:
        logger.error("Error send_packet_into_kafka_producer topic: %s | packet: %s",
                     topic, json.dumps(value), extra={"AppName": "LiveChat"})
        logger.error("Error send_packet_into_kafka_producer kafka_producer, is_kafka_enabled" +
                     str(kafka_producer) + " " + str(is_kafka_enabled), extra={"AppName": "LiveChat"})
        send_broken_mail(
            f'Error send_packet_into_kafka_producer topic kafka_producer={kafka_producer} , is_kafka_enabled={is_kafka_enabled}', livechat_config_obj)
        return
    
    logger.info("Inside send_packet_into_kafka_producer topic: %s | packet: %s", topic, json.dumps(value), extra={"AppName": "LiveChat"})
    try:
        kafka_producer.send(topic, value=value)
        kafka_producer.flush(timeout=3)
    except Exception as e:
        logger.error("%s", str(e), extra={"AppName": "LiveChat"})
        send_broken_mail(f'Not able to send kafka error:{e}', livechat_config_obj)
    logger.info("Exit send_packet_into_kafka_producer %s", json.dumps(value), extra={"AppName": "LiveChat"})
