#coding:utf-8
from nowstagram import app
import os
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526 import StopInstanceRequest
import oss2
import requests

# 创建AcsClient实例
client = AcsClient(
   app.config['ALI_ACCESS_KEY_ID'],
   app.config['ALI_SECRET_KEY'],
   app.config['ALI_REGION_ID']
);
# 创建request，并设置参数
request = DescribeInstancesRequest.DescribeInstancesRequest()
request.set_PageSize(10)
# 发起API请求并显示返回值
response = client.do_action_with_exception(request)



# 上传文件
auth = oss2.Auth(app.config['ALI_ACCESS_KEY_ID'], app.config['ALI_SECRET_KEY'])
bucket = oss2.Bucket(auth, app.config['ALI_ENDPOINT'], app.config['ALI_BUCKET_NAME'])
# bucket.put_object_from_file('instance_download.jpeg', '/Users/icarus/Documents/nowstagram/instance.jpeg')
#
# bucket.get_object_to_file('instance_download.jpeg','111.jpeg')

def ali_upload_file(source_file,save_file_name):
   result = bucket.put_object(save_file_name, source_file)
   print('http status: {0}'.format(result.status))
   url = 'http://nowstagram-images.oss-cn-beijing.aliyuncs.com/'+save_file_name
   if result.status == 200:
      return url
   return None