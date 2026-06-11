import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "change-me-in-production")
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # IronStack dependencies
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",

    # IronStack core
    "api",
    "workflow",

    "masters",
    "indemnity",

    "tax_requests.apps.TaxRequestsConfig",
    "reports",
    # Your apps (add here)
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
CORS_ALLOW_CREDENTIALS = True

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
PROJECT_NAME = "my-project"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "api.pagination.CustomPageNumberPagination",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "TOKEN_OBTAIN_SERIALIZER": "api.serializers.CustomTokenObtainPairSerializer",
}

# Add your project apps here
PROJECT_APPS = [
    "masters",
    "indemnity",
    "tax_requests",
    "reports",
]

FRAMEWORK_SETTINGS = {
    "AUTHENTICATION": {
        "LDAP_SERVERS": [],
        "LDAP_AUTH": False,
        "AUTO_USER_CREATION": False,
    },
    "LDAP_CONFIG": {
        "HOST": os.environ.get("LDAP_HOST", ""),
        "USER_DN": os.environ.get("LDAP_USER_DN", ""),
        "PASSWORD": os.environ.get("LDAP_PASSWORD", ""),
        "ATTRIBUTES": [],
    },
    "AWS": {
        "BUCKET_NAME": os.environ.get("AWS_BUCKET_NAME", ""),
    },
    "EMAIL": {
        "EMAIL_SERVER": os.environ.get("EMAIL_HOST", ""),
        "EMAIL_PORT": 25,
        "EMAIL_USE_TLS": False,
    },
    "UI_CONFIG": {
        "HEADER_ITEMS": [
            {"name": "My Application", "icon": "GalleryVerticalEnd", "description": "My Company"},
        ],
        "NAVIGATION_ITEMS": [
            {"title": "Master Data", "url": "#", "icon": "SquareTerminal", "isActive": True},
            {"title": "Indemnity", "url": "indemnity/indemnitytracker", "icon": "SquareTerminal", "isActive": True},
            {"title": "Tax Requests", "url": "tax-requests/", "icon": "SquareTerminal", "isActive": True},
            {"title": "Report", "url": "reports/remittancereport", "icon": "SquareTerminal", "isActive": True},
            {"title": "Administration", "url": "admin/access", "icon": "Shield", "isActive": True},
            {"title": "Workflows", "url": "admin/workflows", "icon": "GitBranch", "isActive": True},
            {"title": "My Approvals", "url": "approvals", "icon": "ClipboardCheck", "isActive": True},
        ],
    },
}