# Guide de Déploiement VPS - Horoscope App

Ce guide explique comment déployer l'application Horoscope sur un VPS (Virtual Private Server) en production.

## Pré-requis

### Matériel minimum
- **RAM**: 2 Go minimum (4 Go recommandé)
- **CPU**: 1 vCPU minimum (2 vCPU recommandé)
- **Disque**: 20 Go SSD minimum
- **OS**: Ubuntu 22.04 LTS ou Debian 12

### Logiciels requis
- Docker 24+ et Docker Compose v2
- Git

### Installation Docker (Ubuntu/Debian)

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances
sudo apt install -y ca-certificates curl gnupg

# Ajout de la clé GPG Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Ajout du repository Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installation Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Ajout de l'utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker
```

## Configuration

### 1. Cloner le repository

```bash
cd /opt
sudo mkdir horoscope && sudo chown $USER:$USER horoscope
cd horoscope
git clone https://github.com/your-org/horoscope_front.git .
```

### 2. Créer le fichier `.env`

Créez le fichier `.env` avec toutes les variables requises (docker-compose utilise `.env` par défaut) :

```bash
cp .env.example .env
nano .env
```

**Variables obligatoires** :

```env
# ===================
# Database PostgreSQL
# ===================
POSTGRES_USER=horoscope_user
POSTGRES_PASSWORD=<SECURE_PASSWORD_32_CHARS>
POSTGRES_DB=horoscope_prod

# ===================
# Sécurité
# ===================
JWT_SECRET_KEY=<SECURE_RANDOM_64_CHARS>
API_CREDENTIALS_SECRET_KEY=<SECURE_RANDOM_64_CHARS>
LLM_ANONYMIZATION_SALT=<SECURE_RANDOM_64_CHARS>
REFERENCE_SEED_ADMIN_TOKEN=<SECURE_RANDOM_64_CHARS>

# ===================
# AI Engine (OpenAI)
# ===================
OPENAI_API_KEY=sk-...
OPENAI_MODEL_DEFAULT=gpt-4o-mini
AI_ENGINE_TIMEOUT_SECONDS=30
AI_ENGINE_RATE_LIMIT_PER_MIN=30
AI_ENGINE_RATE_LIMIT_ENABLED=true
AI_ENGINE_CACHE_ENABLED=true
AI_ENGINE_CACHE_TTL_SECONDS=3600

# ===================
# App Configuration
# ===================
CORS_ORIGINS=https://yourdomain.com
```

**Génération de secrets sécurisés** :

```bash
# Générer un secret 64 caractères
openssl rand -hex 32
```

## Déploiement

> **Note**: Le build du frontend est automatiquement effectué par Docker lors du `docker compose up --build`. Il n'est pas nécessaire de builder manuellement.

### Démarrage des services

```bash
# Build et démarrage
docker compose -f docker-compose.prod.yml up -d --build

# Vérification des services
docker compose -f docker-compose.prod.yml ps

# Vérification des logs
docker compose -f docker-compose.prod.yml logs -f
```

### Vérification des healthchecks

```bash
# Status des conteneurs
docker ps

# Test de l'endpoint health
curl http://localhost/health
```

Réponse attendue :
```json
{
  "status": "healthy",
  "services": {
    "db": {"status": "ok"},
    "redis": {"status": "ok"}
  }
}
```

### Vérification des endpoints

```bash
# Frontend
curl -I http://localhost/

# API docs
curl http://localhost/docs

# API generate (nécessite auth)
curl http://localhost/v1/ai/generate
```

## Configuration TLS/HTTPS

### Option 1: Caddy (Recommandé)

Caddy gère automatiquement les certificats Let's Encrypt.

1. Installer Caddy :
```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

2. Configurer `/etc/caddy/Caddyfile` :
```
yourdomain.com {
    reverse_proxy localhost:80
}
```

3. Redémarrer Caddy :
```bash
sudo systemctl restart caddy
```

### Option 2: Traefik

Ajoutez Traefik au `docker-compose.prod.yml` :

```yaml
  traefik:
    image: traefik:v3.0
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=your@email.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - letsencrypt:/letsencrypt
```

