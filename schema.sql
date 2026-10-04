CREATE TABLE IF NOT EXISTS salas (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    livro_nome TEXT NOT NULL,
    licao_inicial INTEGER NOT NULL DEFAULT 1,
    licao_limit INTEGER NOT NULL DEFAULT 50,
    licao_atual INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    telefone TEXT,
    tipo_usuario TEXT NOT NULL DEFAULT 'PROFESSOR' CHECK (tipo_usuario IN ('ADM', 'ADMIN', 'PROFESSOR')),
    sala_id INTEGER REFERENCES salas(id) ON DELETE SET NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS duplas (
    id SERIAL PRIMARY KEY,
    nome_dupla TEXT NOT NULL,
    sala_id INTEGER NOT NULL REFERENCES salas(id) ON DELETE CASCADE,
    professor_1_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    professor_2_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS escalas (
    id SERIAL PRIMARY KEY,
    data_domingo DATE NOT NULL,
    semana_numero INTEGER,
    sala_id INTEGER NOT NULL REFERENCES salas(id) ON DELETE CASCADE,
    dupla_id INTEGER NOT NULL REFERENCES duplas(id) ON DELETE CASCADE,
    numero_licao INTEGER NOT NULL,
    observacao TEXT,
    UNIQUE (sala_id, data_domingo)
);

CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_duplas_sala ON duplas(sala_id);
CREATE INDEX IF NOT EXISTS idx_escalas_sala_data ON escalas(sala_id, data_domingo);
