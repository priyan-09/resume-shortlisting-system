-- Table: public.candidates

-- DROP TABLE IF EXISTS public.candidates;

CREATE TABLE IF NOT EXISTS public.candidates
(
    candidate_id integer NOT NULL DEFAULT nextval('candidates_candidate_id_seq'::regclass),
    full_name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    email character varying(100) COLLATE pg_catalog."default" NOT NULL,
    phone character varying(20) COLLATE pg_catalog."default",
    location character varying(100) COLLATE pg_catalog."default",
    years_experience integer,
    resume_file_path character varying(255) COLLATE pg_catalog."default",
    status character varying(20) COLLATE pg_catalog."default" DEFAULT 'pending'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT candidates_pkey PRIMARY KEY (candidate_id),
    CONSTRAINT candidates_email_key UNIQUE (email)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.candidates
    OWNER to postgres;


-- Table: public.education

-- DROP TABLE IF EXISTS public.education;

CREATE TABLE IF NOT EXISTS public.education
(
    education_id integer NOT NULL DEFAULT nextval('education_education_id_seq'::regclass),
    candidate_id integer,
    degree character varying(100) COLLATE pg_catalog."default",
    institution character varying(100) COLLATE pg_catalog."default",
    graduation_year integer,
    gpa numeric(3,2),
    CONSTRAINT education_pkey PRIMARY KEY (education_id),
    CONSTRAINT education_candidate_id_fkey FOREIGN KEY (candidate_id)
        REFERENCES public.candidates (candidate_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.education
    OWNER to postgres;


-- Table: public.job_descriptions

-- DROP TABLE IF EXISTS public.job_descriptions;

CREATE TABLE IF NOT EXISTS public.job_descriptions
(
    id integer NOT NULL DEFAULT nextval('job_descriptions_id_seq'::regclass),
    description text COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT job_descriptions_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.job_descriptions
    OWNER to postgres;


-- Table: public.shortlists

-- DROP TABLE IF EXISTS public.shortlists;

CREATE TABLE IF NOT EXISTS public.shortlists
(
    id integer NOT NULL DEFAULT nextval('shortlists_id_seq'::regclass),
    job_description_id integer NOT NULL,
    candidate_id integer NOT NULL,
    score double precision,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT shortlists_pkey PRIMARY KEY (id),
    CONSTRAINT shortlists_candidate_id_fkey FOREIGN KEY (candidate_id)
        REFERENCES public.candidates (candidate_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT shortlists_job_description_id_fkey FOREIGN KEY (job_description_id)
        REFERENCES public.job_descriptions (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.shortlists
    OWNER to postgres;



-- Table: public.skills

-- DROP TABLE IF EXISTS public.skills;

CREATE TABLE IF NOT EXISTS public.skills
(
    skill_id integer NOT NULL DEFAULT nextval('skills_skill_id_seq'::regclass),
    candidate_id integer,
    skill_name character varying(100) COLLATE pg_catalog."default",
    skill_category character varying(20) COLLATE pg_catalog."default",
    proficiency_level character varying(20) COLLATE pg_catalog."default",
    CONSTRAINT skills_pkey PRIMARY KEY (skill_id),
    CONSTRAINT skills_candidate_id_fkey FOREIGN KEY (candidate_id)
        REFERENCES public.candidates (candidate_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.skills
    OWNER to postgres;