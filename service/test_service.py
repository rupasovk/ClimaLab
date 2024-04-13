# list_processing.py

import time

def process_list(items, progress):
    total_items = len(items)
    processed_items = 0
    for item in items:
        # Ваша логика обработки элемента списка здесь

        processed_items += 1
        progress[0] = int(processed_items / total_items * 100)
        time.sleep(1)  # Имитация обработки элемента списка

    return  # Можете вернуть результаты обработки, если это необходимо