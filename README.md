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

14 ta mavjud jadval uchun ishlaydigan bo'limlar bor: lidlar, o'quvchilar, guruhlar, haftalik jadval, darslar, kurslar, xodimlar, o'qituvchi profillari, filiallar, xonalar, qabul manbalari, qabul bosqichlari, rollar va xodim rollari. Bosh sahifadagi ko'rsatkichlar va olti oylik diagramma bazadagi ma'lumotlardan hisoblanadi.

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

## Haftalik jadval va darslar

`Haftalik jadval` (`group_schedules`) guruhning hafta kuni, boshlanish/tugash vaqti va xonasini saqlaydi. Hafta kuni 1 = dushanba, 7 = yakshanba. Xona guruhning asosiy xonasidan farq qilishi mumkin. Jadval guruhning o'qish muddati davomida amal qiladi.

`Darslar` (`lesson_sessions`) aniq sana, mavzu, o'qituvchi, xona, vaqt, holat va izohni saqlaydi. Holatlar: `rejalashtirilgan`, `otilgan`, `bekor_qilingan`. Vaqt Toshkent vaqti (UTC+5) bilan kiritiladi. Tugamagan darsni o'tilgan deb belgilab bo'lmaydi. Darsni bekor qilish uning tarixini saqlaydi; qayta faollashtirishda bandlik yana tekshiriladi.

- Ikkala bo'limda yaratish, tahrirlash, batafsil ko'rish, qidiruv, filtr va CSV eksport bor. Guruh profilidan ham uning jadvali/darslarini ochish mumkin.
- `Jadvaldan darslar yaratish` bilan 1–93 kunlik davrni tanlang. Har bir mos hafta kuni uchun dars yaratiladi; mavjud darslar, shu jumladan bekor qilinganlari ham, qayta yaratilmaydi. Bir to'qnashuv chiqsa, butun yaratish bekor qilinadi.
- Xona, o'qituvchi va guruhning o'z vaqtlari bir-biriga to'qnashmasligi tekshiriladi. 14:00–16:00 va 16:00–18:00 ketma-ket darslar bo'lishi mumkin. Guruhlarning sanalari va haqiqiy umumiy hafta kunlari hisobga olinadi.
- Aniq dars haftalik slot bilan bir xil sana/vaqtga ega bo'lsa, o'sha kungi o'qituvchi/xona bandligi aniq darsdan olinadi. Dars vaqtini ko'chirish haftalik rejani o'zgartirmaydi.
- Haftalik rejani o'zgartirish yoki o'chirish avval yaratilgan darslarga tegmaydi. Guruhning asosiy o'qituvchisi almashsa ham yaratilgan darsning o'qituvchisi saqlanadi; kerakli aniq darsni alohida tahrirlash mumkin.
- Jadval/darslarni buzadigan guruh, xona va o'qituvchi o'zgarishlari bloklanadi. Parallel so'rovlar MySQL'dagi umumiy jadval qulfi bilan ketma-ket tekshiriladi.
- Filial bo'yicha ruxsatlar barcha amallarda tekshiriladi; asosiy administrator barcha filiallarga kira oladi.

| API | Vazifasi |
| --- | --- |
| `GET/POST /group-schedules/` | Haftalik jadval ro'yxati / yaratish |
| `GET/PUT/DELETE /group-schedules/{id}` | Ko'rish / tahrirlash / haftalik slotni o'chirish |
| `GET/POST /lesson-sessions/` | Darslar ro'yxati / yaratish |
| `GET/PUT /lesson-sessions/{id}` | Ko'rish / tahrirlash |
| `PATCH /lesson-sessions/{id}/status` | Dars holatini o'zgartirish |
| `DELETE /lesson-sessions/{id}` | Darsni bekor qilish, tarixini saqlash |
| `POST /lesson-sessions/generate` | Guruh va sanalar bo'yicha jadvaldan darslar yaratish |

`b731c9a42004` migratsiyasi ikkala jadvalni yaratadi.

## Mustaqil integratsion testlar

`python -m pytest tests/test_groups.py tests/test_workspace.py tests/test_main_admin.py tests/test_timetable.py -q`

Bu testlar alohida SQLite xotira bazasida ishlaydi. Loyihaning MySQL bazasiga tegmaydi. Avvalgi testlarning `conftest.py` va `test_course.py` fayllarida MySQL test bazasi alohida sozlangan.
