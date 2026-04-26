# 🚀 django-magicapi

[![PyPI version](https://img.shields.io/pypi/v/django-magicapi)](https://pypi.org/project/django-magicapi/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-magicapi)](https://pypi.org/project/django-magicapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Automatically generate production-ready Django REST Framework APIs with zero boilerplate.**

`django-magicapi` helps you instantly generate CRUD APIs for your Django models without manually writing serializers, viewsets, routers, pagination logic, or permissions.

---

## ✨ Why django-magicapi?

Building APIs in Django REST Framework usually requires repetitive setup:

- Writing serializers
- Creating viewsets
- Registering routers
- Configuring pagination
- Setting permissions
- Adding Swagger docs
- Registering models in admin

This package automates all of that with **one command**.

```bash
python manage.py magicapi --app blog
```

And you're done.

---

# 📌 Features

✅ Auto-generates full CRUD APIs  
✅ Creates serializers automatically  
✅ Creates viewsets automatically  
✅ Generates routers automatically  
✅ Supports API versioning (`/api/v1/`)  
✅ Swagger UI support  
✅ ReDoc support  
✅ Automatic Django admin registration  
✅ Hybrid pagination support  
✅ Safe regeneration (won’t overwrite custom code unless forced)  
✅ Cleanup command for generated files  

---

# 📦 Installation

Install the package:

```bash
pip install django-magicapi
```

Add it to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "django_magicapi",
]
```

---

## Optional Swagger Support

For API documentation UI:

```bash
pip install drf-yasg
```

Then add:

```python
INSTALLED_APPS = [
    ...
    "drf_yasg",
]
```

---

# ⚡ Quick Start

## Step 1: Create models

Example:

```python
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
```

---

## Step 2: Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Step 3: Generate APIs

```bash
python manage.py magicapi --app blog
```

---

## Step 4: Run server

```bash
python manage.py runserver
```

---

# 🌐 Generated Endpoints

After running the command:

### API Root
```bash
http://127.0.0.1:8000/api/v1/
```

### Swagger UI
```bash
http://127.0.0.1:8000/swagger/
```

### ReDoc
```bash
http://127.0.0.1:8000/redoc/
```

---

# 🧠 Available Commands

| Command | Description |
|----------|-------------|
| `magicapi --app yourapp` | Generate API for an app |
| `magicapi --app yourapp --clean` | Remove generated files |
| `magicapi --app yourapp --clean --force` | Force remove generated files |
| `magicapi --app app1 app2` | Generate APIs for multiple apps |

---

# 📁 Generated Project Structure

```bash
yourapp/
│
├── models.py
├── admin.py
│
├── utilities/
│   ├── permissions.py
│   ├── pagination.py
│   └── importbase.py
│
├── serializers/
│   ├── __init__.py
│   └── post_serializers.py
│
├── viewsets/
│   ├── __init__.py
│   └── post_viewsets.py
│
└── routers/
    └── routers.py
```

---

# 🔐 Permissions

Modify:

```bash
utilities/permissions.py
```

Use this file to:

- Add owner-based permissions
- Add role-based permissions
- Integrate Django default permissions
- Create custom access logic

---

# 📄 Pagination

Modify:

```bash
utilities/pagination.py
```

Supports:

- Page number pagination
- Limit/offset pagination
- Custom page sizes

---

# 🔧 Customizing Generated Code

Each generated file is independent.

You can safely customize:

- Serializers
- Viewsets
- Routers
- Permissions
- Pagination

Your custom code won’t be overwritten unless you explicitly force it.

---

# 🧹 Cleanup Generated Files

Remove generated files:

```bash
python manage.py magicapi --app blog --clean
```

Force cleanup:

```bash
python manage.py magicapi --app blog --clean --force
```

---

# 🛠 Tech Stack

Built with:

- Django
- Django REST Framework
- drf-yasg
- django-filter

---

# 🤝 Contributing

Contributions are welcome.

You can help by:

- Reporting bugs
- Suggesting features
- Improving documentation
- Submitting pull requests

---

# 📜 License

This project is licensed under the **MIT License**

---

# 👨‍💻 Maintainer

**Prashant Karna**  
📧 prashantkarna21@gmail.com

---

# ⭐ Support

If this project helped you, consider giving it a **GitHub star** ⭐
