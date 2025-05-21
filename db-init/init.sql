CREATE TYPE "stipulation" AS ENUM (
  'STANDARD',
  'ELIMINATION',
  'NO_DQ',
  'TABLES',
  'LADDER'
);

CREATE TYPE "match_type" AS ENUM (
  'SINGLES',
  'TAG',
  'TRIOS',
  'THREE_WAY',
  'FOUR_WAY',
  'FIVE_WAY',
  'SIX_WAY',
  'THREE_WAY_TAG',
  'FOUR_WAY_TAG',
  'BATTLE_ROYALE'
);

CREATE TYPE "victory_type" AS ENUM (
  'CLEAN',
  'DISQUALIFICATION',
  'COUNT_OUT',
  'DRAW',
  'ITEM_RETRIEVAL'
);

CREATE TYPE "championship_type" AS ENUM (
  'SINGLES',
  'TAG',
  'TRIOS',
  'TROPHY_TOURNAMENT'
);

CREATE TYPE "championship_status" AS ENUM (
  'PRIMARY',
  'SECONDARY',
  'TERTIARY',
  'RETIRED',
  'VACANT'
);

CREATE TABLE "wrestlers" (
  "id" SERIAL PRIMARY KEY,
  "name" VARCHAR NOT NULL UNIQUE,
  "promotion_id" INT,
  "height_cm" INT,
  "weight_kg" INT,
  "debut" DATE,
  "age" int,
  "is_active" BOOLEAN,
  "years_active" INT,
  "retirement_date" DATE,
  "cagematch_id" INT,
  "title_reigns" INT,
  "titles_won" INT,
  "is_champion" boolean
);

CREATE TABLE "gimmicks" (
  "id" serial PRIMARY KEY,
  "wrestler_id" int,
  "gimmick_name" varchar,
  "promotion_id" int,
  "is_default" boolean,
  "date_created" date,
  "last_seen" date
);

CREATE TABLE "tag_teams" (
  "id" serial PRIMARY KEY,
  "name" varchar,
  "wrestler_one_id" int,
  "wrestler_two_id" int,
  "stable_id_nullable" int,
  "gimmick_wrestler_one_id_nullable" int,
  "gimmick_wrestler_two_id_nullable" int
);

CREATE TABLE "stables" (
  "id" serial PRIMARY KEY,
  "name" varchar,
  "promotion_id" int,
  "is_active" boolean,
  "years_active" int,
  "date_founded" date,
  "date_disbanded" date
);

CREATE TABLE "trios" (
  "id" serial PRIMARY KEY,
  "name" varchar NOT NULL,
  "promotion_id" int,
  "stable_id_nullable" int,
  "debut_date" date,
  "is_active" boolean
);

CREATE TABLE "trio_members" (
  "id" serial PRIMARY KEY,
  "trio_id" int,
  "wrestler_id" int,
  "gimmick_id" int,
  "joined_date" date,
  "left_date" date,
  "is_primary_lineup" boolean
);

CREATE TABLE "stable_members" (
  "id" serial PRIMARY KEY,
  "stable_id" int,
  "wrestler_id" int,
  "gimmick_id_nullable" int,
  "date_joined" date,
  "date_removed_nullable" date,
  "is_leader" boolean
);

CREATE TABLE "promotions" (
  "id" serial PRIMARY KEY,
  "name" VARCHAR NOT NULL,
  "country" VARCHAR,
  "year_founded" int,
  "is_active" boolean,
  "years_active" int,
  "year_disbanded" int,
  "cagematch_id" int UNIQUE
);

CREATE TABLE "events" (
  "id" serial PRIMARY KEY,
  "promotion_id" int,
  "date_of_event" date,
  "event_type_id" int,
  "headliner_match_id" int,
  "arena_id" int,
  "attendance" int
);

