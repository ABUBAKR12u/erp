# O'quv markaz ERP / CRM

FastAPI, SQLAlchemy va MySQL asosidagi loyiha. Web interfeys oddiy HTML, CSS va JavaScript bilan `static` papkasida yozilgan.

## Ishga tushirish

1. Virtual muhitni faollashtiring va kutubxonalarni o'rnating: `pip install -r requirements.txt`.
2. `.env` faylida `DB_USERNAME`, `DB_PASS`, `DB_NAME`, `SECRET_KEY` va `ALGORITHM` qiymatlarini sozlang. MySQL bazasi oldindan yaratilgan bo'lishi kerak.
3. Migratsiyalarni bajaring: `python -m alembic upgrade head`.
4. Loyiha ildizidan serverni ishga tushiring: `python -m uvicorn app.main:app --reload`.
5. Brauzerda <http://127.0.0.1:8000> manzilini oching. HTML faylni alohida Live Server yoki PyCharm preview orqali ochish API'ga ulanish o'rnini bosmaydi.

Mavjud xodim hisobi bilan kiring. Menyu va amallar xodim roliga qarab ko'rsatiladi. `boss` va `admin` boshqaruv bo'limlariga kira oladi; rol biriktirish va rollarni boshqarish rahbar uchun. Rolning `branch_id` qiymati filial doirasini belgilaydi; `NULL` barcha filiallarga amal qiladi. Guruh yaratish uchun faol filial, kurs, xona va o'qituvchi profili kerak.

## Web interfeys

12 ta mavjud jadval uchun ishlaydigan bo'limlar bor: lidlar, o'quvchilar, guruhlar, kurslar, xodimlar, o'qituvchi profillari, filiallar, xonalar, qabul manbalari, qabul bosqichlari, rollar va xodim rollari. Bosh sahifadagi ko'rsatkichlar va olti oylik diagramma bazadagi ma'lumotlardan hisoblanadi.

- Lidlar uchun Kanban va jadval; boshqa bo'limlar uchun mos kartochka va jadval ko'rinishlari.
- Qidiruvli, klaviatura bilan boshqariladigan selectlar, bog'liq filial/xona/o'qituvchi tanlovlari.
- Yaratish, tahrirlash, batafsil profil, holatni o'zgartirish va mavjud API amallari.
- Liddan yangi o'quvchi yaratish yoki mavjud o'quvchi bilan bog'lash.
- Sahifalash, qidiruv, filtrlar va ko'rinayotgan/tanlangan yozuvlarni CSV eksport qilish.
- `Ctrl K` — bo'lim qidiruvi, `N` — yangi yozuv, `/` — ro'yxatdan qidirish, `Esc` — oynani yopish.
- Mobil menyu, bir xil scrollbarlar, kontrastli holat ranglari va lokal Manrope shrifti. Shrift litsenziyasi `static/Manrope-LICENSE.txt` faylida.

Autentifikatsiya tokenlari brauzer oynasining `sessionStorage` xotirasida saqlanadi. Refresh token orqali access token avtomatik yangilanadi.

## Asosiy administrator

`employees.is_superadmin` belgisi asosiy hisobga barcha bo'limlar va filiallarga kirish beradi. Bu belgi oddiy yaratish/tahrirlash API'sida o'zgartirilmaydi. Asosiy hisobni o'chirish, faolsizlantirish va uning `boss`/`admin` boshqaruv rolini olib tashlash API darajasida bloklanadi.

`f42a9c731b03` migratsiyasi birinchi faol `boss` hisobini, u bo'lmasa birinchi faol `admin` hisobini asosiy administrator qiladi. MySQL'dagi ikkita trigger hisobni o'chirish, asosiy admin belgisini olib tashlash, faolsizlantirish va ishdan bo'shatish urinishlarini bloklaydi. Check constraint asosiy hisob doim faol bo'lishini tekshiradi.

Dizayn izlanishlari: [Conceptzilla CRM](https://dribbble.com/shots/27071630-CRM-Dashboard-Design-for-Sales-Performance-Management), [Ronas IT CRM](https://dribbble.com/shots/25742359-CRM-Dashboard-App-Design), [Figma dashboard galereyasi](https://www.figma.com/templates/dashboard-designs/).

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

## Mustaqil integratsion testlar

`python -m pytest tests/test_groups.py tests/test_workspace.py tests/test_main_admin.py -q`

Bu testlar alohida SQLite xotira bazasida ishlaydi. Loyihaning MySQL bazasiga tegmaydi. Avvalgi testlarning `conftest.py` va `test_course.py` fayllarida MySQL test bazasi alohida sozlangan.
