--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8
-- Dumped by pg_dump version 17.4

-- Started on 2025-05-11 20:00:11

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
-- TOC entry 218 (class 1259 OID 16438)
-- Name: id_sequence; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.id_sequence
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.id_sequence OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 215 (class 1259 OID 16399)
-- Name: agricultor; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agricultor (
    usuario character varying NOT NULL,
    telefono character varying NOT NULL,
    correo character varying NOT NULL,
    contrasena character varying NOT NULL,
    estado character varying,
    municipio character varying,
    "ID" integer DEFAULT nextval('public.id_sequence'::regclass) NOT NULL
);


ALTER TABLE public.agricultor OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 16404)
-- Name: cosecha; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cosecha (
    "nombreCultivo" character varying NOT NULL,
    "FechaSiembra" date NOT NULL,
    "Ubicacion" character varying NOT NULL,
    "SuperficieSembrada" character varying NOT NULL
);


ALTER TABLE public.cosecha OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16481)
-- Name: cultivos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cultivos (
    id_cultivo integer NOT NULL,
    tipo character varying(100) NOT NULL,
    riego boolean NOT NULL,
    fecha_siembra date NOT NULL,
    id_terreno integer NOT NULL,
    id_agricultor integer NOT NULL,
    nombre character varying(100) NOT NULL
);


ALTER TABLE public.cultivos OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16480)
-- Name: cultivos_id_cultivo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cultivos_id_cultivo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cultivos_id_cultivo_seq OWNER TO postgres;

--
-- TOC entry 4962 (class 0 OID 0)
-- Dependencies: 221
-- Name: cultivos_id_cultivo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cultivos_id_cultivo_seq OWNED BY public.cultivos.id_cultivo;


--
-- TOC entry 217 (class 1259 OID 16409)
-- Name: login; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.login (
    usuario character varying NOT NULL,
    contrasena character varying NOT NULL
);


ALTER TABLE public.login OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16499)
-- Name: predicciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.predicciones (
    id_prediccion integer NOT NULL,
    rendimiento_hectarea numeric NOT NULL,
    rendimiento_total numeric NOT NULL,
    uso_fertilizante boolean NOT NULL,
    fecha timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id_cultivo integer NOT NULL,
    id_agricultor integer NOT NULL,
    rendimiento_real numeric(10,2)
);


ALTER TABLE public.predicciones OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16498)
-- Name: predicciones_id_prediccion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.predicciones_id_prediccion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.predicciones_id_prediccion_seq OWNER TO postgres;

--
-- TOC entry 4963 (class 0 OID 0)
-- Dependencies: 223
-- Name: predicciones_id_prediccion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.predicciones_id_prediccion_seq OWNED BY public.predicciones.id_prediccion;


--
-- TOC entry 220 (class 1259 OID 16466)
-- Name: terrenos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.terrenos (
    id_terreno integer NOT NULL,
    nombre character varying(255) NOT NULL,
    extension numeric NOT NULL,
    suelo character varying(100) NOT NULL,
    estado character varying(100) NOT NULL,
    municipio character varying(100) NOT NULL,
    id_agricultor integer NOT NULL,
    precipitacion numeric NOT NULL,
    temperatura numeric NOT NULL,
    CONSTRAINT terrenos_temperatura_check CHECK (((temperatura >= ('-50'::integer)::numeric) AND (temperatura <= (60)::numeric)))
);


ALTER TABLE public.terrenos OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16465)
-- Name: terreno_id_terreno_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.terreno_id_terreno_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.terreno_id_terreno_seq OWNER TO postgres;

--
-- TOC entry 4964 (class 0 OID 0)
-- Dependencies: 219
-- Name: terreno_id_terreno_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.terreno_id_terreno_seq OWNED BY public.terrenos.id_terreno;


--
-- TOC entry 228 (class 1259 OID 16540)
-- Name: tipo_suelo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tipo_suelo (
    id_suelo integer NOT NULL,
    tipo character varying(255) NOT NULL
);


ALTER TABLE public.tipo_suelo OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16539)
-- Name: tipo_suelo_id_suelo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tipo_suelo_id_suelo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tipo_suelo_id_suelo_seq OWNER TO postgres;

--
-- TOC entry 4965 (class 0 OID 0)
-- Dependencies: 227
-- Name: tipo_suelo_id_suelo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tipo_suelo_id_suelo_seq OWNED BY public.tipo_suelo.id_suelo;


--
-- TOC entry 226 (class 1259 OID 16519)
-- Name: variedad_cultivo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.variedad_cultivo (
    id_variedad integer NOT NULL,
    tipo text NOT NULL,
    dias_cosecha integer NOT NULL
);


ALTER TABLE public.variedad_cultivo OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16518)
-- Name: variedad_cultivo_id_variedad_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.variedad_cultivo_id_variedad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.variedad_cultivo_id_variedad_seq OWNER TO postgres;

