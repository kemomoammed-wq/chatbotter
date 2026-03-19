# دليل استخدام Database Migrations

## نظرة عامة
تم إعداد نظام Alembic migrations لإدارة تحديثات قاعدة البيانات تلقائياً.

## الملفات المضافة:
- `alembic.ini` - إعدادات Alembic
- `migrations/` - مجلد يحتوي على ملفات migrations
- `migrations/env.py` - إعدادات الاتصال بقاعدة البيانات
- `run_migrations.py` - سكريبت Python لتشغيل migrations
- `run_migrations.bat` - سكريبت Windows لتشغيل migrations

## كيفية الاستخدام:

### 1. إنشاء Migration جديد (عند تعديل Models):
```bash
# Python
python run_migrations.py --init

# أو مباشرة
alembic revision --autogenerate -m "وصف التغيير"
```

### 2. تطبيق Migrations:
```bash
# Python
python run_migrations.py --upgrade
# أو
python run_migrations.py

# Windows Batch
run_migrations.bat --upgrade
# أو
run_migrations.bat
```

### 3. التراجع عن آخر Migration:
```bash
python run_migrations.py --downgrade
# أو
run_migrations.bat --downgrade
```

### 4. عرض الحالة الحالية:
```bash
python run_migrations.py --current
alembic current
```

### 5. عرض تاريخ Migrations:
```bash
python run_migrations.py --history
alembic history
```

## مثال على إضافة عمود جديد:

### الخطوة 1: تعديل Model في `database.py`
```python
class Conversation(Base):
    __tablename__ = 'conversations'
    # ... الأعمدة الموجودة
    new_field = Column(String)  # عمود جديد
```

### الخطوة 2: إنشاء Migration
```bash
alembic revision --autogenerate -m "Add new_field to conversations"
```

### الخطوة 3: مراجعة ملف Migration
افتح `migrations/versions/XXXXX_add_new_field_to_conversations.py` وتأكد من التغييرات.

### الخطوة 4: تطبيق Migration
```bash
python run_migrations.py --upgrade
```

## ملاحظات مهمة:

1. **النسخ الاحتياطي**: دائماً اعمل backup للقاعدة قبل تطبيق migrations في الإنتاج.

2. **SQL Server**: النظام يدعم SQL Server (`DESKTOP-EETM136\SQLEXPRESS`) و SQLite تلقائياً.

3. **التحقق**: بعد أي migration، تحقق من أن البيانات سليمة والجداول محدثة.

4. **التعليقات**: اكتب وصف واضح في رسالة Migration (`-m "وصف"`).

## الأوامر المتقدمة:

```bash
# تطبيق migration محدد
alembic upgrade <revision_id>

# التراجع لـ revision محدد
alembic downgrade <revision_id>

# عرض تفاصيل migration
alembic show <revision_id>

# تعديل migration موجود
alembic edit <revision_id>
```

## استكشاف الأخطاء:

### المشكلة: Migration فاضي (pass فقط)
**الحل**: الـ tables موجودة بالفعل. هذا طبيعي في أول migration.

### المشكلة: خطأ في الاتصال بقاعدة البيانات
**الحل**: تأكد من إعدادات `database.py` و `migrations/env.py`.

### المشكلة: تعارض في البيانات
**الحل**: استخدم `alembic downgrade` للتراجع ثم راجع التغييرات.

## الملفات المرجعية:
- `database.py` - Models والجداول
- `migrations/env.py` - إعدادات الاتصال
- `alembic.ini` - إعدادات Alembic العامة

