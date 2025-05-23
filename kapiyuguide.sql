PGDMP  )                    }            kapiyuguide    17.2    17.2 �    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false            �           1262    172341    kapiyuguide    DATABASE     �   CREATE DATABASE kapiyuguide WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_United States.1252';
    DROP DATABASE kapiyuguide;
                     postgres    false            �            1259    229797    announcement_images    TABLE       CREATE TABLE public.announcement_images (
    id integer NOT NULL,
    announcement_id integer NOT NULL,
    image_path character varying(255) NOT NULL,
    caption character varying(255),
    display_order integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT now()
);
 '   DROP TABLE public.announcement_images;
       public         heap r       postgres    false            �           0    0    TABLE announcement_images    COMMENT     ^   COMMENT ON TABLE public.announcement_images IS 'Stores images associated with announcements';
          public               postgres    false    244            �            1259    229796    announcement_images_id_seq    SEQUENCE     �   CREATE SEQUENCE public.announcement_images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.announcement_images_id_seq;
       public               postgres    false    244            �           0    0    announcement_images_id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public.announcement_images_id_seq OWNED BY public.announcement_images.id;
          public               postgres    false    243            �            1259    172484    announcements    TABLE       CREATE TABLE public.announcements (
    id integer NOT NULL,
    author_id integer,
    title text NOT NULL,
    content text NOT NULL,
    target_office_id integer,
    is_public boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
 !   DROP TABLE public.announcements;
       public         heap r       postgres    false            �            1259    172483    announcements_id_seq    SEQUENCE     �   CREATE SEQUENCE public.announcements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.announcements_id_seq;
       public               postgres    false    234            �           0    0    announcements_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.announcements_id_seq OWNED BY public.announcements.id;
          public               postgres    false    233            �            1259    180608 
   audit_logs    TABLE     1  CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    actor_id integer,
    actor_role character varying(20),
    action character varying(100) NOT NULL,
    target_type character varying(50),
    inquiry_id integer,
    office_id integer,
    status_snapshot character varying(50),
    is_success boolean DEFAULT true,
    failure_reason character varying(255),
    ip_address character varying(45),
    user_agent character varying(255),
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    retention_days integer DEFAULT 365
);
    DROP TABLE public.audit_logs;
       public         heap r       postgres    false            �            1259    180607    audit_logs_id_seq    SEQUENCE     �   CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.audit_logs_id_seq;
       public               postgres    false    242            �           0    0    audit_logs_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;
          public               postgres    false    241            �            1259    172458    counseling_sessions    TABLE     �  CREATE TABLE public.counseling_sessions (
    id integer NOT NULL,
    student_id integer,
    office_id integer,
    counselor_id integer,
    scheduled_at timestamp without time zone NOT NULL,
    status text DEFAULT 'pending'::text,
    notes text,
    CONSTRAINT counseling_sessions_status_check CHECK ((status = ANY (ARRAY['pending'::text, 'approved'::text, 'completed'::text, 'cancelled'::text])))
);
 '   DROP TABLE public.counseling_sessions;
       public         heap r       postgres    false            �            1259    172457    counseling_sessions_id_seq    SEQUENCE     �   CREATE SEQUENCE public.counseling_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.counseling_sessions_id_seq;
       public               postgres    false    232            �           0    0    counseling_sessions_id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public.counseling_sessions_id_seq OWNED BY public.counseling_sessions.id;
          public               postgres    false    231            �            1259    172398 	   inquiries    TABLE     |  CREATE TABLE public.inquiries (
    id integer NOT NULL,
    student_id integer,
    office_id integer,
    subject text NOT NULL,
    status text DEFAULT 'open'::text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT inquiries_status_check CHECK ((status = ANY (ARRAY['open'::text, 'in_progress'::text, 'resolved'::text, 'closed'::text])))
);
    DROP TABLE public.inquiries;
       public         heap r       postgres    false            �            1259    172397    inquiries_id_seq    SEQUENCE     �   CREATE SEQUENCE public.inquiries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 '   DROP SEQUENCE public.inquiries_id_seq;
       public               postgres    false    226            �           0    0    inquiries_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE public.inquiries_id_seq OWNED BY public.inquiries.id;
          public               postgres    false    225            �            1259    172420    inquiry_messages    TABLE     �  CREATE TABLE public.inquiry_messages (
    id integer NOT NULL,
    inquiry_id integer,
    sender_id integer,
    content text NOT NULL,
    status text DEFAULT 'sent'::text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    delivered_at timestamp without time zone,
    read_at timestamp without time zone,
    CONSTRAINT inquiry_messages_status_check CHECK ((status = ANY (ARRAY['sent'::text, 'delivered'::text, 'read'::text])))
);
 $   DROP TABLE public.inquiry_messages;
       public         heap r       postgres    false            �            1259    172419    inquiry_messages_id_seq    SEQUENCE     �   CREATE SEQUENCE public.inquiry_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.inquiry_messages_id_seq;
       public               postgres    false    228            �           0    0    inquiry_messages_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.inquiry_messages_id_seq OWNED BY public.inquiry_messages.id;
          public               postgres    false    227            �            1259    172442    notifications    TABLE     �   CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id integer,
    title text NOT NULL,
    message text NOT NULL,
    is_read boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
 !   DROP TABLE public.notifications;
       public         heap r       postgres    false            �            1259    172441    notifications_id_seq    SEQUENCE     �   CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.notifications_id_seq;
       public               postgres    false    230            �           0    0    notifications_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;
          public               postgres    false    229            �            1259    172367    office_admins    TABLE     k   CREATE TABLE public.office_admins (
    id integer NOT NULL,
    user_id integer,
    office_id integer
);
 !   DROP TABLE public.office_admins;
       public         heap r       postgres    false            �            1259    172366    office_admins_id_seq    SEQUENCE     �   CREATE SEQUENCE public.office_admins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.office_admins_id_seq;
       public               postgres    false    222            �           0    0    office_admins_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.office_admins_id_seq OWNED BY public.office_admins.id;
          public               postgres    false    221            �            1259    180556    office_login_logs    TABLE     �  CREATE TABLE public.office_login_logs (
    id integer NOT NULL,
    office_admin_id integer,
    login_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    logout_time timestamp without time zone,
    ip_address character varying(45),
    user_agent character varying(255),
    session_duration integer,
    is_success boolean DEFAULT true,
    failure_reason character varying(255),
    retention_days integer DEFAULT 365
);
 %   DROP TABLE public.office_login_logs;
       public         heap r       postgres    false            �            1259    180555    office_login_logs_id_seq    SEQUENCE     �   CREATE SEQUENCE public.office_login_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.office_login_logs_id_seq;
       public               postgres    false    238            �           0    0    office_login_logs_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.office_login_logs_id_seq OWNED BY public.office_login_logs.id;
          public               postgres    false    237            �            1259    172357    offices    TABLE     �   CREATE TABLE public.offices (
    id integer NOT NULL,
    name text NOT NULL,
    description text,
    supports_video boolean DEFAULT false
);
    DROP TABLE public.offices;
       public         heap r       postgres    false            �            1259    172356    offices_id_seq    SEQUENCE     �   CREATE SEQUENCE public.offices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 %   DROP SEQUENCE public.offices_id_seq;
       public               postgres    false    220            �           0    0    offices_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public.offices_id_seq OWNED BY public.offices.id;
          public               postgres    false    219            �            1259    180534    student_activity_logs    TABLE     �  CREATE TABLE public.student_activity_logs (
    id integer NOT NULL,
    student_id integer,
    action character varying(100) NOT NULL,
    related_id integer,
    related_type character varying(50),
    is_success boolean DEFAULT true,
    failure_reason character varying(255),
    ip_address character varying(45),
    user_agent character varying(255),
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    retention_days integer DEFAULT 365
);
 )   DROP TABLE public.student_activity_logs;
       public         heap r       postgres    false            �            1259    180533    student_activity_logs_id_seq    SEQUENCE     �   CREATE SEQUENCE public.student_activity_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.student_activity_logs_id_seq;
       public               postgres    false    236            �           0    0    student_activity_logs_id_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public.student_activity_logs_id_seq OWNED BY public.student_activity_logs.id;
          public               postgres    false    235            �            1259    172384    students    TABLE     h   CREATE TABLE public.students (
    id integer NOT NULL,
    user_id integer,
    student_number text
);
    DROP TABLE public.students;
       public         heap r       postgres    false            �            1259    172383    students_id_seq    SEQUENCE     �   CREATE SEQUENCE public.students_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public.students_id_seq;
       public               postgres    false    224            �           0    0    students_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public.students_id_seq OWNED BY public.students.id;
          public               postgres    false    223            �            1259    180575    super_admin_activity_logs    TABLE       CREATE TABLE public.super_admin_activity_logs (
    id integer NOT NULL,
    super_admin_id integer,
    action character varying(100) NOT NULL,
    target_type character varying(50),
    target_user_id integer,
    target_office_id integer,
    details text,
    is_success boolean DEFAULT true,
    failure_reason character varying(255),
    ip_address character varying(45),
    user_agent character varying(255),
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    retention_days integer DEFAULT 730
);
 -   DROP TABLE public.super_admin_activity_logs;
       public         heap r       postgres    false            �            1259    180574     super_admin_activity_logs_id_seq    SEQUENCE     �   CREATE SEQUENCE public.super_admin_activity_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public.super_admin_activity_logs_id_seq;
       public               postgres    false    240            �           0    0     super_admin_activity_logs_id_seq    SEQUENCE OWNED BY     e   ALTER SEQUENCE public.super_admin_activity_logs_id_seq OWNED BY public.super_admin_activity_logs.id;
          public               postgres    false    239            �            1259    172343    users    TABLE     �  CREATE TABLE public.users (
    id integer NOT NULL,
    email text NOT NULL,
    password_hash text NOT NULL,
    role text NOT NULL,
    profile_pic text,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    first_name character varying(50),
    middle_name character varying(50),
    last_name character varying(50),
    CONSTRAINT users_role_check CHECK ((role = ANY (ARRAY['student'::text, 'office_admin'::text, 'super_admin'::text])))
);
    DROP TABLE public.users;
       public         heap r       postgres    false            �            1259    172342    users_id_seq    SEQUENCE     �   CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.users_id_seq;
       public               postgres    false    218            �           0    0    users_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
          public               postgres    false    217            �           2604    229800    announcement_images id    DEFAULT     �   ALTER TABLE ONLY public.announcement_images ALTER COLUMN id SET DEFAULT nextval('public.announcement_images_id_seq'::regclass);
 E   ALTER TABLE public.announcement_images ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    243    244    244            t           2604    172487    announcements id    DEFAULT     t   ALTER TABLE ONLY public.announcements ALTER COLUMN id SET DEFAULT nextval('public.announcements_id_seq'::regclass);
 ?   ALTER TABLE public.announcements ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    233    234    234            �           2604    180611    audit_logs id    DEFAULT     n   ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);
 <   ALTER TABLE public.audit_logs ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    242    241    242            r           2604    172461    counseling_sessions id    DEFAULT     �   ALTER TABLE ONLY public.counseling_sessions ALTER COLUMN id SET DEFAULT nextval('public.counseling_sessions_id_seq'::regclass);
 E   ALTER TABLE public.counseling_sessions ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    232    231    232            i           2604    172401    inquiries id    DEFAULT     l   ALTER TABLE ONLY public.inquiries ALTER COLUMN id SET DEFAULT nextval('public.inquiries_id_seq'::regclass);
 ;   ALTER TABLE public.inquiries ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    225    226    226            l           2604    172423    inquiry_messages id    DEFAULT     z   ALTER TABLE ONLY public.inquiry_messages ALTER COLUMN id SET DEFAULT nextval('public.inquiry_messages_id_seq'::regclass);
 B   ALTER TABLE public.inquiry_messages ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    227    228    228            o           2604    172445    notifications id    DEFAULT     t   ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);
 ?   ALTER TABLE public.notifications ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    230    229    230            g           2604    172370    office_admins id    DEFAULT     t   ALTER TABLE ONLY public.office_admins ALTER COLUMN id SET DEFAULT nextval('public.office_admins_id_seq'::regclass);
 ?   ALTER TABLE public.office_admins ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    221    222    222            {           2604    180559    office_login_logs id    DEFAULT     |   ALTER TABLE ONLY public.office_login_logs ALTER COLUMN id SET DEFAULT nextval('public.office_login_logs_id_seq'::regclass);
 C   ALTER TABLE public.office_login_logs ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    237    238    238            e           2604    172360 
   offices id    DEFAULT     h   ALTER TABLE ONLY public.offices ALTER COLUMN id SET DEFAULT nextval('public.offices_id_seq'::regclass);
 9   ALTER TABLE public.offices ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    219    220    220            w           2604    180537    student_activity_logs id    DEFAULT     �   ALTER TABLE ONLY public.student_activity_logs ALTER COLUMN id SET DEFAULT nextval('public.student_activity_logs_id_seq'::regclass);
 G   ALTER TABLE public.student_activity_logs ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    236    235    236            h           2604    172387    students id    DEFAULT     j   ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);
 :   ALTER TABLE public.students ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    224    223    224                       2604    180578    super_admin_activity_logs id    DEFAULT     �   ALTER TABLE ONLY public.super_admin_activity_logs ALTER COLUMN id SET DEFAULT nextval('public.super_admin_activity_logs_id_seq'::regclass);
 K   ALTER TABLE public.super_admin_activity_logs ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    239    240    240            b           2604    172346    users id    DEFAULT     d   ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
 7   ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    217    218    218            �          0    229797    announcement_images 
   TABLE DATA           r   COPY public.announcement_images (id, announcement_id, image_path, caption, display_order, created_at) FROM stdin;
    public               postgres    false    244   �       y          0    172484    announcements 
   TABLE DATA           o   COPY public.announcements (id, author_id, title, content, target_office_id, is_public, created_at) FROM stdin;
    public               postgres    false    234   ��       �          0    180608 
   audit_logs 
   TABLE DATA           �   COPY public.audit_logs (id, actor_id, actor_role, action, target_type, inquiry_id, office_id, status_snapshot, is_success, failure_reason, ip_address, user_agent, "timestamp", retention_days) FROM stdin;
    public               postgres    false    242   ��       w          0    172458    counseling_sessions 
   TABLE DATA           s   COPY public.counseling_sessions (id, student_id, office_id, counselor_id, scheduled_at, status, notes) FROM stdin;
    public               postgres    false    232   ��       q          0    172398 	   inquiries 
   TABLE DATA           [   COPY public.inquiries (id, student_id, office_id, subject, status, created_at) FROM stdin;
    public               postgres    false    226   ��       s          0    172420    inquiry_messages 
   TABLE DATA           y   COPY public.inquiry_messages (id, inquiry_id, sender_id, content, status, created_at, delivered_at, read_at) FROM stdin;
    public               postgres    false    228   ��       u          0    172442    notifications 
   TABLE DATA           Y   COPY public.notifications (id, user_id, title, message, is_read, created_at) FROM stdin;
    public               postgres    false    230   �       m          0    172367    office_admins 
   TABLE DATA           ?   COPY public.office_admins (id, user_id, office_id) FROM stdin;
    public               postgres    false    222   #�       }          0    180556    office_login_logs 
   TABLE DATA           �   COPY public.office_login_logs (id, office_admin_id, login_time, logout_time, ip_address, user_agent, session_duration, is_success, failure_reason, retention_days) FROM stdin;
    public               postgres    false    238   p�       k          0    172357    offices 
   TABLE DATA           H   COPY public.offices (id, name, description, supports_video) FROM stdin;
    public               postgres    false    220   ��       {          0    180534    student_activity_logs 
   TABLE DATA           �   COPY public.student_activity_logs (id, student_id, action, related_id, related_type, is_success, failure_reason, ip_address, user_agent, "timestamp", retention_days) FROM stdin;
    public               postgres    false    236   H�       o          0    172384    students 
   TABLE DATA           ?   COPY public.students (id, user_id, student_number) FROM stdin;
    public               postgres    false    224   e�                 0    180575    super_admin_activity_logs 
   TABLE DATA           �   COPY public.super_admin_activity_logs (id, super_admin_id, action, target_type, target_user_id, target_office_id, details, is_success, failure_reason, ip_address, user_agent, "timestamp", retention_days) FROM stdin;
    public               postgres    false    240   ��       i          0    172343    users 
   TABLE DATA           �   COPY public.users (id, email, password_hash, role, profile_pic, is_active, created_at, first_name, middle_name, last_name) FROM stdin;
    public               postgres    false    218   ��       �           0    0    announcement_images_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.announcement_images_id_seq', 6, true);
          public               postgres    false    243            �           0    0    announcements_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.announcements_id_seq', 1, true);
          public               postgres    false    233            �           0    0    audit_logs_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.audit_logs_id_seq', 37, true);
          public               postgres    false    241            �           0    0    counseling_sessions_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.counseling_sessions_id_seq', 1, false);
          public               postgres    false    231            �           0    0    inquiries_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.inquiries_id_seq', 1, false);
          public               postgres    false    225            �           0    0    inquiry_messages_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.inquiry_messages_id_seq', 1, false);
          public               postgres    false    227            �           0    0    notifications_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.notifications_id_seq', 1, false);
          public               postgres    false    229            �           0    0    office_admins_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.office_admins_id_seq', 12, true);
          public               postgres    false    221            �           0    0    office_login_logs_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.office_login_logs_id_seq', 1, false);
          public               postgres    false    237            �           0    0    offices_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.offices_id_seq', 10, true);
          public               postgres    false    219            �           0    0    student_activity_logs_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.student_activity_logs_id_seq', 1, false);
          public               postgres    false    235            �           0    0    students_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.students_id_seq', 3, true);
          public               postgres    false    223            �           0    0     super_admin_activity_logs_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.super_admin_activity_logs_id_seq', 1, false);
          public               postgres    false    239            �           0    0    users_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.users_id_seq', 33, true);
          public               postgres    false    217            �           2606    229806 ,   announcement_images announcement_images_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.announcement_images
    ADD CONSTRAINT announcement_images_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.announcement_images DROP CONSTRAINT announcement_images_pkey;
       public                 postgres    false    244            �           2606    172493     announcements announcements_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.announcements
    ADD CONSTRAINT announcements_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.announcements DROP CONSTRAINT announcements_pkey;
       public                 postgres    false    234            �           2606    180618    audit_logs audit_logs_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.audit_logs DROP CONSTRAINT audit_logs_pkey;
       public                 postgres    false    242            �           2606    172467 ,   counseling_sessions counseling_sessions_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.counseling_sessions
    ADD CONSTRAINT counseling_sessions_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.counseling_sessions DROP CONSTRAINT counseling_sessions_pkey;
       public                 postgres    false    232            �           2606    172408    inquiries inquiries_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.inquiries
    ADD CONSTRAINT inquiries_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.inquiries DROP CONSTRAINT inquiries_pkey;
       public                 postgres    false    226            �           2606    172430 &   inquiry_messages inquiry_messages_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.inquiry_messages
    ADD CONSTRAINT inquiry_messages_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.inquiry_messages DROP CONSTRAINT inquiry_messages_pkey;
       public                 postgres    false    228            �           2606    172451     notifications notifications_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.notifications DROP CONSTRAINT notifications_pkey;
       public                 postgres    false    230            �           2606    172372     office_admins office_admins_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.office_admins
    ADD CONSTRAINT office_admins_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.office_admins DROP CONSTRAINT office_admins_pkey;
       public                 postgres    false    222            �           2606    180566 (   office_login_logs office_login_logs_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.office_login_logs
    ADD CONSTRAINT office_login_logs_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.office_login_logs DROP CONSTRAINT office_login_logs_pkey;
       public                 postgres    false    238            �           2606    172365    offices offices_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.offices
    ADD CONSTRAINT offices_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.offices DROP CONSTRAINT offices_pkey;
       public                 postgres    false    220            �           2606    180544 0   student_activity_logs student_activity_logs_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.student_activity_logs
    ADD CONSTRAINT student_activity_logs_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.student_activity_logs DROP CONSTRAINT student_activity_logs_pkey;
       public                 postgres    false    236            �           2606    172391    students students_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.students DROP CONSTRAINT students_pkey;
       public                 postgres    false    224            �           2606    180585 8   super_admin_activity_logs super_admin_activity_logs_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.super_admin_activity_logs
    ADD CONSTRAINT super_admin_activity_logs_pkey PRIMARY KEY (id);
 b   ALTER TABLE ONLY public.super_admin_activity_logs DROP CONSTRAINT super_admin_activity_logs_pkey;
       public                 postgres    false    240            �           2606    172355    users users_email_key 
   CONSTRAINT     Q   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);
 ?   ALTER TABLE ONLY public.users DROP CONSTRAINT users_email_key;
       public                 postgres    false    218            �           2606    172353    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public                 postgres    false    218            �           1259    229812 '   idx_announcement_images_announcement_id    INDEX     r   CREATE INDEX idx_announcement_images_announcement_id ON public.announcement_images USING btree (announcement_id);
 ;   DROP INDEX public.idx_announcement_images_announcement_id;
       public                 postgres    false    244            �           1259    180636    idx_audit_logs_action    INDEX     N   CREATE INDEX idx_audit_logs_action ON public.audit_logs USING btree (action);
 )   DROP INDEX public.idx_audit_logs_action;
       public                 postgres    false    242            �           1259    180634    idx_audit_logs_actor_id    INDEX     R   CREATE INDEX idx_audit_logs_actor_id ON public.audit_logs USING btree (actor_id);
 +   DROP INDEX public.idx_audit_logs_actor_id;
       public                 postgres    false    242            �           1259    180635    idx_audit_logs_actor_role    INDEX     V   CREATE INDEX idx_audit_logs_actor_role ON public.audit_logs USING btree (actor_role);
 -   DROP INDEX public.idx_audit_logs_actor_role;
       public                 postgres    false    242            �           1259    180638    idx_audit_logs_inquiry_id    INDEX     V   CREATE INDEX idx_audit_logs_inquiry_id ON public.audit_logs USING btree (inquiry_id);
 -   DROP INDEX public.idx_audit_logs_inquiry_id;
       public                 postgres    false    242            �           1259    180639    idx_audit_logs_office_id    INDEX     T   CREATE INDEX idx_audit_logs_office_id ON public.audit_logs USING btree (office_id);
 ,   DROP INDEX public.idx_audit_logs_office_id;
       public                 postgres    false    242            �           1259    180637    idx_audit_logs_target_type    INDEX     X   CREATE INDEX idx_audit_logs_target_type ON public.audit_logs USING btree (target_type);
 .   DROP INDEX public.idx_audit_logs_target_type;
       public                 postgres    false    242            �           1259    180640    idx_audit_logs_timestamp    INDEX     V   CREATE INDEX idx_audit_logs_timestamp ON public.audit_logs USING btree ("timestamp");
 ,   DROP INDEX public.idx_audit_logs_timestamp;
       public                 postgres    false    242            �           1259    180573     office_login_logs_login_time_idx    INDEX     d   CREATE INDEX office_login_logs_login_time_idx ON public.office_login_logs USING btree (login_time);
 4   DROP INDEX public.office_login_logs_login_time_idx;
       public                 postgres    false    238            �           1259    180572 %   office_login_logs_office_admin_id_idx    INDEX     n   CREATE INDEX office_login_logs_office_admin_id_idx ON public.office_login_logs USING btree (office_admin_id);
 9   DROP INDEX public.office_login_logs_office_admin_id_idx;
       public                 postgres    false    238            �           1259    180551     student_activity_logs_action_idx    INDEX     d   CREATE INDEX student_activity_logs_action_idx ON public.student_activity_logs USING btree (action);
 4   DROP INDEX public.student_activity_logs_action_idx;
       public                 postgres    false    236            �           1259    180552 $   student_activity_logs_related_id_idx    INDEX     l   CREATE INDEX student_activity_logs_related_id_idx ON public.student_activity_logs USING btree (related_id);
 8   DROP INDEX public.student_activity_logs_related_id_idx;
       public                 postgres    false    236            �           1259    180553 &   student_activity_logs_related_type_idx    INDEX     p   CREATE INDEX student_activity_logs_related_type_idx ON public.student_activity_logs USING btree (related_type);
 :   DROP INDEX public.student_activity_logs_related_type_idx;
       public                 postgres    false    236            �           1259    180550 $   student_activity_logs_student_id_idx    INDEX     l   CREATE INDEX student_activity_logs_student_id_idx ON public.student_activity_logs USING btree (student_id);
 8   DROP INDEX public.student_activity_logs_student_id_idx;
       public                 postgres    false    236            �           1259    180554 #   student_activity_logs_timestamp_idx    INDEX     l   CREATE INDEX student_activity_logs_timestamp_idx ON public.student_activity_logs USING btree ("timestamp");
 7   DROP INDEX public.student_activity_logs_timestamp_idx;
       public                 postgres    false    236            �           1259    180602 $   super_admin_activity_logs_action_idx    INDEX     l   CREATE INDEX super_admin_activity_logs_action_idx ON public.super_admin_activity_logs USING btree (action);
 8   DROP INDEX public.super_admin_activity_logs_action_idx;
       public                 postgres    false    240            �           1259    180601 ,   super_admin_activity_logs_super_admin_id_idx    INDEX     |   CREATE INDEX super_admin_activity_logs_super_admin_id_idx ON public.super_admin_activity_logs USING btree (super_admin_id);
 @   DROP INDEX public.super_admin_activity_logs_super_admin_id_idx;
       public                 postgres    false    240            �           1259    180605 .   super_admin_activity_logs_target_office_id_idx    INDEX     �   CREATE INDEX super_admin_activity_logs_target_office_id_idx ON public.super_admin_activity_logs USING btree (target_office_id);
 B   DROP INDEX public.super_admin_activity_logs_target_office_id_idx;
       public                 postgres    false    240            �           1259    180603 )   super_admin_activity_logs_target_type_idx    INDEX     v   CREATE INDEX super_admin_activity_logs_target_type_idx ON public.super_admin_activity_logs USING btree (target_type);
 =   DROP INDEX public.super_admin_activity_logs_target_type_idx;
       public                 postgres    false    240            �           1259    180604 ,   super_admin_activity_logs_target_user_id_idx    INDEX     |   CREATE INDEX super_admin_activity_logs_target_user_id_idx ON public.super_admin_activity_logs USING btree (target_user_id);
 @   DROP INDEX public.super_admin_activity_logs_target_user_id_idx;
       public                 postgres    false    240            �           1259    180606 '   super_admin_activity_logs_timestamp_idx    INDEX     t   CREATE INDEX super_admin_activity_logs_timestamp_idx ON public.super_admin_activity_logs USING btree ("timestamp");
 ;   DROP INDEX public.super_admin_activity_logs_timestamp_idx;
       public                 postgres    false    240            �           2606    229807 <   announcement_images announcement_images_announcement_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.announcement_images
    ADD CONSTRAINT announcement_images_announcement_id_fkey FOREIGN KEY (announcement_id) REFERENCES public.announcements(id) ON DELETE CASCADE;
 f   ALTER TABLE ONLY public.announcement_images DROP CONSTRAINT announcement_images_announcement_id_fkey;
       public               postgres    false    244    234    4769            �           2606    172494 *   announcements announcements_author_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.announcements
    ADD CONSTRAINT announcements_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE CASCADE;
 T   ALTER TABLE ONLY public.announcements DROP CONSTRAINT announcements_author_id_fkey;
       public               postgres    false    4753    218    234            �           2606    172499 1   announcements announcements_target_office_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.announcements
    ADD CONSTRAINT announcements_target_office_id_fkey FOREIGN KEY (target_office_id) REFERENCES public.offices(id);
 [   ALTER TABLE ONLY public.announcements DROP CONSTRAINT announcements_target_office_id_fkey;
       public               postgres    false    234    220    4755            �           2606    180619 #   audit_logs audit_logs_actor_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES public.users(id) ON DELETE SET NULL;
 M   ALTER TABLE ONLY public.audit_logs DROP CONSTRAINT audit_logs_actor_id_fkey;
       public               postgres    false    242    4753    218            �           2606    180624 %   audit_logs audit_logs_inquiry_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_inquiry_id_fkey FOREIGN KEY (inquiry_id) REFERENCES public.inquiries(id) ON DELETE SET NULL;
 O   ALTER TABLE ONLY public.audit_logs DROP CONSTRAINT audit_logs_inquiry_id_fkey;
       public               postgres    false    242    226    4761            �           2606    180629 $   audit_logs audit_logs_office_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_office_id_fkey FOREIGN KEY (office_id) REFERENCES public.offices(id) ON DELETE SET NULL;
 N   ALTER TABLE ONLY public.audit_logs DROP CONSTRAINT audit_logs_office_id_fkey;
       public               postgres    false    220    242    4755            �           2606    172478 9   counseling_sessions counseling_sessions_counselor_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.counseling_sessions
    ADD CONSTRAINT counseling_sessions_counselor_id_fkey FOREIGN KEY (counselor_id) REFERENCES public.users(id) ON DELETE CASCADE;
 c   ALTER TABLE ONLY public.counseling_sessions DROP CONSTRAINT counseling_sessions_counselor_id_fkey;
       public               postgres    false    218    232    4753            �           2606    172473 6   counseling_sessions counseling_sessions_office_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.counseling_sessions
    ADD CONSTRAINT counseling_sessions_office_id_fkey FOREIGN KEY (office_id) REFERENCES public.offices(id) ON DELETE CASCADE;
 `   ALTER TABLE ONLY public.counseling_sessions DROP CONSTRAINT counseling_sessions_office_id_fkey;
       public               postgres    false    4755    232    220            �           2606    172468 7   counseling_sessions counseling_sessions_student_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.counseling_sessions
    ADD CONSTRAINT counseling_sessions_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;
 a   ALTER TABLE ONLY public.counseling_sessions DROP CONSTRAINT counseling_sessions_student_id_fkey;
       public               postgres    false    232    4759    224            �           2606    172414 "   inquiries inquiries_office_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.inquiries
    ADD CONSTRAINT inquiries_office_id_fkey FOREIGN KEY (office_id) REFERENCES public.offices(id) ON DELETE CASCADE;
 L   ALTER TABLE ONLY public.inquiries DROP CONSTRAINT inquiries_office_id_fkey;
       public               postgres    false    220    226    4755            �           2606    172409 #   inquiries inquiries_student_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.inquiries
    ADD CONSTRAINT inquiries_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;
 M   ALTER TABLE ONLY public.inquiries DROP CONSTRAINT inquiries_student_id_fkey;
       public               postgres    false    224    226    4759            �           2606    172431 1   inquiry_messages inquiry_messages_inquiry_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.inquiry_messages
    ADD CONSTRAINT inquiry_messages_inquiry_id_fkey FOREIGN KEY (inquiry_id) REFERENCES public.inquiries(id) ON DELETE CASCADE;
 [   ALTER TABLE ONLY public.inquiry_messages DROP CONSTRAINT inquiry_messages_inquiry_id_fkey;
       public               postgres    false    228    4761    226            �           2606    172436 0   inquiry_messages inquiry_messages_sender_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.inquiry_messages
    ADD CONSTRAINT inquiry_messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id) ON DELETE CASCADE;
 Z   ALTER TABLE ONLY public.inquiry_messages DROP CONSTRAINT inquiry_messages_sender_id_fkey;
       public               postgres    false    228    218    4753            �           2606    172452 (   notifications notifications_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
 R   ALTER TABLE ONLY public.notifications DROP CONSTRAINT notifications_user_id_fkey;
       public               postgres    false    218    230    4753            �           2606    172378 *   office_admins office_admins_office_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.office_admins
    ADD CONSTRAINT office_admins_office_id_fkey FOREIGN KEY (office_id) REFERENCES public.offices(id) ON DELETE CASCADE;
 T   ALTER TABLE ONLY public.office_admins DROP CONSTRAINT office_admins_office_id_fkey;
       public               postgres    false    222    4755    220            �           2606    172373 (   office_admins office_admins_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.office_admins
    ADD CONSTRAINT office_admins_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
 R   ALTER TABLE ONLY public.office_admins DROP CONSTRAINT office_admins_user_id_fkey;
       public               postgres    false    4753    222    218            �           2606    180567 8   office_login_logs office_login_logs_office_admin_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.office_login_logs
    ADD CONSTRAINT office_login_logs_office_admin_id_fkey FOREIGN KEY (office_admin_id) REFERENCES public.office_admins(id) ON DELETE CASCADE;
 b   ALTER TABLE ONLY public.office_login_logs DROP CONSTRAINT office_login_logs_office_admin_id_fkey;
       public               postgres    false    4757    238    222            �           2606    180545 ;   student_activity_logs student_activity_logs_student_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.student_activity_logs
    ADD CONSTRAINT student_activity_logs_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;
 e   ALTER TABLE ONLY public.student_activity_logs DROP CONSTRAINT student_activity_logs_student_id_fkey;
       public               postgres    false    4759    224    236            �           2606    172392    students students_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
 H   ALTER TABLE ONLY public.students DROP CONSTRAINT students_user_id_fkey;
       public               postgres    false    218    224    4753            �           2606    180586 G   super_admin_activity_logs super_admin_activity_logs_super_admin_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.super_admin_activity_logs
    ADD CONSTRAINT super_admin_activity_logs_super_admin_id_fkey FOREIGN KEY (super_admin_id) REFERENCES public.users(id) ON DELETE SET NULL;
 q   ALTER TABLE ONLY public.super_admin_activity_logs DROP CONSTRAINT super_admin_activity_logs_super_admin_id_fkey;
       public               postgres    false    218    4753    240            �           2606    180596 I   super_admin_activity_logs super_admin_activity_logs_target_office_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.super_admin_activity_logs
    ADD CONSTRAINT super_admin_activity_logs_target_office_id_fkey FOREIGN KEY (target_office_id) REFERENCES public.offices(id) ON DELETE SET NULL;
 s   ALTER TABLE ONLY public.super_admin_activity_logs DROP CONSTRAINT super_admin_activity_logs_target_office_id_fkey;
       public               postgres    false    240    4755    220            �           2606    180591 G   super_admin_activity_logs super_admin_activity_logs_target_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.super_admin_activity_logs
    ADD CONSTRAINT super_admin_activity_logs_target_user_id_fkey FOREIGN KEY (target_user_id) REFERENCES public.users(id) ON DELETE SET NULL;
 q   ALTER TABLE ONLY public.super_admin_activity_logs DROP CONSTRAINT super_admin_activity_logs_target_user_id_fkey;
       public               postgres    false    240    4753    218            �   t   x��K�  �5����gi���IE������?'Fq��������y����A/��"��Iv	c�%GJ��k��nH����o��a�_��[�d�`��MZ+�wZ>����"T      y   R   x�3�4��H,(�Tp�,*�HI2J�2�K9�"y�
.�yy��1~�%�FF��&�F�
&VƖV�&z�F����\1z\\\       �   �  x������0���S�Vhf4I�R(Jo�-�8����l�>G�R��٥��|�53�����r}��~���c�|;?=u���k��s��];�}��=?��n�].͐�b�� /�"?X��~kc�����|C�7� �7@��7�|��K��bd����9b�����8>�5!���Y}	��� �FB�#(� (�kn� ±�kp4:�@�F�a9`�89%9I�A���:��ѐ[k�p�
j&@tPA3�p($�q"9֣���xR���t��0t/�3�:�;�C��՞������]��2�����'҄�H5O�w�?1^�Ĥ������k%}����u/�jڿ�X�5������ �z�S����m�$�ɡq���L���{�LIZ̔��I}iy�AhD�|,	�+��|b����X2B�C���p�uKjI��0D��坣�|�`���%�:Ǉ2O�wRO�����X�N�c1i��T{0N-b9�ˁ�U��#�#���#)���AiRp0V�6���$�CI���j�MMb!�غ�GF*�h�y�ї�D�$-?_�@�	Q����q�;%��&��Q��R%-?`�@�ƺ��9��;��3t�ACV��[c�� �O갡J��z�/)d��|���=�U��K�DcT��G��l~��=      w      x������ � �      q      x������ � �      s      x������ � �      u      x������ � �      m   =   x�ʹ�@��X*�s������aRi�CZ\�I^��n��}��`plQ�5�J��l��Q�|
      }      x������ � �      k   �  x�uRˎ�0<;_�`Ĳ,��2+�E��q�ۉ%��Π��m�y	�S.WWWՍ��7��ӹC�[ϙ���6 k0`��F�DV~D+��}�������\�fGwʣŘ��s�i�vB��)�gJo��g�'��aH�*7��d�����t��G��C���"B>Pש�Dh�v�2��x�J-A?)~�Go'�<�12ۅS��n�(��V�9-�p~�>��#2��Jx>�;Q�y��d�z�� }��4`�z��N=b�X-}��4���y��ۧ,�
�?#�BS�v���@Xf������-��J]��]W�{QfꟌ��)���Q~��UG�(p�Ԓ� �"�f��wsF:̺�G�k�=��4���	�)�K�bɇ��HK��2�FH2`"�y=�,}�L�����V�1u!w���5�MӼ �)2`      {      x������ � �      o      x�3�4���2�42�Ɯ�� :F��� D�            x������ � �      i   6  x��W�rG|~�*���'��J�.S�WG(b������� H��z'���z2b�����1Ùnd�no/���-f�i]-�m�\�w�51�1�<���lN�!o�t�?��Bl���{�d��%��BHԫ�&U|�&����|�FS7�x՞�rNE���]Ӑk�ZDzR!C�p�F�h)�F�ss94eoj+u�9�n�<�6�C��"w��1�H<R�rL!�����L��SY6��	�g�����ԯ�A��Y_<<����ey=	Qk��lP�Chb����B+�s��BJ�&-�p��W�T%Ր��\E�1��"��jrj-�^:>�Ԍ��]P��ZW��FLê�Y�?`�ﰍ=f;�M������p2ܕ�ld{d��-:�������|���j���χu�غ��b|�n^������o���9��/�LLh�H��S��%&�V9Y�xS��i�J�ݸX�������_y3�i4f4<���>=>ٟv�/>2i(�٬���j�`s~��������/;���n~��$t�� C�іD��@�b��ܩ�hb�-�j%/�9��k�#x��A��8L;Ta��sKd
>�!�P4�\-�r�P��0SM������t3[V��0������Ad>���C�����'�ϯ���yBd S{��$L�����Xޔ�{K�mL��L�q��@��RLW[\g,��J&X�Ƌ�#I�y�R���V"�IY��Nm
��(�aty$3�ٰ�Ý/LA��(3������������>	�&>��(�T�g۳w�b��M��x�m,��Si�����MҨ���ӑ�L�;�����p���?����]dGè8��#1g�ͨ��T����@ۧ5��3>~�����b"�
��fomM���XK0�r�!g�d�ߔ�bù�MĽaV-�za�7�{7/l�\���#�!�B�����fŊ���q�q�0��z����;ni8���!�=�_w^}Z_�ݛp�'��^���ԳC�(�.N�]h�E2%J�v߸v.&k�n��ƛ^a��J�8��t�p�)`��,5��60��l�H��������G�H���������(M�K9���/�^�m;]���>,&��L�F	�e*�s�s!�c`s��R�0�`�l����l�[#cl���k�Y�JŉŦڔ����u"���q"�z��2�?����S�r����ؗ�9�ÇsYȬ}y�ow?���X��?��I@&�2$x��`M��P8�S�*u���:�2օC���3<�ecF��^�hꅺr��Y����
*?�gFzũ�=`x��0�\-�f�k&,���!П����Y��Sڽ{0�}r��j���d@M���:e�Ĩ 2*Ig�7p_8`b��X �ֈ'��;���t����� �y7j��|L�����|%m��z��3p�ӹ��W��l�;oru����B:]/���u֍�gG	x�A@��#�u����?(%���>��|xzz���j���� _�H'6�d��clB�MB@�}9�#�� �js���J�;&3Z?��2e�痓��|S��Vmu�����e�z�?��>����pVe�.��t/[�v���sv�F�ʔ������vd%�d��T�m�1���7�=��P���8��y �2_$�ä���XEe�4:?r�ԇ����0��(���t�%��B��f4�$��.�:���ޣ�;��b�a��9� �ƙ �(�gg=2�0��-�J*�"@B��x@Ec)xA�#���肮�WF�������a�a�$t���oEp:f?�8Z;������ǋ�ӣ����y�]     