--
-- TOC entry 4966 (class 0 OID 0)
-- Dependencies: 225
-- Name: variedad_cultivo_id_variedad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.variedad_cultivo_id_variedad_seq OWNED BY public.variedad_cultivo.id_variedad;


--
-- TOC entry 4770 (class 2604 OID 16484)
-- Name: cultivos id_cultivo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cultivos ALTER COLUMN id_cultivo SET DEFAULT nextval('public.cultivos_id_cultivo_seq'::regclass);


--
-- TOC entry 4771 (class 2604 OID 16502)
-- Name: predicciones id_prediccion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.predicciones ALTER COLUMN id_prediccion SET DEFAULT nextval('public.predicciones_id_prediccion_seq'::regclass);


--
-- TOC entry 4769 (class 2604 OID 16469)
-- Name: terrenos id_terreno; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.terrenos ALTER COLUMN id_terreno SET DEFAULT nextval('public.terreno_id_terreno_seq'::regclass);


--
-- TOC entry 4774 (class 2604 OID 16543)
-- Name: tipo_suelo id_suelo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipo_suelo ALTER COLUMN id_suelo SET DEFAULT nextval('public.tipo_suelo_id_suelo_seq'::regclass);


--
-- TOC entry 4773 (class 2604 OID 16522)
-- Name: variedad_cultivo id_variedad; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.variedad_cultivo ALTER COLUMN id_variedad SET DEFAULT nextval('public.variedad_cultivo_id_variedad_seq'::regclass);


--
-- TOC entry 4943 (class 0 OID 16399)
-- Dependencies: 215
-- Data for Name: agricultor; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.agricultor (usuario, telefono, correo, contrasena, estado, municipio, "ID") FROM stdin;
GSS	12345	g@g	ADMIN	Durango	Guadalupe Victoria	1
GSS2	6120	1@1	ADMIN2	Durango	Guadalupe Victoria	3
\.


--
-- TOC entry 4944 (class 0 OID 16404)
-- Dependencies: 216
-- Data for Name: cosecha; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cosecha ("nombreCultivo", "FechaSiembra", "Ubicacion", "SuperficieSembrada") FROM stdin;
\.


--
-- TOC entry 4950 (class 0 OID 16481)
-- Dependencies: 222
-- Data for Name: cultivos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cultivos (id_cultivo, tipo, riego, fecha_siembra, id_terreno, id_agricultor, nombre) FROM stdin;
1	Ma¡z amarillo	t	2025-06-11	3	1	Cultivo 1
2	Ma¡z amarillo	f	2025-11-07	4	3	Cultivo 1
3	Frijol negro	t	2025-06-06	3	1	Cultivo 2
4	Ma¡z amarillo	f	2025-06-11	5	1	Cultivo 2
5	Frijol rojo	t	2025-05-12	6	1	Frijo 2
\.


--
-- TOC entry 4945 (class 0 OID 16409)
-- Dependencies: 217
-- Data for Name: login; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.login (usuario, contrasena) FROM stdin;
GSS	ADMIN
GSS2	ADMIN2
\.


--
-- TOC entry 4952 (class 0 OID 16499)
-- Dependencies: 224
-- Data for Name: predicciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.predicciones (id_prediccion, rendimiento_hectarea, rendimiento_total, uso_fertilizante, fecha, id_cultivo, id_agricultor, rendimiento_real) FROM stdin;
1	4.459859242222674	240.83239908002437	f	2025-05-11 18:06:35.052096	4	1	\N
2	2.023665634266782	48.567975222402765	f	2025-05-11 18:06:53.65473	1	1	46.00
3	4.409937242059644	101.4285565673718	t	2025-05-11 19:54:45.557126	5	1	\N
\.


--
-- TOC entry 4948 (class 0 OID 16466)
-- Dependencies: 220
-- Data for Name: terrenos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.terrenos (id_terreno, nombre, extension, suelo, estado, municipio, id_agricultor, precipitacion, temperatura) FROM stdin;
3	TERRENO 3	24	duro	Durango	Guadalupe Victoria	1	24	25.5
4	Terreno 1	12	Duro	Durango	Guadalupe Victoria	3	12	28.0
5	Terreno sur	54	Duro	Durango	Cuencame	1	512	26
6	Terreno norte	23	Limoso	Durango	Guadalupe Victoria	1	502	20
\.


--
-- TOC entry 4956 (class 0 OID 16540)
-- Dependencies: 228
-- Data for Name: tipo_suelo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tipo_suelo (id_suelo, tipo) FROM stdin;
1	Franco
2	Arcilloso
3	Arenoso
4	Limoso
5	Calc reo
\.


--
-- TOC entry 4954 (class 0 OID 16519)
-- Dependencies: 226
-- Data for Name: variedad_cultivo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.variedad_cultivo (id_variedad, tipo, dias_cosecha) FROM stdin;
1	Ma¡z amarillo	150
2	Ma¡z blanco	140
3	Frijol negro	120
4	Frijol rojo	110
5	Trigo	180
\.


