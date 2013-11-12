'''
Created on Nov 11, 2013

@author: amitshah
'''

import boto

class Notification(object):
    
    def __init__(self,topic='sobersteering'):
        access_key_id = 'AKIAIFIOW5MGTIRHF4VA'
        secret_access_key = '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'
        self.sns = boto.connect_sns(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
        self.displayname= {
                           'sobersteering01':'STTD',
                           'sobersteering02': 'BUS #1104'
                           }
        self.topicarn = {}
        
        topic_response= self.sns.create_topic('sobersteering-sobersteering01')  
        self.topicarn['sobersteering01'] = topic_response['CreateTopicResponse']['CreateTopicResult']['TopicArn']
        self.sns.set_topic_attributes(self.topicarn['sobersteering01'], 'DisplayName', 'sobersteering')  
        
        topic_response= self.sns.create_topic('sobersteering-sobersteering02')  
        self.topicarn['sobersteering02'] = topic_response['CreateTopicResponse']['CreateTopicResult']['TopicArn']
        self.sns.set_topic_attributes(self.topicarn['sobersteering02'], 'DisplayName', 'sobersteering')  
        
        
        
    def write_message(self,event):
        topicarn = self.topicarn[event['deviceID']]
        if(event['rfidTemperature'] == 7.2):
            msg = "alcohol above limit on %s @ %s,%s" % (self.displayname[event['deviceID']],event['timestamp'],event['latitude'],event['longitude'])
            self.sns.publish(topic=topicarn,
                             message=msg)
        if(event['rfidTemperature'] == 7.6):
            msg = "override on %s @ %s,%s" % (self.displayname[event['deviceID']],event['timestamp'],event['latitude'],event['longitude'])
            self.sns.publish(topic=topicarn,
                             message=msg)

if __name__ == '__main__':
    n = Notification()
    n.publish_to_topic('helloworld')
    pass