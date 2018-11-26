# -*- coding: utf-8 -*-
__author__ = 'yijingping'
import time
from django.core.management.base import BaseCommand
from configs.models import Proxy
from configs.util import check_proxy


class Command(BaseCommand):
    help = 'check proxies'

    def handle(self, *args, **options):
        while True:
            self.check_all_proxies()
            time.sleep(60)

    def check_all_proxies(self):
        # 检测新代理
        qs1 = Proxy.objects.filter(status=Proxy.STATUS_NEW)
        # 检测成功代理
        qs2 = Proxy.objects.filter(status=Proxy.STATUS_SUCCESS)
        # 检测失败代理
        qs3 = Proxy.objects.filter(status=Proxy.STATUS_FAIL, retry__lt=3)
        for qs in [qs1, qs2, qs3]:
            for item in qs:
                has_exception, proxy_detected, time_diff = check_proxy(item.host, item.port)
                if has_exception or not proxy_detected:
                    item.status = Proxy.STATUS_FAIL
                    item.retry += 1
                    item.save()
                else:
                    item.status = Proxy.STATUS_SUCCESS
                    item.speed = time_diff * 1000
                    item.retry = 0
                    item.save()
