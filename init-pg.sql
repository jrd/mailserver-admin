--
-- PostgreSQL database dump
--

-- Dumped from database version 14.1 (Debian 14.1-1.pgdg110+1)
-- Dumped by pg_dump version 14.1 (Debian 14.1-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: mail_aliases; Type: TABLE; Schema: public; Owner: mailserver
--

CREATE TABLE public.mail_aliases (
    id integer NOT NULL,
    domain_id integer,
    name character varying(255) NOT NULL,
    destination character varying(255) NOT NULL
);


ALTER TABLE public.mail_aliases OWNER TO mailserver;

--
-- Name: mail_aliases_id_seq; Type: SEQUENCE; Schema: public; Owner: mailserver
--

CREATE SEQUENCE public.mail_aliases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mail_aliases_id_seq OWNER TO mailserver;

--
-- Name: mail_aliases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mailserver
--

ALTER SEQUENCE public.mail_aliases_id_seq OWNED BY public.mail_aliases.id;


--
-- Name: mail_domains; Type: TABLE; Schema: public; Owner: mailserver
--

CREATE TABLE public.mail_domains (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.mail_domains OWNER TO mailserver;

--
-- Name: mail_domains_id_seq; Type: SEQUENCE; Schema: public; Owner: mailserver
--

CREATE SEQUENCE public.mail_domains_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mail_domains_id_seq OWNER TO mailserver;

--
-- Name: mail_domains_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mailserver
--

ALTER SEQUENCE public.mail_domains_id_seq OWNED BY public.mail_domains.id;


--
-- Name: mail_users; Type: TABLE; Schema: public; Owner: mailserver
--

CREATE TABLE public.mail_users (
    id integer NOT NULL,
    domain_id integer,
    name character varying(255) NOT NULL,
    password character varying(255) NOT NULL
);


ALTER TABLE public.mail_users OWNER TO mailserver;

--
-- Name: mail_users_id_seq; Type: SEQUENCE; Schema: public; Owner: mailserver
--

CREATE SEQUENCE public.mail_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mail_users_id_seq OWNER TO mailserver;

--
-- Name: mail_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mailserver
--

ALTER SEQUENCE public.mail_users_id_seq OWNED BY public.mail_users.id;


--
-- Name: migration_versions; Type: TABLE; Schema: public; Owner: mailserver
--

CREATE TABLE public.migration_versions (
    version character varying(255) NOT NULL
);


ALTER TABLE public.migration_versions OWNER TO mailserver;

--
-- Name: mail_aliases id; Type: DEFAULT; Schema: public; Owner: mailserver
--

ALTER TABLE ONLY public.mail_aliases ALTER COLUMN id SET DEFAULT nextval('public.mail_aliases_id_seq'::regclass);


--
-- Name: mail_domains id; Type: DEFAULT; Schema: public; Owner: mailserver
--

ALTER TABLE ONLY public.mail_domains ALTER COLUMN id SET DEFAULT nextval('public.mail_domains_id_seq'::regclass);


--
-- Name: mail_users id; Type: DEFAULT; Schema: public; Owner: mailserver
--

ALTER TABLE ONLY public.mail_users ALTER COLUMN id SET DEFAULT nextval('public.mail_users_id_seq'::regclass);


--
-- Data for Name: mail_aliases; Type: TABLE DATA; Schema: public; Owner: mailserver
--

COPY public.mail_aliases (id, domain_id, name, destination) FROM stdin;
\.


--
-- Data for Name: mail_domains; Type: TABLE DATA; Schema: public; Owner: mailserver
--

COPY public.mail_domains (id, name) FROM stdin;
\.


--
-- Data for Name: mail_users; Type: TABLE DATA; Schema: public; Owner: mailserver
--

COPY public.mail_users (id, domain_id, name, password) FROM stdin;
\.


--
-- Data for Name: migration_versions; Type: TABLE DATA; Schema: public; Owner: mailserver
--

COPY public.migration_versions (version) FROM stdin;
20180320164351
20180320171339
\.


--
-- Name: mail_aliases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mailserver
--

SELECT pg_catalog.setval('public.mail_aliases_id_seq', 1, false);


--
-- Name: mail_domains_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mailserver
--

SELECT pg_catalog.setval('public.mail_domains_id_seq', 1, false);


--
-- Name: mail_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mailserver
--

SELECT pg_catalog.setval('public.mail_users_id_seq', 1, false);


--
-- Name: mail_domains UNIQ_56C63EF25E237E06; Type: CONSTRAINT; Schema: public; Owner: mailserver
--

ALTER TABLE ONLY public.mail_domains
    ADD CONSTRAINT "UNIQ_56C63EF25E237E06" UNIQUE (name);


--
-- Name: mail_aliases alias_idx; Type: CONSTRAINT; Schema: public; Owner: mailserver
--

ALTER TABLE ONLY public.mail_aliases
    ADD CONSTRAINT alias_idx UNIQUE (domain_id, name, destination);


--
-- Name: mail_aliases mail_aliases_pkey; Type: CONSTRAINT; Schema: public; Owner: mailserver
--

ALTER TABLE ONLY public.mail_aliases
    ADD CONSTRAINT mail_aliases_pkey PRIMARY KEY (id);


--
-- Name: mail_domains mail_domains_pkey; Type: CONSTRAINT; Schema: public; Owner: mailserver
--

ALTER TABLE ONLY public.mail_domains
    ADD CONSTRAINT mail_domains_pkey PRIMARY KEY (id);


--
-- Name: mail_users mail_users_pkey; Type: CONSTRAINT; Schema: public; Owner: mailserver
--

ALTER TABLE ONLY public.mail_users
    ADD CONSTRAINT mail_users_pkey PRIMARY KEY (id);


--
-- Name: migration_versions migration_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: mailserver
--

ALTER TABLE ONLY public.migration_versions
    ADD CONSTRAINT migration_versions_pkey PRIMARY KEY (version);


--
-- Name: mail_users user_idx; Type: CONSTRAINT; Schema: public; Owner: mailserver
--

ALTER TABLE ONLY public.mail_users
    ADD CONSTRAINT user_idx UNIQUE (name, domain_id);


--
-- Name: mail_users FK_1483A5E9115F0EE5; Type: FK CONSTRAINT; Schema: public; Owner: mailserver
--

ALTER TABLE ONLY public.mail_users
    ADD CONSTRAINT "FK_1483A5E9115F0EE5" FOREIGN KEY (domain_id) REFERENCES public.mail_domains(id);


--
-- Name: mail_aliases fk_5f12bb39115f0ee5; Type: FK CONSTRAINT; Schema: public; Owner: mailserver
--

ALTER TABLE ONLY public.mail_aliases
    ADD CONSTRAINT fk_5f12bb39115f0ee5 FOREIGN KEY (domain_id) REFERENCES public.mail_domains(id);


--
-- PostgreSQL database dump complete
--

