-- Hangman Reimagined Supabase Schema Migration

CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    avatar_url TEXT,
    coins INTEGER NOT NULL DEFAULT 100 CHECK (coins >= 0),
    xp INTEGER NOT NULL DEFAULT 0 CHECK (xp >= 0),
    level INTEGER NOT NULL DEFAULT 1,
    games_played INTEGER NOT NULL DEFAULT 0,
    games_won INTEGER NOT NULL DEFAULT 0,
    current_streak INTEGER NOT NULL DEFAULT 0,
    best_streak INTEGER NOT NULL DEFAULT 0,
    total_hints_used INTEGER NOT NULL DEFAULT 0,
    favorite_category TEXT DEFAULT 'General',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.words (
    id SERIAL PRIMARY KEY,
    word TEXT UNIQUE NOT NULL,
    length INTEGER NOT NULL,
    vowel_count INTEGER NOT NULL,
    consonant_count INTEGER NOT NULL,
    has_repeated_letters BOOLEAN NOT NULL,
    frequency REAL NOT NULL,
    difficulty INTEGER NOT NULL,
    part_of_speech TEXT NOT NULL,
    definition TEXT NOT NULL,
    synonyms JSONB NOT NULL DEFAULT '[]'::jsonb,
    category TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_words_difficulty ON public.words(difficulty);
CREATE INDEX IF NOT EXISTS idx_words_category ON public.words(category);

CREATE TABLE IF NOT EXISTS public.games (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    word_id INTEGER REFERENCES public.words(id),
    mode TEXT NOT NULL DEFAULT 'classic',
    status TEXT NOT NULL DEFAULT 'in_progress',
    score INTEGER NOT NULL DEFAULT 0,
    mistakes INTEGER NOT NULL DEFAULT 0,
    lives_remaining INTEGER NOT NULL DEFAULT 6,
    hints_used INTEGER NOT NULL DEFAULT 0,
    time_seconds INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS public.daily_challenges (
    challenge_date DATE PRIMARY KEY,
    word_id INTEGER REFERENCES public.words(id),
    category TEXT NOT NULL,
    difficulty INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS public.achievements (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL,
    coin_reward INTEGER NOT NULL DEFAULT 50,
    xp_reward INTEGER NOT NULL DEFAULT 100
);

CREATE TABLE IF NOT EXISTS public.user_achievements (
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    achievement_id TEXT REFERENCES public.achievements(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, achievement_id)
);

-- Seed static achievements
INSERT INTO public.achievements (id, title, description, icon, coin_reward, xp_reward) VALUES
('first_victory', 'First Victory', 'Win your first Hangman game', 'trophy', 50, 100),
('ten_wins', 'Word Novice', 'Win 10 games', 'award', 100, 250),
('hundred_wins', 'Vocabulary Master', 'Win 100 games', 'crown', 500, 1000),
('perfect_game', 'Flawless Mind', 'Win a game with 0 mistakes', 'star', 150, 300),
('no_hint_victory', 'Pure Genius', 'Win a game without using hints', 'brain', 100, 200),
('streak_7', 'Weekly Scholar', 'Maintain a 7-day streak', 'flame', 200, 400),
('streak_30', 'Unstoppable', 'Maintain a 30-day streak', 'zap', 1000, 2500)
ON CONFLICT (id) DO NOTHING;

-- Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.words ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.games ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_achievements ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Public profiles read" ON public.profiles FOR SELECT USING (true);
CREATE POLICY "Owner profile update" ON public.profiles FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Public words read" ON public.words FOR SELECT USING (true);
CREATE POLICY "Public daily challenge read" ON public.daily_challenges FOR SELECT USING (true);
CREATE POLICY "Public achievements read" ON public.achievements FOR SELECT USING (true);

CREATE POLICY "Owner games read" ON public.games FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);
CREATE POLICY "Owner games write" ON public.games FOR ALL USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Owner achievements read" ON public.user_achievements FOR SELECT USING (auth.uid() = user_id);