CREATE TABLE "arenas" (
  "id" serial PRIMARY KEY,
  "name" varchar NOT NULL,
  "country" varchar NOT NULL,
  "city" varchar,
  "state" varchar,
  "capacity" int,
  "last_visited" date,
  "last_promotion_id" int
);

CREATE TABLE "matches" (
  "id" serial PRIMARY KEY,
  "event_id" int,
  "promotion_id" int,
  "date" date,
  "match_type" match_type,
  "stipulation" stipulation,
  "title_defense" boolean,
  "title_id_nullable" int,
  "champion_id_nullable" int,
  "victor_id" int,
  "victory_type_id" int,
  "match_length" time,
  "match_rating" double,
  "position_on_event_card" int,
  "victor_team_number" int,
  "match_notes" TEXT
);

CREATE TABLE "match_participants" (
  "id" SERIAL PRIMARY KEY,
  "match_id" INT,
  "wrestler_id" INT,
  "tag_team_id" INT,
  "trio_id" INT,
  "participant_number" INT,
  "team_number" INT
);

CREATE TABLE "championship_history" (
  "id" serial PRIMARY KEY,
  "championship_id" int,
  "champion_id" int,
  "reign_number" int,
  "date_won" date,
  "match_id" int,
  "last_title_defense_date" date,
  "last_title_defense_match_id" int,
  "number_of_defenses" int,
  "date_lost" date
);

CREATE TABLE "championships" (
  "id" serial PRIMARY KEY,
  "name" varchar NOT NULL,
  "promotion_id" int,
  "championship_type" championship_type,
  "current_champion_id" int,
  "championship_status_id" championship_status,
  "is_active" boolean,
  "created_at" date
);

COMMENT ON COLUMN "trios"."stable_id_nullable" IS 'If this trio is a subset of a stable';

COMMENT ON COLUMN "trio_members"."is_primary_lineup" IS 'True if this member is part of the standard trio lineup';

COMMENT ON COLUMN "events"."event_type_id" IS 'Enum: NON-TELE,TV, PPV, PLE';

COMMENT ON COLUMN "events"."headliner_match_id" IS 'Main Event Match ID';

COMMENT ON COLUMN "events"."arena_id" IS 'Eventually will add arenas and capacity and attendance numbers';

COMMENT ON COLUMN "matches"."match_type" IS 'Enum: SINGLES, TAG, TRIOS, 3-WAY, 4-WAY, BATTLE_ROYAL etc etc';

COMMENT ON COLUMN "matches"."stipulation" IS 'ENUM: STANDARD, NO DQ, TABLES, LADDER, etc etc';

COMMENT ON COLUMN "matches"."victory_type_id" IS 'ENUM: CLEAN, DISQUALIFICATION, etc';

COMMENT ON COLUMN "matches"."match_rating" IS 'Wrestling Observer Newsletter based rating';

COMMENT ON COLUMN "matches"."position_on_event_card" IS '0 is main event, +1 for distance from the main event';

COMMENT ON COLUMN "championships"."championship_type" IS 'Enum: SINGLES, TAG, TRIOS, TROPHY/TOURNEY';

COMMENT ON COLUMN "championships"."current_champion_id" IS 'Wrestler''s Gimmick ID';

COMMENT ON COLUMN "championships"."championship_status_id" IS 'Enum: Primary, Secondary, Tertiary';

ALTER TABLE "wrestlers" ADD FOREIGN KEY ("promotion_id") REFERENCES "promotions" ("id");

ALTER TABLE "gimmicks" ADD FOREIGN KEY ("wrestler_id") REFERENCES "wrestlers" ("id");

ALTER TABLE "gimmicks" ADD FOREIGN KEY ("gimmick_id") REFERENCES "gimmicks" ("id");

ALTER TABLE "gimmicks" ADD FOREIGN KEY ("promotion_id") REFERENCES "promotions" ("id");

ALTER TABLE gimmicks ADD CONSTRAINT unique_gimmick_per_wrestler UNIQUE (wrestler_id, gimmick_name);

