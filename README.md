# O'quv markaz ERP / CRM

FastAPI, SQLAlchemy va MySQL asosidagi loyiha. Web interfeys oddiy HTML, CSS va JavaScript bilan `static` papkasida yozilgan.

## Ishga tushirish

1. Virtual muhitni faollashtiring va kutubxonalarni o'rnating: `pip install -r requirements.txt`.
2. `.env` faylida `DB_USERNAME`, `DB_PASS`, `DB_NAME`, `SECRET_KEY` va `ALGORITHM` qiymatlarini sozlang. MySQL bazasi oldindan yaratilgan bo'lishi kerak.
3. Migratsiyalarni bajaring: `python -m alembic upgrade head`.
4. Loyiha ildizidan serverni ishga tushiring: `python -m uvicorn app.main:app --reload`.
5. Brauzerda <http://127.0.0.1:8000> manzilini oching. HTML faylni alohida Live Server yoki PyCharm preview orqali ochish API'ga ulanish o'rnini bosmaydi.

Mavjud administrator yoki rahbar hisobi bilan kiring. Hisobga `admin` yoki `boss` roli biriktirilgan bo'lishi kerak. Rolning `branch_id` qiymati filialga ruxsatni belgilaydi; `NULL` barcha filiallarga ruxsat beradi. Guruh yaratish uchun faol filial, kurs, xona va o'qituvchi profili kerak.

## Guruhlar

| API | Vazifasi |
| --- | --- |
| `GET /groups/options` | Formadagi filial, kurs, xona va o'qituvchilar |
| `GET /groups/` | Qidiruv, filtrlar va sahifalangan ro'yxat |
| `GET /groups/{id}` | Bitta guruh |
| `POST /groups/` | Guruh yaratish |
| `PUT /groups/{id}` | Guruhni qisman yoki to'liq yangilash |
| `PATCH /groups/{id}/status` | Holatni o'zgartirish |
| `DELETE /groups/{id}` | Guruhni bekor qilish, tarixini saqlash |

Guruh narxi bo'sh bo'lsa kurs narxi olinadi; `0` alohida bepul narx hisoblanadi. O'quvchilar soni API orqali qo'lda kiritilmaydi. Xona sig'imi, o'qituvchi limiti, sanalar va filial ruxsatlari tekshiriladi. O'quvchilari bor guruhning filialini yoki kursini almashtirish va uni bekor qilish cheklangan.

`e31f8b620a01` migratsiyasi mavjud `courses` jadvalini tarixga kiritadi va yangi bazada uni yaratadi. Orqaga qaytarilganda bu jadval va undagi ma'lumotlar saqlanadi. Keyingi migratsiya `groups` jadvalini yaratadi.

## Guruhlar testlari

`python -m pytest tests/test_groups.py -q`

Bu testlar alohida SQLite xotira bazasida ishlaydi. Loyihaning MySQL bazasiga tegmaydi.
