import base64
import hashlib
import os
import tempfile
import oss2

def calculate_file_crc64(file_name, block_size=64 * 1024, init_crc=0):
  with open(file_name, 'rb') as f:
      crc64 = oss2.utils.Crc64(init_crc)
      while True:
          data = f.read(block_size)
          if not data:
              break
          crc64.update(data)
          
  return crc64.crc

crc64 = calculate_file_crc64("/root/7f99ba3da6024c6182c88afc235066b4.png")
print(crc64)

https://ali-beijing.oss-cn-beijing.aliyuncs.com/sc_seeyouyima_com_201805171730_201805171756__0.log.gz
