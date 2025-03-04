# import concurrent.futures
# import threading

# class KeepLiveThreadPoolExecutor:
#     THREAD_NUM = 1

#     def __init__(self, core_pool_size=50, max_pool_size=100, keep_alive_time=5, queue_size=1000):
#         self.core_pool_size = core_pool_size
#         self.max_pool_size = max_pool_size
#         self.keep_alive_time = keep_alive_time
#         self.queue_size = queue_size
#         self.executor_service = concurrent.futures.ThreadPoolExecutor(max_workers=max_pool_size)

#     def create_thread(self, target, *args, **kwargs):
#         thread_name = f"KeepLiveThreadPool-{KeepLiveThreadPoolExecutor.THREAD_NUM}"
#         KeepLiveThreadPoolExecutor.THREAD_NUM += 1
#         thread = threading.Thread(target=target, args=args, kwargs=kwargs, name=thread_name)
#         self.executor_service.submit(thread.start)

# # Usage example:
# # executor = KeepLiveThreadPoolExecutor()
# # executor.create_thread(your_function, arg1, arg2)
        
# # --------------------------------------------------------------------------------------------
# def sample_task(arg):
#     print(f"Task running with argument: {arg}")

# # Example usage
# if __name__ == "__main__":
#     executor = KeepLiveThreadPoolExecutor()

#     # Create and run threads
#     executor.create_thread(sample_task, "Test Argument 1")
#     executor.create_thread(sample_task, "Test Argument 2")





# ---------------------------------------
import threading
import concurrent.futures
import queue
import time

class AtomicInteger:
    def __init__(self, initial=0):
        self.value = initial
        self._lock = threading.Lock()

    def getAndIncrement(self):
        with self._lock:
            current = self.value
            self.value += 1
            return current

class KeepLiveThreadPoolExecutor:
    THREAD_NUM = AtomicInteger(1)
    CORE_POOL_SIZE = 50
    MAX_POOL_SIZE = 100
    KEEP_ALIVE_TIME = 5  # Note: Not directly applicable in Python
    QUEUE_SIZE = 1000

    # Use the ThreadPoolExecutor for thread management
    def __init__(self):
        self.executor_service = concurrent.futures.ThreadPoolExecutor(max_workers=self.MAX_POOL_SIZE)

    def create_thread(self, target, *args, **kwargs):
        thread_name = f"KeepLiveThreadPool-{self.THREAD_NUM.getAndIncrement()}"
        thread = threading.Thread(target=target, args=args, kwargs=kwargs, name=thread_name)
        self.executor_service.submit(thread.start)

    class NVRThreadFactory:
        def __init__(self, namePrefix):
            self.namePrefix = namePrefix

        def newThread(self, r):
            thread_name = f"{self.namePrefix}-{KeepLiveThreadPoolExecutor.THREAD_NUM.getAndIncrement()}"
            return threading.Thread(target=r, name=thread_name)

def sample_task(arg):
    print(f"Task running with argument: {arg}")

if __name__ == "__main__":
    executor = KeepLiveThreadPoolExecutor()
    executor.create_thread(sample_task, "Test Argument 1")
    executor.create_thread(sample_task, "Test Argument 2")
