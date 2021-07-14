--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2
-- Dumped by pg_dump version 12.2

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
-- Name: Blocked; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Blocked" (
    blocker_id integer,
    blocked_id integer
);


ALTER TABLE public."Blocked" OWNER TO postgres;

--
-- Name: Not_Interested; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Not_Interested" (
    user_id integer,
    post_id integer
);


ALTER TABLE public."Not_Interested" OWNER TO postgres;

--
-- Name: clap; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clap (
    clap_id integer NOT NULL,
    user_id integer,
    post_id integer
);


ALTER TABLE public.clap OWNER TO postgres;

--
-- Name: clap_clap_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clap_clap_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.clap_clap_id_seq OWNER TO postgres;

--
-- Name: clap_clap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clap_clap_id_seq OWNED BY public.clap.clap_id;


--
-- Name: country; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.country (
    id integer NOT NULL,
    name character varying,
    code character varying
);


ALTER TABLE public.country OWNER TO postgres;

--
-- Name: country_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.country_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.country_id_seq OWNER TO postgres;

--
-- Name: country_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.country_id_seq OWNED BY public.country.id;


--
-- Name: followers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.followers (
    follower_id integer,
    followed_id integer
);


ALTER TABLE public.followers OWNER TO postgres;

--
-- Name: language; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.language (
    id integer NOT NULL,
    lang_type character varying(30) NOT NULL,
    code character varying(16) NOT NULL,
    name character varying(40) NOT NULL
);


ALTER TABLE public.language OWNER TO postgres;

--
-- Name: language_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.language_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.language_id_seq OWNER TO postgres;

--
-- Name: language_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.language_id_seq OWNED BY public.language.id;


--
-- Name: notification; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification (
    id integer NOT NULL,
    name character varying,
    user_id integer,
    post_id integer,
    seen boolean NOT NULL,
    "timestamp" double precision,
    payload_json text
);


ALTER TABLE public.notification OWNER TO postgres;

--
-- Name: notification_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notification_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notification_id_seq OWNER TO postgres;

--
-- Name: notification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notification_id_seq OWNED BY public.notification.id;


--
-- Name: posts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.posts (
    id integer NOT NULL,
    title character varying(160),
    uuid character varying(60),
    description character varying(200),
    post_url character varying(200),
    thumb_url character varying(200),
    text_content text,
    picture_url character varying(200),
    audio_url character varying(200),
    video_url character varying(200),
    "Country" integer NOT NULL,
    translate boolean NOT NULL,
    summarize boolean NOT NULL,
    created_on timestamp without time zone,
    author integer NOT NULL,
    post_type integer NOT NULL,
    orig_lang integer
);


ALTER TABLE public.posts OWNER TO postgres;

--
-- Name: posts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.posts_id_seq OWNER TO postgres;

--
-- Name: posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.posts_id_seq OWNED BY public.posts.id;


