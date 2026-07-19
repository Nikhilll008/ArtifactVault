"""
CONCEPT: Django (management command) + Threading + OOP
------------------------------------------------------------
Run with: python manage.py check_mongo

A tiny diagnostic command. It pings MongoDB `times` times concurrently
using a pool of threads (instead of one-after-another), to show that
the MongoConnection singleton (apps/common/mongo.py) is safely shared
across threads, and prints how many of the concurrent pings succeeded.
"""
import threading
import time

from django.core.management.base import BaseCommand
from apps.common.mongo import MongoConnection


class Command(BaseCommand):
    help = 'Ping MongoDB concurrently from multiple threads to verify connectivity.'

    def add_arguments(self, parser):
        parser.add_argument('--times', type=int, default=5, help='Number of concurrent pings to fire.')

    def handle(self, *args, **options):
        times = options['times']
        results = [None] * times
        lock = threading.Lock()

        def worker(index):
            ok = MongoConnection().ping()
            with lock:
                results[index] = ok

        start = time.perf_counter()
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(times)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.perf_counter() - start

        successes = sum(1 for r in results if r)
        if successes == times:
            self.stdout.write(self.style.SUCCESS(
                f'MongoDB reachable — {successes}/{times} concurrent pings succeeded in {elapsed:.3f}s.'
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f'Only {successes}/{times} pings succeeded. Check MONGO_URI in your .env file.'
            ))