--
-- TOC entry 4967 (class 0 OID 0)
-- Dependencies: 221
-- Name: cultivos_id_cultivo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cultivos_id_cultivo_seq', 5, true);


--
-- TOC entry 4968 (class 0 OID 0)
-- Dependencies: 218
-- Name: id_sequence; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.id_sequence', 3, true);


--
-- TOC entry 4969 (class 0 OID 0)
-- Dependencies: 223
-- Name: predicciones_id_prediccion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.predicciones_id_prediccion_seq', 3, true);


--
-- TOC entry 4970 (class 0 OID 0)
-- Dependencies: 219
-- Name: terreno_id_terreno_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.terreno_id_terreno_seq', 6, true);


--
-- TOC entry 4971 (class 0 OID 0)
-- Dependencies: 227
-- Name: tipo_suelo_id_suelo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tipo_suelo_id_suelo_seq', 5, true);


--
-- TOC entry 4972 (class 0 OID 0)
-- Dependencies: 225
-- Name: variedad_cultivo_id_variedad_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.variedad_cultivo_id_variedad_seq', 5, true);


--
-- TOC entry 4781 (class 2606 OID 16420)
-- Name: login BASE_LOGIN_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.login
    ADD CONSTRAINT "BASE_LOGIN_pkey" PRIMARY KEY (usuario);


--
-- TOC entry 4779 (class 2606 OID 16422)
-- Name: cosecha COSECHA_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cosecha
    ADD CONSTRAINT "COSECHA_pkey" PRIMARY KEY ("nombreCultivo");


--
-- TOC entry 4777 (class 2606 OID 16441)
-- Name: agricultor agricultor_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agricultor
    ADD CONSTRAINT agricultor_pkey PRIMARY KEY ("ID");


--
-- TOC entry 4785 (class 2606 OID 16486)
-- Name: cultivos cultivos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cultivos
    ADD CONSTRAINT cultivos_pkey PRIMARY KEY (id_cultivo);


--
-- TOC entry 4787 (class 2606 OID 16507)
-- Name: predicciones predicciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.predicciones
    ADD CONSTRAINT predicciones_pkey PRIMARY KEY (id_prediccion);


--
-- TOC entry 4783 (class 2606 OID 16473)
-- Name: terrenos terreno_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.terrenos
    ADD CONSTRAINT terreno_pkey PRIMARY KEY (id_terreno);


--
-- TOC entry 4793 (class 2606 OID 16545)
-- Name: tipo_suelo tipo_suelo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipo_suelo
    ADD CONSTRAINT tipo_suelo_pkey PRIMARY KEY (id_suelo);


--
-- TOC entry 4789 (class 2606 OID 16526)
-- Name: variedad_cultivo variedad_cultivo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.variedad_cultivo
    ADD CONSTRAINT variedad_cultivo_pkey PRIMARY KEY (id_variedad);


--
-- TOC entry 4791 (class 2606 OID 16528)
-- Name: variedad_cultivo variedad_cultivo_tipo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.variedad_cultivo
    ADD CONSTRAINT variedad_cultivo_tipo_key UNIQUE (tipo);


--
-- TOC entry 4794 (class 2606 OID 16474)
-- Name: terrenos fk_agricultor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.terrenos
    ADD CONSTRAINT fk_agricultor FOREIGN KEY (id_agricultor) REFERENCES public.agricultor("ID") ON DELETE CASCADE;


--
-- TOC entry 4795 (class 2606 OID 16492)
-- Name: cultivos fk_agricultor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cultivos
    ADD CONSTRAINT fk_agricultor FOREIGN KEY (id_agricultor) REFERENCES public.agricultor("ID") ON DELETE CASCADE;


--
-- TOC entry 4798 (class 2606 OID 16513)
-- Name: predicciones fk_agricultor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.predicciones
    ADD CONSTRAINT fk_agricultor FOREIGN KEY (id_agricultor) REFERENCES public.agricultor("ID") ON DELETE CASCADE;


--
-- TOC entry 4799 (class 2606 OID 16508)
-- Name: predicciones fk_cultivo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.predicciones
    ADD CONSTRAINT fk_cultivo FOREIGN KEY (id_cultivo) REFERENCES public.cultivos(id_cultivo) ON DELETE CASCADE;


--
-- TOC entry 4796 (class 2606 OID 16487)
-- Name: cultivos fk_terreno; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cultivos
    ADD CONSTRAINT fk_terreno FOREIGN KEY (id_terreno) REFERENCES public.terrenos(id_terreno) ON DELETE CASCADE;


--
-- TOC entry 4797 (class 2606 OID 16534)
-- Name: cultivos fk_tipo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cultivos
    ADD CONSTRAINT fk_tipo FOREIGN KEY (tipo) REFERENCES public.variedad_cultivo(tipo) ON DELETE CASCADE;


-- Completed on 2025-05-11 20:00:11

--
-- PostgreSQL database dump complete
--

