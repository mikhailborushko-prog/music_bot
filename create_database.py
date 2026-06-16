import pandas as pd
import sqlite3

# Загружаем CSV
df = pd.read_csv("data/album_ratings.csv")

# Оставляем хорошие альбомы
df = df[df["AOTY User Score"] >= 70]

# Удаляем дубликаты
df = df.drop_duplicates(subset=["Artist", "Title"])

# Оставляем нужные поля
df = df[
    [
        "Artist",
        "Title",
        "Genre",
        "Release Year",
        "AOTY User Score",
        "AOTY User Reviews"
    ]
]

# Добавляем колонку для отметки выданных альбомов
df["status"] = "not_listened"
df["user_action"] = None   # like / dislike / listened / None
df["weight"] = 1           # важность для рекомендаций

# Создаём SQLite базу
conn = sqlite3.connect("albums.db")

df.to_sql(
    "albums",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("База создана")
print(f"Количество альбомов: {len(df)}")