<div align="center">

# 🔤 Hangman Reimagined

### *A Strategic Word Discovery, Multiplayer Duel & Cloud-Synced Vocabulary Game*

[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flutter.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Neon Database](https://img.shields.io/badge/Neon_DB-PostgreSQL-00E599?style=for-the-badge&logo=postgresql&logoColor=black)](https://neon.tech)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

---

</div>

## 📖 Overview

**Hangman Reimagined** elevates traditional blind-guessing hangman into an immersive, strategic vocabulary discovery platform. Built with a sleek **Cyber-Dark Glassmorphism** interface in **Flutter**, backed by a high-performance **FastAPI** server, and synced to **Neon PostgreSQL** cloud storage, it features 100 progressive level tiers, 1v1 turn-based multiplayer duels, custom timed challenges, and an extensive dictionary database of **38,000+ words**.

---

## ⚡ Key Features

### 🏆 Classic Mode & 100-Level Campaign
- **Progressive Difficulty**: 100 levels mapped across 5 difficulty tiers (*Very Easy, Easy, Moderate, Challenging, Hard, Expert, Hardcore Expert*).
- **5-Heart System with Auto-Regeneration**: Play with 5 hearts that automatically regenerate 1 heart every 2 minutes.
- **Zero Word Repetition Guarantee**: A 5-tier selection algorithm ensures no user ever encounters a repeated word across Classic Mode or any game mode.
- **Witty 5-Loss Streak Support**: Encouraging popup dialogues on 5 consecutive defeats featuring targeted vocabulary suggestions.

### ⚔️ 1v1 Room Duel (Multiplayer Mode)
- **Private Room Codes**: Create or join custom 6-digit match rooms with friends.
- **Real-Time Turn-Based Combat**: Players alternate turns guessing letters, with live room status polling and instant winner/loser resolution.

### ⏱️ Custom Timed Mode
- **Custom Timer Selectors**: Choose custom round durations (30s, 45s, 60s, 90s, or 120s).
- **Real-Time Ticking Clock**: Ticking countdown starts immediately upon the first letter selection.

### 📚 Vocabulary Vault (Codex) & 12 Preset Categories
- **12 Preset Categories**: Filter words across *Technology, Science, Nature, Animals, Space, Geography, Food & Cooking, Sports, History, Medicine, Arts & Culture, Business*.
- **Post-Game Knowledge Cards**: Detailed dictionary cards displaying definition, part of speech, category, and masked context sentences after every match.
- **Personal Vocabulary Codex**: Track all encountered words, win rates, definitions, and mastery levels in cloud storage.

### ☁️ Cloud Sync & Database Architecture
- **Neon PostgreSQL Cloud Storage**: Persists user profiles, XP, streaks, level progression, codex history, and multiplayer matches.
- **SQLite Local Corpus**: Embedded 38,795-word linguistic corpus with offline fallback support.

---

## 🏗️ Architecture & Tech Stack

```mermaid
flowchart TD
    subgraph Frontend["Flutter Client (Web / Mobile)"]
        UI["Material 3 Glassmorphism UI"]
        State["Riverpod State Management"]
        Router["GoRouter Navigation"]
    end

    subgraph Backend["FastAPI REST API"]
        Engine["Game Engine & Heart Regen"]
        WordSvc["Multi-Tier Word Selection"]
        MultiSvc["1v1 Room Duel Manager"]
        CodexSvc["User Codex & Stats Manager"]
    end

    subgraph Storage["Data Tier"]
        NeonDB[("Neon Cloud PostgreSQL")]
        SQLiteDB[("Local SQLite Words Database (38.7k+ Words)")]
    end

    UI -->|HTTPS / JSON| Backend
    Backend --> Engine
    Backend --> WordSvc
    Backend --> MultiSvc
    Backend --> CodexSvc
    WordSvc --> SQLiteDB
    CodexSvc --> NeonDB
    Engine --> NeonDB
```

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Flutter 3.x, Dart | Cross-platform UI, Glassmorphism design system, Riverpod |
| **Backend API** | Python 3.13, FastAPI, Pydantic v2 | Server-authoritative game logic, auth, multiplayer, REST routes |
| **Cloud DB** | Neon PostgreSQL / SQLAlchemy | Cloud persistence for profiles, XP, streaks, codex, and room state |
| **Local DB** | SQLite (`words.db`) | 38,795 preprocessed English words with definitions & metadata |
| **Corpus Tooling** | NLTK WordNet, `wordfreq` | Linguistic analysis, Zipf frequency scoring, definition extraction |

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.10 or higher
- **Flutter SDK**: 3.x or higher
- **Git**

---

### 1. Clone the Repository
```bash
git clone https://github.com/pathakpk7/Hangman_Re_imagined.git
cd HangMan_Game
```

---

### 2. Backend Setup (FastAPI)

1. **Create Virtual Environment & Install Dependencies**:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

2. **Configure Environment Variables** (Optional - Default uses local SQLite):
   Set your Neon PostgreSQL connection string in `.env` or system environment:
   ```env
   DATABASE_URL=postgresql://user:password@ep-cool-endpoint.neon.tech/neondb?sslmode=require
   ```

3. **Run Backend Server**:
   ```bash
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   - **Interactive API Documentation**: Navigate to `http://127.0.0.1:8000/docs`

---

### 3. Frontend Setup (Flutter)

```bash
cd frontend

# Install dependencies
flutter pub get

# Run on Web (Chrome)
flutter run -d chrome --web-port 3000
```

---

## 🧪 Testing & Quality Assurance

### Run Backend Unit Tests (Pytest)
```bash
python -m pytest backend/tests
```
*Executes auth verification, heart deduction, game engine state, multiplayer duel logic, and the zero-word-repetition suite.*

### Run Frontend Unit Tests (Flutter Test)
```bash
cd frontend
flutter test
```

---

## 📂 Project Structure

```
HangMan_Game/
├── backend/
│   ├── app/
│   │   ├── models/           # Pydantic API Schemas & Request Models
│   │   ├── models_db.py      # SQLAlchemy DB ORM Models (User, Codex, History)
│   │   ├── routers/          # FastAPI Route Handlers (Auth, Game, Codex, Multiplayer, Profile)
│   │   ├── services/         # Game Engine, Word Service, Level Service, Codex Service
│   │   ├── config.py         # App Configuration Settings
│   │   ├── database.py       # Database Connection & Session Factory
│   │   └── main.py           # FastAPI Application Entry Point
│   ├── data/
│   │   └── words.db          # Preprocessed 38,795 Word SQLite Database
│   └── tests/                # Automated Pytest Test Suite
├── frontend/
│   ├── lib/
│   │   ├── core/             # Theme, Constants, API Client, Riverpod Providers
│   │   ├── features/         # Clean Architecture Feature Modules (Home, Game, Codex, Multiplayer, Auth)
│   │   └── main.dart         # Flutter Application Entry Point
│   ├── test/                 # Flutter Widget & Integration Tests
│   └── pubspec.yaml          # Flutter Dependencies Configuration
├── scripts/                  # Corpus Processing & Word Data Validation Scripts
└── README.md
```

---

## 📄 License & Attributions

Distributed under the **MIT License**. See `LICENSE` for details.

### Data Attributions
- **NLTK WordNet**: Semantic relations, parts of speech, and lexical definitions.
- **wordfreq**: Zipf frequency ranking model for difficulty determination.
- **dwyl/english-words**: Base English vocabulary corpus.
