# -*- coding: utf-8 -*-
__author__ = 'yijingping'
from abc import ABCMeta
from abc import abstractmethod
import requests
import oss2
from oss2.exceptions import NotFound
from copy import copy
from hashlib import md5
from lxml import etree
from io import StringIO
from django.conf import settings
import logging
logger = logging.getLogger()


OSS2_CONF = settings.OSS2_CONFIG
BUCKET = None


def get_bucket():
    global BUCKET
    if not BUCKET:
        auth = oss2.Auth(OSS2_CONF['ACCESS_KEY_ID'], OSS2_CONF['ACCESS_KEY_SECRET'])
        BUCKET = oss2.Bucket(auth, 'http://%s' % OSS2_CONF['BUCKET_DOMAIN'], OSS2_CONF['BUCKET_NAME'])

    return BUCKET


def download_to_oss(url, path, timeout=3600):
    r = requests.get(url, timeout=timeout)
    r.close()
    key = path + md5(r.content).hexdigest()
    bucket = get_bucket()
    try:
        bucket.head_object(key)
    except NotFound as e:
        logging.exception(e)
        bucket.put_object(key, r, headers={'Content-Type': r.headers.get('Content-Type', '')})

    return 'http://%s/%s' % (OSS2_CONF["CDN_DOMAIN"], key)


class BaseExtractor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def extract(self):
        pass


class ImageExtractor(BaseExtractor):
    def __init__(self, data):
        """ data 是图片url,或者图片url的列表,或者包含img标签的内容
        :param data:
        :return: 如果是url,返回新的url; 如果是列表,返回新的url列表
        """
        self.data = data

    def extract(self):
        d = self.data
        res = None
        if not d:
            return d
        elif isinstance(d, basestring):
            if d.startswith('http'):
                ## 内容是图片地址
                res = download_to_oss(d, OSS2_CONF["IMAGES_PATH"], timeout=120)
            else:
                ## 内容是包含图片的文字
                htmlparser = etree.HTMLParser()
                tree = etree.parse(StringIO(d), htmlparser)
                # 找出所有图片src
                srcs = tree.xpath("//img[starts-with(@src,'http')]/@src")
                data_srcs = tree.xpath("//img[starts-with(@data-src,'http')]/@data-src")
                srcs = list(set(srcs + data_srcs))
                # 下载并传到OSS中
                new_srcs = [download_to_oss(item, OSS2_CONF["IMAGES_PATH"], timeout=120) for item in srcs]
                # 替换掉原文中的图片src
                res = self.replace_all(d, srcs, new_srcs)
        elif isinstance(d, list):
            res = [download_to_oss(item, OSS2_CONF["IMAGES_PATH"], timeout=120) for item in d]

        return res


    def replace_all(self, content, srcs, new_srcs):
        """ 将content中的srcs全部替换成new_srcs
        """
        replaces = zip(srcs, new_srcs)
        for src, new_src in replaces:
            content = content.replace(src.split('?')[0], new_src)
        return content


class VideoExtractor(BaseExtractor):
    def __init__(self, data):
        """ data 是视频url,或者视频url的列表
        :param data:
        :return: 如果是url,返回新的url; 如果是列表,返回新的url列表
        """
        self.data = data

    def extract(self):
        d = self.data
        new_url = None
        if not d:
            return d
        elif isinstance(d, basestring):
            new_url = download_to_oss(d, OSS2_CONF["VIDEOS_PATH"])
        elif isinstance(d, list):
            new_url = [download_to_oss(item, OSS2_CONF["VIDEOS_PATH"]) for item in d]

        return new_url


class XPathExtractor(BaseExtractor):
    def __init__(self, content, rule):
        htmlparser = etree.HTMLParser()
        self.tree = etree.parse(StringIO(content), htmlparser)
        self.rule = rule

    def extract(self):
        return self.tree.xpath(self.rule)


class PythonExtractor(BaseExtractor):
    def __init__(self, code, in_val, context):
        self.code = code
        self.in_val = in_val
        self.context = copy(context)
        self.context.update({'in_val': in_val})

    def extract(self):
        res = self.in_val
        g, l = {}, self.context
        try:
            exec(self.code, g, l)
            res = l["out_val"]
        except Exception as e:
            logger.exception(e)
        finally:
            return res
