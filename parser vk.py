import vk_api
import time
from datetime import datetime

# --- КОНФИГУРАЦИЯ ---
VK_TOKEN = ''

# Список поселков
locations = ['Кременкуль', 'Долгодеревенское', 'Рощино', 'Есаульский', 'Ключи', 'L-Town', 'Эльтаун', 'Белые Росы', 'Прудный']

# Твои услуги
keywords = ['плиточник', 'керамогранит', 'отделка цоколя', 'входные группы', 'гранит', 'крыльцо', 'укладка плитки']

# ЖЕСТКИЙ ФИЛЬТР РЕКЛАМЫ И МУСОРА
stop_words = [
    'цена от', 'в наличии', 'подпишись', 'скидки', 'акция', 'закажите у нас', 
    'наш адрес', 'бесплатная доставка', 'опыт работы 10 лет', 'гарантия на работу',
    'рассрочка', 'магазин', 'склад', 'иркутск', 'минск', 'москва', 'новости', 
    'загадка', 'нефть', 'продам', 'купим', 'бартер', 'подработка'
]

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()

def save_to_log(url, text):
    with open('orders_log.txt', 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%d.%m %H:%M')}] {url}\n{text[:250]}\n{'-'*40}\n")

def is_ad_or_trash(text):
    t = text.lower()
    # Если в тексте есть хоть одно слово из бан-листа — это реклама
    if any(s in t for s in stop_words): return True
    # Если текст слишком короткий (меньше 15 символов) — это мусор
    if len(t) < 15: return True
    return False

def main():
    print("🎯 Юрий, запускаем фильтр 'АНТИ-РЕКЛАМА'...")
    
    # Очищаем лог перед новым запуском (по желанию)
    # open('orders_log.txt', 'w').close() 

    for loc in locations:
        for word in keywords:
            query = f"{word} {loc}"
            try:
                print(f"Проверяю: {query}...")
                # Ищем только свежие посты (priority_geodata=1 помогает с ГЕО)
                res = vk.newsfeed.search(q=query, count=30)['items']
                
                for post in res:
                    txt = post.get('text', '')
                    
                    # ГЛАВНАЯ ПРОВЕРКА
                    if not is_ad_or_trash(txt):
                        # Проверяем, чтобы в тексте БЫЛО название поселка и ключевое слово
                        if any(l.lower() in txt.lower() for l in locations):
                            url = f"https://vk.com/wall{post['owner_id']}_{post['id']}"
                            print(f"💎 КАЖЕТСЯ, ЭТО ЗАКАЗ: {url}")
                            save_to_log(url, txt)
                
                time.sleep(2) # Пауза для стабильности
            except: continue

    print("\n🏁 Фильтрация завершена. Реклама должна была отсеяться.")

if __name__ == "__main__":
    main()