## Maintenance

### Commandes utiles

```bash
# Voir les logs d'un service
docker compose -f docker-compose.prod.yml logs api -f
docker compose -f docker-compose.prod.yml logs web -f
docker compose -f docker-compose.prod.yml logs db -f

# Redémarrer un service
docker compose -f docker-compose.prod.yml restart api

# Redémarrer tous les services
docker compose -f docker-compose.prod.yml restart

# Arrêter les services
docker compose -f docker-compose.prod.yml down

# Arrêter et supprimer les volumes (ATTENTION: perte de données)
docker compose -f docker-compose.prod.yml down -v
```

### Accès shell aux conteneurs

```bash
# Shell dans le backend
docker compose -f docker-compose.prod.yml exec api sh

# Shell dans la base de données
docker compose -f docker-compose.prod.yml exec db psql -U horoscope_user -d horoscope_prod

# Shell dans Redis
docker compose -f docker-compose.prod.yml exec redis redis-cli
```

### Mise à jour de l'application

```bash
# Récupérer les dernières modifications
git pull origin main

# Rebuild et redéploiement (le frontend est buildé automatiquement par Docker)
docker compose -f docker-compose.prod.yml up -d --build

# Vérification
docker compose -f docker-compose.prod.yml ps
curl http://localhost/health
```

### Sauvegarde de la base de données

```bash
# Créer un dump
docker compose -f docker-compose.prod.yml exec db pg_dump -U horoscope_user horoscope_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurer un dump
docker compose -f docker-compose.prod.yml exec -T db psql -U horoscope_user horoscope_prod < backup_20260222_120000.sql
```

### Nettoyage Docker

```bash
# Supprimer les images non utilisées
docker image prune -a

# Supprimer les volumes non utilisés
docker volume prune

# Nettoyage complet
docker system prune -a
```

## Troubleshooting

### Le service API ne démarre pas

1. Vérifier les logs :
```bash
docker compose -f docker-compose.prod.yml logs api
```

2. Vérifier que la base de données est accessible :
```bash
docker compose -f docker-compose.prod.yml exec db pg_isready
```

3. Vérifier les variables d'environnement :
```bash
docker compose -f docker-compose.prod.yml config
```

### Erreur 502 Bad Gateway

1. Vérifier que l'API est en cours d'exécution :
```bash
docker compose -f docker-compose.prod.yml ps api
```

2. Vérifier les logs Nginx :
```bash
docker compose -f docker-compose.prod.yml logs web
```

### Problèmes de connexion Redis

1. Vérifier le status Redis :
```bash
docker compose -f docker-compose.prod.yml exec redis redis-cli ping
```

2. L'application fonctionne en mode dégradé (fallback mémoire) si Redis est indisponible.

### Performances dégradées

1. Vérifier l'utilisation des ressources :
```bash
docker stats
```

2. Vérifier les logs pour des erreurs de rate limiting :
```bash
docker compose -f docker-compose.prod.yml logs api | grep rate_limit
```

3. Ajuster `AI_ENGINE_RATE_LIMIT_PER_MIN` si nécessaire.

## Architecture

```
┌─────────────┐
│   Internet  │
└──────┬──────┘
       │ :80/:443
┌──────▼──────┐
│    Nginx    │  (web container)
│  + Frontend │
└──────┬──────┘
       │ internal network
┌──────▼──────┐
│     API     │  (api container)
│   FastAPI   │
└──────┬──────┘
       │ internal network
┌──────┴──────┐
│             │
▼             ▼
┌─────────┐  ┌─────────┐
│ Postgres│  │  Redis  │
│   (db)  │  │ (cache) │
└─────────┘  └─────────┘
```

## Sécurité

- Le service `api` n'est pas exposé publiquement (réseau interne Docker uniquement)
- Les services `db` et `redis` ne sont accessibles que depuis le réseau interne
- Seul le service `web` (Nginx) est exposé sur le port 80/443
- Utilisez toujours HTTPS en production via Caddy/Traefik
- Les secrets sont gérés via le fichier `.env` (ne jamais commiter ce fichier)