ALTER TABLE "tag_teams" ADD FOREIGN KEY ("wrestler_one_id") REFERENCES "wrestlers" ("id");

ALTER TABLE "tag_teams" ADD FOREIGN KEY ("wrestler_two_id") REFERENCES "wrestlers" ("id");

ALTER TABLE "tag_teams" ADD FOREIGN KEY ("stable_id_nullable") REFERENCES "stables" ("id");

ALTER TABLE "tag_teams" ADD FOREIGN KEY ("gimmick_wrestler_one_id_nullable") REFERENCES "gimmicks" ("id");

ALTER TABLE "tag_teams" ADD FOREIGN KEY ("gimmick_wrestler_two_id_nullable") REFERENCES "gimmicks" ("id");

ALTER TABLE "stables" ADD FOREIGN KEY ("promotion_id") REFERENCES "promotions" ("id");

ALTER TABLE "trios" ADD FOREIGN KEY ("promotion_id") REFERENCES "promotions" ("id");

ALTER TABLE "trios" ADD FOREIGN KEY ("stable_id_nullable") REFERENCES "stables" ("id");

ALTER TABLE "trio_members" ADD FOREIGN KEY ("trio_id") REFERENCES "trios" ("id");

ALTER TABLE "trio_members" ADD FOREIGN KEY ("wrestler_id") REFERENCES "wrestlers" ("id");

ALTER TABLE "trio_members" ADD FOREIGN KEY ("gimmick_id") REFERENCES "gimmicks" ("id");

ALTER TABLE "stable_members" ADD FOREIGN KEY ("stable_id") REFERENCES "stables" ("id");

ALTER TABLE "stable_members" ADD FOREIGN KEY ("wrestler_id") REFERENCES "wrestlers" ("id");

ALTER TABLE "stable_members" ADD FOREIGN KEY ("gimmick_id_nullable") REFERENCES "gimmicks" ("id");

ALTER TABLE "events" ADD FOREIGN KEY ("promotion_id") REFERENCES "promotions" ("id");

ALTER TABLE "events" ADD FOREIGN KEY ("headliner_match_id") REFERENCES "matches" ("id");

ALTER TABLE "events" ADD FOREIGN KEY ("arena_id") REFERENCES "arenas" ("id");

ALTER TABLE "arenas" ADD FOREIGN KEY ("last_promotion_id") REFERENCES "promotions" ("id");

ALTER TABLE "matches" ADD FOREIGN KEY ("event_id") REFERENCES "events" ("id");

ALTER TABLE "matches" ADD FOREIGN KEY ("promotion_id") REFERENCES "promotions" ("id");

ALTER TABLE "matches" ADD FOREIGN KEY ("title_id_nullable") REFERENCES "championships" ("id");

ALTER TABLE "match_participants" ADD FOREIGN KEY ("match_id") REFERENCES "matches" ("id");

ALTER TABLE "match_participants" ADD FOREIGN KEY ("wrestler_id") REFERENCES "wrestlers" ("id");

ALTER TABLE "match_participants" ADD FOREIGN KEY ("tag_team_id") REFERENCES "tag_teams" ("id");

ALTER TABLE "match_participants" ADD FOREIGN KEY ("trio_id") REFERENCES "trios" ("id");

ALTER TABLE "championship_history" ADD FOREIGN KEY ("championship_id") REFERENCES "championships" ("id");

ALTER TABLE "championship_history" ADD FOREIGN KEY ("match_id") REFERENCES "matches" ("id");

ALTER TABLE "championship_history" ADD FOREIGN KEY ("last_title_defense_match_id") REFERENCES "matches" ("id");

ALTER TABLE "championships" ADD FOREIGN KEY ("promotion_id") REFERENCES "promotions" ("id");

ALTER TABLE "championships" ADD FOREIGN KEY ("current_champion_id") REFERENCES "gimmicks" ("id");
