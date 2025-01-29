# WebTech2025# Projet Django

## Installation et exécution

Suivez ces étapes pour configurer et lancer le projet Django :

### 1️⃣ Créer et activer un environnement virtuel

```bash
python3 -m venv .venv
```

- **Sur macOS/Linux** :
  ```bash
  source .venv/bin/activate
  ```
- **Sur Windows** :
  ```bash
  .venv\Scripts\activate
  ```

### 2️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3️⃣ Appliquer les migrations

```bash
python manage.py migrate
```

### 4️⃣ Lancer le serveur

```bash
python manage.py runserver
```

Si vous rencontrez des problèmes avec le rechargement automatique, essayez :

```bash
python manage.py runserver --noreload
```

🚀 **Votre projet est maintenant prêt !** Ouvrez `http://127.0.0.1:8000/` dans votre navigateur. 🎉
