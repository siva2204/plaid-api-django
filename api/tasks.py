"""This files conatins async tasks, i.e Plaid Async fetch requests"""
from celery import shared_task


@shared_task
def add(a, b):
    return a + b
