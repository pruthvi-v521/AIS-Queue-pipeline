--
-- NOTE:
--
-- File paths need to be edited. Search for $$PATH$$ and
-- replace it with the path to the directory containing
-- the extracted data files.
--
--
-- PostgreSQL database dump
--

-- Dumped from database version 17.8 (Homebrew)
-- Dumped by pg_dump version 18.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE ais;
--
-- Name: ais; Type: DATABASE; Schema: -; Owner: ammar
--

CREATE DATABASE ais WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';


ALTER DATABASE ais OWNER TO ammar;

\unrestrict (null)
\connect ais
\restrict (null)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ais_collision_alert; Type: TABLE; Schema: public; Owner: ammar
--

CREATE TABLE public.ais_collision_alert (
    id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    ts timestamp with time zone NOT NULL,
    mmsi_a bigint NOT NULL,
    mmsi_b bigint NOT NULL,
    dcpa_m double precision NOT NULL,
    tcpa_s double precision NOT NULL,
    geom_a public.geography(Point,4326),
    geom_b public.geography(Point,4326),
    sog_a real,
    cog_a real,
    sog_b real,
    cog_b real,
    severity integer NOT NULL,
    reason text,
    details jsonb
);


ALTER TABLE public.ais_collision_alert OWNER TO ammar;

--
-- Name: ais_collision_alert_id_seq; Type: SEQUENCE; Schema: public; Owner: ammar
--

CREATE SEQUENCE public.ais_collision_alert_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ais_collision_alert_id_seq OWNER TO ammar;

--
-- Name: ais_collision_alert_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ammar
--

ALTER SEQUENCE public.ais_collision_alert_id_seq OWNED BY public.ais_collision_alert.id;


--
-- Name: ais_latest_position; Type: TABLE; Schema: public; Owner: ammar
--

