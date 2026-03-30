import dj_database_url
import os

# هذا السطر يقرأ الرابط من Railway
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL')
    )
}