--
-- Name: postsummary; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.postsummary (
    id integer NOT NULL,
    post_id integer NOT NULL,
    content character varying,
    language_id integer NOT NULL,
    status character varying,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.postsummary OWNER TO postgres;

--
-- Name: postsummary_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.postsummary_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.postsummary_id_seq OWNER TO postgres;

--
-- Name: postsummary_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.postsummary_id_seq OWNED BY public.postsummary.id;


--
-- Name: posttype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.posttype (
    id integer NOT NULL,
    content character varying
);


ALTER TABLE public.posttype OWNER TO postgres;

--
-- Name: posttype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.posttype_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.posttype_id_seq OWNER TO postgres;

--
-- Name: posttype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.posttype_id_seq OWNED BY public.posttype.id;


--
-- Name: rating; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rating (
    id integer NOT NULL,
    ratingtype integer NOT NULL,
    rater integer NOT NULL,
    post_id integer NOT NULL
);


ALTER TABLE public.rating OWNER TO postgres;

--
-- Name: rating_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rating_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rating_id_seq OWNER TO postgres;

--
-- Name: rating_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rating_id_seq OWNED BY public.rating.id;


--
-- Name: ratingtype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ratingtype (
    id integer NOT NULL,
    content character varying
);


ALTER TABLE public.ratingtype OWNER TO postgres;

--
-- Name: ratingtype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ratingtype_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ratingtype_id_seq OWNER TO postgres;

--
-- Name: ratingtype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ratingtype_id_seq OWNED BY public.ratingtype.id;


--
-- Name: report; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report (
    id integer NOT NULL,
    reason character varying,
    reporter integer NOT NULL,
    post_id integer NOT NULL,
    user_reported integer NOT NULL,
    rtype integer NOT NULL,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.report OWNER TO postgres;

--
-- Name: report_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.report_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.report_id_seq OWNER TO postgres;

--
-- Name: report_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.report_id_seq OWNED BY public.report.id;


--
-- Name: reporttype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reporttype (
    id integer NOT NULL,
    content character varying
);


ALTER TABLE public.reporttype OWNER TO postgres;

--
-- Name: reporttype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reporttype_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reporttype_id_seq OWNER TO postgres;

--
-- Name: reporttype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reporttype_id_seq OWNED BY public.reporttype.id;


--
-- Name: save; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.save (
    id integer NOT NULL,
    user_id integer NOT NULL,
    post_id integer NOT NULL
);


ALTER TABLE public.save OWNER TO postgres;

--
-- Name: save_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.save_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.save_id_seq OWNER TO postgres;

--
-- Name: save_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.save_id_seq OWNED BY public.save.id;


--
-- Name: setting; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.setting (
    id integer NOT NULL,
    language_id integer NOT NULL,
    users_id integer NOT NULL,
    theme character varying(50) NOT NULL,
    "N_S_F_W" boolean NOT NULL
);


ALTER TABLE public.setting OWNER TO postgres;

--
-- Name: setting_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.setting_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.setting_id_seq OWNER TO postgres;

--
-- Name: setting_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.setting_id_seq OWNED BY public.setting.id;


--
-- Name: task; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task (
    id character varying(36) NOT NULL,
    name character varying(128),
    description character varying(128),
    user_id integer,
    complete boolean
);


ALTER TABLE public.task OWNER TO postgres;

--
-- Name: translated; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.translated (
    id integer NOT NULL,
    title character varying(250) NOT NULL,
    content character varying NOT NULL,
    language_id integer NOT NULL,
    post_id integer NOT NULL,
    tags text,
    status character varying,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.translated OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(120) NOT NULL,
    email character varying(120),
    phone character varying(120),
    uuid character varying(60) NOT NULL,
    password_hash character varying(256),
    bio character varying(350),
    picture character varying(120),
    code integer,
    user_visibility boolean NOT NULL,
    last_code integer,
    code_expires_in timestamp without time zone,
    verified_email boolean NOT NULL,
    verified_phone boolean NOT NULL,
    tries integer,
    created_on timestamp without time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: clap clap_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clap ALTER COLUMN clap_id SET DEFAULT nextval('public.clap_clap_id_seq'::regclass);


--
-- Name: country id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.country ALTER COLUMN id SET DEFAULT nextval('public.country_id_seq'::regclass);


--
-- Name: language id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.language ALTER COLUMN id SET DEFAULT nextval('public.language_id_seq'::regclass);


--
-- Name: notification id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification ALTER COLUMN id SET DEFAULT nextval('public.notification_id_seq'::regclass);


--
-- Name: posts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts ALTER COLUMN id SET DEFAULT nextval('public.posts_id_seq'::regclass);


--
-- Name: postsummary id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.postsummary ALTER COLUMN id SET DEFAULT nextval('public.postsummary_id_seq'::regclass);


--
-- Name: posttype id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posttype ALTER COLUMN id SET DEFAULT nextval('public.posttype_id_seq'::regclass);


--
-- Name: rating id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rating ALTER COLUMN id SET DEFAULT nextval('public.rating_id_seq'::regclass);


--
-- Name: ratingtype id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratingtype ALTER COLUMN id SET DEFAULT nextval('public.ratingtype_id_seq'::regclass);


--
-- Name: report id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report ALTER COLUMN id SET DEFAULT nextval('public.report_id_seq'::regclass);


--
-- Name: reporttype id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reporttype ALTER COLUMN id SET DEFAULT nextval('public.reporttype_id_seq'::regclass);


--
-- Name: save id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.save ALTER COLUMN id SET DEFAULT nextval('public.save_id_seq'::regclass);


--
-- Name: setting id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.setting ALTER COLUMN id SET DEFAULT nextval('public.setting_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: Blocked; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Blocked" (blocker_id, blocked_id) FROM stdin;
\.


--
-- Data for Name: Not_Interested; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Not_Interested" (user_id, post_id) FROM stdin;
\.


--
-- Data for Name: clap; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.clap (clap_id, user_id, post_id) FROM stdin;
\.


--
-- Data for Name: country; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.country (id, name, code) FROM stdin;
\.


--
-- Data for Name: followers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.followers (follower_id, followed_id) FROM stdin;
\.


--
-- Data for Name: language; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.language (id, lang_type, code, name) FROM stdin;
\.


--
-- Data for Name: notification; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notification (id, name, user_id, post_id, seen, "timestamp", payload_json) FROM stdin;
\.


--
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.posts (id, title, uuid, description, post_url, thumb_url, text_content, picture_url, audio_url, video_url, "Country", translate, summarize, created_on, author, post_type, orig_lang) FROM stdin;
\.


--
-- Data for Name: postsummary; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.postsummary (id, post_id, content, language_id, status, "timestamp") FROM stdin;
\.


--
-- Data for Name: posttype; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.posttype (id, content) FROM stdin;
\.


--
-- Data for Name: rating; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rating (id, ratingtype, rater, post_id) FROM stdin;
\.


--
-- Data for Name: ratingtype; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ratingtype (id, content) FROM stdin;
\.


--
-- Data for Name: report; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.report (id, reason, reporter, post_id, user_reported, rtype, "timestamp") FROM stdin;
\.


--
-- Data for Name: reporttype; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reporttype (id, content) FROM stdin;
\.


--
-- Data for Name: save; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.save (id, user_id, post_id) FROM stdin;
\.


--
-- Data for Name: setting; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.setting (id, language_id, users_id, theme, "N_S_F_W") FROM stdin;
\.


--
-- Data for Name: task; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task (id, name, description, user_id, complete) FROM stdin;
\.


--
-- Data for Name: translated; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.translated (id, title, content, language_id, post_id, tags, status, "timestamp") FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, phone, uuid, password_hash, bio, picture, code, user_visibility, last_code, code_expires_in, verified_email, verified_phone, tries, created_on) FROM stdin;
\.


--
-- Name: clap_clap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clap_clap_id_seq', 1, false);


--
-- Name: country_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.country_id_seq', 1, false);


--
-- Name: language_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.language_id_seq', 1, false);


--
-- Name: notification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notification_id_seq', 1, false);


--
-- Name: posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.posts_id_seq', 1, false);


--
-- Name: postsummary_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.postsummary_id_seq', 1, false);


--
-- Name: posttype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.posttype_id_seq', 1, false);


--
-- Name: rating_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rating_id_seq', 1, false);


--
-- Name: ratingtype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ratingtype_id_seq', 1, false);


--
-- Name: report_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.report_id_seq', 1, false);


--
-- Name: reporttype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reporttype_id_seq', 1, false);


--
-- Name: save_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.save_id_seq', 1, false);


--
-- Name: setting_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.setting_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: clap clap_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clap
    ADD CONSTRAINT clap_pkey PRIMARY KEY (clap_id);


--
-- Name: country country_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.country
    ADD CONSTRAINT country_pkey PRIMARY KEY (id);


--
-- Name: language language_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.language
    ADD CONSTRAINT language_pkey PRIMARY KEY (id);


--
-- Name: notification notification_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT notification_pkey PRIMARY KEY (id);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: postsummary postsummary_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.postsummary
    ADD CONSTRAINT postsummary_pkey PRIMARY KEY (id);


--
-- Name: posttype posttype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posttype
    ADD CONSTRAINT posttype_pkey PRIMARY KEY (id);


--
-- Name: rating rating_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rating
    ADD CONSTRAINT rating_pkey PRIMARY KEY (id);


--
-- Name: ratingtype ratingtype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratingtype
    ADD CONSTRAINT ratingtype_pkey PRIMARY KEY (id);


--
-- Name: report report_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report
    ADD CONSTRAINT report_pkey PRIMARY KEY (id);


--
-- Name: reporttype reporttype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reporttype
    ADD CONSTRAINT reporttype_pkey PRIMARY KEY (id);


--
-- Name: save save_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.save
    ADD CONSTRAINT save_pkey PRIMARY KEY (id);


--
-- Name: setting setting_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.setting
    ADD CONSTRAINT setting_pkey PRIMARY KEY (id);


--
-- Name: task task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_pkey PRIMARY KEY (id);


--
-- Name: translated translated_content_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.translated
    ADD CONSTRAINT translated_content_key UNIQUE (content);


--
-- Name: translated translated_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.translated
    ADD CONSTRAINT translated_pkey PRIMARY KEY (id);


--
-- Name: translated translated_title_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.translated
    ADD CONSTRAINT translated_title_key UNIQUE (title);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_notification_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_name ON public.notification USING btree (name);


--
-- Name: ix_notification_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_timestamp ON public.notification USING btree ("timestamp");


--
-- Name: ix_posts_created_on; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_posts_created_on ON public.posts USING btree (created_on);


--
-- Name: ix_postsummary_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_postsummary_timestamp ON public.postsummary USING btree ("timestamp");


--
-- Name: ix_report_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_report_timestamp ON public.report USING btree ("timestamp");


--
-- Name: ix_task_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_task_name ON public.task USING btree (name);


--
-- Name: ix_translated_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_translated_timestamp ON public.translated USING btree ("timestamp");


--
-- Name: Not_Interested Not_Interested_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Not_Interested"
    ADD CONSTRAINT "Not_Interested_post_id_fkey" FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: clap clap_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clap
    ADD CONSTRAINT clap_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: notification notification_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT notification_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: posts posts_Country_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT "posts_Country_fkey" FOREIGN KEY ("Country") REFERENCES public.country(id);


--
-- Name: posts posts_orig_lang_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_orig_lang_fkey FOREIGN KEY (orig_lang) REFERENCES public.language(id);


--
-- Name: posts posts_post_type_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_post_type_fkey FOREIGN KEY (post_type) REFERENCES public.posttype(id);


--
-- Name: postsummary postsummary_language_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.postsummary
    ADD CONSTRAINT postsummary_language_id_fkey FOREIGN KEY (language_id) REFERENCES public.language(id);


--
-- Name: postsummary postsummary_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.postsummary
    ADD CONSTRAINT postsummary_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: rating rating_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rating
    ADD CONSTRAINT rating_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: rating rating_ratingtype_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rating
    ADD CONSTRAINT rating_ratingtype_fkey FOREIGN KEY (ratingtype) REFERENCES public.ratingtype(id);


--
-- Name: report report_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report
    ADD CONSTRAINT report_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: report report_rtype_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report
    ADD CONSTRAINT report_rtype_fkey FOREIGN KEY (rtype) REFERENCES public.reporttype(id);


--
-- Name: save save_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.save
    ADD CONSTRAINT save_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: setting setting_language_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.setting
    ADD CONSTRAINT setting_language_id_fkey FOREIGN KEY (language_id) REFERENCES public.language(id);


--
-- Name: translated translated_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.translated
    ADD CONSTRAINT translated_id_fkey FOREIGN KEY (id) REFERENCES public.posts(id);


--
-- Name: translated translated_language_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.translated
    ADD CONSTRAINT translated_language_id_fkey FOREIGN KEY (language_id) REFERENCES public.language(id);


--
-- Name: translated translated_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.translated
    ADD CONSTRAINT translated_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- PostgreSQL database dump complete
--