CREATE TABLE public.ais_latest_position (
    mmsi bigint NOT NULL,
    ts timestamp with time zone NOT NULL,
    geom public.geography(Point,4326) NOT NULL,
    sog real,
    cog real,
    heading integer,
    nav_status integer,
    last_raw_id bigint,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.ais_latest_position OWNER TO ammar;

--
-- Name: ais_positions; Type: TABLE; Schema: public; Owner: ammar
--

CREATE TABLE public.ais_positions (
    id bigint NOT NULL,
    raw_id bigint NOT NULL,
    msg_type integer NOT NULL,
    mmsi bigint NOT NULL,
    ts timestamp with time zone NOT NULL,
    station_id text,
    geom public.geography(Point,4326) NOT NULL,
    accuracy boolean,
    sog real,
    cog real,
    heading integer,
    nav_status integer,
    rot real,
    altitude integer,
    extra jsonb
);


ALTER TABLE public.ais_positions OWNER TO ammar;

--
-- Name: ais_positions_id_seq; Type: SEQUENCE; Schema: public; Owner: ammar
--

CREATE SEQUENCE public.ais_positions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ais_positions_id_seq OWNER TO ammar;

--
-- Name: ais_positions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ammar
--

ALTER SEQUENCE public.ais_positions_id_seq OWNED BY public.ais_positions.id;


--
-- Name: ais_raw; Type: TABLE; Schema: public; Owner: ammar
--

CREATE TABLE public.ais_raw (
    id bigint NOT NULL,
    received_at timestamp with time zone DEFAULT now() NOT NULL,
    payload_ts timestamp with time zone,
    msg_type integer NOT NULL,
    mmsi bigint NOT NULL,
    station_id text,
    payload jsonb NOT NULL
);


ALTER TABLE public.ais_raw OWNER TO ammar;

--
-- Name: ais_raw_id_seq; Type: SEQUENCE; Schema: public; Owner: ammar
--

CREATE SEQUENCE public.ais_raw_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ais_raw_id_seq OWNER TO ammar;

--
-- Name: ais_raw_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ammar
--

ALTER SEQUENCE public.ais_raw_id_seq OWNED BY public.ais_raw.id;


--
-- Name: ais_static; Type: TABLE; Schema: public; Owner: ammar
--

CREATE TABLE public.ais_static (
    mmsi bigint NOT NULL,
    shipname text,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    last_raw_id bigint,
    extra jsonb
);


ALTER TABLE public.ais_static OWNER TO ammar;

--
-- Name: flyway_schema_history; Type: TABLE; Schema: public; Owner: ammar
--

CREATE TABLE public.flyway_schema_history (
    installed_rank integer NOT NULL,
    version character varying(50),
    description character varying(200) NOT NULL,
    type character varying(20) NOT NULL,
    script character varying(1000) NOT NULL,
    checksum integer,
    installed_by character varying(100) NOT NULL,
    installed_on timestamp without time zone DEFAULT now() NOT NULL,
    execution_time integer NOT NULL,
    success boolean NOT NULL
);


ALTER TABLE public.flyway_schema_history OWNER TO ammar;

--
-- Name: ais_collision_alert id; Type: DEFAULT; Schema: public; Owner: ammar
--

ALTER TABLE ONLY public.ais_collision_alert ALTER COLUMN id SET DEFAULT nextval('public.ais_collision_alert_id_seq'::regclass);


--
-- Name: ais_positions id; Type: DEFAULT; Schema: public; Owner: ammar
--

ALTER TABLE ONLY public.ais_positions ALTER COLUMN id SET DEFAULT nextval('public.ais_positions_id_seq'::regclass);


--
-- Name: ais_raw id; Type: DEFAULT; Schema: public; Owner: ammar
--

ALTER TABLE ONLY public.ais_raw ALTER COLUMN id SET DEFAULT nextval('public.ais_raw_id_seq'::regclass);


--
-- Data for Name: ais_collision_alert; Type: TABLE DATA; Schema: public; Owner: ammar
--

COPY public.ais_collision_alert (id, created_at, ts, mmsi_a, mmsi_b, dcpa_m, tcpa_s, geom_a, geom_b, sog_a, cog_a, sog_b, cog_b, severity, reason, details) FROM stdin;
\.
COPY public.ais_collision_alert (id, created_at, ts, mmsi_a, mmsi_b, dcpa_m, tcpa_s, geom_a, geom_b, sog_a, cog_a, sog_b, cog_b, severity, reason, details) FROM '$$PATH$$/4810.dat';

--
-- Data for Name: ais_latest_position; Type: TABLE DATA; Schema: public; Owner: ammar
--

COPY public.ais_latest_position (mmsi, ts, geom, sog, cog, heading, nav_status, last_raw_id, updated_at) FROM stdin;
\.
COPY public.ais_latest_position (mmsi, ts, geom, sog, cog, heading, nav_status, last_raw_id, updated_at) FROM '$$PATH$$/4808.dat';

--
-- Data for Name: ais_positions; Type: TABLE DATA; Schema: public; Owner: ammar
--

COPY public.ais_positions (id, raw_id, msg_type, mmsi, ts, station_id, geom, accuracy, sog, cog, heading, nav_status, rot, altitude, extra) FROM stdin;
\.
COPY public.ais_positions (id, raw_id, msg_type, mmsi, ts, station_id, geom, accuracy, sog, cog, heading, nav_status, rot, altitude, extra) FROM '$$PATH$$/4806.dat';

--
-- Data for Name: ais_raw; Type: TABLE DATA; Schema: public; Owner: ammar
--

COPY public.ais_raw (id, received_at, payload_ts, msg_type, mmsi, station_id, payload) FROM stdin;
\.
COPY public.ais_raw (id, received_at, payload_ts, msg_type, mmsi, station_id, payload) FROM '$$PATH$$/4804.dat';

--
-- Data for Name: ais_static; Type: TABLE DATA; Schema: public; Owner: ammar
--

COPY public.ais_static (mmsi, shipname, updated_at, last_raw_id, extra) FROM stdin;
\.
COPY public.ais_static (mmsi, shipname, updated_at, last_raw_id, extra) FROM '$$PATH$$/4807.dat';

--
-- Data for Name: flyway_schema_history; Type: TABLE DATA; Schema: public; Owner: ammar
--

COPY public.flyway_schema_history (installed_rank, version, description, type, script, checksum, installed_by, installed_on, execution_time, success) FROM stdin;
\.
COPY public.flyway_schema_history (installed_rank, version, description, type, script, checksum, installed_by, installed_on, execution_time, success) FROM '$$PATH$$/4802.dat';

--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: ammar
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.
COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM '$$PATH$$/4614.dat';

--
-- Name: ais_collision_alert_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ammar
--

SELECT pg_catalog.setval('public.ais_collision_alert_id_seq', 1, false);


--
-- Name: ais_positions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ammar
--

SELECT pg_catalog.setval('public.ais_positions_id_seq', 95706, true);


--
-- Name: ais_raw_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ammar
--

SELECT pg_catalog.setval('public.ais_raw_id_seq', 119757, true);


--
-- Name: ais_collision_alert ais_collision_alert_pkey; Type: CONSTRAINT; Schema: public; Owner: ammar
--

ALTER TABLE ONLY public.ais_collision_alert
    ADD CONSTRAINT ais_collision_alert_pkey PRIMARY KEY (id);


--
-- Name: ais_latest_position ais_latest_position_pkey; Type: CONSTRAINT; Schema: public; Owner: ammar
--

ALTER TABLE ONLY public.ais_latest_position
    ADD CONSTRAINT ais_latest_position_pkey PRIMARY KEY (mmsi);


--
-- Name: ais_positions ais_positions_pkey; Type: CONSTRAINT; Schema: public; Owner: ammar
--

ALTER TABLE ONLY public.ais_positions
    ADD CONSTRAINT ais_positions_pkey PRIMARY KEY (id);


--
-- Name: ais_raw ais_raw_pkey; Type: CONSTRAINT; Schema: public; Owner: ammar
--

ALTER TABLE ONLY public.ais_raw
    ADD CONSTRAINT ais_raw_pkey PRIMARY KEY (id);


--
-- Name: ais_static ais_static_pkey; Type: CONSTRAINT; Schema: public; Owner: ammar
--

ALTER TABLE ONLY public.ais_static
    ADD CONSTRAINT ais_static_pkey PRIMARY KEY (mmsi);


--
-- Name: flyway_schema_history flyway_schema_history_pk; Type: CONSTRAINT; Schema: public; Owner: ammar
--

ALTER TABLE ONLY public.flyway_schema_history
    ADD CONSTRAINT flyway_schema_history_pk PRIMARY KEY (installed_rank);


--
-- Name: flyway_schema_history_s_idx; Type: INDEX; Schema: public; Owner: ammar
--

CREATE INDEX flyway_schema_history_s_idx ON public.flyway_schema_history USING btree (success);


--
-- Name: idx_ais_latest_geom_gist; Type: INDEX; Schema: public; Owner: ammar
--

CREATE INDEX idx_ais_latest_geom_gist ON public.ais_latest_position USING gist (geom);


--
-- Name: idx_ais_latest_ts; Type: INDEX; Schema: public; Owner: ammar
--

CREATE INDEX idx_ais_latest_ts ON public.ais_latest_position USING btree (ts DESC);


--
-- Name: idx_ais_pos_geom_gist; Type: INDEX; Schema: public; Owner: ammar
--

CREATE INDEX idx_ais_pos_geom_gist ON public.ais_positions USING gist (geom);


--
-- Name: idx_ais_pos_mmsi_ts; Type: INDEX; Schema: public; Owner: ammar
--

CREATE INDEX idx_ais_pos_mmsi_ts ON public.ais_positions USING btree (mmsi, ts DESC);


--
-- Name: idx_ais_pos_ts; Type: INDEX; Schema: public; Owner: ammar
--

CREATE INDEX idx_ais_pos_ts ON public.ais_positions USING btree (ts DESC);


--
-- Name: idx_ais_raw_mmsi_ts; Type: INDEX; Schema: public; Owner: ammar
--

CREATE INDEX idx_ais_raw_mmsi_ts ON public.ais_raw USING btree (mmsi, payload_ts DESC);


--
-- Name: idx_ais_raw_payload_gin; Type: INDEX; Schema: public; Owner: ammar
--

CREATE INDEX idx_ais_raw_payload_gin ON public.ais_raw USING gin (payload);


--
-- Name: idx_ais_raw_type_ts; Type: INDEX; Schema: public; Owner: ammar
--

CREATE INDEX idx_ais_raw_type_ts ON public.ais_raw USING btree (msg_type, payload_ts DESC);


--
-- Name: idx_alert_pair_ts; Type: INDEX; Schema: public; Owner: ammar
--

CREATE INDEX idx_alert_pair_ts ON public.ais_collision_alert USING btree (mmsi_a, mmsi_b, ts DESC);


--
-- Name: idx_alert_ts; Type: INDEX; Schema: public; Owner: ammar
--

CREATE INDEX idx_alert_ts ON public.ais_collision_alert USING btree (ts DESC);


--
-- Name: ais_latest_position ais_latest_position_last_raw_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ammar
--

ALTER TABLE ONLY public.ais_latest_position
    ADD CONSTRAINT ais_latest_position_last_raw_id_fkey FOREIGN KEY (last_raw_id) REFERENCES public.ais_raw(id) ON DELETE SET NULL;


--
-- Name: ais_positions ais_positions_raw_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ammar
--

ALTER TABLE ONLY public.ais_positions
    ADD CONSTRAINT ais_positions_raw_id_fkey FOREIGN KEY (raw_id) REFERENCES public.ais_raw(id) ON DELETE CASCADE;


--
-- Name: ais_static ais_static_last_raw_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ammar
--

ALTER TABLE ONLY public.ais_static
    ADD CONSTRAINT ais_static_last_raw_id_fkey FOREIGN KEY (last_raw_id) REFERENCES public.ais_raw(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

