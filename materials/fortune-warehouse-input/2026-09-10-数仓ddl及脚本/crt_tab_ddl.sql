SET
  search_path = ods;

CREATE TABLE
  ods_usms_lm_user_t_df (
    uid character varying (128),
    wx_union_id character varying (128),
    nickname character varying (256),
    phone character varying (128),
    login_cipher character varying (128),
    sex character varying (128),
    head_img_url character varying (2048),
    email character varying (128),
    birthday timestamp without TIME zone,
    initial_channel_id character varying (128),
    is_first_in character varying (128),
    protocol_version character varying (128),
    show_asset character varying (128),
    create_time timestamp without TIME zone,
    update_time timestamp without TIME zone,
    allow_login character varying (128),
    phone_credit character varying (128),
    password_salt character varying (128),
    register_ip_addr character varying (128),
    activity_type character varying (128),
    agreement_status character varying (128),
    ext_lhj2 character varying (128),
    ext_lhj3 character varying (128),
    ext_lhj4 character varying (128),
    ext_lhj5 character varying (128),
    register_type character varying (128),
    statu character varying (128),
    agreement_sign_time timestamp without TIME zone,
    agreement_sign_channel character varying (128),
    ext_lhj6 character varying (128),
    ext_lhj7 character varying (128),
    ext_lhj8 character varying (128),
    table_flg character varying (128),
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '30 days',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(uid) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE ods_usms_lm_user_t_df IS '广场用户表';

COMMENT ON COLUMN ods_usms_lm_user_t_df.uid IS '用户主键';

COMMENT ON COLUMN ods_usms_lm_user_t_df.wx_union_id IS '微信UnionID';

COMMENT ON COLUMN ods_usms_lm_user_t_df.nickname IS '用户昵称';

COMMENT ON COLUMN ods_usms_lm_user_t_df.phone IS '用户手机号';

COMMENT ON COLUMN ods_usms_lm_user_t_df.sex IS '用户性别:0:未知,1:male,2:female';

COMMENT ON COLUMN ods_usms_lm_user_t_df.head_img_url IS '用户头像';

COMMENT ON COLUMN ods_usms_lm_user_t_df.email IS '用户邮箱';

COMMENT ON COLUMN ods_usms_lm_user_t_df.birthday IS '用户生日';

COMMENT ON COLUMN ods_usms_lm_user_t_df.initial_channel_id IS '用户初始渠道id';

COMMENT ON COLUMN ods_usms_lm_user_t_df.is_first_in IS '首次进入系统标志位';

COMMENT ON COLUMN ods_usms_lm_user_t_df.protocol_version IS '协议版本';

COMMENT ON COLUMN ods_usms_lm_user_t_df.show_asset IS '脱敏显示:true不脱敏,false脱敏';

COMMENT ON COLUMN ods_usms_lm_user_t_df.create_time IS '创建时间';

COMMENT ON COLUMN ods_usms_lm_user_t_df.update_time IS '更新时间';

COMMENT ON COLUMN ods_usms_lm_user_t_df.allow_login IS '是否允许登录标志位';

COMMENT ON COLUMN ods_usms_lm_user_t_df.phone_credit IS '手机号信誉评分';

COMMENT ON COLUMN ods_usms_lm_user_t_df.password_salt IS '密码盐值';

COMMENT ON COLUMN ods_usms_lm_user_t_df.register_ip_addr IS '注册IP';

COMMENT ON COLUMN ods_usms_lm_user_t_df.activity_type IS '活动标识';

COMMENT ON COLUMN ods_usms_lm_user_t_df.agreement_status IS '协议状态(0签订,1未签订)';

COMMENT ON COLUMN ods_usms_lm_user_t_df.ext_lhj2 IS '扩展字段';

COMMENT ON COLUMN ods_usms_lm_user_t_df.ext_lhj3 IS '扩展字段';

COMMENT ON COLUMN ods_usms_lm_user_t_df.ext_lhj4 IS '扩展字段';

COMMENT ON COLUMN ods_usms_lm_user_t_df.ext_lhj5 IS '扩展字段';

COMMENT ON COLUMN ods_usms_lm_user_t_df.register_type IS '注册渠道（联盟）类型';

COMMENT ON COLUMN ods_usms_lm_user_t_df.statu IS '用户状态0有效,1注销';

COMMENT ON COLUMN ods_usms_lm_user_t_df.agreement_sign_time IS '协议签订时间';

COMMENT ON COLUMN ods_usms_lm_user_t_df.agreement_sign_channel IS '协议签订渠道';

COMMENT ON COLUMN ods_usms_lm_user_t_df.ext_lhj6 IS '扩展字段';

COMMENT ON COLUMN ods_usms_lm_user_t_df.ext_lhj7 IS '扩展字段';

COMMENT ON COLUMN ods_usms_lm_user_t_df.ext_lhj8 IS '扩展字段';

COMMENT ON COLUMN ods_usms_lm_user_t_df.table_flg IS '分表编号';



SET
  search_path = ods;

CREATE TABLE
  ods_usms_lml_account_t_df (
    id character varying (128),
    channel_id character varying (128),
    payment_password character varying (128),
    identity_authentication character varying (128),
    identity_card_no character varying (128),
    real_name character varying (128),
    first_citic_bankcard character varying (128),
    create_time timestamp without TIME zone,
    update_time timestamp without TIME zone,
    first_citic_credit_card character varying (128),
    auth_time timestamp without TIME zone,
    last_auth_time timestamp without TIME zone,
    card_no_type character varying (128),
    auth_way character varying (128),
    auth_type character varying (128),
    birthday character varying (128),
    table_flg character varying (128),
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '30 days',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(id) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE ods_usms_lml_account_t_df IS '实名账户表';

COMMENT ON COLUMN ods_usms_lml_account_t_df.id IS 'ID';

COMMENT ON COLUMN ods_usms_lml_account_t_df.channel_id IS '渠道标识';

COMMENT ON COLUMN ods_usms_lml_account_t_df.payment_password IS '支付密码加密';

COMMENT ON COLUMN ods_usms_lml_account_t_df.identity_authentication IS '是否已实名';

COMMENT ON COLUMN ods_usms_lml_account_t_df.identity_card_no IS '证件号码加密';

COMMENT ON COLUMN ods_usms_lml_account_t_df.real_name IS '实名姓名';

COMMENT ON COLUMN ods_usms_lml_account_t_df.first_citic_bankcard IS '首次中信借记卡';

COMMENT ON COLUMN ods_usms_lml_account_t_df.create_time IS '创建时间';

COMMENT ON COLUMN ods_usms_lml_account_t_df.update_time IS '更新时间';

COMMENT ON COLUMN ods_usms_lml_account_t_df.first_citic_credit_card IS '首次绑定中信信用卡';

COMMENT ON COLUMN ods_usms_lml_account_t_df.auth_time IS '实名时间';

COMMENT ON COLUMN ods_usms_lml_account_t_df.last_auth_time IS '最后一次实名时间';

COMMENT ON COLUMN ods_usms_lml_account_t_df.card_no_type IS '证件类型:01-居民身份证;02-军官证;03-护照;04-回乡证港澳;05-台胞证;06-警官证;07-士兵证;99-其它证件';

COMMENT ON COLUMN ods_usms_lml_account_t_df.auth_way IS '实名认证方式:0子公司同步,1银行卡四要素';

COMMENT ON COLUMN ods_usms_lml_account_t_df.auth_type IS '实名认证类型:0子公司同步,1财富广场';

COMMENT ON COLUMN ods_usms_lml_account_t_df.birthday IS '生日';

COMMENT ON COLUMN ods_usms_lml_account_t_df.table_flg IS '分表编号';


SET
  search_path = ods;

CREATE TABLE
  ods_usms_lm_user_t_yx_df (
    uid CHARACTER VARYING (128),
    wx_union_id CHARACTER VARYING (128),
    nickname CHARACTER VARYING (256),
    phone CHARACTER VARYING (128),
    login_cipher CHARACTER VARYING (128),
    sex CHARACTER VARYING (128),
    head_img_url CHARACTER VARYING (2048),
    email CHARACTER VARYING (128),
    birthday TIMESTAMP WITHOUT TIME ZONE,
    initial_channel_id CHARACTER VARYING (128),
    is_first_in CHARACTER VARYING (128),
    protocol_version CHARACTER VARYING (128),
    show_asset CHARACTER VARYING (128),
    create_time TIMESTAMP WITHOUT TIME ZONE,
    update_time TIMESTAMP WITHOUT TIME ZONE,
    allow_login CHARACTER VARYING (128),
    phone_credit CHARACTER VARYING (128),
    password_salt CHARACTER VARYING (128),
    register_ip_addr CHARACTER VARYING (128),
    activity_type CHARACTER VARYING (128),
    agreement_status CHARACTER VARYING (128),
    ext_lhj2 CHARACTER VARYING (128),
    ext_lhj3 CHARACTER VARYING (128),
    ext_lhj4 CHARACTER VARYING (128),
    ext_lhj5 CHARACTER VARYING (128),
    register_type CHARACTER VARYING (128),
    statu CHARACTER VARYING (128),
    agreement_sign_time TIMESTAMP WITHOUT TIME ZONE,
    agreement_sign_channel CHARACTER VARYING (128),
    ext_lhj6 CHARACTER VARYING (128),
    ext_lhj7 CHARACTER VARYING (128),
    ext_lhj8 CHARACTER VARYING (128),
    table_flg CHARACTER VARYING (128),
    etl_time TIMESTAMP WITHOUT TIME ZONE
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    COMPRESSION = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE,
    max_batchrow = 60000
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH (uid) TO GROUP v3_logical;

COMMENT ON
TABLE ods_usms_lm_user_t_yx_df IS '广场用户表';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.uid IS '用户主键';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.wx_union_id IS '微信UnionID';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.nickname IS '用户昵称';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.phone IS '用户手机号';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.sex IS '用户性别:0:未知,1:male,2:female';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.head_img_url IS '用户头像';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.email IS '用户邮箱';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.birthday IS '用户生日';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.initial_channel_id IS '用户初始渠道id';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.is_first_in IS '首次进入系统标志位';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.protocol_version IS '协议版本';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.show_asset IS '脱敏显示:true不脱敏,false脱敏';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.create_time IS '创建时间';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.update_time IS '更新时间';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.allow_login IS '是否允许登录标志位';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.phone_credit IS '手机号信誉评分';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.password_salt IS '密码盐值';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.register_ip_addr IS '注册IP';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.activity_type IS '活动标识';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.agreement_status IS '协议状态(0签订,1未签订)';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.ext_lhj2 IS '扩展字段';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.ext_lhj3 IS '扩展字段';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.ext_lhj4 IS '扩展字段';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.ext_lhj5 IS '扩展字段';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.register_type IS '注册渠道（联盟）类型';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.statu IS '用户状态0有效,1注销';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.agreement_sign_time IS '协议签订时间';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.agreement_sign_channel IS '协议签订渠道';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.ext_lhj6 IS '扩展字段';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.ext_lhj7 IS '扩展字段';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.ext_lhj8 IS '扩展字段';

COMMENT ON COLUMN ods_usms_lm_user_t_yx_df.table_flg IS '分表编号';


SET
  search_path = ods;

CREATE TABLE
  ods_usms_sub_company_real_name_sync_record_df (
    id character varying (100),
    channel_id character varying (100),
    real_name character varying (500),
    id_card_type character varying (10),
    id_card_number character varying (500),
    user_id character varying (500),
    create_time timestamp without TIME zone,
    update_time timestamp without TIME zone,
    phone character varying (500),
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_turbo_store = ON,
    enable_hstore_opt = TRUE,
    compression = middle,
    ttl = '3 years',
    period = '1 day',
    enable_delta = FALSE,
    enable_hstore = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY ROUNDROBIN TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1
    VALUES
      LESS THAN (
        '2025-12-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767196800
    VALUES
      LESS THAN (
        '2026-01-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767283200
    VALUES
      LESS THAN (
        '2026-01-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767369600
    VALUES
      LESS THAN (
        '2026-01-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767456000
    VALUES
      LESS THAN (
        '2026-01-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767542400
    VALUES
      LESS THAN (
        '2026-01-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767628800
    VALUES
      LESS THAN (
        '2026-01-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767715200
    VALUES
      LESS THAN (
        '2026-01-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767801600
    VALUES
      LESS THAN (
        '2026-01-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767888000
    VALUES
      LESS THAN (
        '2026-01-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767974400
    VALUES
      LESS THAN (
        '2026-01-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768060800
    VALUES
      LESS THAN (
        '2026-01-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768147200
    VALUES
      LESS THAN (
        '2026-01-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768233600
    VALUES
      LESS THAN (
        '2026-01-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768320000
    VALUES
      LESS THAN (
        '2026-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768406400
    VALUES
      LESS THAN (
        '2026-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768492800
    VALUES
      LESS THAN (
        '2026-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768579200
    VALUES
      LESS THAN (
        '2026-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768665600
    VALUES
      LESS THAN (
        '2026-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768752000
    VALUES
      LESS THAN (
        '2026-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768838400
    VALUES
      LESS THAN (
        '2026-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768924800
    VALUES
      LESS THAN (
        '2026-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769011200
    VALUES
      LESS THAN (
        '2026-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769097600
    VALUES
      LESS THAN (
        '2026-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769184000
    VALUES
      LESS THAN (
        '2026-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769270400
    VALUES
      LESS THAN (
        '2026-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769356800
    VALUES
      LESS THAN (
        '2026-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769443200
    VALUES
      LESS THAN (
        '2026-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769529600
    VALUES
      LESS THAN (
        '2026-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769616000
    VALUES
      LESS THAN (
        '2026-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769702400
    VALUES
      LESS THAN (
        '2026-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769788800
    VALUES
      LESS THAN (
        '2026-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769875200
    VALUES
      LESS THAN (
        '2026-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769961600
    VALUES
      LESS THAN (
        '2026-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770048000
    VALUES
      LESS THAN (
        '2026-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770134400
    VALUES
      LESS THAN (
        '2026-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770220800
    VALUES
      LESS THAN (
        '2026-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770307200
    VALUES
      LESS THAN (
        '2026-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770393600
    VALUES
      LESS THAN (
        '2026-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770480000
    VALUES
      LESS THAN (
        '2026-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770566400
    VALUES
      LESS THAN (
        '2026-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770652800
    VALUES
      LESS THAN (
        '2026-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770739200
    VALUES
      LESS THAN (
        '2026-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770825600
    VALUES
      LESS THAN (
        '2026-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770912000
    VALUES
      LESS THAN (
        '2026-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770998400
    VALUES
      LESS THAN (
        '2026-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771084800
    VALUES
      LESS THAN (
        '2026-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771171200
    VALUES
      LESS THAN (
        '2026-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771257600
    VALUES
      LESS THAN (
        '2026-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771344000
    VALUES
      LESS THAN (
        '2026-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771430400
    VALUES
      LESS THAN (
        '2026-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771516800
    VALUES
      LESS THAN (
        '2026-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771603200
    VALUES
      LESS THAN (
        '2026-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771689600
    VALUES
      LESS THAN (
        '2026-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771776000
    VALUES
      LESS THAN (
        '2026-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771862400
    VALUES
      LESS THAN (
        '2026-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771948800
    VALUES
      LESS THAN (
        '2026-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772035200
    VALUES
      LESS THAN (
        '2026-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772121600
    VALUES
      LESS THAN (
        '2026-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772208000
    VALUES
      LESS THAN (
        '2026-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772294400
    VALUES
      LESS THAN (
        '2026-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772380800
    VALUES
      LESS THAN (
        '2026-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772467200
    VALUES
      LESS THAN (
        '2026-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772553600
    VALUES
      LESS THAN (
        '2026-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772640000
    VALUES
      LESS THAN (
        '2026-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772726400
    VALUES
      LESS THAN (
        '2026-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772812800
    VALUES
      LESS THAN (
        '2026-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772899200
    VALUES
      LESS THAN (
        '2026-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772985600
    VALUES
      LESS THAN (
        '2026-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773072000
    VALUES
      LESS THAN (
        '2026-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773158400
    VALUES
      LESS THAN (
        '2026-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773244800
    VALUES
      LESS THAN (
        '2026-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773331200
    VALUES
      LESS THAN (
        '2026-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773417600
    VALUES
      LESS THAN (
        '2026-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773504000
    VALUES
      LESS THAN (
        '2026-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773590400
    VALUES
      LESS THAN (
        '2026-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773676800
    VALUES
      LESS THAN (
        '2026-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773763200
    VALUES
      LESS THAN (
        '2026-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773849600
    VALUES
      LESS THAN (
        '2026-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773936000
    VALUES
      LESS THAN (
        '2026-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774022400
    VALUES
      LESS THAN (
        '2026-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774108800
    VALUES
      LESS THAN (
        '2026-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774195200
    VALUES
      LESS THAN (
        '2026-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774281600
    VALUES
      LESS THAN (
        '2026-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774368000
    VALUES
      LESS THAN (
        '2026-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774454400
    VALUES
      LESS THAN (
        '2026-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774540800
    VALUES
      LESS THAN (
        '2026-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774627200
    VALUES
      LESS THAN (
        '2026-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774713600
    VALUES
      LESS THAN (
        '2026-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774800000
    VALUES
      LESS THAN (
        '2026-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774886400
    VALUES
      LESS THAN (
        '2026-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774972800
    VALUES
      LESS THAN (
        '2026-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775059200
    VALUES
      LESS THAN (
        '2026-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775145600
    VALUES
      LESS THAN (
        '2026-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775232000
    VALUES
      LESS THAN (
        '2026-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775318400
    VALUES
      LESS THAN (
        '2026-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775404800
    VALUES
      LESS THAN (
        '2026-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775491200
    VALUES
      LESS THAN (
        '2026-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775577600
    VALUES
      LESS THAN (
        '2026-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775664000
    VALUES
      LESS THAN (
        '2026-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775750400
    VALUES
      LESS THAN (
        '2026-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775836800
    VALUES
      LESS THAN (
        '2026-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775923200
    VALUES
      LESS THAN (
        '2026-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776009600
    VALUES
      LESS THAN (
        '2026-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776096000
    VALUES
      LESS THAN (
        '2026-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776182400
    VALUES
      LESS THAN (
        '2026-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776268800
    VALUES
      LESS THAN (
        '2026-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776355200
    VALUES
      LESS THAN (
        '2026-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776441600
    VALUES
      LESS THAN (
        '2026-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776528000
    VALUES
      LESS THAN (
        '2026-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776614400
    VALUES
      LESS THAN (
        '2026-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776700800
    VALUES
      LESS THAN (
        '2026-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776787200
    VALUES
      LESS THAN (
        '2026-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776873600
    VALUES
      LESS THAN (
        '2026-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776960000
    VALUES
      LESS THAN (
        '2026-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777046400
    VALUES
      LESS THAN (
        '2026-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777132800
    VALUES
      LESS THAN (
        '2026-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777219200
    VALUES
      LESS THAN (
        '2026-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777305600
    VALUES
      LESS THAN (
        '2026-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777392000
    VALUES
      LESS THAN (
        '2026-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777478400
    VALUES
      LESS THAN (
        '2026-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777564800
    VALUES
      LESS THAN (
        '2026-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777651200
    VALUES
      LESS THAN (
        '2026-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777737600
    VALUES
      LESS THAN (
        '2026-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777824000
    VALUES
      LESS THAN (
        '2026-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777910400
    VALUES
      LESS THAN (
        '2026-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777996800
    VALUES
      LESS THAN (
        '2026-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778083200
    VALUES
      LESS THAN (
        '2026-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778169600
    VALUES
      LESS THAN (
        '2026-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778256000
    VALUES
      LESS THAN (
        '2026-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778342400
    VALUES
      LESS THAN (
        '2026-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778428800
    VALUES
      LESS THAN (
        '2026-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778515200
    VALUES
      LESS THAN (
        '2026-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778601600
    VALUES
      LESS THAN (
        '2026-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778688000
    VALUES
      LESS THAN (
        '2026-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778774400
    VALUES
      LESS THAN (
        '2026-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778860800
    VALUES
      LESS THAN (
        '2026-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778947200
    VALUES
      LESS THAN (
        '2026-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779033600
    VALUES
      LESS THAN (
        '2026-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779120000
    VALUES
      LESS THAN (
        '2026-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779206400
    VALUES
      LESS THAN (
        '2026-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779292800
    VALUES
      LESS THAN (
        '2026-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779379200
    VALUES
      LESS THAN (
        '2026-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779465600
    VALUES
      LESS THAN (
        '2026-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779552000
    VALUES
      LESS THAN (
        '2026-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779638400
    VALUES
      LESS THAN (
        '2026-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779724800
    VALUES
      LESS THAN (
        '2026-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779811200
    VALUES
      LESS THAN (
        '2026-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779897600
    VALUES
      LESS THAN (
        '2026-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779984000
    VALUES
      LESS THAN (
        '2026-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780070400
    VALUES
      LESS THAN (
        '2026-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780156800
    VALUES
      LESS THAN (
        '2026-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780243200
    VALUES
      LESS THAN (
        '2026-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780329600
    VALUES
      LESS THAN (
        '2026-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780416000
    VALUES
      LESS THAN (
        '2026-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780502400
    VALUES
      LESS THAN (
        '2026-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780588800
    VALUES
      LESS THAN (
        '2026-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780675200
    VALUES
      LESS THAN (
        '2026-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780761600
    VALUES
      LESS THAN (
        '2026-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780848000
    VALUES
      LESS THAN (
        '2026-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780934400
    VALUES
      LESS THAN (
        '2026-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781020800
    VALUES
      LESS THAN (
        '2026-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781107200
    VALUES
      LESS THAN (
        '2026-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781193600
    VALUES
      LESS THAN (
        '2026-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791734400
    VALUES
      LESS THAN (
        '2026-10-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791820800
    VALUES
      LESS THAN (
        '2026-10-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791907200
    VALUES
      LESS THAN (
        '2026-10-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791993600
    VALUES
      LESS THAN (
        '2026-10-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1792080000
    VALUES
      LESS THAN (
        '2026-10-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1792166400
    VALUES
      LESS THAN (
        '2026-10-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1792252800
    VALUES
      LESS THAN (
        '2026-10-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1792339200
    VALUES
      LESS THAN (
        '2026-10-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1792425600
    VALUES
      LESS THAN (
        '2026-10-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1792512000
    VALUES
      LESS THAN (
        '2026-10-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1792598400
    VALUES
      LESS THAN (
        '2026-10-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1792684800
    VALUES
      LESS THAN (
        '2026-10-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1792771200
    VALUES
      LESS THAN (
        '2026-10-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1792857600
    VALUES
      LESS THAN (
        '2026-10-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1792944000
    VALUES
      LESS THAN (
        '2026-10-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1793030400
    VALUES
      LESS THAN (
        '2026-10-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1793116800
    VALUES
      LESS THAN (
        '2026-10-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1793203200
    VALUES
      LESS THAN (
        '2026-10-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1793289600
    VALUES
      LESS THAN (
        '2026-10-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1793376000
    VALUES
      LESS THAN (
        '2026-10-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1793462400
    VALUES
      LESS THAN (
        '2026-11-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1793548800
    VALUES
      LESS THAN (
        '2026-11-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1793635200
    VALUES
      LESS THAN (
        '2026-11-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1793721600
    VALUES
      LESS THAN (
        '2026-11-04 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE ods_usms_sub_company_real_name_sync_record_df IS '子公司实名信息同步流水表';

COMMENT ON COLUMN ods_usms_sub_company_real_name_sync_record_df.id IS 'ID';

COMMENT ON COLUMN ods_usms_sub_company_real_name_sync_record_df.channel_id IS '子公司渠道ID';

COMMENT ON COLUMN ods_usms_sub_company_real_name_sync_record_df.real_name IS 'SM4加密后的姓名';

COMMENT ON COLUMN ods_usms_sub_company_real_name_sync_record_df.id_card_type IS '证件类型: 1-身份证 2-护照 3-港澳通行证等';

COMMENT ON COLUMN ods_usms_sub_company_real_name_sync_record_df.id_card_number IS 'SM4加密后的证件号码';

COMMENT ON COLUMN ods_usms_sub_company_real_name_sync_record_df.user_id IS '子公司唯一标识';

COMMENT ON COLUMN ods_usms_sub_company_real_name_sync_record_df.create_time IS '同步操作时间';

COMMENT ON COLUMN ods_usms_sub_company_real_name_sync_record_df.update_time IS '更新时间';

COMMENT ON COLUMN ods_usms_sub_company_real_name_sync_record_df.phone IS '手机号';



SET
  search_path = cdm;

CREATE TABLE
  dwd_cu_rgst_fin_di (
    usr_id character varying (128),
    rgst_dt timestamp (0) without TIME zone,
    rgst_dt_src timestamp (0) without TIME zone,
    rgst_tm_src timestamp without TIME zone,
    rgst_enjy_fg character varying (128),
    rgst_type character varying (128),
    rgst_chnl_id character varying (128),
    rgst_sec_chnl_nm character varying (128),
    rgst_act_id character varying (128),
    if_act integer,
    rgst_num integer,
    nonfin_rgst_dt character varying (128),
    nonfin_rgst_chnl_id character varying (128),
    nonfin_rgst_sec_chnl_nm character varying (128),
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '3 years',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(usr_id) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1
    VALUES
      LESS THAN (
        '2025-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752508800
    VALUES
      LESS THAN (
        '2025-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752595200
    VALUES
      LESS THAN (
        '2025-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752681600
    VALUES
      LESS THAN (
        '2025-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752768000
    VALUES
      LESS THAN (
        '2025-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752854400
    VALUES
      LESS THAN (
        '2025-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752940800
    VALUES
      LESS THAN (
        '2025-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753027200
    VALUES
      LESS THAN (
        '2025-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753113600
    VALUES
      LESS THAN (
        '2025-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753200000
    VALUES
      LESS THAN (
        '2025-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753286400
    VALUES
      LESS THAN (
        '2025-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753372800
    VALUES
      LESS THAN (
        '2025-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753459200
    VALUES
      LESS THAN (
        '2025-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753545600
    VALUES
      LESS THAN (
        '2025-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753632000
    VALUES
      LESS THAN (
        '2025-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753718400
    VALUES
      LESS THAN (
        '2025-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753804800
    VALUES
      LESS THAN (
        '2025-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753891200
    VALUES
      LESS THAN (
        '2025-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753977600
    VALUES
      LESS THAN (
        '2025-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754064000
    VALUES
      LESS THAN (
        '2025-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754150400
    VALUES
      LESS THAN (
        '2025-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754236800
    VALUES
      LESS THAN (
        '2025-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754323200
    VALUES
      LESS THAN (
        '2025-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754409600
    VALUES
      LESS THAN (
        '2025-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754496000
    VALUES
      LESS THAN (
        '2025-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754582400
    VALUES
      LESS THAN (
        '2025-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754668800
    VALUES
      LESS THAN (
        '2025-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754755200
    VALUES
      LESS THAN (
        '2025-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754841600
    VALUES
      LESS THAN (
        '2025-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754928000
    VALUES
      LESS THAN (
        '2025-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755014400
    VALUES
      LESS THAN (
        '2025-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755100800
    VALUES
      LESS THAN (
        '2025-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755187200
    VALUES
      LESS THAN (
        '2025-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755273600
    VALUES
      LESS THAN (
        '2025-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755360000
    VALUES
      LESS THAN (
        '2025-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755446400
    VALUES
      LESS THAN (
        '2025-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755532800
    VALUES
      LESS THAN (
        '2025-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755619200
    VALUES
      LESS THAN (
        '2025-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755705600
    VALUES
      LESS THAN (
        '2025-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755792000
    VALUES
      LESS THAN (
        '2025-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755878400
    VALUES
      LESS THAN (
        '2025-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755964800
    VALUES
      LESS THAN (
        '2025-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756051200
    VALUES
      LESS THAN (
        '2025-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756137600
    VALUES
      LESS THAN (
        '2025-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756224000
    VALUES
      LESS THAN (
        '2025-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756310400
    VALUES
      LESS THAN (
        '2025-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756396800
    VALUES
      LESS THAN (
        '2025-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756483200
    VALUES
      LESS THAN (
        '2025-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756569600
    VALUES
      LESS THAN (
        '2025-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756656000
    VALUES
      LESS THAN (
        '2025-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756742400
    VALUES
      LESS THAN (
        '2025-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756828800
    VALUES
      LESS THAN (
        '2025-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756915200
    VALUES
      LESS THAN (
        '2025-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757001600
    VALUES
      LESS THAN (
        '2025-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757088000
    VALUES
      LESS THAN (
        '2025-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757174400
    VALUES
      LESS THAN (
        '2025-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757260800
    VALUES
      LESS THAN (
        '2025-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757347200
    VALUES
      LESS THAN (
        '2025-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757433600
    VALUES
      LESS THAN (
        '2025-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757520000
    VALUES
      LESS THAN (
        '2025-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757606400
    VALUES
      LESS THAN (
        '2025-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757692800
    VALUES
      LESS THAN (
        '2025-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757779200
    VALUES
      LESS THAN (
        '2025-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757865600
    VALUES
      LESS THAN (
        '2025-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757952000
    VALUES
      LESS THAN (
        '2025-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758038400
    VALUES
      LESS THAN (
        '2025-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758124800
    VALUES
      LESS THAN (
        '2025-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758211200
    VALUES
      LESS THAN (
        '2025-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758297600
    VALUES
      LESS THAN (
        '2025-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758384000
    VALUES
      LESS THAN (
        '2025-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758470400
    VALUES
      LESS THAN (
        '2025-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758556800
    VALUES
      LESS THAN (
        '2025-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758643200
    VALUES
      LESS THAN (
        '2025-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758729600
    VALUES
      LESS THAN (
        '2025-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758816000
    VALUES
      LESS THAN (
        '2025-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758902400
    VALUES
      LESS THAN (
        '2025-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758988800
    VALUES
      LESS THAN (
        '2025-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759075200
    VALUES
      LESS THAN (
        '2025-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759161600
    VALUES
      LESS THAN (
        '2025-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759248000
    VALUES
      LESS THAN (
        '2025-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759334400
    VALUES
      LESS THAN (
        '2025-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759420800
    VALUES
      LESS THAN (
        '2025-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759507200
    VALUES
      LESS THAN (
        '2025-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759593600
    VALUES
      LESS THAN (
        '2025-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759680000
    VALUES
      LESS THAN (
        '2025-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759766400
    VALUES
      LESS THAN (
        '2025-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759852800
    VALUES
      LESS THAN (
        '2025-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759939200
    VALUES
      LESS THAN (
        '2025-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760025600
    VALUES
      LESS THAN (
        '2025-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760112000
    VALUES
      LESS THAN (
        '2025-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760198400
    VALUES
      LESS THAN (
        '2025-10-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760284800
    VALUES
      LESS THAN (
        '2025-10-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760371200
    VALUES
      LESS THAN (
        '2025-10-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760457600
    VALUES
      LESS THAN (
        '2025-10-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760544000
    VALUES
      LESS THAN (
        '2025-10-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760630400
    VALUES
      LESS THAN (
        '2025-10-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760716800
    VALUES
      LESS THAN (
        '2025-10-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760803200
    VALUES
      LESS THAN (
        '2025-10-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760889600
    VALUES
      LESS THAN (
        '2025-10-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760976000
    VALUES
      LESS THAN (
        '2025-10-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761062400
    VALUES
      LESS THAN (
        '2025-10-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761148800
    VALUES
      LESS THAN (
        '2025-10-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761235200
    VALUES
      LESS THAN (
        '2025-10-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761321600
    VALUES
      LESS THAN (
        '2025-10-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761408000
    VALUES
      LESS THAN (
        '2025-10-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761494400
    VALUES
      LESS THAN (
        '2025-10-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761580800
    VALUES
      LESS THAN (
        '2025-10-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761667200
    VALUES
      LESS THAN (
        '2025-10-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761753600
    VALUES
      LESS THAN (
        '2025-10-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761840000
    VALUES
      LESS THAN (
        '2025-10-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761926400
    VALUES
      LESS THAN (
        '2025-11-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762012800
    VALUES
      LESS THAN (
        '2025-11-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762099200
    VALUES
      LESS THAN (
        '2025-11-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762185600
    VALUES
      LESS THAN (
        '2025-11-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762272000
    VALUES
      LESS THAN (
        '2025-11-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762358400
    VALUES
      LESS THAN (
        '2025-11-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762444800
    VALUES
      LESS THAN (
        '2025-11-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762531200
    VALUES
      LESS THAN (
        '2025-11-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762617600
    VALUES
      LESS THAN (
        '2025-11-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762704000
    VALUES
      LESS THAN (
        '2025-11-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762790400
    VALUES
      LESS THAN (
        '2025-11-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762876800
    VALUES
      LESS THAN (
        '2025-11-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762963200
    VALUES
      LESS THAN (
        '2025-11-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763049600
    VALUES
      LESS THAN (
        '2025-11-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763136000
    VALUES
      LESS THAN (
        '2025-11-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763222400
    VALUES
      LESS THAN (
        '2025-11-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763308800
    VALUES
      LESS THAN (
        '2025-11-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763395200
    VALUES
      LESS THAN (
        '2025-11-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763481600
    VALUES
      LESS THAN (
        '2025-11-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763568000
    VALUES
      LESS THAN (
        '2025-11-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763654400
    VALUES
      LESS THAN (
        '2025-11-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763740800
    VALUES
      LESS THAN (
        '2025-11-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763827200
    VALUES
      LESS THAN (
        '2025-11-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763913600
    VALUES
      LESS THAN (
        '2025-11-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764000000
    VALUES
      LESS THAN (
        '2025-11-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764086400
    VALUES
      LESS THAN (
        '2025-11-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764172800
    VALUES
      LESS THAN (
        '2025-11-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764259200
    VALUES
      LESS THAN (
        '2025-11-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764345600
    VALUES
      LESS THAN (
        '2025-11-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764432000
    VALUES
      LESS THAN (
        '2025-11-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764518400
    VALUES
      LESS THAN (
        '2025-12-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764604800
    VALUES
      LESS THAN (
        '2025-12-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764691200
    VALUES
      LESS THAN (
        '2025-12-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764777600
    VALUES
      LESS THAN (
        '2025-12-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764864000
    VALUES
      LESS THAN (
        '2025-12-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764950400
    VALUES
      LESS THAN (
        '2025-12-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765036800
    VALUES
      LESS THAN (
        '2025-12-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765123200
    VALUES
      LESS THAN (
        '2025-12-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765209600
    VALUES
      LESS THAN (
        '2025-12-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765296000
    VALUES
      LESS THAN (
        '2025-12-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765382400
    VALUES
      LESS THAN (
        '2025-12-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765468800
    VALUES
      LESS THAN (
        '2025-12-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765555200
    VALUES
      LESS THAN (
        '2025-12-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765641600
    VALUES
      LESS THAN (
        '2025-12-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765728000
    VALUES
      LESS THAN (
        '2025-12-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765814400
    VALUES
      LESS THAN (
        '2025-12-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765900800
    VALUES
      LESS THAN (
        '2025-12-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765987200
    VALUES
      LESS THAN (
        '2025-12-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766073600
    VALUES
      LESS THAN (
        '2025-12-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766160000
    VALUES
      LESS THAN (
        '2025-12-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766246400
    VALUES
      LESS THAN (
        '2025-12-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766332800
    VALUES
      LESS THAN (
        '2025-12-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766419200
    VALUES
      LESS THAN (
        '2025-12-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766505600
    VALUES
      LESS THAN (
        '2025-12-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766592000
    VALUES
      LESS THAN (
        '2025-12-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766678400
    VALUES
      LESS THAN (
        '2025-12-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766764800
    VALUES
      LESS THAN (
        '2025-12-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766851200
    VALUES
      LESS THAN (
        '2025-12-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766937600
    VALUES
      LESS THAN (
        '2025-12-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767024000
    VALUES
      LESS THAN (
        '2025-12-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767110400
    VALUES
      LESS THAN (
        '2025-12-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767196800
    VALUES
      LESS THAN (
        '2026-01-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767283200
    VALUES
      LESS THAN (
        '2026-01-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767369600
    VALUES
      LESS THAN (
        '2026-01-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767456000
    VALUES
      LESS THAN (
        '2026-01-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767542400
    VALUES
      LESS THAN (
        '2026-01-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767628800
    VALUES
      LESS THAN (
        '2026-01-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767715200
    VALUES
      LESS THAN (
        '2026-01-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767801600
    VALUES
      LESS THAN (
        '2026-01-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767888000
    VALUES
      LESS THAN (
        '2026-01-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767974400
    VALUES
      LESS THAN (
        '2026-01-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768060800
    VALUES
      LESS THAN (
        '2026-01-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768147200
    VALUES
      LESS THAN (
        '2026-01-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768233600
    VALUES
      LESS THAN (
        '2026-01-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768320000
    VALUES
      LESS THAN (
        '2026-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768406400
    VALUES
      LESS THAN (
        '2026-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768492800
    VALUES
      LESS THAN (
        '2026-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768579200
    VALUES
      LESS THAN (
        '2026-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768665600
    VALUES
      LESS THAN (
        '2026-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768752000
    VALUES
      LESS THAN (
        '2026-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768838400
    VALUES
      LESS THAN (
        '2026-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768924800
    VALUES
      LESS THAN (
        '2026-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769011200
    VALUES
      LESS THAN (
        '2026-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769097600
    VALUES
      LESS THAN (
        '2026-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769184000
    VALUES
      LESS THAN (
        '2026-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769270400
    VALUES
      LESS THAN (
        '2026-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769356800
    VALUES
      LESS THAN (
        '2026-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769443200
    VALUES
      LESS THAN (
        '2026-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769529600
    VALUES
      LESS THAN (
        '2026-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769616000
    VALUES
      LESS THAN (
        '2026-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769702400
    VALUES
      LESS THAN (
        '2026-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769788800
    VALUES
      LESS THAN (
        '2026-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769875200
    VALUES
      LESS THAN (
        '2026-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769961600
    VALUES
      LESS THAN (
        '2026-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770048000
    VALUES
      LESS THAN (
        '2026-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770134400
    VALUES
      LESS THAN (
        '2026-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770220800
    VALUES
      LESS THAN (
        '2026-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770307200
    VALUES
      LESS THAN (
        '2026-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770393600
    VALUES
      LESS THAN (
        '2026-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770480000
    VALUES
      LESS THAN (
        '2026-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770566400
    VALUES
      LESS THAN (
        '2026-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770652800
    VALUES
      LESS THAN (
        '2026-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770739200
    VALUES
      LESS THAN (
        '2026-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770825600
    VALUES
      LESS THAN (
        '2026-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770912000
    VALUES
      LESS THAN (
        '2026-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770998400
    VALUES
      LESS THAN (
        '2026-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771084800
    VALUES
      LESS THAN (
        '2026-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771171200
    VALUES
      LESS THAN (
        '2026-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771257600
    VALUES
      LESS THAN (
        '2026-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771344000
    VALUES
      LESS THAN (
        '2026-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771430400
    VALUES
      LESS THAN (
        '2026-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771516800
    VALUES
      LESS THAN (
        '2026-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771603200
    VALUES
      LESS THAN (
        '2026-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771689600
    VALUES
      LESS THAN (
        '2026-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771776000
    VALUES
      LESS THAN (
        '2026-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771862400
    VALUES
      LESS THAN (
        '2026-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771948800
    VALUES
      LESS THAN (
        '2026-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772035200
    VALUES
      LESS THAN (
        '2026-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772121600
    VALUES
      LESS THAN (
        '2026-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772208000
    VALUES
      LESS THAN (
        '2026-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772294400
    VALUES
      LESS THAN (
        '2026-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772380800
    VALUES
      LESS THAN (
        '2026-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772467200
    VALUES
      LESS THAN (
        '2026-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772553600
    VALUES
      LESS THAN (
        '2026-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772640000
    VALUES
      LESS THAN (
        '2026-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772726400
    VALUES
      LESS THAN (
        '2026-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772812800
    VALUES
      LESS THAN (
        '2026-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772899200
    VALUES
      LESS THAN (
        '2026-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772985600
    VALUES
      LESS THAN (
        '2026-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773072000
    VALUES
      LESS THAN (
        '2026-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773158400
    VALUES
      LESS THAN (
        '2026-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773244800
    VALUES
      LESS THAN (
        '2026-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773331200
    VALUES
      LESS THAN (
        '2026-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773417600
    VALUES
      LESS THAN (
        '2026-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773504000
    VALUES
      LESS THAN (
        '2026-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773590400
    VALUES
      LESS THAN (
        '2026-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773676800
    VALUES
      LESS THAN (
        '2026-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773763200
    VALUES
      LESS THAN (
        '2026-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773849600
    VALUES
      LESS THAN (
        '2026-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773936000
    VALUES
      LESS THAN (
        '2026-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774022400
    VALUES
      LESS THAN (
        '2026-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774108800
    VALUES
      LESS THAN (
        '2026-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774195200
    VALUES
      LESS THAN (
        '2026-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774281600
    VALUES
      LESS THAN (
        '2026-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774368000
    VALUES
      LESS THAN (
        '2026-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774454400
    VALUES
      LESS THAN (
        '2026-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774540800
    VALUES
      LESS THAN (
        '2026-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774627200
    VALUES
      LESS THAN (
        '2026-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774713600
    VALUES
      LESS THAN (
        '2026-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774800000
    VALUES
      LESS THAN (
        '2026-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774886400
    VALUES
      LESS THAN (
        '2026-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774972800
    VALUES
      LESS THAN (
        '2026-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775059200
    VALUES
      LESS THAN (
        '2026-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775145600
    VALUES
      LESS THAN (
        '2026-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775232000
    VALUES
      LESS THAN (
        '2026-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775318400
    VALUES
      LESS THAN (
        '2026-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775404800
    VALUES
      LESS THAN (
        '2026-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775491200
    VALUES
      LESS THAN (
        '2026-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775577600
    VALUES
      LESS THAN (
        '2026-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775664000
    VALUES
      LESS THAN (
        '2026-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775750400
    VALUES
      LESS THAN (
        '2026-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775836800
    VALUES
      LESS THAN (
        '2026-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775923200
    VALUES
      LESS THAN (
        '2026-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776009600
    VALUES
      LESS THAN (
        '2026-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776096000
    VALUES
      LESS THAN (
        '2026-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776182400
    VALUES
      LESS THAN (
        '2026-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776268800
    VALUES
      LESS THAN (
        '2026-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776355200
    VALUES
      LESS THAN (
        '2026-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776441600
    VALUES
      LESS THAN (
        '2026-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776528000
    VALUES
      LESS THAN (
        '2026-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776614400
    VALUES
      LESS THAN (
        '2026-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776700800
    VALUES
      LESS THAN (
        '2026-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776787200
    VALUES
      LESS THAN (
        '2026-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776873600
    VALUES
      LESS THAN (
        '2026-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776960000
    VALUES
      LESS THAN (
        '2026-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777046400
    VALUES
      LESS THAN (
        '2026-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777132800
    VALUES
      LESS THAN (
        '2026-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777219200
    VALUES
      LESS THAN (
        '2026-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777305600
    VALUES
      LESS THAN (
        '2026-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777392000
    VALUES
      LESS THAN (
        '2026-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777478400
    VALUES
      LESS THAN (
        '2026-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777564800
    VALUES
      LESS THAN (
        '2026-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777651200
    VALUES
      LESS THAN (
        '2026-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777737600
    VALUES
      LESS THAN (
        '2026-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777824000
    VALUES
      LESS THAN (
        '2026-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777910400
    VALUES
      LESS THAN (
        '2026-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777996800
    VALUES
      LESS THAN (
        '2026-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778083200
    VALUES
      LESS THAN (
        '2026-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778169600
    VALUES
      LESS THAN (
        '2026-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778256000
    VALUES
      LESS THAN (
        '2026-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778342400
    VALUES
      LESS THAN (
        '2026-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778428800
    VALUES
      LESS THAN (
        '2026-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778515200
    VALUES
      LESS THAN (
        '2026-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778601600
    VALUES
      LESS THAN (
        '2026-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778688000
    VALUES
      LESS THAN (
        '2026-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778774400
    VALUES
      LESS THAN (
        '2026-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778860800
    VALUES
      LESS THAN (
        '2026-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778947200
    VALUES
      LESS THAN (
        '2026-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779033600
    VALUES
      LESS THAN (
        '2026-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779120000
    VALUES
      LESS THAN (
        '2026-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779206400
    VALUES
      LESS THAN (
        '2026-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779292800
    VALUES
      LESS THAN (
        '2026-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779379200
    VALUES
      LESS THAN (
        '2026-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779465600
    VALUES
      LESS THAN (
        '2026-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779552000
    VALUES
      LESS THAN (
        '2026-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779638400
    VALUES
      LESS THAN (
        '2026-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779724800
    VALUES
      LESS THAN (
        '2026-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779811200
    VALUES
      LESS THAN (
        '2026-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779897600
    VALUES
      LESS THAN (
        '2026-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779984000
    VALUES
      LESS THAN (
        '2026-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780070400
    VALUES
      LESS THAN (
        '2026-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780156800
    VALUES
      LESS THAN (
        '2026-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780243200
    VALUES
      LESS THAN (
        '2026-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780329600
    VALUES
      LESS THAN (
        '2026-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780416000
    VALUES
      LESS THAN (
        '2026-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780502400
    VALUES
      LESS THAN (
        '2026-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780588800
    VALUES
      LESS THAN (
        '2026-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780675200
    VALUES
      LESS THAN (
        '2026-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780761600
    VALUES
      LESS THAN (
        '2026-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780848000
    VALUES
      LESS THAN (
        '2026-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780934400
    VALUES
      LESS THAN (
        '2026-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781020800
    VALUES
      LESS THAN (
        '2026-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781107200
    VALUES
      LESS THAN (
        '2026-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781193600
    VALUES
      LESS THAN (
        '2026-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE dwd_cu_rgst_fin_di IS '注册增量表-金融渠道';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.usr_id IS '用户ID';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.rgst_dt IS '注册日期（入库）';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.rgst_dt_src IS '注册日期（原始）';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.rgst_tm_src IS '注册时间（原始）';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.rgst_enjy_fg IS '是否优享升级注册';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.rgst_type IS '注册类型';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.rgst_chnl_id IS '注册渠道ID';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.rgst_sec_chnl_nm IS '注册二级渠道';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.rgst_act_id IS '注册活动ID';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.if_act IS '是否激活';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.rgst_num IS '注册用户数标志位';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.nonfin_rgst_dt IS '激活前_原始注册日期';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.nonfin_rgst_chnl_id IS '激活前_原始注册渠道ID';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.nonfin_rgst_sec_chnl_nm IS '激活前_原始注册二级渠道';

COMMENT ON COLUMN dwd_cu_rgst_fin_di.ds IS '分区日期';



SET
  search_path = cdm;

CREATE TABLE
  dwd_cu_rgst_nonfin_di (
    usr_id character varying (128),
    rgst_dt timestamp (0) without TIME zone,
    rgst_dt_src timestamp (0) without TIME zone,
    rgst_tm_src timestamp without TIME zone,
    rgst_enjy_fg character varying (128),
    rgst_type character varying (128),
    rgst_chnl_id character varying (128),
    rgst_sec_chnl_nm character varying (128),
    rgst_act_id character varying (128),
    rgst_num integer,
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '3 years',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(usr_id) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1
    VALUES
      LESS THAN (
        '2025-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752508800
    VALUES
      LESS THAN (
        '2025-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752595200
    VALUES
      LESS THAN (
        '2025-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752681600
    VALUES
      LESS THAN (
        '2025-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752768000
    VALUES
      LESS THAN (
        '2025-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752854400
    VALUES
      LESS THAN (
        '2025-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752940800
    VALUES
      LESS THAN (
        '2025-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753027200
    VALUES
      LESS THAN (
        '2025-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753113600
    VALUES
      LESS THAN (
        '2025-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753200000
    VALUES
      LESS THAN (
        '2025-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753286400
    VALUES
      LESS THAN (
        '2025-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753372800
    VALUES
      LESS THAN (
        '2025-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753459200
    VALUES
      LESS THAN (
        '2025-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753545600
    VALUES
      LESS THAN (
        '2025-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753632000
    VALUES
      LESS THAN (
        '2025-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753718400
    VALUES
      LESS THAN (
        '2025-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753804800
    VALUES
      LESS THAN (
        '2025-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753891200
    VALUES
      LESS THAN (
        '2025-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753977600
    VALUES
      LESS THAN (
        '2025-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754064000
    VALUES
      LESS THAN (
        '2025-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754150400
    VALUES
      LESS THAN (
        '2025-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754236800
    VALUES
      LESS THAN (
        '2025-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754323200
    VALUES
      LESS THAN (
        '2025-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754409600
    VALUES
      LESS THAN (
        '2025-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754496000
    VALUES
      LESS THAN (
        '2025-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754582400
    VALUES
      LESS THAN (
        '2025-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754668800
    VALUES
      LESS THAN (
        '2025-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754755200
    VALUES
      LESS THAN (
        '2025-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754841600
    VALUES
      LESS THAN (
        '2025-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754928000
    VALUES
      LESS THAN (
        '2025-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755014400
    VALUES
      LESS THAN (
        '2025-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755100800
    VALUES
      LESS THAN (
        '2025-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755187200
    VALUES
      LESS THAN (
        '2025-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755273600
    VALUES
      LESS THAN (
        '2025-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755360000
    VALUES
      LESS THAN (
        '2025-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755446400
    VALUES
      LESS THAN (
        '2025-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755532800
    VALUES
      LESS THAN (
        '2025-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755619200
    VALUES
      LESS THAN (
        '2025-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755705600
    VALUES
      LESS THAN (
        '2025-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755792000
    VALUES
      LESS THAN (
        '2025-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755878400
    VALUES
      LESS THAN (
        '2025-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755964800
    VALUES
      LESS THAN (
        '2025-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756051200
    VALUES
      LESS THAN (
        '2025-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756137600
    VALUES
      LESS THAN (
        '2025-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756224000
    VALUES
      LESS THAN (
        '2025-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756310400
    VALUES
      LESS THAN (
        '2025-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756396800
    VALUES
      LESS THAN (
        '2025-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756483200
    VALUES
      LESS THAN (
        '2025-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756569600
    VALUES
      LESS THAN (
        '2025-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756656000
    VALUES
      LESS THAN (
        '2025-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756742400
    VALUES
      LESS THAN (
        '2025-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756828800
    VALUES
      LESS THAN (
        '2025-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756915200
    VALUES
      LESS THAN (
        '2025-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757001600
    VALUES
      LESS THAN (
        '2025-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757088000
    VALUES
      LESS THAN (
        '2025-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757174400
    VALUES
      LESS THAN (
        '2025-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757260800
    VALUES
      LESS THAN (
        '2025-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757347200
    VALUES
      LESS THAN (
        '2025-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757433600
    VALUES
      LESS THAN (
        '2025-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757520000
    VALUES
      LESS THAN (
        '2025-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757606400
    VALUES
      LESS THAN (
        '2025-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757692800
    VALUES
      LESS THAN (
        '2025-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757779200
    VALUES
      LESS THAN (
        '2025-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757865600
    VALUES
      LESS THAN (
        '2025-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757952000
    VALUES
      LESS THAN (
        '2025-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758038400
    VALUES
      LESS THAN (
        '2025-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758124800
    VALUES
      LESS THAN (
        '2025-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758211200
    VALUES
      LESS THAN (
        '2025-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758297600
    VALUES
      LESS THAN (
        '2025-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758384000
    VALUES
      LESS THAN (
        '2025-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758470400
    VALUES
      LESS THAN (
        '2025-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758556800
    VALUES
      LESS THAN (
        '2025-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758643200
    VALUES
      LESS THAN (
        '2025-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758729600
    VALUES
      LESS THAN (
        '2025-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758816000
    VALUES
      LESS THAN (
        '2025-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758902400
    VALUES
      LESS THAN (
        '2025-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758988800
    VALUES
      LESS THAN (
        '2025-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759075200
    VALUES
      LESS THAN (
        '2025-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759161600
    VALUES
      LESS THAN (
        '2025-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759248000
    VALUES
      LESS THAN (
        '2025-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759334400
    VALUES
      LESS THAN (
        '2025-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759420800
    VALUES
      LESS THAN (
        '2025-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759507200
    VALUES
      LESS THAN (
        '2025-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759593600
    VALUES
      LESS THAN (
        '2025-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759680000
    VALUES
      LESS THAN (
        '2025-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759766400
    VALUES
      LESS THAN (
        '2025-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759852800
    VALUES
      LESS THAN (
        '2025-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759939200
    VALUES
      LESS THAN (
        '2025-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760025600
    VALUES
      LESS THAN (
        '2025-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760112000
    VALUES
      LESS THAN (
        '2025-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760198400
    VALUES
      LESS THAN (
        '2025-10-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760284800
    VALUES
      LESS THAN (
        '2025-10-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760371200
    VALUES
      LESS THAN (
        '2025-10-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760457600
    VALUES
      LESS THAN (
        '2025-10-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760544000
    VALUES
      LESS THAN (
        '2025-10-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760630400
    VALUES
      LESS THAN (
        '2025-10-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760716800
    VALUES
      LESS THAN (
        '2025-10-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760803200
    VALUES
      LESS THAN (
        '2025-10-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760889600
    VALUES
      LESS THAN (
        '2025-10-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760976000
    VALUES
      LESS THAN (
        '2025-10-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761062400
    VALUES
      LESS THAN (
        '2025-10-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761148800
    VALUES
      LESS THAN (
        '2025-10-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761235200
    VALUES
      LESS THAN (
        '2025-10-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761321600
    VALUES
      LESS THAN (
        '2025-10-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761408000
    VALUES
      LESS THAN (
        '2025-10-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761494400
    VALUES
      LESS THAN (
        '2025-10-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761580800
    VALUES
      LESS THAN (
        '2025-10-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761667200
    VALUES
      LESS THAN (
        '2025-10-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761753600
    VALUES
      LESS THAN (
        '2025-10-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761840000
    VALUES
      LESS THAN (
        '2025-10-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761926400
    VALUES
      LESS THAN (
        '2025-11-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762012800
    VALUES
      LESS THAN (
        '2025-11-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762099200
    VALUES
      LESS THAN (
        '2025-11-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762185600
    VALUES
      LESS THAN (
        '2025-11-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762272000
    VALUES
      LESS THAN (
        '2025-11-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762358400
    VALUES
      LESS THAN (
        '2025-11-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762444800
    VALUES
      LESS THAN (
        '2025-11-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762531200
    VALUES
      LESS THAN (
        '2025-11-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762617600
    VALUES
      LESS THAN (
        '2025-11-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762704000
    VALUES
      LESS THAN (
        '2025-11-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762790400
    VALUES
      LESS THAN (
        '2025-11-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762876800
    VALUES
      LESS THAN (
        '2025-11-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762963200
    VALUES
      LESS THAN (
        '2025-11-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763049600
    VALUES
      LESS THAN (
        '2025-11-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763136000
    VALUES
      LESS THAN (
        '2025-11-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763222400
    VALUES
      LESS THAN (
        '2025-11-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763308800
    VALUES
      LESS THAN (
        '2025-11-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763395200
    VALUES
      LESS THAN (
        '2025-11-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763481600
    VALUES
      LESS THAN (
        '2025-11-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763568000
    VALUES
      LESS THAN (
        '2025-11-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763654400
    VALUES
      LESS THAN (
        '2025-11-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763740800
    VALUES
      LESS THAN (
        '2025-11-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763827200
    VALUES
      LESS THAN (
        '2025-11-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763913600
    VALUES
      LESS THAN (
        '2025-11-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764000000
    VALUES
      LESS THAN (
        '2025-11-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764086400
    VALUES
      LESS THAN (
        '2025-11-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764172800
    VALUES
      LESS THAN (
        '2025-11-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764259200
    VALUES
      LESS THAN (
        '2025-11-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764345600
    VALUES
      LESS THAN (
        '2025-11-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764432000
    VALUES
      LESS THAN (
        '2025-11-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764518400
    VALUES
      LESS THAN (
        '2025-12-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764604800
    VALUES
      LESS THAN (
        '2025-12-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764691200
    VALUES
      LESS THAN (
        '2025-12-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764777600
    VALUES
      LESS THAN (
        '2025-12-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764864000
    VALUES
      LESS THAN (
        '2025-12-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764950400
    VALUES
      LESS THAN (
        '2025-12-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765036800
    VALUES
      LESS THAN (
        '2025-12-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765123200
    VALUES
      LESS THAN (
        '2025-12-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765209600
    VALUES
      LESS THAN (
        '2025-12-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765296000
    VALUES
      LESS THAN (
        '2025-12-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765382400
    VALUES
      LESS THAN (
        '2025-12-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765468800
    VALUES
      LESS THAN (
        '2025-12-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765555200
    VALUES
      LESS THAN (
        '2025-12-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765641600
    VALUES
      LESS THAN (
        '2025-12-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765728000
    VALUES
      LESS THAN (
        '2025-12-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765814400
    VALUES
      LESS THAN (
        '2025-12-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765900800
    VALUES
      LESS THAN (
        '2025-12-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765987200
    VALUES
      LESS THAN (
        '2025-12-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766073600
    VALUES
      LESS THAN (
        '2025-12-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766160000
    VALUES
      LESS THAN (
        '2025-12-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766246400
    VALUES
      LESS THAN (
        '2025-12-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766332800
    VALUES
      LESS THAN (
        '2025-12-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766419200
    VALUES
      LESS THAN (
        '2025-12-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766505600
    VALUES
      LESS THAN (
        '2025-12-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766592000
    VALUES
      LESS THAN (
        '2025-12-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766678400
    VALUES
      LESS THAN (
        '2025-12-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766764800
    VALUES
      LESS THAN (
        '2025-12-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766851200
    VALUES
      LESS THAN (
        '2025-12-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766937600
    VALUES
      LESS THAN (
        '2025-12-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767024000
    VALUES
      LESS THAN (
        '2025-12-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767110400
    VALUES
      LESS THAN (
        '2025-12-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767196800
    VALUES
      LESS THAN (
        '2026-01-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767283200
    VALUES
      LESS THAN (
        '2026-01-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767369600
    VALUES
      LESS THAN (
        '2026-01-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767456000
    VALUES
      LESS THAN (
        '2026-01-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767542400
    VALUES
      LESS THAN (
        '2026-01-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767628800
    VALUES
      LESS THAN (
        '2026-01-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767715200
    VALUES
      LESS THAN (
        '2026-01-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767801600
    VALUES
      LESS THAN (
        '2026-01-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767888000
    VALUES
      LESS THAN (
        '2026-01-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767974400
    VALUES
      LESS THAN (
        '2026-01-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768060800
    VALUES
      LESS THAN (
        '2026-01-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768147200
    VALUES
      LESS THAN (
        '2026-01-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768233600
    VALUES
      LESS THAN (
        '2026-01-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768320000
    VALUES
      LESS THAN (
        '2026-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768406400
    VALUES
      LESS THAN (
        '2026-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768492800
    VALUES
      LESS THAN (
        '2026-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768579200
    VALUES
      LESS THAN (
        '2026-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768665600
    VALUES
      LESS THAN (
        '2026-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768752000
    VALUES
      LESS THAN (
        '2026-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768838400
    VALUES
      LESS THAN (
        '2026-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768924800
    VALUES
      LESS THAN (
        '2026-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769011200
    VALUES
      LESS THAN (
        '2026-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769097600
    VALUES
      LESS THAN (
        '2026-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769184000
    VALUES
      LESS THAN (
        '2026-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769270400
    VALUES
      LESS THAN (
        '2026-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769356800
    VALUES
      LESS THAN (
        '2026-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769443200
    VALUES
      LESS THAN (
        '2026-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769529600
    VALUES
      LESS THAN (
        '2026-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769616000
    VALUES
      LESS THAN (
        '2026-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769702400
    VALUES
      LESS THAN (
        '2026-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769788800
    VALUES
      LESS THAN (
        '2026-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769875200
    VALUES
      LESS THAN (
        '2026-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769961600
    VALUES
      LESS THAN (
        '2026-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770048000
    VALUES
      LESS THAN (
        '2026-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770134400
    VALUES
      LESS THAN (
        '2026-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770220800
    VALUES
      LESS THAN (
        '2026-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770307200
    VALUES
      LESS THAN (
        '2026-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770393600
    VALUES
      LESS THAN (
        '2026-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770480000
    VALUES
      LESS THAN (
        '2026-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770566400
    VALUES
      LESS THAN (
        '2026-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770652800
    VALUES
      LESS THAN (
        '2026-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770739200
    VALUES
      LESS THAN (
        '2026-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770825600
    VALUES
      LESS THAN (
        '2026-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770912000
    VALUES
      LESS THAN (
        '2026-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770998400
    VALUES
      LESS THAN (
        '2026-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771084800
    VALUES
      LESS THAN (
        '2026-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771171200
    VALUES
      LESS THAN (
        '2026-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771257600
    VALUES
      LESS THAN (
        '2026-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771344000
    VALUES
      LESS THAN (
        '2026-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771430400
    VALUES
      LESS THAN (
        '2026-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771516800
    VALUES
      LESS THAN (
        '2026-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771603200
    VALUES
      LESS THAN (
        '2026-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771689600
    VALUES
      LESS THAN (
        '2026-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771776000
    VALUES
      LESS THAN (
        '2026-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771862400
    VALUES
      LESS THAN (
        '2026-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771948800
    VALUES
      LESS THAN (
        '2026-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772035200
    VALUES
      LESS THAN (
        '2026-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772121600
    VALUES
      LESS THAN (
        '2026-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772208000
    VALUES
      LESS THAN (
        '2026-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772294400
    VALUES
      LESS THAN (
        '2026-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772380800
    VALUES
      LESS THAN (
        '2026-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772467200
    VALUES
      LESS THAN (
        '2026-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772553600
    VALUES
      LESS THAN (
        '2026-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772640000
    VALUES
      LESS THAN (
        '2026-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772726400
    VALUES
      LESS THAN (
        '2026-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772812800
    VALUES
      LESS THAN (
        '2026-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772899200
    VALUES
      LESS THAN (
        '2026-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772985600
    VALUES
      LESS THAN (
        '2026-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773072000
    VALUES
      LESS THAN (
        '2026-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773158400
    VALUES
      LESS THAN (
        '2026-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773244800
    VALUES
      LESS THAN (
        '2026-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773331200
    VALUES
      LESS THAN (
        '2026-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773417600
    VALUES
      LESS THAN (
        '2026-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773504000
    VALUES
      LESS THAN (
        '2026-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773590400
    VALUES
      LESS THAN (
        '2026-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773676800
    VALUES
      LESS THAN (
        '2026-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773763200
    VALUES
      LESS THAN (
        '2026-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773849600
    VALUES
      LESS THAN (
        '2026-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773936000
    VALUES
      LESS THAN (
        '2026-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774022400
    VALUES
      LESS THAN (
        '2026-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774108800
    VALUES
      LESS THAN (
        '2026-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774195200
    VALUES
      LESS THAN (
        '2026-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774281600
    VALUES
      LESS THAN (
        '2026-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774368000
    VALUES
      LESS THAN (
        '2026-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774454400
    VALUES
      LESS THAN (
        '2026-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774540800
    VALUES
      LESS THAN (
        '2026-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774627200
    VALUES
      LESS THAN (
        '2026-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774713600
    VALUES
      LESS THAN (
        '2026-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774800000
    VALUES
      LESS THAN (
        '2026-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774886400
    VALUES
      LESS THAN (
        '2026-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774972800
    VALUES
      LESS THAN (
        '2026-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775059200
    VALUES
      LESS THAN (
        '2026-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775145600
    VALUES
      LESS THAN (
        '2026-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775232000
    VALUES
      LESS THAN (
        '2026-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775318400
    VALUES
      LESS THAN (
        '2026-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775404800
    VALUES
      LESS THAN (
        '2026-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775491200
    VALUES
      LESS THAN (
        '2026-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775577600
    VALUES
      LESS THAN (
        '2026-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775664000
    VALUES
      LESS THAN (
        '2026-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775750400
    VALUES
      LESS THAN (
        '2026-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775836800
    VALUES
      LESS THAN (
        '2026-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775923200
    VALUES
      LESS THAN (
        '2026-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776009600
    VALUES
      LESS THAN (
        '2026-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776096000
    VALUES
      LESS THAN (
        '2026-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776182400
    VALUES
      LESS THAN (
        '2026-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776268800
    VALUES
      LESS THAN (
        '2026-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776355200
    VALUES
      LESS THAN (
        '2026-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776441600
    VALUES
      LESS THAN (
        '2026-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776528000
    VALUES
      LESS THAN (
        '2026-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776614400
    VALUES
      LESS THAN (
        '2026-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776700800
    VALUES
      LESS THAN (
        '2026-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776787200
    VALUES
      LESS THAN (
        '2026-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776873600
    VALUES
      LESS THAN (
        '2026-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776960000
    VALUES
      LESS THAN (
        '2026-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777046400
    VALUES
      LESS THAN (
        '2026-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777132800
    VALUES
      LESS THAN (
        '2026-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777219200
    VALUES
      LESS THAN (
        '2026-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777305600
    VALUES
      LESS THAN (
        '2026-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777392000
    VALUES
      LESS THAN (
        '2026-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777478400
    VALUES
      LESS THAN (
        '2026-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777564800
    VALUES
      LESS THAN (
        '2026-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777651200
    VALUES
      LESS THAN (
        '2026-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777737600
    VALUES
      LESS THAN (
        '2026-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777824000
    VALUES
      LESS THAN (
        '2026-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777910400
    VALUES
      LESS THAN (
        '2026-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777996800
    VALUES
      LESS THAN (
        '2026-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778083200
    VALUES
      LESS THAN (
        '2026-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778169600
    VALUES
      LESS THAN (
        '2026-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778256000
    VALUES
      LESS THAN (
        '2026-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778342400
    VALUES
      LESS THAN (
        '2026-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778428800
    VALUES
      LESS THAN (
        '2026-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778515200
    VALUES
      LESS THAN (
        '2026-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778601600
    VALUES
      LESS THAN (
        '2026-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778688000
    VALUES
      LESS THAN (
        '2026-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778774400
    VALUES
      LESS THAN (
        '2026-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778860800
    VALUES
      LESS THAN (
        '2026-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778947200
    VALUES
      LESS THAN (
        '2026-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779033600
    VALUES
      LESS THAN (
        '2026-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779120000
    VALUES
      LESS THAN (
        '2026-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779206400
    VALUES
      LESS THAN (
        '2026-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779292800
    VALUES
      LESS THAN (
        '2026-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779379200
    VALUES
      LESS THAN (
        '2026-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779465600
    VALUES
      LESS THAN (
        '2026-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779552000
    VALUES
      LESS THAN (
        '2026-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779638400
    VALUES
      LESS THAN (
        '2026-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779724800
    VALUES
      LESS THAN (
        '2026-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779811200
    VALUES
      LESS THAN (
        '2026-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779897600
    VALUES
      LESS THAN (
        '2026-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779984000
    VALUES
      LESS THAN (
        '2026-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780070400
    VALUES
      LESS THAN (
        '2026-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780156800
    VALUES
      LESS THAN (
        '2026-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780243200
    VALUES
      LESS THAN (
        '2026-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780329600
    VALUES
      LESS THAN (
        '2026-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780416000
    VALUES
      LESS THAN (
        '2026-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780502400
    VALUES
      LESS THAN (
        '2026-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780588800
    VALUES
      LESS THAN (
        '2026-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780675200
    VALUES
      LESS THAN (
        '2026-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780761600
    VALUES
      LESS THAN (
        '2026-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780848000
    VALUES
      LESS THAN (
        '2026-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780934400
    VALUES
      LESS THAN (
        '2026-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781020800
    VALUES
      LESS THAN (
        '2026-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781107200
    VALUES
      LESS THAN (
        '2026-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781193600
    VALUES
      LESS THAN (
        '2026-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE dwd_cu_rgst_nonfin_di IS '注册增量表-非金融渠道';

COMMENT ON COLUMN dwd_cu_rgst_nonfin_di.usr_id IS '用户ID';

COMMENT ON COLUMN dwd_cu_rgst_nonfin_di.rgst_dt IS '注册日期（入库）';

COMMENT ON COLUMN dwd_cu_rgst_nonfin_di.rgst_dt_src IS '注册日期（原始）';

COMMENT ON COLUMN dwd_cu_rgst_nonfin_di.rgst_tm_src IS '注册时间（原始）';

COMMENT ON COLUMN dwd_cu_rgst_nonfin_di.rgst_enjy_fg IS '是否优享升级注册';

COMMENT ON COLUMN dwd_cu_rgst_nonfin_di.rgst_type IS '注册类型';

COMMENT ON COLUMN dwd_cu_rgst_nonfin_di.rgst_chnl_id IS '注册渠道ID';

COMMENT ON COLUMN dwd_cu_rgst_nonfin_di.rgst_sec_chnl_nm IS '注册二级渠道';

COMMENT ON COLUMN dwd_cu_rgst_nonfin_di.rgst_act_id IS '注册活动ID';

COMMENT ON COLUMN dwd_cu_rgst_nonfin_di.rgst_num IS '注册用户数标志位';

COMMENT ON COLUMN dwd_cu_rgst_nonfin_di.ds IS '分区日期';

SET
  search_path = cdm;

CREATE TABLE
  dwd_cu_actv_df (
    usr_id character varying (128),
    actv_dt timestamp (0) without TIME zone,
    actv_tm timestamp without TIME zone,
    actv_chnl_id character varying (128),
    actv_chnl_nm character varying (128),
    actv_sec_chnl_id character varying (128),
    actv_sec_chnl_nm character varying (128),
    actv_chnl_sub_nm character varying (128),
    actv_tag integer,
    actv_date_src timestamp (0) without TIME zone,
    rgst_dt timestamp (0) without TIME zone,
    rgst_sec_chnl_nm character varying (128),
    rgst_enjy_fg integer,
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '3 years',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(usr_id) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1
    VALUES
      LESS THAN (
        '2025-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752508800
    VALUES
      LESS THAN (
        '2025-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752595200
    VALUES
      LESS THAN (
        '2025-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752681600
    VALUES
      LESS THAN (
        '2025-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752768000
    VALUES
      LESS THAN (
        '2025-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752854400
    VALUES
      LESS THAN (
        '2025-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752940800
    VALUES
      LESS THAN (
        '2025-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753027200
    VALUES
      LESS THAN (
        '2025-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753113600
    VALUES
      LESS THAN (
        '2025-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753200000
    VALUES
      LESS THAN (
        '2025-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753286400
    VALUES
      LESS THAN (
        '2025-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753372800
    VALUES
      LESS THAN (
        '2025-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753459200
    VALUES
      LESS THAN (
        '2025-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753545600
    VALUES
      LESS THAN (
        '2025-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753632000
    VALUES
      LESS THAN (
        '2025-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753718400
    VALUES
      LESS THAN (
        '2025-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753804800
    VALUES
      LESS THAN (
        '2025-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753891200
    VALUES
      LESS THAN (
        '2025-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753977600
    VALUES
      LESS THAN (
        '2025-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754064000
    VALUES
      LESS THAN (
        '2025-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754150400
    VALUES
      LESS THAN (
        '2025-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754236800
    VALUES
      LESS THAN (
        '2025-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754323200
    VALUES
      LESS THAN (
        '2025-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754409600
    VALUES
      LESS THAN (
        '2025-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754496000
    VALUES
      LESS THAN (
        '2025-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754582400
    VALUES
      LESS THAN (
        '2025-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754668800
    VALUES
      LESS THAN (
        '2025-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754755200
    VALUES
      LESS THAN (
        '2025-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754841600
    VALUES
      LESS THAN (
        '2025-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754928000
    VALUES
      LESS THAN (
        '2025-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755014400
    VALUES
      LESS THAN (
        '2025-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755100800
    VALUES
      LESS THAN (
        '2025-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755187200
    VALUES
      LESS THAN (
        '2025-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755273600
    VALUES
      LESS THAN (
        '2025-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755360000
    VALUES
      LESS THAN (
        '2025-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755446400
    VALUES
      LESS THAN (
        '2025-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755532800
    VALUES
      LESS THAN (
        '2025-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755619200
    VALUES
      LESS THAN (
        '2025-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755705600
    VALUES
      LESS THAN (
        '2025-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755792000
    VALUES
      LESS THAN (
        '2025-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755878400
    VALUES
      LESS THAN (
        '2025-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755964800
    VALUES
      LESS THAN (
        '2025-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756051200
    VALUES
      LESS THAN (
        '2025-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756137600
    VALUES
      LESS THAN (
        '2025-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756224000
    VALUES
      LESS THAN (
        '2025-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756310400
    VALUES
      LESS THAN (
        '2025-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756396800
    VALUES
      LESS THAN (
        '2025-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756483200
    VALUES
      LESS THAN (
        '2025-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756569600
    VALUES
      LESS THAN (
        '2025-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756656000
    VALUES
      LESS THAN (
        '2025-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756742400
    VALUES
      LESS THAN (
        '2025-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756828800
    VALUES
      LESS THAN (
        '2025-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756915200
    VALUES
      LESS THAN (
        '2025-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757001600
    VALUES
      LESS THAN (
        '2025-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757088000
    VALUES
      LESS THAN (
        '2025-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757174400
    VALUES
      LESS THAN (
        '2025-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757260800
    VALUES
      LESS THAN (
        '2025-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757347200
    VALUES
      LESS THAN (
        '2025-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757433600
    VALUES
      LESS THAN (
        '2025-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757520000
    VALUES
      LESS THAN (
        '2025-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757606400
    VALUES
      LESS THAN (
        '2025-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757692800
    VALUES
      LESS THAN (
        '2025-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757779200
    VALUES
      LESS THAN (
        '2025-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757865600
    VALUES
      LESS THAN (
        '2025-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757952000
    VALUES
      LESS THAN (
        '2025-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758038400
    VALUES
      LESS THAN (
        '2025-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758124800
    VALUES
      LESS THAN (
        '2025-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758211200
    VALUES
      LESS THAN (
        '2025-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758297600
    VALUES
      LESS THAN (
        '2025-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758384000
    VALUES
      LESS THAN (
        '2025-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758470400
    VALUES
      LESS THAN (
        '2025-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758556800
    VALUES
      LESS THAN (
        '2025-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758643200
    VALUES
      LESS THAN (
        '2025-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758729600
    VALUES
      LESS THAN (
        '2025-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758816000
    VALUES
      LESS THAN (
        '2025-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758902400
    VALUES
      LESS THAN (
        '2025-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758988800
    VALUES
      LESS THAN (
        '2025-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759075200
    VALUES
      LESS THAN (
        '2025-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759161600
    VALUES
      LESS THAN (
        '2025-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759248000
    VALUES
      LESS THAN (
        '2025-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759334400
    VALUES
      LESS THAN (
        '2025-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759420800
    VALUES
      LESS THAN (
        '2025-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759507200
    VALUES
      LESS THAN (
        '2025-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759593600
    VALUES
      LESS THAN (
        '2025-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759680000
    VALUES
      LESS THAN (
        '2025-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759766400
    VALUES
      LESS THAN (
        '2025-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759852800
    VALUES
      LESS THAN (
        '2025-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759939200
    VALUES
      LESS THAN (
        '2025-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760025600
    VALUES
      LESS THAN (
        '2025-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760112000
    VALUES
      LESS THAN (
        '2025-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760198400
    VALUES
      LESS THAN (
        '2025-10-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760284800
    VALUES
      LESS THAN (
        '2025-10-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760371200
    VALUES
      LESS THAN (
        '2025-10-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760457600
    VALUES
      LESS THAN (
        '2025-10-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760544000
    VALUES
      LESS THAN (
        '2025-10-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760630400
    VALUES
      LESS THAN (
        '2025-10-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760716800
    VALUES
      LESS THAN (
        '2025-10-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760803200
    VALUES
      LESS THAN (
        '2025-10-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760889600
    VALUES
      LESS THAN (
        '2025-10-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760976000
    VALUES
      LESS THAN (
        '2025-10-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761062400
    VALUES
      LESS THAN (
        '2025-10-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761148800
    VALUES
      LESS THAN (
        '2025-10-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761235200
    VALUES
      LESS THAN (
        '2025-10-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761321600
    VALUES
      LESS THAN (
        '2025-10-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761408000
    VALUES
      LESS THAN (
        '2025-10-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761494400
    VALUES
      LESS THAN (
        '2025-10-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761580800
    VALUES
      LESS THAN (
        '2025-10-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761667200
    VALUES
      LESS THAN (
        '2025-10-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761753600
    VALUES
      LESS THAN (
        '2025-10-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761840000
    VALUES
      LESS THAN (
        '2025-10-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761926400
    VALUES
      LESS THAN (
        '2025-11-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762012800
    VALUES
      LESS THAN (
        '2025-11-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762099200
    VALUES
      LESS THAN (
        '2025-11-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762185600
    VALUES
      LESS THAN (
        '2025-11-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762272000
    VALUES
      LESS THAN (
        '2025-11-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762358400
    VALUES
      LESS THAN (
        '2025-11-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762444800
    VALUES
      LESS THAN (
        '2025-11-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762531200
    VALUES
      LESS THAN (
        '2025-11-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762617600
    VALUES
      LESS THAN (
        '2025-11-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762704000
    VALUES
      LESS THAN (
        '2025-11-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762790400
    VALUES
      LESS THAN (
        '2025-11-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762876800
    VALUES
      LESS THAN (
        '2025-11-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762963200
    VALUES
      LESS THAN (
        '2025-11-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763049600
    VALUES
      LESS THAN (
        '2025-11-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763136000
    VALUES
      LESS THAN (
        '2025-11-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763222400
    VALUES
      LESS THAN (
        '2025-11-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763308800
    VALUES
      LESS THAN (
        '2025-11-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763395200
    VALUES
      LESS THAN (
        '2025-11-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763481600
    VALUES
      LESS THAN (
        '2025-11-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763568000
    VALUES
      LESS THAN (
        '2025-11-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763654400
    VALUES
      LESS THAN (
        '2025-11-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763740800
    VALUES
      LESS THAN (
        '2025-11-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763827200
    VALUES
      LESS THAN (
        '2025-11-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763913600
    VALUES
      LESS THAN (
        '2025-11-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764000000
    VALUES
      LESS THAN (
        '2025-11-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764086400
    VALUES
      LESS THAN (
        '2025-11-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764172800
    VALUES
      LESS THAN (
        '2025-11-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764259200
    VALUES
      LESS THAN (
        '2025-11-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764345600
    VALUES
      LESS THAN (
        '2025-11-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764432000
    VALUES
      LESS THAN (
        '2025-11-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764518400
    VALUES
      LESS THAN (
        '2025-12-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764604800
    VALUES
      LESS THAN (
        '2025-12-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764691200
    VALUES
      LESS THAN (
        '2025-12-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764777600
    VALUES
      LESS THAN (
        '2025-12-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764864000
    VALUES
      LESS THAN (
        '2025-12-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764950400
    VALUES
      LESS THAN (
        '2025-12-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765036800
    VALUES
      LESS THAN (
        '2025-12-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765123200
    VALUES
      LESS THAN (
        '2025-12-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765209600
    VALUES
      LESS THAN (
        '2025-12-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765296000
    VALUES
      LESS THAN (
        '2025-12-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765382400
    VALUES
      LESS THAN (
        '2025-12-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765468800
    VALUES
      LESS THAN (
        '2025-12-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765555200
    VALUES
      LESS THAN (
        '2025-12-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765641600
    VALUES
      LESS THAN (
        '2025-12-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765728000
    VALUES
      LESS THAN (
        '2025-12-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765814400
    VALUES
      LESS THAN (
        '2025-12-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765900800
    VALUES
      LESS THAN (
        '2025-12-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765987200
    VALUES
      LESS THAN (
        '2025-12-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766073600
    VALUES
      LESS THAN (
        '2025-12-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766160000
    VALUES
      LESS THAN (
        '2025-12-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766246400
    VALUES
      LESS THAN (
        '2025-12-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766332800
    VALUES
      LESS THAN (
        '2025-12-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766419200
    VALUES
      LESS THAN (
        '2025-12-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766505600
    VALUES
      LESS THAN (
        '2025-12-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766592000
    VALUES
      LESS THAN (
        '2025-12-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766678400
    VALUES
      LESS THAN (
        '2025-12-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766764800
    VALUES
      LESS THAN (
        '2025-12-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766851200
    VALUES
      LESS THAN (
        '2025-12-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766937600
    VALUES
      LESS THAN (
        '2025-12-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767024000
    VALUES
      LESS THAN (
        '2025-12-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767110400
    VALUES
      LESS THAN (
        '2025-12-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767196800
    VALUES
      LESS THAN (
        '2026-01-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767283200
    VALUES
      LESS THAN (
        '2026-01-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767369600
    VALUES
      LESS THAN (
        '2026-01-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767456000
    VALUES
      LESS THAN (
        '2026-01-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767542400
    VALUES
      LESS THAN (
        '2026-01-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767628800
    VALUES
      LESS THAN (
        '2026-01-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767715200
    VALUES
      LESS THAN (
        '2026-01-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767801600
    VALUES
      LESS THAN (
        '2026-01-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767888000
    VALUES
      LESS THAN (
        '2026-01-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767974400
    VALUES
      LESS THAN (
        '2026-01-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768060800
    VALUES
      LESS THAN (
        '2026-01-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768147200
    VALUES
      LESS THAN (
        '2026-01-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768233600
    VALUES
      LESS THAN (
        '2026-01-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768320000
    VALUES
      LESS THAN (
        '2026-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768406400
    VALUES
      LESS THAN (
        '2026-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768492800
    VALUES
      LESS THAN (
        '2026-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768579200
    VALUES
      LESS THAN (
        '2026-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768665600
    VALUES
      LESS THAN (
        '2026-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768752000
    VALUES
      LESS THAN (
        '2026-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768838400
    VALUES
      LESS THAN (
        '2026-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768924800
    VALUES
      LESS THAN (
        '2026-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769011200
    VALUES
      LESS THAN (
        '2026-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769097600
    VALUES
      LESS THAN (
        '2026-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769184000
    VALUES
      LESS THAN (
        '2026-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769270400
    VALUES
      LESS THAN (
        '2026-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769356800
    VALUES
      LESS THAN (
        '2026-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769443200
    VALUES
      LESS THAN (
        '2026-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769529600
    VALUES
      LESS THAN (
        '2026-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769616000
    VALUES
      LESS THAN (
        '2026-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769702400
    VALUES
      LESS THAN (
        '2026-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769788800
    VALUES
      LESS THAN (
        '2026-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769875200
    VALUES
      LESS THAN (
        '2026-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769961600
    VALUES
      LESS THAN (
        '2026-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770048000
    VALUES
      LESS THAN (
        '2026-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770134400
    VALUES
      LESS THAN (
        '2026-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770220800
    VALUES
      LESS THAN (
        '2026-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770307200
    VALUES
      LESS THAN (
        '2026-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770393600
    VALUES
      LESS THAN (
        '2026-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770480000
    VALUES
      LESS THAN (
        '2026-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770566400
    VALUES
      LESS THAN (
        '2026-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770652800
    VALUES
      LESS THAN (
        '2026-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770739200
    VALUES
      LESS THAN (
        '2026-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770825600
    VALUES
      LESS THAN (
        '2026-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770912000
    VALUES
      LESS THAN (
        '2026-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770998400
    VALUES
      LESS THAN (
        '2026-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771084800
    VALUES
      LESS THAN (
        '2026-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771171200
    VALUES
      LESS THAN (
        '2026-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771257600
    VALUES
      LESS THAN (
        '2026-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771344000
    VALUES
      LESS THAN (
        '2026-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771430400
    VALUES
      LESS THAN (
        '2026-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771516800
    VALUES
      LESS THAN (
        '2026-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771603200
    VALUES
      LESS THAN (
        '2026-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771689600
    VALUES
      LESS THAN (
        '2026-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771776000
    VALUES
      LESS THAN (
        '2026-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771862400
    VALUES
      LESS THAN (
        '2026-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771948800
    VALUES
      LESS THAN (
        '2026-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772035200
    VALUES
      LESS THAN (
        '2026-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772121600
    VALUES
      LESS THAN (
        '2026-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772208000
    VALUES
      LESS THAN (
        '2026-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772294400
    VALUES
      LESS THAN (
        '2026-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772380800
    VALUES
      LESS THAN (
        '2026-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772467200
    VALUES
      LESS THAN (
        '2026-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772553600
    VALUES
      LESS THAN (
        '2026-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772640000
    VALUES
      LESS THAN (
        '2026-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772726400
    VALUES
      LESS THAN (
        '2026-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772812800
    VALUES
      LESS THAN (
        '2026-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772899200
    VALUES
      LESS THAN (
        '2026-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772985600
    VALUES
      LESS THAN (
        '2026-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773072000
    VALUES
      LESS THAN (
        '2026-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773158400
    VALUES
      LESS THAN (
        '2026-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773244800
    VALUES
      LESS THAN (
        '2026-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773331200
    VALUES
      LESS THAN (
        '2026-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773417600
    VALUES
      LESS THAN (
        '2026-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773504000
    VALUES
      LESS THAN (
        '2026-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773590400
    VALUES
      LESS THAN (
        '2026-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773676800
    VALUES
      LESS THAN (
        '2026-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773763200
    VALUES
      LESS THAN (
        '2026-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773849600
    VALUES
      LESS THAN (
        '2026-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773936000
    VALUES
      LESS THAN (
        '2026-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774022400
    VALUES
      LESS THAN (
        '2026-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774108800
    VALUES
      LESS THAN (
        '2026-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774195200
    VALUES
      LESS THAN (
        '2026-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774281600
    VALUES
      LESS THAN (
        '2026-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774368000
    VALUES
      LESS THAN (
        '2026-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774454400
    VALUES
      LESS THAN (
        '2026-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774540800
    VALUES
      LESS THAN (
        '2026-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774627200
    VALUES
      LESS THAN (
        '2026-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774713600
    VALUES
      LESS THAN (
        '2026-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774800000
    VALUES
      LESS THAN (
        '2026-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774886400
    VALUES
      LESS THAN (
        '2026-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774972800
    VALUES
      LESS THAN (
        '2026-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775059200
    VALUES
      LESS THAN (
        '2026-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775145600
    VALUES
      LESS THAN (
        '2026-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775232000
    VALUES
      LESS THAN (
        '2026-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775318400
    VALUES
      LESS THAN (
        '2026-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775404800
    VALUES
      LESS THAN (
        '2026-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775491200
    VALUES
      LESS THAN (
        '2026-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775577600
    VALUES
      LESS THAN (
        '2026-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775664000
    VALUES
      LESS THAN (
        '2026-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775750400
    VALUES
      LESS THAN (
        '2026-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775836800
    VALUES
      LESS THAN (
        '2026-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775923200
    VALUES
      LESS THAN (
        '2026-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776009600
    VALUES
      LESS THAN (
        '2026-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776096000
    VALUES
      LESS THAN (
        '2026-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776182400
    VALUES
      LESS THAN (
        '2026-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776268800
    VALUES
      LESS THAN (
        '2026-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776355200
    VALUES
      LESS THAN (
        '2026-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776441600
    VALUES
      LESS THAN (
        '2026-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776528000
    VALUES
      LESS THAN (
        '2026-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776614400
    VALUES
      LESS THAN (
        '2026-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776700800
    VALUES
      LESS THAN (
        '2026-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776787200
    VALUES
      LESS THAN (
        '2026-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776873600
    VALUES
      LESS THAN (
        '2026-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776960000
    VALUES
      LESS THAN (
        '2026-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777046400
    VALUES
      LESS THAN (
        '2026-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777132800
    VALUES
      LESS THAN (
        '2026-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777219200
    VALUES
      LESS THAN (
        '2026-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777305600
    VALUES
      LESS THAN (
        '2026-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777392000
    VALUES
      LESS THAN (
        '2026-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777478400
    VALUES
      LESS THAN (
        '2026-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777564800
    VALUES
      LESS THAN (
        '2026-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777651200
    VALUES
      LESS THAN (
        '2026-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777737600
    VALUES
      LESS THAN (
        '2026-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777824000
    VALUES
      LESS THAN (
        '2026-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777910400
    VALUES
      LESS THAN (
        '2026-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777996800
    VALUES
      LESS THAN (
        '2026-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778083200
    VALUES
      LESS THAN (
        '2026-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778169600
    VALUES
      LESS THAN (
        '2026-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778256000
    VALUES
      LESS THAN (
        '2026-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778342400
    VALUES
      LESS THAN (
        '2026-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778428800
    VALUES
      LESS THAN (
        '2026-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778515200
    VALUES
      LESS THAN (
        '2026-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778601600
    VALUES
      LESS THAN (
        '2026-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778688000
    VALUES
      LESS THAN (
        '2026-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778774400
    VALUES
      LESS THAN (
        '2026-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778860800
    VALUES
      LESS THAN (
        '2026-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778947200
    VALUES
      LESS THAN (
        '2026-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779033600
    VALUES
      LESS THAN (
        '2026-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779120000
    VALUES
      LESS THAN (
        '2026-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779206400
    VALUES
      LESS THAN (
        '2026-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779292800
    VALUES
      LESS THAN (
        '2026-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779379200
    VALUES
      LESS THAN (
        '2026-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779465600
    VALUES
      LESS THAN (
        '2026-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779552000
    VALUES
      LESS THAN (
        '2026-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779638400
    VALUES
      LESS THAN (
        '2026-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779724800
    VALUES
      LESS THAN (
        '2026-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779811200
    VALUES
      LESS THAN (
        '2026-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779897600
    VALUES
      LESS THAN (
        '2026-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779984000
    VALUES
      LESS THAN (
        '2026-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780070400
    VALUES
      LESS THAN (
        '2026-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780156800
    VALUES
      LESS THAN (
        '2026-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780243200
    VALUES
      LESS THAN (
        '2026-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780329600
    VALUES
      LESS THAN (
        '2026-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780416000
    VALUES
      LESS THAN (
        '2026-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780502400
    VALUES
      LESS THAN (
        '2026-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780588800
    VALUES
      LESS THAN (
        '2026-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780675200
    VALUES
      LESS THAN (
        '2026-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780761600
    VALUES
      LESS THAN (
        '2026-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780848000
    VALUES
      LESS THAN (
        '2026-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780934400
    VALUES
      LESS THAN (
        '2026-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781020800
    VALUES
      LESS THAN (
        '2026-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781107200
    VALUES
      LESS THAN (
        '2026-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781193600
    VALUES
      LESS THAN (
        '2026-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE dwd_cu_actv_df IS '用户激活表';

COMMENT ON COLUMN dwd_cu_actv_df.usr_id IS '用户ID';

COMMENT ON COLUMN dwd_cu_actv_df.actv_dt IS '激活日期';

COMMENT ON COLUMN dwd_cu_actv_df.actv_tm IS '激活时间';

COMMENT ON COLUMN dwd_cu_actv_df.actv_chnl_id IS '激活渠道ID';

COMMENT ON COLUMN dwd_cu_actv_df.actv_chnl_nm IS '激活渠道名称';

COMMENT ON COLUMN dwd_cu_actv_df.actv_sec_chnl_id IS '激活二级渠道ID';

COMMENT ON COLUMN dwd_cu_actv_df.actv_sec_chnl_nm IS '激活二级渠道名称';

COMMENT ON COLUMN dwd_cu_actv_df.actv_chnl_sub_nm IS '激活报送渠道名称';

COMMENT ON COLUMN dwd_cu_actv_df.actv_tag IS '激活类型(1-关联渠道2-企微3-公众号)';

COMMENT ON COLUMN dwd_cu_actv_df.actv_date_src IS '激活日期原始';

COMMENT ON COLUMN dwd_cu_actv_df.rgst_dt IS '注册日期';

COMMENT ON COLUMN dwd_cu_actv_df.rgst_sec_chnl_nm IS '注册二级渠道';

COMMENT ON COLUMN dwd_cu_actv_df.rgst_enjy_fg IS '注册类型0同步1登录';

COMMENT ON COLUMN dwd_cu_actv_df.ds IS '分区日期';

SET
  search_path = cdm;

CREATE TABLE
  dwd_cu_real_df (
    usr_id character varying (128),
    real_dt timestamp (0) without TIME zone,
    real_tm timestamp without TIME zone,
    real_way character varying (128),
    real_type character varying (128),
    real_chnl_id character varying (128),
    rgst_chnl_id character varying (128),
    rgst_sec_chnl_nm character varying (128),
    rgst_dt timestamp (0) without TIME zone,
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '3 years',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(usr_id) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1
    VALUES
      LESS THAN (
        '2025-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752595200
    VALUES
      LESS THAN (
        '2025-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752681600
    VALUES
      LESS THAN (
        '2025-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752768000
    VALUES
      LESS THAN (
        '2025-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752854400
    VALUES
      LESS THAN (
        '2025-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752940800
    VALUES
      LESS THAN (
        '2025-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753027200
    VALUES
      LESS THAN (
        '2025-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753113600
    VALUES
      LESS THAN (
        '2025-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753200000
    VALUES
      LESS THAN (
        '2025-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753286400
    VALUES
      LESS THAN (
        '2025-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753372800
    VALUES
      LESS THAN (
        '2025-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753459200
    VALUES
      LESS THAN (
        '2025-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753545600
    VALUES
      LESS THAN (
        '2025-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753632000
    VALUES
      LESS THAN (
        '2025-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753718400
    VALUES
      LESS THAN (
        '2025-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753804800
    VALUES
      LESS THAN (
        '2025-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753891200
    VALUES
      LESS THAN (
        '2025-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753977600
    VALUES
      LESS THAN (
        '2025-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754064000
    VALUES
      LESS THAN (
        '2025-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754150400
    VALUES
      LESS THAN (
        '2025-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754236800
    VALUES
      LESS THAN (
        '2025-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754323200
    VALUES
      LESS THAN (
        '2025-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754409600
    VALUES
      LESS THAN (
        '2025-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754496000
    VALUES
      LESS THAN (
        '2025-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754582400
    VALUES
      LESS THAN (
        '2025-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754668800
    VALUES
      LESS THAN (
        '2025-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754755200
    VALUES
      LESS THAN (
        '2025-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754841600
    VALUES
      LESS THAN (
        '2025-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754928000
    VALUES
      LESS THAN (
        '2025-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755014400
    VALUES
      LESS THAN (
        '2025-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755100800
    VALUES
      LESS THAN (
        '2025-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755187200
    VALUES
      LESS THAN (
        '2025-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755273600
    VALUES
      LESS THAN (
        '2025-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755360000
    VALUES
      LESS THAN (
        '2025-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755446400
    VALUES
      LESS THAN (
        '2025-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755532800
    VALUES
      LESS THAN (
        '2025-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755619200
    VALUES
      LESS THAN (
        '2025-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755705600
    VALUES
      LESS THAN (
        '2025-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755792000
    VALUES
      LESS THAN (
        '2025-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755878400
    VALUES
      LESS THAN (
        '2025-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755964800
    VALUES
      LESS THAN (
        '2025-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756051200
    VALUES
      LESS THAN (
        '2025-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756137600
    VALUES
      LESS THAN (
        '2025-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756224000
    VALUES
      LESS THAN (
        '2025-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756310400
    VALUES
      LESS THAN (
        '2025-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756396800
    VALUES
      LESS THAN (
        '2025-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756483200
    VALUES
      LESS THAN (
        '2025-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756569600
    VALUES
      LESS THAN (
        '2025-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756656000
    VALUES
      LESS THAN (
        '2025-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756742400
    VALUES
      LESS THAN (
        '2025-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756828800
    VALUES
      LESS THAN (
        '2025-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756915200
    VALUES
      LESS THAN (
        '2025-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757001600
    VALUES
      LESS THAN (
        '2025-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757088000
    VALUES
      LESS THAN (
        '2025-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757174400
    VALUES
      LESS THAN (
        '2025-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757260800
    VALUES
      LESS THAN (
        '2025-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757347200
    VALUES
      LESS THAN (
        '2025-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757433600
    VALUES
      LESS THAN (
        '2025-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757520000
    VALUES
      LESS THAN (
        '2025-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757606400
    VALUES
      LESS THAN (
        '2025-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757692800
    VALUES
      LESS THAN (
        '2025-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757779200
    VALUES
      LESS THAN (
        '2025-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757865600
    VALUES
      LESS THAN (
        '2025-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757952000
    VALUES
      LESS THAN (
        '2025-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758038400
    VALUES
      LESS THAN (
        '2025-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758124800
    VALUES
      LESS THAN (
        '2025-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758211200
    VALUES
      LESS THAN (
        '2025-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758297600
    VALUES
      LESS THAN (
        '2025-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758384000
    VALUES
      LESS THAN (
        '2025-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758470400
    VALUES
      LESS THAN (
        '2025-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758556800
    VALUES
      LESS THAN (
        '2025-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758643200
    VALUES
      LESS THAN (
        '2025-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758729600
    VALUES
      LESS THAN (
        '2025-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758816000
    VALUES
      LESS THAN (
        '2025-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758902400
    VALUES
      LESS THAN (
        '2025-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758988800
    VALUES
      LESS THAN (
        '2025-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759075200
    VALUES
      LESS THAN (
        '2025-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759161600
    VALUES
      LESS THAN (
        '2025-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759248000
    VALUES
      LESS THAN (
        '2025-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759334400
    VALUES
      LESS THAN (
        '2025-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759420800
    VALUES
      LESS THAN (
        '2025-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759507200
    VALUES
      LESS THAN (
        '2025-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759593600
    VALUES
      LESS THAN (
        '2025-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759680000
    VALUES
      LESS THAN (
        '2025-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759766400
    VALUES
      LESS THAN (
        '2025-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759852800
    VALUES
      LESS THAN (
        '2025-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759939200
    VALUES
      LESS THAN (
        '2025-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760025600
    VALUES
      LESS THAN (
        '2025-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760112000
    VALUES
      LESS THAN (
        '2025-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760198400
    VALUES
      LESS THAN (
        '2025-10-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760284800
    VALUES
      LESS THAN (
        '2025-10-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760371200
    VALUES
      LESS THAN (
        '2025-10-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760457600
    VALUES
      LESS THAN (
        '2025-10-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760544000
    VALUES
      LESS THAN (
        '2025-10-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760630400
    VALUES
      LESS THAN (
        '2025-10-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760716800
    VALUES
      LESS THAN (
        '2025-10-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760803200
    VALUES
      LESS THAN (
        '2025-10-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760889600
    VALUES
      LESS THAN (
        '2025-10-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760976000
    VALUES
      LESS THAN (
        '2025-10-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761062400
    VALUES
      LESS THAN (
        '2025-10-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761148800
    VALUES
      LESS THAN (
        '2025-10-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761235200
    VALUES
      LESS THAN (
        '2025-10-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761321600
    VALUES
      LESS THAN (
        '2025-10-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761408000
    VALUES
      LESS THAN (
        '2025-10-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761494400
    VALUES
      LESS THAN (
        '2025-10-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761580800
    VALUES
      LESS THAN (
        '2025-10-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761667200
    VALUES
      LESS THAN (
        '2025-10-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761753600
    VALUES
      LESS THAN (
        '2025-10-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761840000
    VALUES
      LESS THAN (
        '2025-10-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761926400
    VALUES
      LESS THAN (
        '2025-11-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762012800
    VALUES
      LESS THAN (
        '2025-11-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762099200
    VALUES
      LESS THAN (
        '2025-11-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762185600
    VALUES
      LESS THAN (
        '2025-11-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762272000
    VALUES
      LESS THAN (
        '2025-11-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762358400
    VALUES
      LESS THAN (
        '2025-11-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762444800
    VALUES
      LESS THAN (
        '2025-11-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762531200
    VALUES
      LESS THAN (
        '2025-11-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762617600
    VALUES
      LESS THAN (
        '2025-11-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762704000
    VALUES
      LESS THAN (
        '2025-11-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762790400
    VALUES
      LESS THAN (
        '2025-11-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762876800
    VALUES
      LESS THAN (
        '2025-11-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762963200
    VALUES
      LESS THAN (
        '2025-11-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763049600
    VALUES
      LESS THAN (
        '2025-11-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763136000
    VALUES
      LESS THAN (
        '2025-11-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763222400
    VALUES
      LESS THAN (
        '2025-11-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763308800
    VALUES
      LESS THAN (
        '2025-11-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763395200
    VALUES
      LESS THAN (
        '2025-11-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763481600
    VALUES
      LESS THAN (
        '2025-11-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763568000
    VALUES
      LESS THAN (
        '2025-11-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763654400
    VALUES
      LESS THAN (
        '2025-11-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763740800
    VALUES
      LESS THAN (
        '2025-11-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763827200
    VALUES
      LESS THAN (
        '2025-11-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763913600
    VALUES
      LESS THAN (
        '2025-11-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764000000
    VALUES
      LESS THAN (
        '2025-11-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764086400
    VALUES
      LESS THAN (
        '2025-11-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764172800
    VALUES
      LESS THAN (
        '2025-11-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764259200
    VALUES
      LESS THAN (
        '2025-11-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764345600
    VALUES
      LESS THAN (
        '2025-11-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764432000
    VALUES
      LESS THAN (
        '2025-11-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764518400
    VALUES
      LESS THAN (
        '2025-12-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764604800
    VALUES
      LESS THAN (
        '2025-12-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764691200
    VALUES
      LESS THAN (
        '2025-12-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764777600
    VALUES
      LESS THAN (
        '2025-12-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764864000
    VALUES
      LESS THAN (
        '2025-12-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764950400
    VALUES
      LESS THAN (
        '2025-12-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765036800
    VALUES
      LESS THAN (
        '2025-12-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765123200
    VALUES
      LESS THAN (
        '2025-12-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765209600
    VALUES
      LESS THAN (
        '2025-12-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765296000
    VALUES
      LESS THAN (
        '2025-12-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765382400
    VALUES
      LESS THAN (
        '2025-12-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765468800
    VALUES
      LESS THAN (
        '2025-12-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765555200
    VALUES
      LESS THAN (
        '2025-12-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765641600
    VALUES
      LESS THAN (
        '2025-12-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765728000
    VALUES
      LESS THAN (
        '2025-12-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765814400
    VALUES
      LESS THAN (
        '2025-12-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765900800
    VALUES
      LESS THAN (
        '2025-12-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765987200
    VALUES
      LESS THAN (
        '2025-12-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766073600
    VALUES
      LESS THAN (
        '2025-12-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766160000
    VALUES
      LESS THAN (
        '2025-12-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766246400
    VALUES
      LESS THAN (
        '2025-12-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766332800
    VALUES
      LESS THAN (
        '2025-12-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766419200
    VALUES
      LESS THAN (
        '2025-12-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766505600
    VALUES
      LESS THAN (
        '2025-12-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766592000
    VALUES
      LESS THAN (
        '2025-12-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766678400
    VALUES
      LESS THAN (
        '2025-12-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766764800
    VALUES
      LESS THAN (
        '2025-12-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766851200
    VALUES
      LESS THAN (
        '2025-12-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766937600
    VALUES
      LESS THAN (
        '2025-12-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767024000
    VALUES
      LESS THAN (
        '2025-12-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767110400
    VALUES
      LESS THAN (
        '2025-12-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767196800
    VALUES
      LESS THAN (
        '2026-01-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767283200
    VALUES
      LESS THAN (
        '2026-01-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767369600
    VALUES
      LESS THAN (
        '2026-01-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767456000
    VALUES
      LESS THAN (
        '2026-01-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767542400
    VALUES
      LESS THAN (
        '2026-01-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767628800
    VALUES
      LESS THAN (
        '2026-01-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767715200
    VALUES
      LESS THAN (
        '2026-01-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767801600
    VALUES
      LESS THAN (
        '2026-01-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767888000
    VALUES
      LESS THAN (
        '2026-01-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767974400
    VALUES
      LESS THAN (
        '2026-01-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768060800
    VALUES
      LESS THAN (
        '2026-01-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768147200
    VALUES
      LESS THAN (
        '2026-01-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768233600
    VALUES
      LESS THAN (
        '2026-01-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768320000
    VALUES
      LESS THAN (
        '2026-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768406400
    VALUES
      LESS THAN (
        '2026-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768492800
    VALUES
      LESS THAN (
        '2026-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768579200
    VALUES
      LESS THAN (
        '2026-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768665600
    VALUES
      LESS THAN (
        '2026-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768752000
    VALUES
      LESS THAN (
        '2026-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768838400
    VALUES
      LESS THAN (
        '2026-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768924800
    VALUES
      LESS THAN (
        '2026-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769011200
    VALUES
      LESS THAN (
        '2026-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769097600
    VALUES
      LESS THAN (
        '2026-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769184000
    VALUES
      LESS THAN (
        '2026-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769270400
    VALUES
      LESS THAN (
        '2026-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769356800
    VALUES
      LESS THAN (
        '2026-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769443200
    VALUES
      LESS THAN (
        '2026-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769529600
    VALUES
      LESS THAN (
        '2026-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769616000
    VALUES
      LESS THAN (
        '2026-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769702400
    VALUES
      LESS THAN (
        '2026-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769788800
    VALUES
      LESS THAN (
        '2026-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769875200
    VALUES
      LESS THAN (
        '2026-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769961600
    VALUES
      LESS THAN (
        '2026-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770048000
    VALUES
      LESS THAN (
        '2026-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770134400
    VALUES
      LESS THAN (
        '2026-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770220800
    VALUES
      LESS THAN (
        '2026-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770307200
    VALUES
      LESS THAN (
        '2026-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770393600
    VALUES
      LESS THAN (
        '2026-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770480000
    VALUES
      LESS THAN (
        '2026-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770566400
    VALUES
      LESS THAN (
        '2026-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770652800
    VALUES
      LESS THAN (
        '2026-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770739200
    VALUES
      LESS THAN (
        '2026-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770825600
    VALUES
      LESS THAN (
        '2026-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770912000
    VALUES
      LESS THAN (
        '2026-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770998400
    VALUES
      LESS THAN (
        '2026-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771084800
    VALUES
      LESS THAN (
        '2026-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771171200
    VALUES
      LESS THAN (
        '2026-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771257600
    VALUES
      LESS THAN (
        '2026-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771344000
    VALUES
      LESS THAN (
        '2026-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771430400
    VALUES
      LESS THAN (
        '2026-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771516800
    VALUES
      LESS THAN (
        '2026-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771603200
    VALUES
      LESS THAN (
        '2026-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771689600
    VALUES
      LESS THAN (
        '2026-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771776000
    VALUES
      LESS THAN (
        '2026-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771862400
    VALUES
      LESS THAN (
        '2026-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771948800
    VALUES
      LESS THAN (
        '2026-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772035200
    VALUES
      LESS THAN (
        '2026-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772121600
    VALUES
      LESS THAN (
        '2026-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772208000
    VALUES
      LESS THAN (
        '2026-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772294400
    VALUES
      LESS THAN (
        '2026-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772380800
    VALUES
      LESS THAN (
        '2026-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772467200
    VALUES
      LESS THAN (
        '2026-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772553600
    VALUES
      LESS THAN (
        '2026-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772640000
    VALUES
      LESS THAN (
        '2026-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772726400
    VALUES
      LESS THAN (
        '2026-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772812800
    VALUES
      LESS THAN (
        '2026-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772899200
    VALUES
      LESS THAN (
        '2026-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772985600
    VALUES
      LESS THAN (
        '2026-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773072000
    VALUES
      LESS THAN (
        '2026-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773158400
    VALUES
      LESS THAN (
        '2026-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773244800
    VALUES
      LESS THAN (
        '2026-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773331200
    VALUES
      LESS THAN (
        '2026-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773417600
    VALUES
      LESS THAN (
        '2026-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773504000
    VALUES
      LESS THAN (
        '2026-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773590400
    VALUES
      LESS THAN (
        '2026-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773676800
    VALUES
      LESS THAN (
        '2026-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773763200
    VALUES
      LESS THAN (
        '2026-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773849600
    VALUES
      LESS THAN (
        '2026-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773936000
    VALUES
      LESS THAN (
        '2026-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774022400
    VALUES
      LESS THAN (
        '2026-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774108800
    VALUES
      LESS THAN (
        '2026-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774195200
    VALUES
      LESS THAN (
        '2026-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774281600
    VALUES
      LESS THAN (
        '2026-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774368000
    VALUES
      LESS THAN (
        '2026-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774454400
    VALUES
      LESS THAN (
        '2026-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774540800
    VALUES
      LESS THAN (
        '2026-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774627200
    VALUES
      LESS THAN (
        '2026-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774713600
    VALUES
      LESS THAN (
        '2026-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774800000
    VALUES
      LESS THAN (
        '2026-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774886400
    VALUES
      LESS THAN (
        '2026-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774972800
    VALUES
      LESS THAN (
        '2026-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775059200
    VALUES
      LESS THAN (
        '2026-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775145600
    VALUES
      LESS THAN (
        '2026-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775232000
    VALUES
      LESS THAN (
        '2026-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775318400
    VALUES
      LESS THAN (
        '2026-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775404800
    VALUES
      LESS THAN (
        '2026-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775491200
    VALUES
      LESS THAN (
        '2026-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775577600
    VALUES
      LESS THAN (
        '2026-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775664000
    VALUES
      LESS THAN (
        '2026-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775750400
    VALUES
      LESS THAN (
        '2026-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775836800
    VALUES
      LESS THAN (
        '2026-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775923200
    VALUES
      LESS THAN (
        '2026-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776009600
    VALUES
      LESS THAN (
        '2026-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776096000
    VALUES
      LESS THAN (
        '2026-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776182400
    VALUES
      LESS THAN (
        '2026-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776268800
    VALUES
      LESS THAN (
        '2026-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776355200
    VALUES
      LESS THAN (
        '2026-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776441600
    VALUES
      LESS THAN (
        '2026-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776528000
    VALUES
      LESS THAN (
        '2026-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776614400
    VALUES
      LESS THAN (
        '2026-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776700800
    VALUES
      LESS THAN (
        '2026-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776787200
    VALUES
      LESS THAN (
        '2026-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776873600
    VALUES
      LESS THAN (
        '2026-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776960000
    VALUES
      LESS THAN (
        '2026-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777046400
    VALUES
      LESS THAN (
        '2026-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777132800
    VALUES
      LESS THAN (
        '2026-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777219200
    VALUES
      LESS THAN (
        '2026-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777305600
    VALUES
      LESS THAN (
        '2026-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777392000
    VALUES
      LESS THAN (
        '2026-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777478400
    VALUES
      LESS THAN (
        '2026-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777564800
    VALUES
      LESS THAN (
        '2026-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777651200
    VALUES
      LESS THAN (
        '2026-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777737600
    VALUES
      LESS THAN (
        '2026-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777824000
    VALUES
      LESS THAN (
        '2026-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777910400
    VALUES
      LESS THAN (
        '2026-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777996800
    VALUES
      LESS THAN (
        '2026-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778083200
    VALUES
      LESS THAN (
        '2026-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778169600
    VALUES
      LESS THAN (
        '2026-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778256000
    VALUES
      LESS THAN (
        '2026-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778342400
    VALUES
      LESS THAN (
        '2026-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778428800
    VALUES
      LESS THAN (
        '2026-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778515200
    VALUES
      LESS THAN (
        '2026-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778601600
    VALUES
      LESS THAN (
        '2026-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778688000
    VALUES
      LESS THAN (
        '2026-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778774400
    VALUES
      LESS THAN (
        '2026-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778860800
    VALUES
      LESS THAN (
        '2026-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778947200
    VALUES
      LESS THAN (
        '2026-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779033600
    VALUES
      LESS THAN (
        '2026-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779120000
    VALUES
      LESS THAN (
        '2026-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779206400
    VALUES
      LESS THAN (
        '2026-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779292800
    VALUES
      LESS THAN (
        '2026-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779379200
    VALUES
      LESS THAN (
        '2026-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779465600
    VALUES
      LESS THAN (
        '2026-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779552000
    VALUES
      LESS THAN (
        '2026-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779638400
    VALUES
      LESS THAN (
        '2026-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779724800
    VALUES
      LESS THAN (
        '2026-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779811200
    VALUES
      LESS THAN (
        '2026-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779897600
    VALUES
      LESS THAN (
        '2026-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779984000
    VALUES
      LESS THAN (
        '2026-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780070400
    VALUES
      LESS THAN (
        '2026-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780156800
    VALUES
      LESS THAN (
        '2026-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780243200
    VALUES
      LESS THAN (
        '2026-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780329600
    VALUES
      LESS THAN (
        '2026-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780416000
    VALUES
      LESS THAN (
        '2026-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780502400
    VALUES
      LESS THAN (
        '2026-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780588800
    VALUES
      LESS THAN (
        '2026-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780675200
    VALUES
      LESS THAN (
        '2026-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780761600
    VALUES
      LESS THAN (
        '2026-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780848000
    VALUES
      LESS THAN (
        '2026-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780934400
    VALUES
      LESS THAN (
        '2026-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781020800
    VALUES
      LESS THAN (
        '2026-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781107200
    VALUES
      LESS THAN (
        '2026-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781193600
    VALUES
      LESS THAN (
        '2026-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE dwd_cu_real_df IS '用户实名表';

COMMENT ON COLUMN dwd_cu_real_df.usr_id IS '用户ID';

COMMENT ON COLUMN dwd_cu_real_df.real_dt IS '实名认证日期';

COMMENT ON COLUMN dwd_cu_real_df.real_tm IS '实名认证时间';

COMMENT ON COLUMN dwd_cu_real_df.real_way IS '实名认证方式：0子公司同步,1银行卡四要素';

COMMENT ON COLUMN dwd_cu_real_df.real_type IS '实名认证类型：0子公司同步,1财富广场';

COMMENT ON COLUMN dwd_cu_real_df.real_chnl_id IS '实名渠道ID';

COMMENT ON COLUMN dwd_cu_real_df.rgst_chnl_id IS '注册渠道ID';

COMMENT ON COLUMN dwd_cu_real_df.rgst_sec_chnl_nm IS '注册二级渠道';

COMMENT ON COLUMN dwd_cu_real_df.rgst_dt IS '注册日期';

COMMENT ON COLUMN dwd_cu_real_df.ds IS '分区日期';




SET
  search_path = cdm;

CREATE TABLE
  dwd_ch_usr_rltv_df (
    usr_id character varying (256),
    rltv_chnl_id character varying (256),
    create_dt timestamp (0) without TIME zone,
    create_tm timestamp without TIME zone,
    update_tm timestamp without TIME zone,
    rltv_fst_chnl_id character varying (256),
    rltv_fst_chnl_nm character varying (256),
    rltv_sec_chnl_id character varying (256),
    rltv_sec_chnl_nm character varying (256),
    rltv_thd_chnl_id character varying (256),
    rltv_thd_chnl_nm character varying (256),
    rltv_chnl_nm character varying (256),
    rltv_is_sec_oth_chnl character varying (256),
    rltv_is_fst_oth_chnl character varying (256),
    grant_dt timestamp (0) without TIME zone,
    grant_tm timestamp without TIME zone,
    grant_result character varying (256),
    grant_fg character varying (256),
    rltv_usr_status character varying (256),
    rltv_fin_chnl_ind character varying (256),
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '30 days',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(usr_id) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE dwd_ch_usr_rltv_df IS '用户渠道关联授权表';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.usr_id IS '用户ID';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.rltv_chnl_id IS '渠道ID';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.create_dt IS '关联创建日期';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.create_tm IS '关联创建时间';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.update_tm IS '关联修改时间';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.rltv_fst_chnl_id IS '关联一级渠道id';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.rltv_fst_chnl_nm IS '关联一级渠道名称';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.rltv_sec_chnl_id IS '关联二级渠道id';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.rltv_sec_chnl_nm IS '关联二级渠道名称';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.rltv_thd_chnl_id IS '注册三级渠道ID';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.rltv_thd_chnl_nm IS '注册三级渠道名称';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.rltv_chnl_nm IS '关联渠道名称';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.rltv_is_sec_oth_chnl IS '关联是否二级其他渠道';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.rltv_is_fst_oth_chnl IS '关联是否一级其他渠道';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.grant_dt IS '授权日期';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.grant_tm IS '授权时间';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.grant_result IS '授权结果：1授权3无账户4拒绝授权0未授权';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.grant_fg IS '是否授权：1是0否';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.rltv_usr_status IS '用户关联状态: 0正常1已解绑2已删除34历史数据';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.rltv_fin_chnl_ind IS '关联金融渠道标识';

COMMENT ON COLUMN dwd_ch_usr_rltv_df.ds IS '分区字段';


SET
  search_path = cdm;

CREATE TABLE
  dim_cu_usr_info_df (
    usr_id character varying (256),
    rgst_dt character varying (16),
    rgst_tm character varying (128),
    usr_stat_fg character varying (256),
    rgst_enjy_fg character varying (256),
    rgst_type character varying (256),
    rgst_fin_chnl_ind character varying (256),
    rgst_fst_chnl_id character varying (256),
    rgst_fst_chnl_nm character varying (256),
    rgst_sec_chnl_id character varying (256),
    rgst_sec_chnl_nm character varying (256),
    rgst_thd_chnl_id character varying (256),
    rgst_thd_chnl_nm character varying (256),
    rgst_chnl_id character varying (256),
    rgst_chnl_nm character varying (256),
    rgst_act_id character varying (256),
    rgst_prot_ver character varying (256),
    real_fg character varying (16),
    real_dt character varying (16),
    real_tm character varying (128),
    real_way character varying (16),
    real_type character varying (16),
    real_chnl_id character varying (256),
    usr_real_name_md5 character varying (256),
    usr_sex character varying (256),
    usr_birthday timestamp (0) without TIME zone,
    usr_phone_erpt character varying (256),
    usr_idcardno_erpt character varying (256),
    usr_idcardno_type character varying (256),
    fst_debt_card_fg character varying (256),
    fst_bind_crdt_fg character varying (256),
    intl_chnl_id character varying (256),
    mobile_score character varying (256),
    allow_login_fg character varying (256),
    first_enter_stat_cd character varying (256),
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE,
    period = '1 day',
    ttl = '10 years'
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(usr_id) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1768320000
    VALUES
      LESS THAN (
        '2026-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768406400
    VALUES
      LESS THAN (
        '2026-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768492800
    VALUES
      LESS THAN (
        '2026-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768579200
    VALUES
      LESS THAN (
        '2026-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768665600
    VALUES
      LESS THAN (
        '2026-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768752000
    VALUES
      LESS THAN (
        '2026-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768838400
    VALUES
      LESS THAN (
        '2026-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768924800
    VALUES
      LESS THAN (
        '2026-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769011200
    VALUES
      LESS THAN (
        '2026-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769097600
    VALUES
      LESS THAN (
        '2026-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769184000
    VALUES
      LESS THAN (
        '2026-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769270400
    VALUES
      LESS THAN (
        '2026-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769356800
    VALUES
      LESS THAN (
        '2026-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769443200
    VALUES
      LESS THAN (
        '2026-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769529600
    VALUES
      LESS THAN (
        '2026-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769616000
    VALUES
      LESS THAN (
        '2026-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769702400
    VALUES
      LESS THAN (
        '2026-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769788800
    VALUES
      LESS THAN (
        '2026-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769875200
    VALUES
      LESS THAN (
        '2026-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769961600
    VALUES
      LESS THAN (
        '2026-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770048000
    VALUES
      LESS THAN (
        '2026-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770134400
    VALUES
      LESS THAN (
        '2026-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770220800
    VALUES
      LESS THAN (
        '2026-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770307200
    VALUES
      LESS THAN (
        '2026-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770393600
    VALUES
      LESS THAN (
        '2026-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770480000
    VALUES
      LESS THAN (
        '2026-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770566400
    VALUES
      LESS THAN (
        '2026-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770652800
    VALUES
      LESS THAN (
        '2026-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770739200
    VALUES
      LESS THAN (
        '2026-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770825600
    VALUES
      LESS THAN (
        '2026-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770912000
    VALUES
      LESS THAN (
        '2026-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770998400
    VALUES
      LESS THAN (
        '2026-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771084800
    VALUES
      LESS THAN (
        '2026-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771171200
    VALUES
      LESS THAN (
        '2026-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771257600
    VALUES
      LESS THAN (
        '2026-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771344000
    VALUES
      LESS THAN (
        '2026-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771430400
    VALUES
      LESS THAN (
        '2026-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771516800
    VALUES
      LESS THAN (
        '2026-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771603200
    VALUES
      LESS THAN (
        '2026-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771689600
    VALUES
      LESS THAN (
        '2026-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771776000
    VALUES
      LESS THAN (
        '2026-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771862400
    VALUES
      LESS THAN (
        '2026-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771948800
    VALUES
      LESS THAN (
        '2026-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772035200
    VALUES
      LESS THAN (
        '2026-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772121600
    VALUES
      LESS THAN (
        '2026-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772208000
    VALUES
      LESS THAN (
        '2026-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772294400
    VALUES
      LESS THAN (
        '2026-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772380800
    VALUES
      LESS THAN (
        '2026-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772467200
    VALUES
      LESS THAN (
        '2026-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772553600
    VALUES
      LESS THAN (
        '2026-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772640000
    VALUES
      LESS THAN (
        '2026-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772726400
    VALUES
      LESS THAN (
        '2026-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772812800
    VALUES
      LESS THAN (
        '2026-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772899200
    VALUES
      LESS THAN (
        '2026-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772985600
    VALUES
      LESS THAN (
        '2026-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773072000
    VALUES
      LESS THAN (
        '2026-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773158400
    VALUES
      LESS THAN (
        '2026-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773244800
    VALUES
      LESS THAN (
        '2026-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773331200
    VALUES
      LESS THAN (
        '2026-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773417600
    VALUES
      LESS THAN (
        '2026-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773504000
    VALUES
      LESS THAN (
        '2026-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773590400
    VALUES
      LESS THAN (
        '2026-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773676800
    VALUES
      LESS THAN (
        '2026-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773763200
    VALUES
      LESS THAN (
        '2026-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773849600
    VALUES
      LESS THAN (
        '2026-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773936000
    VALUES
      LESS THAN (
        '2026-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774022400
    VALUES
      LESS THAN (
        '2026-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774108800
    VALUES
      LESS THAN (
        '2026-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774195200
    VALUES
      LESS THAN (
        '2026-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774281600
    VALUES
      LESS THAN (
        '2026-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774368000
    VALUES
      LESS THAN (
        '2026-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774454400
    VALUES
      LESS THAN (
        '2026-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774540800
    VALUES
      LESS THAN (
        '2026-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774627200
    VALUES
      LESS THAN (
        '2026-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774713600
    VALUES
      LESS THAN (
        '2026-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774800000
    VALUES
      LESS THAN (
        '2026-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774886400
    VALUES
      LESS THAN (
        '2026-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774972800
    VALUES
      LESS THAN (
        '2026-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775059200
    VALUES
      LESS THAN (
        '2026-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775145600
    VALUES
      LESS THAN (
        '2026-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775232000
    VALUES
      LESS THAN (
        '2026-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775318400
    VALUES
      LESS THAN (
        '2026-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775404800
    VALUES
      LESS THAN (
        '2026-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775491200
    VALUES
      LESS THAN (
        '2026-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775577600
    VALUES
      LESS THAN (
        '2026-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775664000
    VALUES
      LESS THAN (
        '2026-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775750400
    VALUES
      LESS THAN (
        '2026-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775836800
    VALUES
      LESS THAN (
        '2026-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775923200
    VALUES
      LESS THAN (
        '2026-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776009600
    VALUES
      LESS THAN (
        '2026-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776096000
    VALUES
      LESS THAN (
        '2026-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776182400
    VALUES
      LESS THAN (
        '2026-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776268800
    VALUES
      LESS THAN (
        '2026-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776355200
    VALUES
      LESS THAN (
        '2026-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776441600
    VALUES
      LESS THAN (
        '2026-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776528000
    VALUES
      LESS THAN (
        '2026-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776614400
    VALUES
      LESS THAN (
        '2026-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776700800
    VALUES
      LESS THAN (
        '2026-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776787200
    VALUES
      LESS THAN (
        '2026-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776873600
    VALUES
      LESS THAN (
        '2026-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776960000
    VALUES
      LESS THAN (
        '2026-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777046400
    VALUES
      LESS THAN (
        '2026-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777132800
    VALUES
      LESS THAN (
        '2026-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777219200
    VALUES
      LESS THAN (
        '2026-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777305600
    VALUES
      LESS THAN (
        '2026-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777392000
    VALUES
      LESS THAN (
        '2026-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777478400
    VALUES
      LESS THAN (
        '2026-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777564800
    VALUES
      LESS THAN (
        '2026-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777651200
    VALUES
      LESS THAN (
        '2026-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777737600
    VALUES
      LESS THAN (
        '2026-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777824000
    VALUES
      LESS THAN (
        '2026-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777910400
    VALUES
      LESS THAN (
        '2026-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777996800
    VALUES
      LESS THAN (
        '2026-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778083200
    VALUES
      LESS THAN (
        '2026-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778169600
    VALUES
      LESS THAN (
        '2026-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778256000
    VALUES
      LESS THAN (
        '2026-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778342400
    VALUES
      LESS THAN (
        '2026-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778428800
    VALUES
      LESS THAN (
        '2026-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778515200
    VALUES
      LESS THAN (
        '2026-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778601600
    VALUES
      LESS THAN (
        '2026-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778688000
    VALUES
      LESS THAN (
        '2026-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778774400
    VALUES
      LESS THAN (
        '2026-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778860800
    VALUES
      LESS THAN (
        '2026-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778947200
    VALUES
      LESS THAN (
        '2026-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779033600
    VALUES
      LESS THAN (
        '2026-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779120000
    VALUES
      LESS THAN (
        '2026-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779206400
    VALUES
      LESS THAN (
        '2026-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779292800
    VALUES
      LESS THAN (
        '2026-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779379200
    VALUES
      LESS THAN (
        '2026-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779465600
    VALUES
      LESS THAN (
        '2026-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779552000
    VALUES
      LESS THAN (
        '2026-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779638400
    VALUES
      LESS THAN (
        '2026-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779724800
    VALUES
      LESS THAN (
        '2026-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779811200
    VALUES
      LESS THAN (
        '2026-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779897600
    VALUES
      LESS THAN (
        '2026-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779984000
    VALUES
      LESS THAN (
        '2026-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780070400
    VALUES
      LESS THAN (
        '2026-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780156800
    VALUES
      LESS THAN (
        '2026-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780243200
    VALUES
      LESS THAN (
        '2026-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780329600
    VALUES
      LESS THAN (
        '2026-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780416000
    VALUES
      LESS THAN (
        '2026-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780502400
    VALUES
      LESS THAN (
        '2026-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780588800
    VALUES
      LESS THAN (
        '2026-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780675200
    VALUES
      LESS THAN (
        '2026-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780761600
    VALUES
      LESS THAN (
        '2026-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780848000
    VALUES
      LESS THAN (
        '2026-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780934400
    VALUES
      LESS THAN (
        '2026-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781020800
    VALUES
      LESS THAN (
        '2026-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781107200
    VALUES
      LESS THAN (
        '2026-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781193600
    VALUES
      LESS THAN (
        '2026-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE dim_cu_usr_info_df IS '注册用户信息维度表';

COMMENT ON COLUMN dim_cu_usr_info_df.usr_id IS '用户ID';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_dt IS '注册日期';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_tm IS '注册时间';

COMMENT ON COLUMN dim_cu_usr_info_df.usr_stat_fg IS '用户状态：1有效,0注销';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_enjy_fg IS '是否优享升级客户：1是0否';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_type IS '注册类型：0（子公司）同步注册1登录注册';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_fin_chnl_ind IS '注册金融渠道标识';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_fst_chnl_id IS '注册一级渠道ID';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_fst_chnl_nm IS '注册一级渠道名称';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_sec_chnl_id IS '注册二级渠道ID';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_sec_chnl_nm IS '注册二级渠道名称';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_thd_chnl_id IS '注册三级渠道ID';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_thd_chnl_nm IS '注册三级渠道名称';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_chnl_id IS '注册渠道ID';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_chnl_nm IS '注册渠道名称';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_act_id IS '注册活动ID';

COMMENT ON COLUMN dim_cu_usr_info_df.rgst_prot_ver IS '注册协议版本';

COMMENT ON COLUMN dim_cu_usr_info_df.real_fg IS '是否实名：1是0否';

COMMENT ON COLUMN dim_cu_usr_info_df.real_dt IS '实名认证日期';

COMMENT ON COLUMN dim_cu_usr_info_df.real_tm IS '实名认证时间';

COMMENT ON COLUMN dim_cu_usr_info_df.real_way IS '实名认证方式：0子公司同步,1银行卡四要素';

COMMENT ON COLUMN dim_cu_usr_info_df.real_type IS '实名认证类型：0子公司同步,1财富广场';

COMMENT ON COLUMN dim_cu_usr_info_df.real_chnl_id IS '实名渠道ID';

COMMENT ON COLUMN dim_cu_usr_info_df.usr_real_name_md5 IS '用户姓名加密（sm3）';

COMMENT ON COLUMN dim_cu_usr_info_df.usr_sex IS '用户性别1:男,2:女';

COMMENT ON COLUMN dim_cu_usr_info_df.usr_birthday IS '用户生日';

COMMENT ON COLUMN dim_cu_usr_info_df.usr_phone_erpt IS '用户手机号加密（aes）';

COMMENT ON COLUMN dim_cu_usr_info_df.usr_idcardno_erpt IS '身份证号加密（aes）';

COMMENT ON COLUMN dim_cu_usr_info_df.usr_idcardno_type IS '证件类型：01-居民身份证;02-军官证;03-护照;04-回乡证(港澳);05-台胞证;06-警官证;07-士兵证;99-其它证件';

COMMENT ON COLUMN dim_cu_usr_info_df.fst_debt_card_fg IS '首次绑定借记卡';

COMMENT ON COLUMN dim_cu_usr_info_df.fst_bind_crdt_fg IS '首次绑定信用卡';

COMMENT ON COLUMN dim_cu_usr_info_df.intl_chnl_id IS '用户初始渠道ID';

COMMENT ON COLUMN dim_cu_usr_info_df.mobile_score IS '手机号信誉评分';

COMMENT ON COLUMN dim_cu_usr_info_df.allow_login_fg IS '允许登录标志';

COMMENT ON COLUMN dim_cu_usr_info_df.first_enter_stat_cd IS '首次进入系统状态代码';


SET
  search_path = cdm;

CREATE TABLE
  dim_ch_chl_df (
    chnl_id character varying (128),
    chnl_nm character varying (128),
    chnl_stat character varying (128),
    chnl_dc character varying (128),
    thd_chnl_id character varying (128),
    thd_chnl_nm character varying (128),
    thd_chnl_stat character varying (128),
    thd_chnl_dc character varying (128),
    sec_chnl_id character varying (128),
    sec_chnl_nm character varying (128),
    sec_chnl_stat character varying (128),
    sec_chnl_dc character varying (128),
    fst_chnl_id character varying (128),
    fst_chnl_nm character varying (128),
    fst_chnl_stat character varying (128),
    fst_chnl_dc character varying (128),
    chnl_lvl character varying (128),
    fin_chnl_flg character varying (128),
    auto_auth_fg character varying (128),
    wallet_fg character varying (128),
    chnl_effect_dt character varying (10),
    effect_tm timestamp without TIME zone,
    is_sec_oth_chnl character varying (128),
    is_fst_oth_chnl character varying (128),
    chnl_type character varying (128),
    chnl_sub_nm character varying (128),
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE,
    period = '1 day',
    ttl = '90 days'
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY REPLICATION TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1781193600
    VALUES
      LESS THAN (
        '2026-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE dim_ch_chl_df IS '渠道维度表';

COMMENT ON COLUMN dim_ch_chl_df.chnl_id IS '四级渠道ID';

COMMENT ON COLUMN dim_ch_chl_df.chnl_nm IS '四级渠道名称';

COMMENT ON COLUMN dim_ch_chl_df.chnl_stat IS '四级渠道状态';

COMMENT ON COLUMN dim_ch_chl_df.chnl_dc IS '四级渠道描述';

COMMENT ON COLUMN dim_ch_chl_df.thd_chnl_id IS '三级渠道ID';

COMMENT ON COLUMN dim_ch_chl_df.thd_chnl_nm IS '三级渠道名称';

COMMENT ON COLUMN dim_ch_chl_df.thd_chnl_stat IS '三级渠道状态';

COMMENT ON COLUMN dim_ch_chl_df.thd_chnl_dc IS '三级渠道描述';

COMMENT ON COLUMN dim_ch_chl_df.sec_chnl_id IS '二级渠道ID';

COMMENT ON COLUMN dim_ch_chl_df.sec_chnl_nm IS '二级渠道名称';

COMMENT ON COLUMN dim_ch_chl_df.sec_chnl_stat IS '二级渠道状态';

COMMENT ON COLUMN dim_ch_chl_df.sec_chnl_dc IS '二级渠道描述';

COMMENT ON COLUMN dim_ch_chl_df.fst_chnl_id IS '一级渠道ID';

COMMENT ON COLUMN dim_ch_chl_df.fst_chnl_nm IS '一级渠道名称';

COMMENT ON COLUMN dim_ch_chl_df.fst_chnl_stat IS '一级渠道状态';

COMMENT ON COLUMN dim_ch_chl_df.fst_chnl_dc IS '一级渠道描述';

COMMENT ON COLUMN dim_ch_chl_df.chnl_lvl IS '渠道等级';

COMMENT ON COLUMN dim_ch_chl_df.fin_chnl_flg IS '金融渠道标识';

COMMENT ON COLUMN dim_ch_chl_df.auto_auth_fg IS '自动授权标识';

COMMENT ON COLUMN dim_ch_chl_df.wallet_fg IS '支持钱包标识';

COMMENT ON COLUMN dim_ch_chl_df.chnl_effect_dt IS '生效日期';

COMMENT ON COLUMN dim_ch_chl_df.effect_tm IS '生效时间';

COMMENT ON COLUMN dim_ch_chl_df.is_sec_oth_chnl IS '是否二级其他渠道';

COMMENT ON COLUMN dim_ch_chl_df.is_fst_oth_chnl IS '是否一级其他渠道';

COMMENT ON COLUMN dim_ch_chl_df.chnl_type IS '渠道类型';

COMMENT ON COLUMN dim_ch_chl_df.chnl_sub_nm IS '报送渠道名称';

SET
  search_path = rec;

CREATE TABLE
  ads_rgst_chnl_cnt_df (
    data_dt timestamp (0) without TIME zone,
    fst_lvl_chnl_id character varying (128),
    fst_lvl_chnl_nm character varying (128),
    sec_chnl_id character varying (128),
    sec_chnl_nm character varying (128),
    thd_cls_chnl_id character varying (128),
    thd_cls_chnl_nm character varying (128),
    new_rgst_cnt_d bigint,
    new_rgst_cnt_7d bigint,
    new_rgst_cnt_m bigint,
    new_rgst_cnt_y bigint,
    new_rgst_cnt_a bigint,
    fin_chnl_flg character varying (128),
    chnl_type character varying (128),
    chnl_sub_nm character varying (128),
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '10 years',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(data_dt) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1
    VALUES
      LESS THAN (
        '2025-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752595200
    VALUES
      LESS THAN (
        '2025-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752681600
    VALUES
      LESS THAN (
        '2025-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752768000
    VALUES
      LESS THAN (
        '2025-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752854400
    VALUES
      LESS THAN (
        '2025-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752940800
    VALUES
      LESS THAN (
        '2025-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753027200
    VALUES
      LESS THAN (
        '2025-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753113600
    VALUES
      LESS THAN (
        '2025-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753200000
    VALUES
      LESS THAN (
        '2025-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753286400
    VALUES
      LESS THAN (
        '2025-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753372800
    VALUES
      LESS THAN (
        '2025-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753459200
    VALUES
      LESS THAN (
        '2025-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753545600
    VALUES
      LESS THAN (
        '2025-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753632000
    VALUES
      LESS THAN (
        '2025-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753718400
    VALUES
      LESS THAN (
        '2025-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753804800
    VALUES
      LESS THAN (
        '2025-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753891200
    VALUES
      LESS THAN (
        '2025-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753977600
    VALUES
      LESS THAN (
        '2025-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754064000
    VALUES
      LESS THAN (
        '2025-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754150400
    VALUES
      LESS THAN (
        '2025-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754236800
    VALUES
      LESS THAN (
        '2025-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754323200
    VALUES
      LESS THAN (
        '2025-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754409600
    VALUES
      LESS THAN (
        '2025-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754496000
    VALUES
      LESS THAN (
        '2025-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754582400
    VALUES
      LESS THAN (
        '2025-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754668800
    VALUES
      LESS THAN (
        '2025-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754755200
    VALUES
      LESS THAN (
        '2025-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754841600
    VALUES
      LESS THAN (
        '2025-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754928000
    VALUES
      LESS THAN (
        '2025-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755014400
    VALUES
      LESS THAN (
        '2025-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755100800
    VALUES
      LESS THAN (
        '2025-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755187200
    VALUES
      LESS THAN (
        '2025-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755273600
    VALUES
      LESS THAN (
        '2025-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755360000
    VALUES
      LESS THAN (
        '2025-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755446400
    VALUES
      LESS THAN (
        '2025-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755532800
    VALUES
      LESS THAN (
        '2025-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755619200
    VALUES
      LESS THAN (
        '2025-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755705600
    VALUES
      LESS THAN (
        '2025-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755792000
    VALUES
      LESS THAN (
        '2025-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755878400
    VALUES
      LESS THAN (
        '2025-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755964800
    VALUES
      LESS THAN (
        '2025-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756051200
    VALUES
      LESS THAN (
        '2025-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756137600
    VALUES
      LESS THAN (
        '2025-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756224000
    VALUES
      LESS THAN (
        '2025-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756310400
    VALUES
      LESS THAN (
        '2025-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756396800
    VALUES
      LESS THAN (
        '2025-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756483200
    VALUES
      LESS THAN (
        '2025-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756569600
    VALUES
      LESS THAN (
        '2025-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756656000
    VALUES
      LESS THAN (
        '2025-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756742400
    VALUES
      LESS THAN (
        '2025-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756828800
    VALUES
      LESS THAN (
        '2025-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756915200
    VALUES
      LESS THAN (
        '2025-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757001600
    VALUES
      LESS THAN (
        '2025-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757088000
    VALUES
      LESS THAN (
        '2025-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757174400
    VALUES
      LESS THAN (
        '2025-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757260800
    VALUES
      LESS THAN (
        '2025-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757347200
    VALUES
      LESS THAN (
        '2025-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757433600
    VALUES
      LESS THAN (
        '2025-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757520000
    VALUES
      LESS THAN (
        '2025-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757606400
    VALUES
      LESS THAN (
        '2025-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757692800
    VALUES
      LESS THAN (
        '2025-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757779200
    VALUES
      LESS THAN (
        '2025-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757865600
    VALUES
      LESS THAN (
        '2025-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757952000
    VALUES
      LESS THAN (
        '2025-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758038400
    VALUES
      LESS THAN (
        '2025-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758124800
    VALUES
      LESS THAN (
        '2025-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758211200
    VALUES
      LESS THAN (
        '2025-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758297600
    VALUES
      LESS THAN (
        '2025-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758384000
    VALUES
      LESS THAN (
        '2025-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758470400
    VALUES
      LESS THAN (
        '2025-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758556800
    VALUES
      LESS THAN (
        '2025-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758643200
    VALUES
      LESS THAN (
        '2025-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758729600
    VALUES
      LESS THAN (
        '2025-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758816000
    VALUES
      LESS THAN (
        '2025-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758902400
    VALUES
      LESS THAN (
        '2025-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758988800
    VALUES
      LESS THAN (
        '2025-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759075200
    VALUES
      LESS THAN (
        '2025-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759161600
    VALUES
      LESS THAN (
        '2025-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759248000
    VALUES
      LESS THAN (
        '2025-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759334400
    VALUES
      LESS THAN (
        '2025-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759420800
    VALUES
      LESS THAN (
        '2025-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759507200
    VALUES
      LESS THAN (
        '2025-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759593600
    VALUES
      LESS THAN (
        '2025-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759680000
    VALUES
      LESS THAN (
        '2025-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759766400
    VALUES
      LESS THAN (
        '2025-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759852800
    VALUES
      LESS THAN (
        '2025-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759939200
    VALUES
      LESS THAN (
        '2025-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760025600
    VALUES
      LESS THAN (
        '2025-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760112000
    VALUES
      LESS THAN (
        '2025-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760198400
    VALUES
      LESS THAN (
        '2025-10-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760284800
    VALUES
      LESS THAN (
        '2025-10-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760371200
    VALUES
      LESS THAN (
        '2025-10-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760457600
    VALUES
      LESS THAN (
        '2025-10-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760544000
    VALUES
      LESS THAN (
        '2025-10-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760630400
    VALUES
      LESS THAN (
        '2025-10-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760716800
    VALUES
      LESS THAN (
        '2025-10-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760803200
    VALUES
      LESS THAN (
        '2025-10-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760889600
    VALUES
      LESS THAN (
        '2025-10-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760976000
    VALUES
      LESS THAN (
        '2025-10-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761062400
    VALUES
      LESS THAN (
        '2025-10-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761148800
    VALUES
      LESS THAN (
        '2025-10-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761235200
    VALUES
      LESS THAN (
        '2025-10-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761321600
    VALUES
      LESS THAN (
        '2025-10-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761408000
    VALUES
      LESS THAN (
        '2025-10-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761494400
    VALUES
      LESS THAN (
        '2025-10-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761580800
    VALUES
      LESS THAN (
        '2025-10-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761667200
    VALUES
      LESS THAN (
        '2025-10-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761753600
    VALUES
      LESS THAN (
        '2025-10-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761840000
    VALUES
      LESS THAN (
        '2025-10-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761926400
    VALUES
      LESS THAN (
        '2025-11-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762012800
    VALUES
      LESS THAN (
        '2025-11-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762099200
    VALUES
      LESS THAN (
        '2025-11-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762185600
    VALUES
      LESS THAN (
        '2025-11-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762272000
    VALUES
      LESS THAN (
        '2025-11-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762358400
    VALUES
      LESS THAN (
        '2025-11-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762444800
    VALUES
      LESS THAN (
        '2025-11-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762531200
    VALUES
      LESS THAN (
        '2025-11-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762617600
    VALUES
      LESS THAN (
        '2025-11-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762704000
    VALUES
      LESS THAN (
        '2025-11-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762790400
    VALUES
      LESS THAN (
        '2025-11-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762876800
    VALUES
      LESS THAN (
        '2025-11-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762963200
    VALUES
      LESS THAN (
        '2025-11-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763049600
    VALUES
      LESS THAN (
        '2025-11-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763136000
    VALUES
      LESS THAN (
        '2025-11-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763222400
    VALUES
      LESS THAN (
        '2025-11-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763308800
    VALUES
      LESS THAN (
        '2025-11-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763395200
    VALUES
      LESS THAN (
        '2025-11-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763481600
    VALUES
      LESS THAN (
        '2025-11-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763568000
    VALUES
      LESS THAN (
        '2025-11-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763654400
    VALUES
      LESS THAN (
        '2025-11-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763740800
    VALUES
      LESS THAN (
        '2025-11-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763827200
    VALUES
      LESS THAN (
        '2025-11-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763913600
    VALUES
      LESS THAN (
        '2025-11-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764000000
    VALUES
      LESS THAN (
        '2025-11-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764086400
    VALUES
      LESS THAN (
        '2025-11-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764172800
    VALUES
      LESS THAN (
        '2025-11-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764259200
    VALUES
      LESS THAN (
        '2025-11-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764345600
    VALUES
      LESS THAN (
        '2025-11-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764432000
    VALUES
      LESS THAN (
        '2025-11-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764518400
    VALUES
      LESS THAN (
        '2025-12-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764604800
    VALUES
      LESS THAN (
        '2025-12-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764691200
    VALUES
      LESS THAN (
        '2025-12-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764777600
    VALUES
      LESS THAN (
        '2025-12-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764864000
    VALUES
      LESS THAN (
        '2025-12-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764950400
    VALUES
      LESS THAN (
        '2025-12-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765036800
    VALUES
      LESS THAN (
        '2025-12-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765123200
    VALUES
      LESS THAN (
        '2025-12-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765209600
    VALUES
      LESS THAN (
        '2025-12-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765296000
    VALUES
      LESS THAN (
        '2025-12-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765382400
    VALUES
      LESS THAN (
        '2025-12-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765468800
    VALUES
      LESS THAN (
        '2025-12-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765555200
    VALUES
      LESS THAN (
        '2025-12-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765641600
    VALUES
      LESS THAN (
        '2025-12-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765728000
    VALUES
      LESS THAN (
        '2025-12-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765814400
    VALUES
      LESS THAN (
        '2025-12-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765900800
    VALUES
      LESS THAN (
        '2025-12-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765987200
    VALUES
      LESS THAN (
        '2025-12-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766073600
    VALUES
      LESS THAN (
        '2025-12-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766160000
    VALUES
      LESS THAN (
        '2025-12-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766246400
    VALUES
      LESS THAN (
        '2025-12-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766332800
    VALUES
      LESS THAN (
        '2025-12-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766419200
    VALUES
      LESS THAN (
        '2025-12-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766505600
    VALUES
      LESS THAN (
        '2025-12-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766592000
    VALUES
      LESS THAN (
        '2025-12-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766678400
    VALUES
      LESS THAN (
        '2025-12-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766764800
    VALUES
      LESS THAN (
        '2025-12-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766851200
    VALUES
      LESS THAN (
        '2025-12-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766937600
    VALUES
      LESS THAN (
        '2025-12-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767024000
    VALUES
      LESS THAN (
        '2025-12-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767110400
    VALUES
      LESS THAN (
        '2025-12-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767196800
    VALUES
      LESS THAN (
        '2026-01-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767283200
    VALUES
      LESS THAN (
        '2026-01-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767369600
    VALUES
      LESS THAN (
        '2026-01-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767456000
    VALUES
      LESS THAN (
        '2026-01-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767542400
    VALUES
      LESS THAN (
        '2026-01-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767628800
    VALUES
      LESS THAN (
        '2026-01-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767715200
    VALUES
      LESS THAN (
        '2026-01-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767801600
    VALUES
      LESS THAN (
        '2026-01-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767888000
    VALUES
      LESS THAN (
        '2026-01-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767974400
    VALUES
      LESS THAN (
        '2026-01-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768060800
    VALUES
      LESS THAN (
        '2026-01-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768147200
    VALUES
      LESS THAN (
        '2026-01-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768233600
    VALUES
      LESS THAN (
        '2026-01-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768320000
    VALUES
      LESS THAN (
        '2026-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768406400
    VALUES
      LESS THAN (
        '2026-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768492800
    VALUES
      LESS THAN (
        '2026-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768579200
    VALUES
      LESS THAN (
        '2026-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768665600
    VALUES
      LESS THAN (
        '2026-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768752000
    VALUES
      LESS THAN (
        '2026-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768838400
    VALUES
      LESS THAN (
        '2026-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768924800
    VALUES
      LESS THAN (
        '2026-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769011200
    VALUES
      LESS THAN (
        '2026-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769097600
    VALUES
      LESS THAN (
        '2026-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769184000
    VALUES
      LESS THAN (
        '2026-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769270400
    VALUES
      LESS THAN (
        '2026-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769356800
    VALUES
      LESS THAN (
        '2026-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769443200
    VALUES
      LESS THAN (
        '2026-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769529600
    VALUES
      LESS THAN (
        '2026-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769616000
    VALUES
      LESS THAN (
        '2026-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769702400
    VALUES
      LESS THAN (
        '2026-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769788800
    VALUES
      LESS THAN (
        '2026-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769875200
    VALUES
      LESS THAN (
        '2026-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769961600
    VALUES
      LESS THAN (
        '2026-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770048000
    VALUES
      LESS THAN (
        '2026-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770134400
    VALUES
      LESS THAN (
        '2026-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770220800
    VALUES
      LESS THAN (
        '2026-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770307200
    VALUES
      LESS THAN (
        '2026-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770393600
    VALUES
      LESS THAN (
        '2026-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770480000
    VALUES
      LESS THAN (
        '2026-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770566400
    VALUES
      LESS THAN (
        '2026-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770652800
    VALUES
      LESS THAN (
        '2026-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770739200
    VALUES
      LESS THAN (
        '2026-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770825600
    VALUES
      LESS THAN (
        '2026-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770912000
    VALUES
      LESS THAN (
        '2026-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770998400
    VALUES
      LESS THAN (
        '2026-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771084800
    VALUES
      LESS THAN (
        '2026-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771171200
    VALUES
      LESS THAN (
        '2026-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771257600
    VALUES
      LESS THAN (
        '2026-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771344000
    VALUES
      LESS THAN (
        '2026-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771430400
    VALUES
      LESS THAN (
        '2026-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771516800
    VALUES
      LESS THAN (
        '2026-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771603200
    VALUES
      LESS THAN (
        '2026-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771689600
    VALUES
      LESS THAN (
        '2026-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771776000
    VALUES
      LESS THAN (
        '2026-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771862400
    VALUES
      LESS THAN (
        '2026-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771948800
    VALUES
      LESS THAN (
        '2026-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772035200
    VALUES
      LESS THAN (
        '2026-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772121600
    VALUES
      LESS THAN (
        '2026-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772208000
    VALUES
      LESS THAN (
        '2026-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772294400
    VALUES
      LESS THAN (
        '2026-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772380800
    VALUES
      LESS THAN (
        '2026-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772467200
    VALUES
      LESS THAN (
        '2026-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772553600
    VALUES
      LESS THAN (
        '2026-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772640000
    VALUES
      LESS THAN (
        '2026-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772726400
    VALUES
      LESS THAN (
        '2026-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772812800
    VALUES
      LESS THAN (
        '2026-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772899200
    VALUES
      LESS THAN (
        '2026-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772985600
    VALUES
      LESS THAN (
        '2026-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773072000
    VALUES
      LESS THAN (
        '2026-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773158400
    VALUES
      LESS THAN (
        '2026-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773244800
    VALUES
      LESS THAN (
        '2026-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773331200
    VALUES
      LESS THAN (
        '2026-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773417600
    VALUES
      LESS THAN (
        '2026-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773504000
    VALUES
      LESS THAN (
        '2026-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773590400
    VALUES
      LESS THAN (
        '2026-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773676800
    VALUES
      LESS THAN (
        '2026-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773763200
    VALUES
      LESS THAN (
        '2026-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773849600
    VALUES
      LESS THAN (
        '2026-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773936000
    VALUES
      LESS THAN (
        '2026-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774022400
    VALUES
      LESS THAN (
        '2026-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774108800
    VALUES
      LESS THAN (
        '2026-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774195200
    VALUES
      LESS THAN (
        '2026-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774281600
    VALUES
      LESS THAN (
        '2026-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774368000
    VALUES
      LESS THAN (
        '2026-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774454400
    VALUES
      LESS THAN (
        '2026-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774540800
    VALUES
      LESS THAN (
        '2026-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774627200
    VALUES
      LESS THAN (
        '2026-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774713600
    VALUES
      LESS THAN (
        '2026-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774800000
    VALUES
      LESS THAN (
        '2026-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774886400
    VALUES
      LESS THAN (
        '2026-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774972800
    VALUES
      LESS THAN (
        '2026-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775059200
    VALUES
      LESS THAN (
        '2026-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775145600
    VALUES
      LESS THAN (
        '2026-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775232000
    VALUES
      LESS THAN (
        '2026-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775318400
    VALUES
      LESS THAN (
        '2026-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775404800
    VALUES
      LESS THAN (
        '2026-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775491200
    VALUES
      LESS THAN (
        '2026-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775577600
    VALUES
      LESS THAN (
        '2026-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775664000
    VALUES
      LESS THAN (
        '2026-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775750400
    VALUES
      LESS THAN (
        '2026-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775836800
    VALUES
      LESS THAN (
        '2026-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775923200
    VALUES
      LESS THAN (
        '2026-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776009600
    VALUES
      LESS THAN (
        '2026-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776096000
    VALUES
      LESS THAN (
        '2026-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776182400
    VALUES
      LESS THAN (
        '2026-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776268800
    VALUES
      LESS THAN (
        '2026-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776355200
    VALUES
      LESS THAN (
        '2026-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776441600
    VALUES
      LESS THAN (
        '2026-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776528000
    VALUES
      LESS THAN (
        '2026-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776614400
    VALUES
      LESS THAN (
        '2026-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776700800
    VALUES
      LESS THAN (
        '2026-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776787200
    VALUES
      LESS THAN (
        '2026-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776873600
    VALUES
      LESS THAN (
        '2026-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776960000
    VALUES
      LESS THAN (
        '2026-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777046400
    VALUES
      LESS THAN (
        '2026-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777132800
    VALUES
      LESS THAN (
        '2026-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777219200
    VALUES
      LESS THAN (
        '2026-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777305600
    VALUES
      LESS THAN (
        '2026-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777392000
    VALUES
      LESS THAN (
        '2026-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777478400
    VALUES
      LESS THAN (
        '2026-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777564800
    VALUES
      LESS THAN (
        '2026-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777651200
    VALUES
      LESS THAN (
        '2026-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777737600
    VALUES
      LESS THAN (
        '2026-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777824000
    VALUES
      LESS THAN (
        '2026-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777910400
    VALUES
      LESS THAN (
        '2026-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777996800
    VALUES
      LESS THAN (
        '2026-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778083200
    VALUES
      LESS THAN (
        '2026-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778169600
    VALUES
      LESS THAN (
        '2026-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778256000
    VALUES
      LESS THAN (
        '2026-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778342400
    VALUES
      LESS THAN (
        '2026-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778428800
    VALUES
      LESS THAN (
        '2026-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778515200
    VALUES
      LESS THAN (
        '2026-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778601600
    VALUES
      LESS THAN (
        '2026-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778688000
    VALUES
      LESS THAN (
        '2026-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778774400
    VALUES
      LESS THAN (
        '2026-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778860800
    VALUES
      LESS THAN (
        '2026-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778947200
    VALUES
      LESS THAN (
        '2026-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779033600
    VALUES
      LESS THAN (
        '2026-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779120000
    VALUES
      LESS THAN (
        '2026-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779206400
    VALUES
      LESS THAN (
        '2026-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779292800
    VALUES
      LESS THAN (
        '2026-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779379200
    VALUES
      LESS THAN (
        '2026-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779465600
    VALUES
      LESS THAN (
        '2026-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779552000
    VALUES
      LESS THAN (
        '2026-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779638400
    VALUES
      LESS THAN (
        '2026-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779724800
    VALUES
      LESS THAN (
        '2026-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779811200
    VALUES
      LESS THAN (
        '2026-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779897600
    VALUES
      LESS THAN (
        '2026-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779984000
    VALUES
      LESS THAN (
        '2026-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780070400
    VALUES
      LESS THAN (
        '2026-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780156800
    VALUES
      LESS THAN (
        '2026-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780243200
    VALUES
      LESS THAN (
        '2026-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780329600
    VALUES
      LESS THAN (
        '2026-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780416000
    VALUES
      LESS THAN (
        '2026-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780502400
    VALUES
      LESS THAN (
        '2026-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780588800
    VALUES
      LESS THAN (
        '2026-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780675200
    VALUES
      LESS THAN (
        '2026-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780761600
    VALUES
      LESS THAN (
        '2026-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780848000
    VALUES
      LESS THAN (
        '2026-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780934400
    VALUES
      LESS THAN (
        '2026-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781020800
    VALUES
      LESS THAN (
        '2026-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781107200
    VALUES
      LESS THAN (
        '2026-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781193600
    VALUES
      LESS THAN (
        '2026-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE ads_rgst_chnl_cnt_df IS '整体分渠道_注册用户数_日度';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.data_dt IS '日期';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.fst_lvl_chnl_id IS '一级渠道ID';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.fst_lvl_chnl_nm IS '一级渠道名称';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.sec_chnl_id IS '二级渠道ID';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.sec_chnl_nm IS '二级渠道名称';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.thd_cls_chnl_id IS '三级渠道ID';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.thd_cls_chnl_nm IS '三级渠道名称';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.new_rgst_cnt_d IS '当日_新增注册用户数';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.new_rgst_cnt_7d IS '近7日_新增注册用户数';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.new_rgst_cnt_m IS '当月_新增注册用户数';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.new_rgst_cnt_y IS '当年累计_新增注册用户数';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.new_rgst_cnt_a IS '历史累计_新增注册用户数';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.fin_chnl_flg IS '金融渠道标识';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.chnl_type IS '渠道类型';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.chnl_sub_nm IS '报送渠道名称';

COMMENT ON COLUMN ads_rgst_chnl_cnt_df.ds IS '分区日期';



SET
  search_path = rec;

CREATE TABLE
  ads_rgst_raw_chnl_cnt_df (
    data_dt timestamp (0) without TIME zone,
    raw_rgst_sec_chnl_nm character varying (128),
    rgst_enjy_fg character varying (128),
    rgst_type character varying (128),
    new_rgst_cnt_d bigint,
    new_rgst_cnt_7d bigint,
    new_rgst_cnt_m bigint,
    new_rgst_cnt_y bigint,
    new_rgst_cnt_a bigint,
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '10 years',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(data_dt) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1
    VALUES
      LESS THAN (
        '2025-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753200000
    VALUES
      LESS THAN (
        '2025-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753286400
    VALUES
      LESS THAN (
        '2025-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753372800
    VALUES
      LESS THAN (
        '2025-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753459200
    VALUES
      LESS THAN (
        '2025-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753545600
    VALUES
      LESS THAN (
        '2025-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753632000
    VALUES
      LESS THAN (
        '2025-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753718400
    VALUES
      LESS THAN (
        '2025-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753804800
    VALUES
      LESS THAN (
        '2025-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753891200
    VALUES
      LESS THAN (
        '2025-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753977600
    VALUES
      LESS THAN (
        '2025-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754064000
    VALUES
      LESS THAN (
        '2025-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754150400
    VALUES
      LESS THAN (
        '2025-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754236800
    VALUES
      LESS THAN (
        '2025-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754323200
    VALUES
      LESS THAN (
        '2025-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754409600
    VALUES
      LESS THAN (
        '2025-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754496000
    VALUES
      LESS THAN (
        '2025-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754582400
    VALUES
      LESS THAN (
        '2025-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754668800
    VALUES
      LESS THAN (
        '2025-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754755200
    VALUES
      LESS THAN (
        '2025-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754841600
    VALUES
      LESS THAN (
        '2025-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754928000
    VALUES
      LESS THAN (
        '2025-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755014400
    VALUES
      LESS THAN (
        '2025-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755100800
    VALUES
      LESS THAN (
        '2025-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755187200
    VALUES
      LESS THAN (
        '2025-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755273600
    VALUES
      LESS THAN (
        '2025-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755360000
    VALUES
      LESS THAN (
        '2025-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755446400
    VALUES
      LESS THAN (
        '2025-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755532800
    VALUES
      LESS THAN (
        '2025-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755619200
    VALUES
      LESS THAN (
        '2025-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755705600
    VALUES
      LESS THAN (
        '2025-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755792000
    VALUES
      LESS THAN (
        '2025-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755878400
    VALUES
      LESS THAN (
        '2025-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755964800
    VALUES
      LESS THAN (
        '2025-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756051200
    VALUES
      LESS THAN (
        '2025-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756137600
    VALUES
      LESS THAN (
        '2025-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756224000
    VALUES
      LESS THAN (
        '2025-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756310400
    VALUES
      LESS THAN (
        '2025-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756396800
    VALUES
      LESS THAN (
        '2025-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756483200
    VALUES
      LESS THAN (
        '2025-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756569600
    VALUES
      LESS THAN (
        '2025-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756656000
    VALUES
      LESS THAN (
        '2025-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756742400
    VALUES
      LESS THAN (
        '2025-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756828800
    VALUES
      LESS THAN (
        '2025-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756915200
    VALUES
      LESS THAN (
        '2025-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757001600
    VALUES
      LESS THAN (
        '2025-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757088000
    VALUES
      LESS THAN (
        '2025-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757174400
    VALUES
      LESS THAN (
        '2025-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757260800
    VALUES
      LESS THAN (
        '2025-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757347200
    VALUES
      LESS THAN (
        '2025-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757433600
    VALUES
      LESS THAN (
        '2025-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757520000
    VALUES
      LESS THAN (
        '2025-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757606400
    VALUES
      LESS THAN (
        '2025-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757692800
    VALUES
      LESS THAN (
        '2025-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757779200
    VALUES
      LESS THAN (
        '2025-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757865600
    VALUES
      LESS THAN (
        '2025-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757952000
    VALUES
      LESS THAN (
        '2025-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758038400
    VALUES
      LESS THAN (
        '2025-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758124800
    VALUES
      LESS THAN (
        '2025-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758211200
    VALUES
      LESS THAN (
        '2025-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758297600
    VALUES
      LESS THAN (
        '2025-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758384000
    VALUES
      LESS THAN (
        '2025-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758470400
    VALUES
      LESS THAN (
        '2025-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758556800
    VALUES
      LESS THAN (
        '2025-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758643200
    VALUES
      LESS THAN (
        '2025-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758729600
    VALUES
      LESS THAN (
        '2025-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758816000
    VALUES
      LESS THAN (
        '2025-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758902400
    VALUES
      LESS THAN (
        '2025-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758988800
    VALUES
      LESS THAN (
        '2025-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759075200
    VALUES
      LESS THAN (
        '2025-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759161600
    VALUES
      LESS THAN (
        '2025-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759248000
    VALUES
      LESS THAN (
        '2025-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759334400
    VALUES
      LESS THAN (
        '2025-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759420800
    VALUES
      LESS THAN (
        '2025-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759507200
    VALUES
      LESS THAN (
        '2025-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759593600
    VALUES
      LESS THAN (
        '2025-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759680000
    VALUES
      LESS THAN (
        '2025-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759766400
    VALUES
      LESS THAN (
        '2025-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759852800
    VALUES
      LESS THAN (
        '2025-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759939200
    VALUES
      LESS THAN (
        '2025-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760025600
    VALUES
      LESS THAN (
        '2025-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760112000
    VALUES
      LESS THAN (
        '2025-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760198400
    VALUES
      LESS THAN (
        '2025-10-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760284800
    VALUES
      LESS THAN (
        '2025-10-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760371200
    VALUES
      LESS THAN (
        '2025-10-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760457600
    VALUES
      LESS THAN (
        '2025-10-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760544000
    VALUES
      LESS THAN (
        '2025-10-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760630400
    VALUES
      LESS THAN (
        '2025-10-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760716800
    VALUES
      LESS THAN (
        '2025-10-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760803200
    VALUES
      LESS THAN (
        '2025-10-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760889600
    VALUES
      LESS THAN (
        '2025-10-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760976000
    VALUES
      LESS THAN (
        '2025-10-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761062400
    VALUES
      LESS THAN (
        '2025-10-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761148800
    VALUES
      LESS THAN (
        '2025-10-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761235200
    VALUES
      LESS THAN (
        '2025-10-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761321600
    VALUES
      LESS THAN (
        '2025-10-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761408000
    VALUES
      LESS THAN (
        '2025-10-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761494400
    VALUES
      LESS THAN (
        '2025-10-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761580800
    VALUES
      LESS THAN (
        '2025-10-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761667200
    VALUES
      LESS THAN (
        '2025-10-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761753600
    VALUES
      LESS THAN (
        '2025-10-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761840000
    VALUES
      LESS THAN (
        '2025-10-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761926400
    VALUES
      LESS THAN (
        '2025-11-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762012800
    VALUES
      LESS THAN (
        '2025-11-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762099200
    VALUES
      LESS THAN (
        '2025-11-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762185600
    VALUES
      LESS THAN (
        '2025-11-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762272000
    VALUES
      LESS THAN (
        '2025-11-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762358400
    VALUES
      LESS THAN (
        '2025-11-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762444800
    VALUES
      LESS THAN (
        '2025-11-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762531200
    VALUES
      LESS THAN (
        '2025-11-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762617600
    VALUES
      LESS THAN (
        '2025-11-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762704000
    VALUES
      LESS THAN (
        '2025-11-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762790400
    VALUES
      LESS THAN (
        '2025-11-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762876800
    VALUES
      LESS THAN (
        '2025-11-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762963200
    VALUES
      LESS THAN (
        '2025-11-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763049600
    VALUES
      LESS THAN (
        '2025-11-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763136000
    VALUES
      LESS THAN (
        '2025-11-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763222400
    VALUES
      LESS THAN (
        '2025-11-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763308800
    VALUES
      LESS THAN (
        '2025-11-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763395200
    VALUES
      LESS THAN (
        '2025-11-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763481600
    VALUES
      LESS THAN (
        '2025-11-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763568000
    VALUES
      LESS THAN (
        '2025-11-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763654400
    VALUES
      LESS THAN (
        '2025-11-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763740800
    VALUES
      LESS THAN (
        '2025-11-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763827200
    VALUES
      LESS THAN (
        '2025-11-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763913600
    VALUES
      LESS THAN (
        '2025-11-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764000000
    VALUES
      LESS THAN (
        '2025-11-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764086400
    VALUES
      LESS THAN (
        '2025-11-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764172800
    VALUES
      LESS THAN (
        '2025-11-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764259200
    VALUES
      LESS THAN (
        '2025-11-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764345600
    VALUES
      LESS THAN (
        '2025-11-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764432000
    VALUES
      LESS THAN (
        '2025-11-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764518400
    VALUES
      LESS THAN (
        '2025-12-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764604800
    VALUES
      LESS THAN (
        '2025-12-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764691200
    VALUES
      LESS THAN (
        '2025-12-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764777600
    VALUES
      LESS THAN (
        '2025-12-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764864000
    VALUES
      LESS THAN (
        '2025-12-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764950400
    VALUES
      LESS THAN (
        '2025-12-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765036800
    VALUES
      LESS THAN (
        '2025-12-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765123200
    VALUES
      LESS THAN (
        '2025-12-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765209600
    VALUES
      LESS THAN (
        '2025-12-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765296000
    VALUES
      LESS THAN (
        '2025-12-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765382400
    VALUES
      LESS THAN (
        '2025-12-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765468800
    VALUES
      LESS THAN (
        '2025-12-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765555200
    VALUES
      LESS THAN (
        '2025-12-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765641600
    VALUES
      LESS THAN (
        '2025-12-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765728000
    VALUES
      LESS THAN (
        '2025-12-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765814400
    VALUES
      LESS THAN (
        '2025-12-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765900800
    VALUES
      LESS THAN (
        '2025-12-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765987200
    VALUES
      LESS THAN (
        '2025-12-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766073600
    VALUES
      LESS THAN (
        '2025-12-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766160000
    VALUES
      LESS THAN (
        '2025-12-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766246400
    VALUES
      LESS THAN (
        '2025-12-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766332800
    VALUES
      LESS THAN (
        '2025-12-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766419200
    VALUES
      LESS THAN (
        '2025-12-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766505600
    VALUES
      LESS THAN (
        '2025-12-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766592000
    VALUES
      LESS THAN (
        '2025-12-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766678400
    VALUES
      LESS THAN (
        '2025-12-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766764800
    VALUES
      LESS THAN (
        '2025-12-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766851200
    VALUES
      LESS THAN (
        '2025-12-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766937600
    VALUES
      LESS THAN (
        '2025-12-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767024000
    VALUES
      LESS THAN (
        '2025-12-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767110400
    VALUES
      LESS THAN (
        '2025-12-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767196800
    VALUES
      LESS THAN (
        '2026-01-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767283200
    VALUES
      LESS THAN (
        '2026-01-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767369600
    VALUES
      LESS THAN (
        '2026-01-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767456000
    VALUES
      LESS THAN (
        '2026-01-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767542400
    VALUES
      LESS THAN (
        '2026-01-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767628800
    VALUES
      LESS THAN (
        '2026-01-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767715200
    VALUES
      LESS THAN (
        '2026-01-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767801600
    VALUES
      LESS THAN (
        '2026-01-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767888000
    VALUES
      LESS THAN (
        '2026-01-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767974400
    VALUES
      LESS THAN (
        '2026-01-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768060800
    VALUES
      LESS THAN (
        '2026-01-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768147200
    VALUES
      LESS THAN (
        '2026-01-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768233600
    VALUES
      LESS THAN (
        '2026-01-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768320000
    VALUES
      LESS THAN (
        '2026-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768406400
    VALUES
      LESS THAN (
        '2026-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768492800
    VALUES
      LESS THAN (
        '2026-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768579200
    VALUES
      LESS THAN (
        '2026-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768665600
    VALUES
      LESS THAN (
        '2026-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768752000
    VALUES
      LESS THAN (
        '2026-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768838400
    VALUES
      LESS THAN (
        '2026-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768924800
    VALUES
      LESS THAN (
        '2026-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769011200
    VALUES
      LESS THAN (
        '2026-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769097600
    VALUES
      LESS THAN (
        '2026-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769184000
    VALUES
      LESS THAN (
        '2026-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769270400
    VALUES
      LESS THAN (
        '2026-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769356800
    VALUES
      LESS THAN (
        '2026-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769443200
    VALUES
      LESS THAN (
        '2026-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769529600
    VALUES
      LESS THAN (
        '2026-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769616000
    VALUES
      LESS THAN (
        '2026-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769702400
    VALUES
      LESS THAN (
        '2026-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769788800
    VALUES
      LESS THAN (
        '2026-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769875200
    VALUES
      LESS THAN (
        '2026-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769961600
    VALUES
      LESS THAN (
        '2026-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770048000
    VALUES
      LESS THAN (
        '2026-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770134400
    VALUES
      LESS THAN (
        '2026-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770220800
    VALUES
      LESS THAN (
        '2026-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770307200
    VALUES
      LESS THAN (
        '2026-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770393600
    VALUES
      LESS THAN (
        '2026-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770480000
    VALUES
      LESS THAN (
        '2026-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770566400
    VALUES
      LESS THAN (
        '2026-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770652800
    VALUES
      LESS THAN (
        '2026-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770739200
    VALUES
      LESS THAN (
        '2026-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770825600
    VALUES
      LESS THAN (
        '2026-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770912000
    VALUES
      LESS THAN (
        '2026-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770998400
    VALUES
      LESS THAN (
        '2026-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771084800
    VALUES
      LESS THAN (
        '2026-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771171200
    VALUES
      LESS THAN (
        '2026-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771257600
    VALUES
      LESS THAN (
        '2026-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771344000
    VALUES
      LESS THAN (
        '2026-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771430400
    VALUES
      LESS THAN (
        '2026-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771516800
    VALUES
      LESS THAN (
        '2026-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771603200
    VALUES
      LESS THAN (
        '2026-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771689600
    VALUES
      LESS THAN (
        '2026-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771776000
    VALUES
      LESS THAN (
        '2026-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771862400
    VALUES
      LESS THAN (
        '2026-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771948800
    VALUES
      LESS THAN (
        '2026-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772035200
    VALUES
      LESS THAN (
        '2026-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772121600
    VALUES
      LESS THAN (
        '2026-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772208000
    VALUES
      LESS THAN (
        '2026-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772294400
    VALUES
      LESS THAN (
        '2026-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772380800
    VALUES
      LESS THAN (
        '2026-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772467200
    VALUES
      LESS THAN (
        '2026-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772553600
    VALUES
      LESS THAN (
        '2026-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772640000
    VALUES
      LESS THAN (
        '2026-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772726400
    VALUES
      LESS THAN (
        '2026-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772812800
    VALUES
      LESS THAN (
        '2026-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772899200
    VALUES
      LESS THAN (
        '2026-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772985600
    VALUES
      LESS THAN (
        '2026-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773072000
    VALUES
      LESS THAN (
        '2026-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773158400
    VALUES
      LESS THAN (
        '2026-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773244800
    VALUES
      LESS THAN (
        '2026-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773331200
    VALUES
      LESS THAN (
        '2026-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773417600
    VALUES
      LESS THAN (
        '2026-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773504000
    VALUES
      LESS THAN (
        '2026-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773590400
    VALUES
      LESS THAN (
        '2026-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773676800
    VALUES
      LESS THAN (
        '2026-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773763200
    VALUES
      LESS THAN (
        '2026-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773849600
    VALUES
      LESS THAN (
        '2026-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773936000
    VALUES
      LESS THAN (
        '2026-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774022400
    VALUES
      LESS THAN (
        '2026-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774108800
    VALUES
      LESS THAN (
        '2026-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774195200
    VALUES
      LESS THAN (
        '2026-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774281600
    VALUES
      LESS THAN (
        '2026-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774368000
    VALUES
      LESS THAN (
        '2026-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774454400
    VALUES
      LESS THAN (
        '2026-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774540800
    VALUES
      LESS THAN (
        '2026-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774627200
    VALUES
      LESS THAN (
        '2026-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774713600
    VALUES
      LESS THAN (
        '2026-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774800000
    VALUES
      LESS THAN (
        '2026-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774886400
    VALUES
      LESS THAN (
        '2026-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774972800
    VALUES
      LESS THAN (
        '2026-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775059200
    VALUES
      LESS THAN (
        '2026-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775145600
    VALUES
      LESS THAN (
        '2026-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775232000
    VALUES
      LESS THAN (
        '2026-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775318400
    VALUES
      LESS THAN (
        '2026-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775404800
    VALUES
      LESS THAN (
        '2026-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775491200
    VALUES
      LESS THAN (
        '2026-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775577600
    VALUES
      LESS THAN (
        '2026-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775664000
    VALUES
      LESS THAN (
        '2026-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775750400
    VALUES
      LESS THAN (
        '2026-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775836800
    VALUES
      LESS THAN (
        '2026-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775923200
    VALUES
      LESS THAN (
        '2026-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776009600
    VALUES
      LESS THAN (
        '2026-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776096000
    VALUES
      LESS THAN (
        '2026-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776182400
    VALUES
      LESS THAN (
        '2026-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776268800
    VALUES
      LESS THAN (
        '2026-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776355200
    VALUES
      LESS THAN (
        '2026-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776441600
    VALUES
      LESS THAN (
        '2026-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776528000
    VALUES
      LESS THAN (
        '2026-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776614400
    VALUES
      LESS THAN (
        '2026-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776700800
    VALUES
      LESS THAN (
        '2026-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776787200
    VALUES
      LESS THAN (
        '2026-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776873600
    VALUES
      LESS THAN (
        '2026-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776960000
    VALUES
      LESS THAN (
        '2026-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777046400
    VALUES
      LESS THAN (
        '2026-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777132800
    VALUES
      LESS THAN (
        '2026-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777219200
    VALUES
      LESS THAN (
        '2026-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777305600
    VALUES
      LESS THAN (
        '2026-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777392000
    VALUES
      LESS THAN (
        '2026-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777478400
    VALUES
      LESS THAN (
        '2026-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777564800
    VALUES
      LESS THAN (
        '2026-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777651200
    VALUES
      LESS THAN (
        '2026-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777737600
    VALUES
      LESS THAN (
        '2026-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777824000
    VALUES
      LESS THAN (
        '2026-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777910400
    VALUES
      LESS THAN (
        '2026-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777996800
    VALUES
      LESS THAN (
        '2026-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778083200
    VALUES
      LESS THAN (
        '2026-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778169600
    VALUES
      LESS THAN (
        '2026-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778256000
    VALUES
      LESS THAN (
        '2026-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778342400
    VALUES
      LESS THAN (
        '2026-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778428800
    VALUES
      LESS THAN (
        '2026-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778515200
    VALUES
      LESS THAN (
        '2026-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778601600
    VALUES
      LESS THAN (
        '2026-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778688000
    VALUES
      LESS THAN (
        '2026-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778774400
    VALUES
      LESS THAN (
        '2026-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778860800
    VALUES
      LESS THAN (
        '2026-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778947200
    VALUES
      LESS THAN (
        '2026-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779033600
    VALUES
      LESS THAN (
        '2026-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779120000
    VALUES
      LESS THAN (
        '2026-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779206400
    VALUES
      LESS THAN (
        '2026-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779292800
    VALUES
      LESS THAN (
        '2026-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779379200
    VALUES
      LESS THAN (
        '2026-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779465600
    VALUES
      LESS THAN (
        '2026-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779552000
    VALUES
      LESS THAN (
        '2026-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779638400
    VALUES
      LESS THAN (
        '2026-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779724800
    VALUES
      LESS THAN (
        '2026-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779811200
    VALUES
      LESS THAN (
        '2026-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779897600
    VALUES
      LESS THAN (
        '2026-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779984000
    VALUES
      LESS THAN (
        '2026-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780070400
    VALUES
      LESS THAN (
        '2026-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780156800
    VALUES
      LESS THAN (
        '2026-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780243200
    VALUES
      LESS THAN (
        '2026-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780329600
    VALUES
      LESS THAN (
        '2026-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780416000
    VALUES
      LESS THAN (
        '2026-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780502400
    VALUES
      LESS THAN (
        '2026-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780588800
    VALUES
      LESS THAN (
        '2026-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780675200
    VALUES
      LESS THAN (
        '2026-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780761600
    VALUES
      LESS THAN (
        '2026-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780848000
    VALUES
      LESS THAN (
        '2026-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780934400
    VALUES
      LESS THAN (
        '2026-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781020800
    VALUES
      LESS THAN (
        '2026-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781107200
    VALUES
      LESS THAN (
        '2026-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781193600
    VALUES
      LESS THAN (
        '2026-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791734400
    VALUES
      LESS THAN (
        '2026-10-12 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE ads_rgst_raw_chnl_cnt_df IS '原始注册渠道_注册用户数_日度';

COMMENT ON COLUMN ads_rgst_raw_chnl_cnt_df.data_dt IS '数据日期';

COMMENT ON COLUMN ads_rgst_raw_chnl_cnt_df.raw_rgst_sec_chnl_nm IS '注册二级渠道（原始渠道）';

COMMENT ON COLUMN ads_rgst_raw_chnl_cnt_df.rgst_enjy_fg IS '是否优享升级客户：1是0否';

COMMENT ON COLUMN ads_rgst_raw_chnl_cnt_df.rgst_type IS '注册类型：0同步注册1登录注册';

COMMENT ON COLUMN ads_rgst_raw_chnl_cnt_df.new_rgst_cnt_d IS '当日_新增注册用户数';

COMMENT ON COLUMN ads_rgst_raw_chnl_cnt_df.new_rgst_cnt_7d IS '近7日_新增注册用户数';

COMMENT ON COLUMN ads_rgst_raw_chnl_cnt_df.new_rgst_cnt_m IS '当月_新增注册用户数';

COMMENT ON COLUMN ads_rgst_raw_chnl_cnt_df.new_rgst_cnt_y IS '当年累计_新增注册用户数';

COMMENT ON COLUMN ads_rgst_raw_chnl_cnt_df.new_rgst_cnt_a IS '历史累计_新增注册用户数';

COMMENT ON COLUMN ads_rgst_raw_chnl_cnt_df.ds IS '分区日期';


SET
  search_path = rec;

CREATE TABLE
  ads_rgst_act_chnl_cnt_df (
    data_dt timestamp (0) without TIME zone,
    raw_rgst_sec_chnl_nm character varying (128),
    act_rgst_sec_chnl_nm character varying (128),
    act_rgst_chnl_sub_nm character varying (128),
    act_rgst_cnt_d bigint,
    act_rgst_cnt_7d bigint,
    act_rgst_cnt_m bigint,
    act_rgst_cnt_y bigint,
    act_rgst_cnt_a bigint,
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '10 years',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(data_dt) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1
    VALUES
      LESS THAN (
        '2025-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752595200
    VALUES
      LESS THAN (
        '2025-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752681600
    VALUES
      LESS THAN (
        '2025-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752768000
    VALUES
      LESS THAN (
        '2025-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752854400
    VALUES
      LESS THAN (
        '2025-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752940800
    VALUES
      LESS THAN (
        '2025-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753027200
    VALUES
      LESS THAN (
        '2025-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753113600
    VALUES
      LESS THAN (
        '2025-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753200000
    VALUES
      LESS THAN (
        '2025-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753286400
    VALUES
      LESS THAN (
        '2025-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753372800
    VALUES
      LESS THAN (
        '2025-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753459200
    VALUES
      LESS THAN (
        '2025-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753545600
    VALUES
      LESS THAN (
        '2025-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753632000
    VALUES
      LESS THAN (
        '2025-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753718400
    VALUES
      LESS THAN (
        '2025-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753804800
    VALUES
      LESS THAN (
        '2025-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753891200
    VALUES
      LESS THAN (
        '2025-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753977600
    VALUES
      LESS THAN (
        '2025-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754064000
    VALUES
      LESS THAN (
        '2025-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754150400
    VALUES
      LESS THAN (
        '2025-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754236800
    VALUES
      LESS THAN (
        '2025-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754323200
    VALUES
      LESS THAN (
        '2025-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754409600
    VALUES
      LESS THAN (
        '2025-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754496000
    VALUES
      LESS THAN (
        '2025-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754582400
    VALUES
      LESS THAN (
        '2025-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754668800
    VALUES
      LESS THAN (
        '2025-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754755200
    VALUES
      LESS THAN (
        '2025-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754841600
    VALUES
      LESS THAN (
        '2025-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754928000
    VALUES
      LESS THAN (
        '2025-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755014400
    VALUES
      LESS THAN (
        '2025-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755100800
    VALUES
      LESS THAN (
        '2025-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755187200
    VALUES
      LESS THAN (
        '2025-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755273600
    VALUES
      LESS THAN (
        '2025-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755360000
    VALUES
      LESS THAN (
        '2025-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755446400
    VALUES
      LESS THAN (
        '2025-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755532800
    VALUES
      LESS THAN (
        '2025-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755619200
    VALUES
      LESS THAN (
        '2025-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755705600
    VALUES
      LESS THAN (
        '2025-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755792000
    VALUES
      LESS THAN (
        '2025-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755878400
    VALUES
      LESS THAN (
        '2025-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755964800
    VALUES
      LESS THAN (
        '2025-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756051200
    VALUES
      LESS THAN (
        '2025-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756137600
    VALUES
      LESS THAN (
        '2025-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756224000
    VALUES
      LESS THAN (
        '2025-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756310400
    VALUES
      LESS THAN (
        '2025-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756396800
    VALUES
      LESS THAN (
        '2025-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756483200
    VALUES
      LESS THAN (
        '2025-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756569600
    VALUES
      LESS THAN (
        '2025-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756656000
    VALUES
      LESS THAN (
        '2025-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756742400
    VALUES
      LESS THAN (
        '2025-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756828800
    VALUES
      LESS THAN (
        '2025-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756915200
    VALUES
      LESS THAN (
        '2025-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757001600
    VALUES
      LESS THAN (
        '2025-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757088000
    VALUES
      LESS THAN (
        '2025-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757174400
    VALUES
      LESS THAN (
        '2025-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757260800
    VALUES
      LESS THAN (
        '2025-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757347200
    VALUES
      LESS THAN (
        '2025-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757433600
    VALUES
      LESS THAN (
        '2025-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757520000
    VALUES
      LESS THAN (
        '2025-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757606400
    VALUES
      LESS THAN (
        '2025-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757692800
    VALUES
      LESS THAN (
        '2025-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757779200
    VALUES
      LESS THAN (
        '2025-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757865600
    VALUES
      LESS THAN (
        '2025-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757952000
    VALUES
      LESS THAN (
        '2025-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758038400
    VALUES
      LESS THAN (
        '2025-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758124800
    VALUES
      LESS THAN (
        '2025-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758211200
    VALUES
      LESS THAN (
        '2025-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758297600
    VALUES
      LESS THAN (
        '2025-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758384000
    VALUES
      LESS THAN (
        '2025-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758470400
    VALUES
      LESS THAN (
        '2025-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758556800
    VALUES
      LESS THAN (
        '2025-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758643200
    VALUES
      LESS THAN (
        '2025-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758729600
    VALUES
      LESS THAN (
        '2025-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758816000
    VALUES
      LESS THAN (
        '2025-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758902400
    VALUES
      LESS THAN (
        '2025-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758988800
    VALUES
      LESS THAN (
        '2025-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759075200
    VALUES
      LESS THAN (
        '2025-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759161600
    VALUES
      LESS THAN (
        '2025-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759248000
    VALUES
      LESS THAN (
        '2025-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759334400
    VALUES
      LESS THAN (
        '2025-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759420800
    VALUES
      LESS THAN (
        '2025-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759507200
    VALUES
      LESS THAN (
        '2025-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759593600
    VALUES
      LESS THAN (
        '2025-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759680000
    VALUES
      LESS THAN (
        '2025-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759766400
    VALUES
      LESS THAN (
        '2025-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759852800
    VALUES
      LESS THAN (
        '2025-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759939200
    VALUES
      LESS THAN (
        '2025-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760025600
    VALUES
      LESS THAN (
        '2025-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760112000
    VALUES
      LESS THAN (
        '2025-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760198400
    VALUES
      LESS THAN (
        '2025-10-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760284800
    VALUES
      LESS THAN (
        '2025-10-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760371200
    VALUES
      LESS THAN (
        '2025-10-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760457600
    VALUES
      LESS THAN (
        '2025-10-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760544000
    VALUES
      LESS THAN (
        '2025-10-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760630400
    VALUES
      LESS THAN (
        '2025-10-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760716800
    VALUES
      LESS THAN (
        '2025-10-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760803200
    VALUES
      LESS THAN (
        '2025-10-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760889600
    VALUES
      LESS THAN (
        '2025-10-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760976000
    VALUES
      LESS THAN (
        '2025-10-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761062400
    VALUES
      LESS THAN (
        '2025-10-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761148800
    VALUES
      LESS THAN (
        '2025-10-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761235200
    VALUES
      LESS THAN (
        '2025-10-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761321600
    VALUES
      LESS THAN (
        '2025-10-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761408000
    VALUES
      LESS THAN (
        '2025-10-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761494400
    VALUES
      LESS THAN (
        '2025-10-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761580800
    VALUES
      LESS THAN (
        '2025-10-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761667200
    VALUES
      LESS THAN (
        '2025-10-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761753600
    VALUES
      LESS THAN (
        '2025-10-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761840000
    VALUES
      LESS THAN (
        '2025-10-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761926400
    VALUES
      LESS THAN (
        '2025-11-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762012800
    VALUES
      LESS THAN (
        '2025-11-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762099200
    VALUES
      LESS THAN (
        '2025-11-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762185600
    VALUES
      LESS THAN (
        '2025-11-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762272000
    VALUES
      LESS THAN (
        '2025-11-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762358400
    VALUES
      LESS THAN (
        '2025-11-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762444800
    VALUES
      LESS THAN (
        '2025-11-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762531200
    VALUES
      LESS THAN (
        '2025-11-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762617600
    VALUES
      LESS THAN (
        '2025-11-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762704000
    VALUES
      LESS THAN (
        '2025-11-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762790400
    VALUES
      LESS THAN (
        '2025-11-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762876800
    VALUES
      LESS THAN (
        '2025-11-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762963200
    VALUES
      LESS THAN (
        '2025-11-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763049600
    VALUES
      LESS THAN (
        '2025-11-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763136000
    VALUES
      LESS THAN (
        '2025-11-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763222400
    VALUES
      LESS THAN (
        '2025-11-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763308800
    VALUES
      LESS THAN (
        '2025-11-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763395200
    VALUES
      LESS THAN (
        '2025-11-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763481600
    VALUES
      LESS THAN (
        '2025-11-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763568000
    VALUES
      LESS THAN (
        '2025-11-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763654400
    VALUES
      LESS THAN (
        '2025-11-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763740800
    VALUES
      LESS THAN (
        '2025-11-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763827200
    VALUES
      LESS THAN (
        '2025-11-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763913600
    VALUES
      LESS THAN (
        '2025-11-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764000000
    VALUES
      LESS THAN (
        '2025-11-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764086400
    VALUES
      LESS THAN (
        '2025-11-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764172800
    VALUES
      LESS THAN (
        '2025-11-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764259200
    VALUES
      LESS THAN (
        '2025-11-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764345600
    VALUES
      LESS THAN (
        '2025-11-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764432000
    VALUES
      LESS THAN (
        '2025-11-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764518400
    VALUES
      LESS THAN (
        '2025-12-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764604800
    VALUES
      LESS THAN (
        '2025-12-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764691200
    VALUES
      LESS THAN (
        '2025-12-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764777600
    VALUES
      LESS THAN (
        '2025-12-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764864000
    VALUES
      LESS THAN (
        '2025-12-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764950400
    VALUES
      LESS THAN (
        '2025-12-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765036800
    VALUES
      LESS THAN (
        '2025-12-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765123200
    VALUES
      LESS THAN (
        '2025-12-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765209600
    VALUES
      LESS THAN (
        '2025-12-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765296000
    VALUES
      LESS THAN (
        '2025-12-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765382400
    VALUES
      LESS THAN (
        '2025-12-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765468800
    VALUES
      LESS THAN (
        '2025-12-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765555200
    VALUES
      LESS THAN (
        '2025-12-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765641600
    VALUES
      LESS THAN (
        '2025-12-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765728000
    VALUES
      LESS THAN (
        '2025-12-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765814400
    VALUES
      LESS THAN (
        '2025-12-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765900800
    VALUES
      LESS THAN (
        '2025-12-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765987200
    VALUES
      LESS THAN (
        '2025-12-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766073600
    VALUES
      LESS THAN (
        '2025-12-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766160000
    VALUES
      LESS THAN (
        '2025-12-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766246400
    VALUES
      LESS THAN (
        '2025-12-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766332800
    VALUES
      LESS THAN (
        '2025-12-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766419200
    VALUES
      LESS THAN (
        '2025-12-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766505600
    VALUES
      LESS THAN (
        '2025-12-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766592000
    VALUES
      LESS THAN (
        '2025-12-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766678400
    VALUES
      LESS THAN (
        '2025-12-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766764800
    VALUES
      LESS THAN (
        '2025-12-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766851200
    VALUES
      LESS THAN (
        '2025-12-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766937600
    VALUES
      LESS THAN (
        '2025-12-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767024000
    VALUES
      LESS THAN (
        '2025-12-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767110400
    VALUES
      LESS THAN (
        '2025-12-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767196800
    VALUES
      LESS THAN (
        '2026-01-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767283200
    VALUES
      LESS THAN (
        '2026-01-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767369600
    VALUES
      LESS THAN (
        '2026-01-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767456000
    VALUES
      LESS THAN (
        '2026-01-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767542400
    VALUES
      LESS THAN (
        '2026-01-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767628800
    VALUES
      LESS THAN (
        '2026-01-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767715200
    VALUES
      LESS THAN (
        '2026-01-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767801600
    VALUES
      LESS THAN (
        '2026-01-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767888000
    VALUES
      LESS THAN (
        '2026-01-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767974400
    VALUES
      LESS THAN (
        '2026-01-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768060800
    VALUES
      LESS THAN (
        '2026-01-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768147200
    VALUES
      LESS THAN (
        '2026-01-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768233600
    VALUES
      LESS THAN (
        '2026-01-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768320000
    VALUES
      LESS THAN (
        '2026-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768406400
    VALUES
      LESS THAN (
        '2026-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768492800
    VALUES
      LESS THAN (
        '2026-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768579200
    VALUES
      LESS THAN (
        '2026-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768665600
    VALUES
      LESS THAN (
        '2026-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768752000
    VALUES
      LESS THAN (
        '2026-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768838400
    VALUES
      LESS THAN (
        '2026-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768924800
    VALUES
      LESS THAN (
        '2026-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769011200
    VALUES
      LESS THAN (
        '2026-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769097600
    VALUES
      LESS THAN (
        '2026-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769184000
    VALUES
      LESS THAN (
        '2026-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769270400
    VALUES
      LESS THAN (
        '2026-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769356800
    VALUES
      LESS THAN (
        '2026-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769443200
    VALUES
      LESS THAN (
        '2026-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769529600
    VALUES
      LESS THAN (
        '2026-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769616000
    VALUES
      LESS THAN (
        '2026-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769702400
    VALUES
      LESS THAN (
        '2026-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769788800
    VALUES
      LESS THAN (
        '2026-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769875200
    VALUES
      LESS THAN (
        '2026-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769961600
    VALUES
      LESS THAN (
        '2026-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770048000
    VALUES
      LESS THAN (
        '2026-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770134400
    VALUES
      LESS THAN (
        '2026-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770220800
    VALUES
      LESS THAN (
        '2026-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770307200
    VALUES
      LESS THAN (
        '2026-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770393600
    VALUES
      LESS THAN (
        '2026-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770480000
    VALUES
      LESS THAN (
        '2026-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770566400
    VALUES
      LESS THAN (
        '2026-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770652800
    VALUES
      LESS THAN (
        '2026-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770739200
    VALUES
      LESS THAN (
        '2026-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770825600
    VALUES
      LESS THAN (
        '2026-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770912000
    VALUES
      LESS THAN (
        '2026-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770998400
    VALUES
      LESS THAN (
        '2026-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771084800
    VALUES
      LESS THAN (
        '2026-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771171200
    VALUES
      LESS THAN (
        '2026-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771257600
    VALUES
      LESS THAN (
        '2026-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771344000
    VALUES
      LESS THAN (
        '2026-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771430400
    VALUES
      LESS THAN (
        '2026-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771516800
    VALUES
      LESS THAN (
        '2026-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771603200
    VALUES
      LESS THAN (
        '2026-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771689600
    VALUES
      LESS THAN (
        '2026-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771776000
    VALUES
      LESS THAN (
        '2026-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771862400
    VALUES
      LESS THAN (
        '2026-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771948800
    VALUES
      LESS THAN (
        '2026-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772035200
    VALUES
      LESS THAN (
        '2026-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772121600
    VALUES
      LESS THAN (
        '2026-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772208000
    VALUES
      LESS THAN (
        '2026-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772294400
    VALUES
      LESS THAN (
        '2026-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772380800
    VALUES
      LESS THAN (
        '2026-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772467200
    VALUES
      LESS THAN (
        '2026-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772553600
    VALUES
      LESS THAN (
        '2026-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772640000
    VALUES
      LESS THAN (
        '2026-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772726400
    VALUES
      LESS THAN (
        '2026-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772812800
    VALUES
      LESS THAN (
        '2026-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772899200
    VALUES
      LESS THAN (
        '2026-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772985600
    VALUES
      LESS THAN (
        '2026-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773072000
    VALUES
      LESS THAN (
        '2026-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773158400
    VALUES
      LESS THAN (
        '2026-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773244800
    VALUES
      LESS THAN (
        '2026-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773331200
    VALUES
      LESS THAN (
        '2026-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773417600
    VALUES
      LESS THAN (
        '2026-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773504000
    VALUES
      LESS THAN (
        '2026-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773590400
    VALUES
      LESS THAN (
        '2026-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773676800
    VALUES
      LESS THAN (
        '2026-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773763200
    VALUES
      LESS THAN (
        '2026-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773849600
    VALUES
      LESS THAN (
        '2026-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773936000
    VALUES
      LESS THAN (
        '2026-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774022400
    VALUES
      LESS THAN (
        '2026-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774108800
    VALUES
      LESS THAN (
        '2026-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774195200
    VALUES
      LESS THAN (
        '2026-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774281600
    VALUES
      LESS THAN (
        '2026-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774368000
    VALUES
      LESS THAN (
        '2026-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774454400
    VALUES
      LESS THAN (
        '2026-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774540800
    VALUES
      LESS THAN (
        '2026-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774627200
    VALUES
      LESS THAN (
        '2026-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774713600
    VALUES
      LESS THAN (
        '2026-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774800000
    VALUES
      LESS THAN (
        '2026-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774886400
    VALUES
      LESS THAN (
        '2026-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774972800
    VALUES
      LESS THAN (
        '2026-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775059200
    VALUES
      LESS THAN (
        '2026-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775145600
    VALUES
      LESS THAN (
        '2026-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775232000
    VALUES
      LESS THAN (
        '2026-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775318400
    VALUES
      LESS THAN (
        '2026-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775404800
    VALUES
      LESS THAN (
        '2026-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775491200
    VALUES
      LESS THAN (
        '2026-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775577600
    VALUES
      LESS THAN (
        '2026-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775664000
    VALUES
      LESS THAN (
        '2026-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775750400
    VALUES
      LESS THAN (
        '2026-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775836800
    VALUES
      LESS THAN (
        '2026-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775923200
    VALUES
      LESS THAN (
        '2026-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776009600
    VALUES
      LESS THAN (
        '2026-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776096000
    VALUES
      LESS THAN (
        '2026-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776182400
    VALUES
      LESS THAN (
        '2026-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776268800
    VALUES
      LESS THAN (
        '2026-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776355200
    VALUES
      LESS THAN (
        '2026-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776441600
    VALUES
      LESS THAN (
        '2026-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776528000
    VALUES
      LESS THAN (
        '2026-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776614400
    VALUES
      LESS THAN (
        '2026-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776700800
    VALUES
      LESS THAN (
        '2026-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776787200
    VALUES
      LESS THAN (
        '2026-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776873600
    VALUES
      LESS THAN (
        '2026-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776960000
    VALUES
      LESS THAN (
        '2026-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777046400
    VALUES
      LESS THAN (
        '2026-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777132800
    VALUES
      LESS THAN (
        '2026-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777219200
    VALUES
      LESS THAN (
        '2026-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777305600
    VALUES
      LESS THAN (
        '2026-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777392000
    VALUES
      LESS THAN (
        '2026-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777478400
    VALUES
      LESS THAN (
        '2026-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777564800
    VALUES
      LESS THAN (
        '2026-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777651200
    VALUES
      LESS THAN (
        '2026-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777737600
    VALUES
      LESS THAN (
        '2026-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777824000
    VALUES
      LESS THAN (
        '2026-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777910400
    VALUES
      LESS THAN (
        '2026-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777996800
    VALUES
      LESS THAN (
        '2026-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778083200
    VALUES
      LESS THAN (
        '2026-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778169600
    VALUES
      LESS THAN (
        '2026-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778256000
    VALUES
      LESS THAN (
        '2026-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778342400
    VALUES
      LESS THAN (
        '2026-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778428800
    VALUES
      LESS THAN (
        '2026-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778515200
    VALUES
      LESS THAN (
        '2026-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778601600
    VALUES
      LESS THAN (
        '2026-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778688000
    VALUES
      LESS THAN (
        '2026-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778774400
    VALUES
      LESS THAN (
        '2026-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778860800
    VALUES
      LESS THAN (
        '2026-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778947200
    VALUES
      LESS THAN (
        '2026-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779033600
    VALUES
      LESS THAN (
        '2026-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779120000
    VALUES
      LESS THAN (
        '2026-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779206400
    VALUES
      LESS THAN (
        '2026-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779292800
    VALUES
      LESS THAN (
        '2026-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779379200
    VALUES
      LESS THAN (
        '2026-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779465600
    VALUES
      LESS THAN (
        '2026-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779552000
    VALUES
      LESS THAN (
        '2026-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779638400
    VALUES
      LESS THAN (
        '2026-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779724800
    VALUES
      LESS THAN (
        '2026-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779811200
    VALUES
      LESS THAN (
        '2026-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779897600
    VALUES
      LESS THAN (
        '2026-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779984000
    VALUES
      LESS THAN (
        '2026-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780070400
    VALUES
      LESS THAN (
        '2026-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780156800
    VALUES
      LESS THAN (
        '2026-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780243200
    VALUES
      LESS THAN (
        '2026-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780329600
    VALUES
      LESS THAN (
        '2026-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780416000
    VALUES
      LESS THAN (
        '2026-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780502400
    VALUES
      LESS THAN (
        '2026-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780588800
    VALUES
      LESS THAN (
        '2026-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780675200
    VALUES
      LESS THAN (
        '2026-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780761600
    VALUES
      LESS THAN (
        '2026-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780848000
    VALUES
      LESS THAN (
        '2026-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780934400
    VALUES
      LESS THAN (
        '2026-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781020800
    VALUES
      LESS THAN (
        '2026-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781107200
    VALUES
      LESS THAN (
        '2026-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781193600
    VALUES
      LESS THAN (
        '2026-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE ads_rgst_act_chnl_cnt_df IS '激活注册渠道_注册用户数_日度';

COMMENT ON COLUMN ads_rgst_act_chnl_cnt_df.data_dt IS '数据日期';

COMMENT ON COLUMN ads_rgst_act_chnl_cnt_df.raw_rgst_sec_chnl_nm IS '原始注册二级渠道';

COMMENT ON COLUMN ads_rgst_act_chnl_cnt_df.act_rgst_sec_chnl_nm IS '激活注册二级渠道';

COMMENT ON COLUMN ads_rgst_act_chnl_cnt_df.act_rgst_chnl_sub_nm IS '激活注册报送渠道';

COMMENT ON COLUMN ads_rgst_act_chnl_cnt_df.act_rgst_cnt_d IS '当日_新增注册用户数';

COMMENT ON COLUMN ads_rgst_act_chnl_cnt_df.act_rgst_cnt_7d IS '近7日_新增注册用户数';

COMMENT ON COLUMN ads_rgst_act_chnl_cnt_df.act_rgst_cnt_m IS '当月_新增注册用户数';

COMMENT ON COLUMN ads_rgst_act_chnl_cnt_df.act_rgst_cnt_y IS '当年累计_新增注册用户数';

COMMENT ON COLUMN ads_rgst_act_chnl_cnt_df.act_rgst_cnt_a IS '历史累计_新增注册用户数';

COMMENT ON COLUMN ads_rgst_act_chnl_cnt_df.ds IS '分区日期';



SET
  search_path = rec;

CREATE TABLE
  ads_chnl_real_user_df (
    data_dt timestamp (0) without TIME zone,
    real_type character varying (128),
    fst_chnl_id character varying (128),
    fst_chnl_nm character varying (128),
    sec_chnl_id character varying (128),
    sec_chnl_nm character varying (128),
    chnl_id character varying (128),
    chnl_nm character varying (128),
    chnl_sub_nm character varying (128),
    real_today bigint,
    real_last7d bigint,
    real_last30d bigint,
    real_curmth bigint,
    real_curyear bigint,
    real_all bigint,
    real_rgst_curyear bigint,
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '10 years',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(data_dt) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1
    VALUES
      LESS THAN (
        '2025-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752595200
    VALUES
      LESS THAN (
        '2025-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752681600
    VALUES
      LESS THAN (
        '2025-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752768000
    VALUES
      LESS THAN (
        '2025-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752854400
    VALUES
      LESS THAN (
        '2025-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752940800
    VALUES
      LESS THAN (
        '2025-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753027200
    VALUES
      LESS THAN (
        '2025-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753113600
    VALUES
      LESS THAN (
        '2025-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753200000
    VALUES
      LESS THAN (
        '2025-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753286400
    VALUES
      LESS THAN (
        '2025-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753372800
    VALUES
      LESS THAN (
        '2025-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753459200
    VALUES
      LESS THAN (
        '2025-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753545600
    VALUES
      LESS THAN (
        '2025-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753632000
    VALUES
      LESS THAN (
        '2025-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753718400
    VALUES
      LESS THAN (
        '2025-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753804800
    VALUES
      LESS THAN (
        '2025-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753891200
    VALUES
      LESS THAN (
        '2025-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753977600
    VALUES
      LESS THAN (
        '2025-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754064000
    VALUES
      LESS THAN (
        '2025-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754150400
    VALUES
      LESS THAN (
        '2025-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754236800
    VALUES
      LESS THAN (
        '2025-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754323200
    VALUES
      LESS THAN (
        '2025-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754409600
    VALUES
      LESS THAN (
        '2025-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754496000
    VALUES
      LESS THAN (
        '2025-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754582400
    VALUES
      LESS THAN (
        '2025-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754668800
    VALUES
      LESS THAN (
        '2025-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754755200
    VALUES
      LESS THAN (
        '2025-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754841600
    VALUES
      LESS THAN (
        '2025-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754928000
    VALUES
      LESS THAN (
        '2025-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755014400
    VALUES
      LESS THAN (
        '2025-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755100800
    VALUES
      LESS THAN (
        '2025-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755187200
    VALUES
      LESS THAN (
        '2025-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755273600
    VALUES
      LESS THAN (
        '2025-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755360000
    VALUES
      LESS THAN (
        '2025-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755446400
    VALUES
      LESS THAN (
        '2025-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755532800
    VALUES
      LESS THAN (
        '2025-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755619200
    VALUES
      LESS THAN (
        '2025-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755705600
    VALUES
      LESS THAN (
        '2025-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755792000
    VALUES
      LESS THAN (
        '2025-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755878400
    VALUES
      LESS THAN (
        '2025-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755964800
    VALUES
      LESS THAN (
        '2025-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756051200
    VALUES
      LESS THAN (
        '2025-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756137600
    VALUES
      LESS THAN (
        '2025-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756224000
    VALUES
      LESS THAN (
        '2025-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756310400
    VALUES
      LESS THAN (
        '2025-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756396800
    VALUES
      LESS THAN (
        '2025-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756483200
    VALUES
      LESS THAN (
        '2025-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756569600
    VALUES
      LESS THAN (
        '2025-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756656000
    VALUES
      LESS THAN (
        '2025-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756742400
    VALUES
      LESS THAN (
        '2025-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756828800
    VALUES
      LESS THAN (
        '2025-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756915200
    VALUES
      LESS THAN (
        '2025-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757001600
    VALUES
      LESS THAN (
        '2025-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757088000
    VALUES
      LESS THAN (
        '2025-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757174400
    VALUES
      LESS THAN (
        '2025-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757260800
    VALUES
      LESS THAN (
        '2025-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757347200
    VALUES
      LESS THAN (
        '2025-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757433600
    VALUES
      LESS THAN (
        '2025-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757520000
    VALUES
      LESS THAN (
        '2025-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757606400
    VALUES
      LESS THAN (
        '2025-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757692800
    VALUES
      LESS THAN (
        '2025-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757779200
    VALUES
      LESS THAN (
        '2025-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757865600
    VALUES
      LESS THAN (
        '2025-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757952000
    VALUES
      LESS THAN (
        '2025-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758038400
    VALUES
      LESS THAN (
        '2025-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758124800
    VALUES
      LESS THAN (
        '2025-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758211200
    VALUES
      LESS THAN (
        '2025-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758297600
    VALUES
      LESS THAN (
        '2025-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758384000
    VALUES
      LESS THAN (
        '2025-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758470400
    VALUES
      LESS THAN (
        '2025-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758556800
    VALUES
      LESS THAN (
        '2025-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758643200
    VALUES
      LESS THAN (
        '2025-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758729600
    VALUES
      LESS THAN (
        '2025-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758816000
    VALUES
      LESS THAN (
        '2025-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758902400
    VALUES
      LESS THAN (
        '2025-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758988800
    VALUES
      LESS THAN (
        '2025-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759075200
    VALUES
      LESS THAN (
        '2025-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759161600
    VALUES
      LESS THAN (
        '2025-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759248000
    VALUES
      LESS THAN (
        '2025-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759334400
    VALUES
      LESS THAN (
        '2025-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759420800
    VALUES
      LESS THAN (
        '2025-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759507200
    VALUES
      LESS THAN (
        '2025-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759593600
    VALUES
      LESS THAN (
        '2025-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759680000
    VALUES
      LESS THAN (
        '2025-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759766400
    VALUES
      LESS THAN (
        '2025-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759852800
    VALUES
      LESS THAN (
        '2025-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759939200
    VALUES
      LESS THAN (
        '2025-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760025600
    VALUES
      LESS THAN (
        '2025-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760112000
    VALUES
      LESS THAN (
        '2025-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760198400
    VALUES
      LESS THAN (
        '2025-10-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760284800
    VALUES
      LESS THAN (
        '2025-10-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760371200
    VALUES
      LESS THAN (
        '2025-10-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760457600
    VALUES
      LESS THAN (
        '2025-10-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760544000
    VALUES
      LESS THAN (
        '2025-10-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760630400
    VALUES
      LESS THAN (
        '2025-10-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760716800
    VALUES
      LESS THAN (
        '2025-10-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760803200
    VALUES
      LESS THAN (
        '2025-10-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760889600
    VALUES
      LESS THAN (
        '2025-10-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760976000
    VALUES
      LESS THAN (
        '2025-10-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761062400
    VALUES
      LESS THAN (
        '2025-10-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761148800
    VALUES
      LESS THAN (
        '2025-10-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761235200
    VALUES
      LESS THAN (
        '2025-10-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761321600
    VALUES
      LESS THAN (
        '2025-10-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761408000
    VALUES
      LESS THAN (
        '2025-10-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761494400
    VALUES
      LESS THAN (
        '2025-10-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761580800
    VALUES
      LESS THAN (
        '2025-10-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761667200
    VALUES
      LESS THAN (
        '2025-10-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761753600
    VALUES
      LESS THAN (
        '2025-10-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761840000
    VALUES
      LESS THAN (
        '2025-10-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761926400
    VALUES
      LESS THAN (
        '2025-11-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762012800
    VALUES
      LESS THAN (
        '2025-11-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762099200
    VALUES
      LESS THAN (
        '2025-11-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762185600
    VALUES
      LESS THAN (
        '2025-11-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762272000
    VALUES
      LESS THAN (
        '2025-11-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762358400
    VALUES
      LESS THAN (
        '2025-11-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762444800
    VALUES
      LESS THAN (
        '2025-11-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762531200
    VALUES
      LESS THAN (
        '2025-11-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762617600
    VALUES
      LESS THAN (
        '2025-11-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762704000
    VALUES
      LESS THAN (
        '2025-11-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762790400
    VALUES
      LESS THAN (
        '2025-11-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762876800
    VALUES
      LESS THAN (
        '2025-11-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762963200
    VALUES
      LESS THAN (
        '2025-11-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763049600
    VALUES
      LESS THAN (
        '2025-11-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763136000
    VALUES
      LESS THAN (
        '2025-11-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763222400
    VALUES
      LESS THAN (
        '2025-11-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763308800
    VALUES
      LESS THAN (
        '2025-11-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763395200
    VALUES
      LESS THAN (
        '2025-11-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763481600
    VALUES
      LESS THAN (
        '2025-11-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763568000
    VALUES
      LESS THAN (
        '2025-11-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763654400
    VALUES
      LESS THAN (
        '2025-11-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763740800
    VALUES
      LESS THAN (
        '2025-11-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763827200
    VALUES
      LESS THAN (
        '2025-11-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763913600
    VALUES
      LESS THAN (
        '2025-11-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764000000
    VALUES
      LESS THAN (
        '2025-11-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764086400
    VALUES
      LESS THAN (
        '2025-11-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764172800
    VALUES
      LESS THAN (
        '2025-11-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764259200
    VALUES
      LESS THAN (
        '2025-11-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764345600
    VALUES
      LESS THAN (
        '2025-11-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764432000
    VALUES
      LESS THAN (
        '2025-11-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764518400
    VALUES
      LESS THAN (
        '2025-12-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764604800
    VALUES
      LESS THAN (
        '2025-12-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764691200
    VALUES
      LESS THAN (
        '2025-12-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764777600
    VALUES
      LESS THAN (
        '2025-12-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764864000
    VALUES
      LESS THAN (
        '2025-12-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764950400
    VALUES
      LESS THAN (
        '2025-12-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765036800
    VALUES
      LESS THAN (
        '2025-12-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765123200
    VALUES
      LESS THAN (
        '2025-12-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765209600
    VALUES
      LESS THAN (
        '2025-12-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765296000
    VALUES
      LESS THAN (
        '2025-12-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765382400
    VALUES
      LESS THAN (
        '2025-12-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765468800
    VALUES
      LESS THAN (
        '2025-12-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765555200
    VALUES
      LESS THAN (
        '2025-12-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765641600
    VALUES
      LESS THAN (
        '2025-12-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765728000
    VALUES
      LESS THAN (
        '2025-12-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765814400
    VALUES
      LESS THAN (
        '2025-12-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765900800
    VALUES
      LESS THAN (
        '2025-12-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765987200
    VALUES
      LESS THAN (
        '2025-12-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766073600
    VALUES
      LESS THAN (
        '2025-12-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766160000
    VALUES
      LESS THAN (
        '2025-12-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766246400
    VALUES
      LESS THAN (
        '2025-12-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766332800
    VALUES
      LESS THAN (
        '2025-12-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766419200
    VALUES
      LESS THAN (
        '2025-12-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766505600
    VALUES
      LESS THAN (
        '2025-12-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766592000
    VALUES
      LESS THAN (
        '2025-12-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766678400
    VALUES
      LESS THAN (
        '2025-12-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766764800
    VALUES
      LESS THAN (
        '2025-12-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766851200
    VALUES
      LESS THAN (
        '2025-12-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766937600
    VALUES
      LESS THAN (
        '2025-12-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767024000
    VALUES
      LESS THAN (
        '2025-12-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767110400
    VALUES
      LESS THAN (
        '2025-12-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767196800
    VALUES
      LESS THAN (
        '2026-01-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767283200
    VALUES
      LESS THAN (
        '2026-01-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767369600
    VALUES
      LESS THAN (
        '2026-01-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767456000
    VALUES
      LESS THAN (
        '2026-01-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767542400
    VALUES
      LESS THAN (
        '2026-01-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767628800
    VALUES
      LESS THAN (
        '2026-01-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767715200
    VALUES
      LESS THAN (
        '2026-01-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767801600
    VALUES
      LESS THAN (
        '2026-01-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767888000
    VALUES
      LESS THAN (
        '2026-01-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767974400
    VALUES
      LESS THAN (
        '2026-01-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768060800
    VALUES
      LESS THAN (
        '2026-01-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768147200
    VALUES
      LESS THAN (
        '2026-01-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768233600
    VALUES
      LESS THAN (
        '2026-01-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768320000
    VALUES
      LESS THAN (
        '2026-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768406400
    VALUES
      LESS THAN (
        '2026-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768492800
    VALUES
      LESS THAN (
        '2026-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768579200
    VALUES
      LESS THAN (
        '2026-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768665600
    VALUES
      LESS THAN (
        '2026-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768752000
    VALUES
      LESS THAN (
        '2026-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768838400
    VALUES
      LESS THAN (
        '2026-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768924800
    VALUES
      LESS THAN (
        '2026-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769011200
    VALUES
      LESS THAN (
        '2026-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769097600
    VALUES
      LESS THAN (
        '2026-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769184000
    VALUES
      LESS THAN (
        '2026-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769270400
    VALUES
      LESS THAN (
        '2026-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769356800
    VALUES
      LESS THAN (
        '2026-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769443200
    VALUES
      LESS THAN (
        '2026-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769529600
    VALUES
      LESS THAN (
        '2026-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769616000
    VALUES
      LESS THAN (
        '2026-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769702400
    VALUES
      LESS THAN (
        '2026-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769788800
    VALUES
      LESS THAN (
        '2026-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769875200
    VALUES
      LESS THAN (
        '2026-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769961600
    VALUES
      LESS THAN (
        '2026-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770048000
    VALUES
      LESS THAN (
        '2026-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770134400
    VALUES
      LESS THAN (
        '2026-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770220800
    VALUES
      LESS THAN (
        '2026-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770307200
    VALUES
      LESS THAN (
        '2026-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770393600
    VALUES
      LESS THAN (
        '2026-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770480000
    VALUES
      LESS THAN (
        '2026-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770566400
    VALUES
      LESS THAN (
        '2026-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770652800
    VALUES
      LESS THAN (
        '2026-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770739200
    VALUES
      LESS THAN (
        '2026-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770825600
    VALUES
      LESS THAN (
        '2026-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770912000
    VALUES
      LESS THAN (
        '2026-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770998400
    VALUES
      LESS THAN (
        '2026-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771084800
    VALUES
      LESS THAN (
        '2026-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771171200
    VALUES
      LESS THAN (
        '2026-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771257600
    VALUES
      LESS THAN (
        '2026-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771344000
    VALUES
      LESS THAN (
        '2026-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771430400
    VALUES
      LESS THAN (
        '2026-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771516800
    VALUES
      LESS THAN (
        '2026-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771603200
    VALUES
      LESS THAN (
        '2026-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771689600
    VALUES
      LESS THAN (
        '2026-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771776000
    VALUES
      LESS THAN (
        '2026-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771862400
    VALUES
      LESS THAN (
        '2026-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771948800
    VALUES
      LESS THAN (
        '2026-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772035200
    VALUES
      LESS THAN (
        '2026-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772121600
    VALUES
      LESS THAN (
        '2026-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772208000
    VALUES
      LESS THAN (
        '2026-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772294400
    VALUES
      LESS THAN (
        '2026-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772380800
    VALUES
      LESS THAN (
        '2026-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772467200
    VALUES
      LESS THAN (
        '2026-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772553600
    VALUES
      LESS THAN (
        '2026-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772640000
    VALUES
      LESS THAN (
        '2026-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772726400
    VALUES
      LESS THAN (
        '2026-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772812800
    VALUES
      LESS THAN (
        '2026-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772899200
    VALUES
      LESS THAN (
        '2026-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772985600
    VALUES
      LESS THAN (
        '2026-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773072000
    VALUES
      LESS THAN (
        '2026-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773158400
    VALUES
      LESS THAN (
        '2026-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773244800
    VALUES
      LESS THAN (
        '2026-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773331200
    VALUES
      LESS THAN (
        '2026-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773417600
    VALUES
      LESS THAN (
        '2026-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773504000
    VALUES
      LESS THAN (
        '2026-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773590400
    VALUES
      LESS THAN (
        '2026-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773676800
    VALUES
      LESS THAN (
        '2026-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773763200
    VALUES
      LESS THAN (
        '2026-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773849600
    VALUES
      LESS THAN (
        '2026-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773936000
    VALUES
      LESS THAN (
        '2026-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774022400
    VALUES
      LESS THAN (
        '2026-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774108800
    VALUES
      LESS THAN (
        '2026-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774195200
    VALUES
      LESS THAN (
        '2026-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774281600
    VALUES
      LESS THAN (
        '2026-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774368000
    VALUES
      LESS THAN (
        '2026-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774454400
    VALUES
      LESS THAN (
        '2026-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774540800
    VALUES
      LESS THAN (
        '2026-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774627200
    VALUES
      LESS THAN (
        '2026-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774713600
    VALUES
      LESS THAN (
        '2026-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774800000
    VALUES
      LESS THAN (
        '2026-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774886400
    VALUES
      LESS THAN (
        '2026-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774972800
    VALUES
      LESS THAN (
        '2026-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775059200
    VALUES
      LESS THAN (
        '2026-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775145600
    VALUES
      LESS THAN (
        '2026-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775232000
    VALUES
      LESS THAN (
        '2026-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775318400
    VALUES
      LESS THAN (
        '2026-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775404800
    VALUES
      LESS THAN (
        '2026-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775491200
    VALUES
      LESS THAN (
        '2026-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775577600
    VALUES
      LESS THAN (
        '2026-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775664000
    VALUES
      LESS THAN (
        '2026-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775750400
    VALUES
      LESS THAN (
        '2026-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775836800
    VALUES
      LESS THAN (
        '2026-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775923200
    VALUES
      LESS THAN (
        '2026-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776009600
    VALUES
      LESS THAN (
        '2026-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776096000
    VALUES
      LESS THAN (
        '2026-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776182400
    VALUES
      LESS THAN (
        '2026-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776268800
    VALUES
      LESS THAN (
        '2026-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776355200
    VALUES
      LESS THAN (
        '2026-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776441600
    VALUES
      LESS THAN (
        '2026-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776528000
    VALUES
      LESS THAN (
        '2026-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776614400
    VALUES
      LESS THAN (
        '2026-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776700800
    VALUES
      LESS THAN (
        '2026-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776787200
    VALUES
      LESS THAN (
        '2026-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776873600
    VALUES
      LESS THAN (
        '2026-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776960000
    VALUES
      LESS THAN (
        '2026-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777046400
    VALUES
      LESS THAN (
        '2026-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777132800
    VALUES
      LESS THAN (
        '2026-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777219200
    VALUES
      LESS THAN (
        '2026-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777305600
    VALUES
      LESS THAN (
        '2026-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777392000
    VALUES
      LESS THAN (
        '2026-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777478400
    VALUES
      LESS THAN (
        '2026-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777564800
    VALUES
      LESS THAN (
        '2026-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777651200
    VALUES
      LESS THAN (
        '2026-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777737600
    VALUES
      LESS THAN (
        '2026-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777824000
    VALUES
      LESS THAN (
        '2026-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777910400
    VALUES
      LESS THAN (
        '2026-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777996800
    VALUES
      LESS THAN (
        '2026-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778083200
    VALUES
      LESS THAN (
        '2026-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778169600
    VALUES
      LESS THAN (
        '2026-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778256000
    VALUES
      LESS THAN (
        '2026-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778342400
    VALUES
      LESS THAN (
        '2026-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778428800
    VALUES
      LESS THAN (
        '2026-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778515200
    VALUES
      LESS THAN (
        '2026-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778601600
    VALUES
      LESS THAN (
        '2026-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778688000
    VALUES
      LESS THAN (
        '2026-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778774400
    VALUES
      LESS THAN (
        '2026-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778860800
    VALUES
      LESS THAN (
        '2026-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778947200
    VALUES
      LESS THAN (
        '2026-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779033600
    VALUES
      LESS THAN (
        '2026-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779120000
    VALUES
      LESS THAN (
        '2026-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779206400
    VALUES
      LESS THAN (
        '2026-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779292800
    VALUES
      LESS THAN (
        '2026-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779379200
    VALUES
      LESS THAN (
        '2026-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779465600
    VALUES
      LESS THAN (
        '2026-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779552000
    VALUES
      LESS THAN (
        '2026-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779638400
    VALUES
      LESS THAN (
        '2026-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779724800
    VALUES
      LESS THAN (
        '2026-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779811200
    VALUES
      LESS THAN (
        '2026-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779897600
    VALUES
      LESS THAN (
        '2026-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779984000
    VALUES
      LESS THAN (
        '2026-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780070400
    VALUES
      LESS THAN (
        '2026-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780156800
    VALUES
      LESS THAN (
        '2026-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780243200
    VALUES
      LESS THAN (
        '2026-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780329600
    VALUES
      LESS THAN (
        '2026-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780416000
    VALUES
      LESS THAN (
        '2026-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780502400
    VALUES
      LESS THAN (
        '2026-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780588800
    VALUES
      LESS THAN (
        '2026-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780675200
    VALUES
      LESS THAN (
        '2026-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780761600
    VALUES
      LESS THAN (
        '2026-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780848000
    VALUES
      LESS THAN (
        '2026-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780934400
    VALUES
      LESS THAN (
        '2026-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781020800
    VALUES
      LESS THAN (
        '2026-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781107200
    VALUES
      LESS THAN (
        '2026-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781193600
    VALUES
      LESS THAN (
        '2026-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE ads_chnl_real_user_df IS '按渠道_实名_日度';

COMMENT ON COLUMN ads_chnl_real_user_df.data_dt IS '数据日期';

COMMENT ON COLUMN ads_chnl_real_user_df.real_type IS '实名类型';

COMMENT ON COLUMN ads_chnl_real_user_df.fst_chnl_id IS '一级渠道ID_注册渠道';

COMMENT ON COLUMN ads_chnl_real_user_df.fst_chnl_nm IS '一级渠道名称_注册渠道';

COMMENT ON COLUMN ads_chnl_real_user_df.sec_chnl_id IS '二级渠道ID_注册渠道';

COMMENT ON COLUMN ads_chnl_real_user_df.sec_chnl_nm IS '二级渠道名称_注册渠道';

COMMENT ON COLUMN ads_chnl_real_user_df.chnl_id IS '渠道ID_注册渠道';

COMMENT ON COLUMN ads_chnl_real_user_df.chnl_nm IS '渠道名称_注册渠道';

COMMENT ON COLUMN ads_chnl_real_user_df.chnl_sub_nm IS '报送渠道名称';

COMMENT ON COLUMN ads_chnl_real_user_df.real_today IS '当日_实名';

COMMENT ON COLUMN ads_chnl_real_user_df.real_last7d IS '近7日_实名';

COMMENT ON COLUMN ads_chnl_real_user_df.real_last30d IS '近30日_实名';

COMMENT ON COLUMN ads_chnl_real_user_df.real_curmth IS '当月_实名';

COMMENT ON COLUMN ads_chnl_real_user_df.real_curyear IS '当年累计_实名';

COMMENT ON COLUMN ads_chnl_real_user_df.real_all IS '历史累计_实名';

COMMENT ON COLUMN ads_chnl_real_user_df.real_rgst_curyear IS '当年注册_当年实名';

COMMENT ON COLUMN ads_chnl_real_user_df.ds IS '分区日期';

SET
  search_path = rec;

CREATE TABLE
  ads_chnl_auth_qty_df (
    data_dt timestamp (0) without TIME zone,
    rgst_sec_chnl_nm character varying (128),
    auth_sec_chnl_nm character varying (128),
    auth_user_cnt bigint,
    auth_user_7d_cnt bigint,
    auth_user_30d_cnt bigint,
    auth_user_mon_cnt bigint,
    auth_user_year_cnt bigint,
    auth_user_all_cnt bigint,
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '10 years',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(data_dt) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1
    VALUES
      LESS THAN (
        '2025-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752768000
    VALUES
      LESS THAN (
        '2025-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752854400
    VALUES
      LESS THAN (
        '2025-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752940800
    VALUES
      LESS THAN (
        '2025-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753027200
    VALUES
      LESS THAN (
        '2025-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753113600
    VALUES
      LESS THAN (
        '2025-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753200000
    VALUES
      LESS THAN (
        '2025-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753286400
    VALUES
      LESS THAN (
        '2025-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753372800
    VALUES
      LESS THAN (
        '2025-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753459200
    VALUES
      LESS THAN (
        '2025-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753545600
    VALUES
      LESS THAN (
        '2025-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753632000
    VALUES
      LESS THAN (
        '2025-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753718400
    VALUES
      LESS THAN (
        '2025-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753804800
    VALUES
      LESS THAN (
        '2025-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753891200
    VALUES
      LESS THAN (
        '2025-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753977600
    VALUES
      LESS THAN (
        '2025-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754064000
    VALUES
      LESS THAN (
        '2025-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754150400
    VALUES
      LESS THAN (
        '2025-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754236800
    VALUES
      LESS THAN (
        '2025-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754323200
    VALUES
      LESS THAN (
        '2025-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754409600
    VALUES
      LESS THAN (
        '2025-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754496000
    VALUES
      LESS THAN (
        '2025-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754582400
    VALUES
      LESS THAN (
        '2025-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754668800
    VALUES
      LESS THAN (
        '2025-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754755200
    VALUES
      LESS THAN (
        '2025-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754841600
    VALUES
      LESS THAN (
        '2025-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754928000
    VALUES
      LESS THAN (
        '2025-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755014400
    VALUES
      LESS THAN (
        '2025-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755100800
    VALUES
      LESS THAN (
        '2025-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755187200
    VALUES
      LESS THAN (
        '2025-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755273600
    VALUES
      LESS THAN (
        '2025-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755360000
    VALUES
      LESS THAN (
        '2025-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755446400
    VALUES
      LESS THAN (
        '2025-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755532800
    VALUES
      LESS THAN (
        '2025-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755619200
    VALUES
      LESS THAN (
        '2025-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755705600
    VALUES
      LESS THAN (
        '2025-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755792000
    VALUES
      LESS THAN (
        '2025-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755878400
    VALUES
      LESS THAN (
        '2025-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755964800
    VALUES
      LESS THAN (
        '2025-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756051200
    VALUES
      LESS THAN (
        '2025-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756137600
    VALUES
      LESS THAN (
        '2025-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756224000
    VALUES
      LESS THAN (
        '2025-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756310400
    VALUES
      LESS THAN (
        '2025-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756396800
    VALUES
      LESS THAN (
        '2025-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756483200
    VALUES
      LESS THAN (
        '2025-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756569600
    VALUES
      LESS THAN (
        '2025-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756656000
    VALUES
      LESS THAN (
        '2025-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756742400
    VALUES
      LESS THAN (
        '2025-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756828800
    VALUES
      LESS THAN (
        '2025-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756915200
    VALUES
      LESS THAN (
        '2025-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757001600
    VALUES
      LESS THAN (
        '2025-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757088000
    VALUES
      LESS THAN (
        '2025-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757174400
    VALUES
      LESS THAN (
        '2025-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757260800
    VALUES
      LESS THAN (
        '2025-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757347200
    VALUES
      LESS THAN (
        '2025-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757433600
    VALUES
      LESS THAN (
        '2025-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757520000
    VALUES
      LESS THAN (
        '2025-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757606400
    VALUES
      LESS THAN (
        '2025-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757692800
    VALUES
      LESS THAN (
        '2025-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757779200
    VALUES
      LESS THAN (
        '2025-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757865600
    VALUES
      LESS THAN (
        '2025-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757952000
    VALUES
      LESS THAN (
        '2025-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758038400
    VALUES
      LESS THAN (
        '2025-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758124800
    VALUES
      LESS THAN (
        '2025-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758211200
    VALUES
      LESS THAN (
        '2025-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758297600
    VALUES
      LESS THAN (
        '2025-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758384000
    VALUES
      LESS THAN (
        '2025-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758470400
    VALUES
      LESS THAN (
        '2025-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758556800
    VALUES
      LESS THAN (
        '2025-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758643200
    VALUES
      LESS THAN (
        '2025-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758729600
    VALUES
      LESS THAN (
        '2025-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758816000
    VALUES
      LESS THAN (
        '2025-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758902400
    VALUES
      LESS THAN (
        '2025-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758988800
    VALUES
      LESS THAN (
        '2025-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759075200
    VALUES
      LESS THAN (
        '2025-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759161600
    VALUES
      LESS THAN (
        '2025-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759248000
    VALUES
      LESS THAN (
        '2025-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759334400
    VALUES
      LESS THAN (
        '2025-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759420800
    VALUES
      LESS THAN (
        '2025-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759507200
    VALUES
      LESS THAN (
        '2025-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759593600
    VALUES
      LESS THAN (
        '2025-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759680000
    VALUES
      LESS THAN (
        '2025-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759766400
    VALUES
      LESS THAN (
        '2025-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759852800
    VALUES
      LESS THAN (
        '2025-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759939200
    VALUES
      LESS THAN (
        '2025-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760025600
    VALUES
      LESS THAN (
        '2025-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760112000
    VALUES
      LESS THAN (
        '2025-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760198400
    VALUES
      LESS THAN (
        '2025-10-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760284800
    VALUES
      LESS THAN (
        '2025-10-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760371200
    VALUES
      LESS THAN (
        '2025-10-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760457600
    VALUES
      LESS THAN (
        '2025-10-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760544000
    VALUES
      LESS THAN (
        '2025-10-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760630400
    VALUES
      LESS THAN (
        '2025-10-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760716800
    VALUES
      LESS THAN (
        '2025-10-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760803200
    VALUES
      LESS THAN (
        '2025-10-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760889600
    VALUES
      LESS THAN (
        '2025-10-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760976000
    VALUES
      LESS THAN (
        '2025-10-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761062400
    VALUES
      LESS THAN (
        '2025-10-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761148800
    VALUES
      LESS THAN (
        '2025-10-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761235200
    VALUES
      LESS THAN (
        '2025-10-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761321600
    VALUES
      LESS THAN (
        '2025-10-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761408000
    VALUES
      LESS THAN (
        '2025-10-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761494400
    VALUES
      LESS THAN (
        '2025-10-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761580800
    VALUES
      LESS THAN (
        '2025-10-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761667200
    VALUES
      LESS THAN (
        '2025-10-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761753600
    VALUES
      LESS THAN (
        '2025-10-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761840000
    VALUES
      LESS THAN (
        '2025-10-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761926400
    VALUES
      LESS THAN (
        '2025-11-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762012800
    VALUES
      LESS THAN (
        '2025-11-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762099200
    VALUES
      LESS THAN (
        '2025-11-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762185600
    VALUES
      LESS THAN (
        '2025-11-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762272000
    VALUES
      LESS THAN (
        '2025-11-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762358400
    VALUES
      LESS THAN (
        '2025-11-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762444800
    VALUES
      LESS THAN (
        '2025-11-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762531200
    VALUES
      LESS THAN (
        '2025-11-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762617600
    VALUES
      LESS THAN (
        '2025-11-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762704000
    VALUES
      LESS THAN (
        '2025-11-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762790400
    VALUES
      LESS THAN (
        '2025-11-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762876800
    VALUES
      LESS THAN (
        '2025-11-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762963200
    VALUES
      LESS THAN (
        '2025-11-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763049600
    VALUES
      LESS THAN (
        '2025-11-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763136000
    VALUES
      LESS THAN (
        '2025-11-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763222400
    VALUES
      LESS THAN (
        '2025-11-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763308800
    VALUES
      LESS THAN (
        '2025-11-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763395200
    VALUES
      LESS THAN (
        '2025-11-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763481600
    VALUES
      LESS THAN (
        '2025-11-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763568000
    VALUES
      LESS THAN (
        '2025-11-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763654400
    VALUES
      LESS THAN (
        '2025-11-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763740800
    VALUES
      LESS THAN (
        '2025-11-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763827200
    VALUES
      LESS THAN (
        '2025-11-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763913600
    VALUES
      LESS THAN (
        '2025-11-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764000000
    VALUES
      LESS THAN (
        '2025-11-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764086400
    VALUES
      LESS THAN (
        '2025-11-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764172800
    VALUES
      LESS THAN (
        '2025-11-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764259200
    VALUES
      LESS THAN (
        '2025-11-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764345600
    VALUES
      LESS THAN (
        '2025-11-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764432000
    VALUES
      LESS THAN (
        '2025-11-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764518400
    VALUES
      LESS THAN (
        '2025-12-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764604800
    VALUES
      LESS THAN (
        '2025-12-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764691200
    VALUES
      LESS THAN (
        '2025-12-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764777600
    VALUES
      LESS THAN (
        '2025-12-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764864000
    VALUES
      LESS THAN (
        '2025-12-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764950400
    VALUES
      LESS THAN (
        '2025-12-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765036800
    VALUES
      LESS THAN (
        '2025-12-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765123200
    VALUES
      LESS THAN (
        '2025-12-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765209600
    VALUES
      LESS THAN (
        '2025-12-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765296000
    VALUES
      LESS THAN (
        '2025-12-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765382400
    VALUES
      LESS THAN (
        '2025-12-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765468800
    VALUES
      LESS THAN (
        '2025-12-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765555200
    VALUES
      LESS THAN (
        '2025-12-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765641600
    VALUES
      LESS THAN (
        '2025-12-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765728000
    VALUES
      LESS THAN (
        '2025-12-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765814400
    VALUES
      LESS THAN (
        '2025-12-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765900800
    VALUES
      LESS THAN (
        '2025-12-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765987200
    VALUES
      LESS THAN (
        '2025-12-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766073600
    VALUES
      LESS THAN (
        '2025-12-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766160000
    VALUES
      LESS THAN (
        '2025-12-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766246400
    VALUES
      LESS THAN (
        '2025-12-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766332800
    VALUES
      LESS THAN (
        '2025-12-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766419200
    VALUES
      LESS THAN (
        '2025-12-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766505600
    VALUES
      LESS THAN (
        '2025-12-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766592000
    VALUES
      LESS THAN (
        '2025-12-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766678400
    VALUES
      LESS THAN (
        '2025-12-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766764800
    VALUES
      LESS THAN (
        '2025-12-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766851200
    VALUES
      LESS THAN (
        '2025-12-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766937600
    VALUES
      LESS THAN (
        '2025-12-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767024000
    VALUES
      LESS THAN (
        '2025-12-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767110400
    VALUES
      LESS THAN (
        '2025-12-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767196800
    VALUES
      LESS THAN (
        '2026-01-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767283200
    VALUES
      LESS THAN (
        '2026-01-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767369600
    VALUES
      LESS THAN (
        '2026-01-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767456000
    VALUES
      LESS THAN (
        '2026-01-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767542400
    VALUES
      LESS THAN (
        '2026-01-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767628800
    VALUES
      LESS THAN (
        '2026-01-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767715200
    VALUES
      LESS THAN (
        '2026-01-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767801600
    VALUES
      LESS THAN (
        '2026-01-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767888000
    VALUES
      LESS THAN (
        '2026-01-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767974400
    VALUES
      LESS THAN (
        '2026-01-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768060800
    VALUES
      LESS THAN (
        '2026-01-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768147200
    VALUES
      LESS THAN (
        '2026-01-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768233600
    VALUES
      LESS THAN (
        '2026-01-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768320000
    VALUES
      LESS THAN (
        '2026-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768406400
    VALUES
      LESS THAN (
        '2026-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768492800
    VALUES
      LESS THAN (
        '2026-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768579200
    VALUES
      LESS THAN (
        '2026-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768665600
    VALUES
      LESS THAN (
        '2026-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768752000
    VALUES
      LESS THAN (
        '2026-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768838400
    VALUES
      LESS THAN (
        '2026-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768924800
    VALUES
      LESS THAN (
        '2026-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769011200
    VALUES
      LESS THAN (
        '2026-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769097600
    VALUES
      LESS THAN (
        '2026-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769184000
    VALUES
      LESS THAN (
        '2026-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769270400
    VALUES
      LESS THAN (
        '2026-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769356800
    VALUES
      LESS THAN (
        '2026-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769443200
    VALUES
      LESS THAN (
        '2026-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769529600
    VALUES
      LESS THAN (
        '2026-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769616000
    VALUES
      LESS THAN (
        '2026-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769702400
    VALUES
      LESS THAN (
        '2026-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769788800
    VALUES
      LESS THAN (
        '2026-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769875200
    VALUES
      LESS THAN (
        '2026-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769961600
    VALUES
      LESS THAN (
        '2026-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770048000
    VALUES
      LESS THAN (
        '2026-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770134400
    VALUES
      LESS THAN (
        '2026-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770220800
    VALUES
      LESS THAN (
        '2026-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770307200
    VALUES
      LESS THAN (
        '2026-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770393600
    VALUES
      LESS THAN (
        '2026-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770480000
    VALUES
      LESS THAN (
        '2026-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770566400
    VALUES
      LESS THAN (
        '2026-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770652800
    VALUES
      LESS THAN (
        '2026-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770739200
    VALUES
      LESS THAN (
        '2026-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770825600
    VALUES
      LESS THAN (
        '2026-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770912000
    VALUES
      LESS THAN (
        '2026-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770998400
    VALUES
      LESS THAN (
        '2026-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771084800
    VALUES
      LESS THAN (
        '2026-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771171200
    VALUES
      LESS THAN (
        '2026-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771257600
    VALUES
      LESS THAN (
        '2026-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771344000
    VALUES
      LESS THAN (
        '2026-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771430400
    VALUES
      LESS THAN (
        '2026-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771516800
    VALUES
      LESS THAN (
        '2026-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771603200
    VALUES
      LESS THAN (
        '2026-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771689600
    VALUES
      LESS THAN (
        '2026-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771776000
    VALUES
      LESS THAN (
        '2026-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771862400
    VALUES
      LESS THAN (
        '2026-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771948800
    VALUES
      LESS THAN (
        '2026-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772035200
    VALUES
      LESS THAN (
        '2026-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772121600
    VALUES
      LESS THAN (
        '2026-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772208000
    VALUES
      LESS THAN (
        '2026-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772294400
    VALUES
      LESS THAN (
        '2026-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772380800
    VALUES
      LESS THAN (
        '2026-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772467200
    VALUES
      LESS THAN (
        '2026-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772553600
    VALUES
      LESS THAN (
        '2026-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772640000
    VALUES
      LESS THAN (
        '2026-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772726400
    VALUES
      LESS THAN (
        '2026-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772812800
    VALUES
      LESS THAN (
        '2026-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772899200
    VALUES
      LESS THAN (
        '2026-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772985600
    VALUES
      LESS THAN (
        '2026-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773072000
    VALUES
      LESS THAN (
        '2026-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773158400
    VALUES
      LESS THAN (
        '2026-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773244800
    VALUES
      LESS THAN (
        '2026-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773331200
    VALUES
      LESS THAN (
        '2026-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773417600
    VALUES
      LESS THAN (
        '2026-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773504000
    VALUES
      LESS THAN (
        '2026-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773590400
    VALUES
      LESS THAN (
        '2026-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773676800
    VALUES
      LESS THAN (
        '2026-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773763200
    VALUES
      LESS THAN (
        '2026-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773849600
    VALUES
      LESS THAN (
        '2026-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773936000
    VALUES
      LESS THAN (
        '2026-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774022400
    VALUES
      LESS THAN (
        '2026-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774108800
    VALUES
      LESS THAN (
        '2026-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774195200
    VALUES
      LESS THAN (
        '2026-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774281600
    VALUES
      LESS THAN (
        '2026-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774368000
    VALUES
      LESS THAN (
        '2026-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774454400
    VALUES
      LESS THAN (
        '2026-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774540800
    VALUES
      LESS THAN (
        '2026-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774627200
    VALUES
      LESS THAN (
        '2026-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774713600
    VALUES
      LESS THAN (
        '2026-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774800000
    VALUES
      LESS THAN (
        '2026-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774886400
    VALUES
      LESS THAN (
        '2026-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774972800
    VALUES
      LESS THAN (
        '2026-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775059200
    VALUES
      LESS THAN (
        '2026-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775145600
    VALUES
      LESS THAN (
        '2026-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775232000
    VALUES
      LESS THAN (
        '2026-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775318400
    VALUES
      LESS THAN (
        '2026-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775404800
    VALUES
      LESS THAN (
        '2026-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775491200
    VALUES
      LESS THAN (
        '2026-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775577600
    VALUES
      LESS THAN (
        '2026-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775664000
    VALUES
      LESS THAN (
        '2026-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775750400
    VALUES
      LESS THAN (
        '2026-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775836800
    VALUES
      LESS THAN (
        '2026-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775923200
    VALUES
      LESS THAN (
        '2026-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776009600
    VALUES
      LESS THAN (
        '2026-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776096000
    VALUES
      LESS THAN (
        '2026-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776182400
    VALUES
      LESS THAN (
        '2026-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776268800
    VALUES
      LESS THAN (
        '2026-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776355200
    VALUES
      LESS THAN (
        '2026-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776441600
    VALUES
      LESS THAN (
        '2026-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776528000
    VALUES
      LESS THAN (
        '2026-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776614400
    VALUES
      LESS THAN (
        '2026-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776700800
    VALUES
      LESS THAN (
        '2026-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776787200
    VALUES
      LESS THAN (
        '2026-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776873600
    VALUES
      LESS THAN (
        '2026-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776960000
    VALUES
      LESS THAN (
        '2026-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777046400
    VALUES
      LESS THAN (
        '2026-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777132800
    VALUES
      LESS THAN (
        '2026-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777219200
    VALUES
      LESS THAN (
        '2026-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777305600
    VALUES
      LESS THAN (
        '2026-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777392000
    VALUES
      LESS THAN (
        '2026-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777478400
    VALUES
      LESS THAN (
        '2026-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777564800
    VALUES
      LESS THAN (
        '2026-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777651200
    VALUES
      LESS THAN (
        '2026-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777737600
    VALUES
      LESS THAN (
        '2026-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777824000
    VALUES
      LESS THAN (
        '2026-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777910400
    VALUES
      LESS THAN (
        '2026-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777996800
    VALUES
      LESS THAN (
        '2026-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778083200
    VALUES
      LESS THAN (
        '2026-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778169600
    VALUES
      LESS THAN (
        '2026-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778256000
    VALUES
      LESS THAN (
        '2026-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778342400
    VALUES
      LESS THAN (
        '2026-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778428800
    VALUES
      LESS THAN (
        '2026-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778515200
    VALUES
      LESS THAN (
        '2026-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778601600
    VALUES
      LESS THAN (
        '2026-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778688000
    VALUES
      LESS THAN (
        '2026-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778774400
    VALUES
      LESS THAN (
        '2026-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778860800
    VALUES
      LESS THAN (
        '2026-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778947200
    VALUES
      LESS THAN (
        '2026-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779033600
    VALUES
      LESS THAN (
        '2026-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779120000
    VALUES
      LESS THAN (
        '2026-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779206400
    VALUES
      LESS THAN (
        '2026-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779292800
    VALUES
      LESS THAN (
        '2026-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779379200
    VALUES
      LESS THAN (
        '2026-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779465600
    VALUES
      LESS THAN (
        '2026-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779552000
    VALUES
      LESS THAN (
        '2026-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779638400
    VALUES
      LESS THAN (
        '2026-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779724800
    VALUES
      LESS THAN (
        '2026-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779811200
    VALUES
      LESS THAN (
        '2026-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779897600
    VALUES
      LESS THAN (
        '2026-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779984000
    VALUES
      LESS THAN (
        '2026-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780070400
    VALUES
      LESS THAN (
        '2026-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780156800
    VALUES
      LESS THAN (
        '2026-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780243200
    VALUES
      LESS THAN (
        '2026-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780329600
    VALUES
      LESS THAN (
        '2026-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780416000
    VALUES
      LESS THAN (
        '2026-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780502400
    VALUES
      LESS THAN (
        '2026-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780588800
    VALUES
      LESS THAN (
        '2026-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780675200
    VALUES
      LESS THAN (
        '2026-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780761600
    VALUES
      LESS THAN (
        '2026-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780848000
    VALUES
      LESS THAN (
        '2026-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780934400
    VALUES
      LESS THAN (
        '2026-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781020800
    VALUES
      LESS THAN (
        '2026-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781107200
    VALUES
      LESS THAN (
        '2026-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781193600
    VALUES
      LESS THAN (
        '2026-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE ads_chnl_auth_qty_df IS '分渠道_授权用户数_日度';

COMMENT ON COLUMN ads_chnl_auth_qty_df.data_dt IS '数据日期';

COMMENT ON COLUMN ads_chnl_auth_qty_df.rgst_sec_chnl_nm IS '注册二级渠道';

COMMENT ON COLUMN ads_chnl_auth_qty_df.auth_sec_chnl_nm IS '授权渠道名称';

COMMENT ON COLUMN ads_chnl_auth_qty_df.auth_user_cnt IS '当日_授权账户量';

COMMENT ON COLUMN ads_chnl_auth_qty_df.auth_user_7d_cnt IS '近7日_授权账户量';

COMMENT ON COLUMN ads_chnl_auth_qty_df.auth_user_30d_cnt IS '近30日_授权账户量';

COMMENT ON COLUMN ads_chnl_auth_qty_df.auth_user_mon_cnt IS '当月累计_授权账户量';

COMMENT ON COLUMN ads_chnl_auth_qty_df.auth_user_year_cnt IS '当年累计_授权账户量';

COMMENT ON COLUMN ads_chnl_auth_qty_df.auth_user_all_cnt IS '历史累计_授权账户量';

COMMENT ON COLUMN ads_chnl_auth_qty_df.ds IS '日期分区';

SET
  search_path = rec;

CREATE TABLE
  ads_chnl_rltv_chnl_df (
    data_dt timestamp (0) without TIME zone,
    rltv_chnl_cnt bigint,
    rltv_chnl_nop bigint,
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '10 years',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(data_dt) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1
    VALUES
      LESS THAN (
        '2025-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752595200
    VALUES
      LESS THAN (
        '2025-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752681600
    VALUES
      LESS THAN (
        '2025-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752768000
    VALUES
      LESS THAN (
        '2025-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752854400
    VALUES
      LESS THAN (
        '2025-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752940800
    VALUES
      LESS THAN (
        '2025-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753027200
    VALUES
      LESS THAN (
        '2025-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753113600
    VALUES
      LESS THAN (
        '2025-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753200000
    VALUES
      LESS THAN (
        '2025-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753286400
    VALUES
      LESS THAN (
        '2025-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753372800
    VALUES
      LESS THAN (
        '2025-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753459200
    VALUES
      LESS THAN (
        '2025-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753545600
    VALUES
      LESS THAN (
        '2025-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753632000
    VALUES
      LESS THAN (
        '2025-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753718400
    VALUES
      LESS THAN (
        '2025-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753804800
    VALUES
      LESS THAN (
        '2025-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753891200
    VALUES
      LESS THAN (
        '2025-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753977600
    VALUES
      LESS THAN (
        '2025-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754064000
    VALUES
      LESS THAN (
        '2025-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754150400
    VALUES
      LESS THAN (
        '2025-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754236800
    VALUES
      LESS THAN (
        '2025-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754323200
    VALUES
      LESS THAN (
        '2025-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754409600
    VALUES
      LESS THAN (
        '2025-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754496000
    VALUES
      LESS THAN (
        '2025-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754582400
    VALUES
      LESS THAN (
        '2025-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754668800
    VALUES
      LESS THAN (
        '2025-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754755200
    VALUES
      LESS THAN (
        '2025-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754841600
    VALUES
      LESS THAN (
        '2025-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754928000
    VALUES
      LESS THAN (
        '2025-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755014400
    VALUES
      LESS THAN (
        '2025-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755100800
    VALUES
      LESS THAN (
        '2025-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755187200
    VALUES
      LESS THAN (
        '2025-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755273600
    VALUES
      LESS THAN (
        '2025-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755360000
    VALUES
      LESS THAN (
        '2025-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755446400
    VALUES
      LESS THAN (
        '2025-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755532800
    VALUES
      LESS THAN (
        '2025-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755619200
    VALUES
      LESS THAN (
        '2025-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755705600
    VALUES
      LESS THAN (
        '2025-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755792000
    VALUES
      LESS THAN (
        '2025-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755878400
    VALUES
      LESS THAN (
        '2025-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755964800
    VALUES
      LESS THAN (
        '2025-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756051200
    VALUES
      LESS THAN (
        '2025-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756137600
    VALUES
      LESS THAN (
        '2025-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756224000
    VALUES
      LESS THAN (
        '2025-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756310400
    VALUES
      LESS THAN (
        '2025-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756396800
    VALUES
      LESS THAN (
        '2025-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756483200
    VALUES
      LESS THAN (
        '2025-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756569600
    VALUES
      LESS THAN (
        '2025-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756656000
    VALUES
      LESS THAN (
        '2025-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756742400
    VALUES
      LESS THAN (
        '2025-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756828800
    VALUES
      LESS THAN (
        '2025-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756915200
    VALUES
      LESS THAN (
        '2025-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757001600
    VALUES
      LESS THAN (
        '2025-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757088000
    VALUES
      LESS THAN (
        '2025-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757174400
    VALUES
      LESS THAN (
        '2025-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757260800
    VALUES
      LESS THAN (
        '2025-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757347200
    VALUES
      LESS THAN (
        '2025-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757433600
    VALUES
      LESS THAN (
        '2025-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757520000
    VALUES
      LESS THAN (
        '2025-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757606400
    VALUES
      LESS THAN (
        '2025-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757692800
    VALUES
      LESS THAN (
        '2025-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757779200
    VALUES
      LESS THAN (
        '2025-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757865600
    VALUES
      LESS THAN (
        '2025-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757952000
    VALUES
      LESS THAN (
        '2025-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758038400
    VALUES
      LESS THAN (
        '2025-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758124800
    VALUES
      LESS THAN (
        '2025-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758211200
    VALUES
      LESS THAN (
        '2025-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758297600
    VALUES
      LESS THAN (
        '2025-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758384000
    VALUES
      LESS THAN (
        '2025-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758470400
    VALUES
      LESS THAN (
        '2025-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758556800
    VALUES
      LESS THAN (
        '2025-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758643200
    VALUES
      LESS THAN (
        '2025-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758729600
    VALUES
      LESS THAN (
        '2025-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758816000
    VALUES
      LESS THAN (
        '2025-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758902400
    VALUES
      LESS THAN (
        '2025-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758988800
    VALUES
      LESS THAN (
        '2025-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759075200
    VALUES
      LESS THAN (
        '2025-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759161600
    VALUES
      LESS THAN (
        '2025-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759248000
    VALUES
      LESS THAN (
        '2025-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759334400
    VALUES
      LESS THAN (
        '2025-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759420800
    VALUES
      LESS THAN (
        '2025-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759507200
    VALUES
      LESS THAN (
        '2025-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759593600
    VALUES
      LESS THAN (
        '2025-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759680000
    VALUES
      LESS THAN (
        '2025-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759766400
    VALUES
      LESS THAN (
        '2025-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759852800
    VALUES
      LESS THAN (
        '2025-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759939200
    VALUES
      LESS THAN (
        '2025-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760025600
    VALUES
      LESS THAN (
        '2025-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760112000
    VALUES
      LESS THAN (
        '2025-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760198400
    VALUES
      LESS THAN (
        '2025-10-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760284800
    VALUES
      LESS THAN (
        '2025-10-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760371200
    VALUES
      LESS THAN (
        '2025-10-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760457600
    VALUES
      LESS THAN (
        '2025-10-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760544000
    VALUES
      LESS THAN (
        '2025-10-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760630400
    VALUES
      LESS THAN (
        '2025-10-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760716800
    VALUES
      LESS THAN (
        '2025-10-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760803200
    VALUES
      LESS THAN (
        '2025-10-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760889600
    VALUES
      LESS THAN (
        '2025-10-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760976000
    VALUES
      LESS THAN (
        '2025-10-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761062400
    VALUES
      LESS THAN (
        '2025-10-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761148800
    VALUES
      LESS THAN (
        '2025-10-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761235200
    VALUES
      LESS THAN (
        '2025-10-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761321600
    VALUES
      LESS THAN (
        '2025-10-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761408000
    VALUES
      LESS THAN (
        '2025-10-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761494400
    VALUES
      LESS THAN (
        '2025-10-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761580800
    VALUES
      LESS THAN (
        '2025-10-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761667200
    VALUES
      LESS THAN (
        '2025-10-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761753600
    VALUES
      LESS THAN (
        '2025-10-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761840000
    VALUES
      LESS THAN (
        '2025-10-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761926400
    VALUES
      LESS THAN (
        '2025-11-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762012800
    VALUES
      LESS THAN (
        '2025-11-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762099200
    VALUES
      LESS THAN (
        '2025-11-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762185600
    VALUES
      LESS THAN (
        '2025-11-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762272000
    VALUES
      LESS THAN (
        '2025-11-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762358400
    VALUES
      LESS THAN (
        '2025-11-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762444800
    VALUES
      LESS THAN (
        '2025-11-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762531200
    VALUES
      LESS THAN (
        '2025-11-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762617600
    VALUES
      LESS THAN (
        '2025-11-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762704000
    VALUES
      LESS THAN (
        '2025-11-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762790400
    VALUES
      LESS THAN (
        '2025-11-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762876800
    VALUES
      LESS THAN (
        '2025-11-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762963200
    VALUES
      LESS THAN (
        '2025-11-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763049600
    VALUES
      LESS THAN (
        '2025-11-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763136000
    VALUES
      LESS THAN (
        '2025-11-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763222400
    VALUES
      LESS THAN (
        '2025-11-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763308800
    VALUES
      LESS THAN (
        '2025-11-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763395200
    VALUES
      LESS THAN (
        '2025-11-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763481600
    VALUES
      LESS THAN (
        '2025-11-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763568000
    VALUES
      LESS THAN (
        '2025-11-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763654400
    VALUES
      LESS THAN (
        '2025-11-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763740800
    VALUES
      LESS THAN (
        '2025-11-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763827200
    VALUES
      LESS THAN (
        '2025-11-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763913600
    VALUES
      LESS THAN (
        '2025-11-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764000000
    VALUES
      LESS THAN (
        '2025-11-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764086400
    VALUES
      LESS THAN (
        '2025-11-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764172800
    VALUES
      LESS THAN (
        '2025-11-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764259200
    VALUES
      LESS THAN (
        '2025-11-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764345600
    VALUES
      LESS THAN (
        '2025-11-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764432000
    VALUES
      LESS THAN (
        '2025-11-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764518400
    VALUES
      LESS THAN (
        '2025-12-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764604800
    VALUES
      LESS THAN (
        '2025-12-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764691200
    VALUES
      LESS THAN (
        '2025-12-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764777600
    VALUES
      LESS THAN (
        '2025-12-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764864000
    VALUES
      LESS THAN (
        '2025-12-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764950400
    VALUES
      LESS THAN (
        '2025-12-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765036800
    VALUES
      LESS THAN (
        '2025-12-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765123200
    VALUES
      LESS THAN (
        '2025-12-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765209600
    VALUES
      LESS THAN (
        '2025-12-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765296000
    VALUES
      LESS THAN (
        '2025-12-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765382400
    VALUES
      LESS THAN (
        '2025-12-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765468800
    VALUES
      LESS THAN (
        '2025-12-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765555200
    VALUES
      LESS THAN (
        '2025-12-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765641600
    VALUES
      LESS THAN (
        '2025-12-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765728000
    VALUES
      LESS THAN (
        '2025-12-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765814400
    VALUES
      LESS THAN (
        '2025-12-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765900800
    VALUES
      LESS THAN (
        '2025-12-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765987200
    VALUES
      LESS THAN (
        '2025-12-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766073600
    VALUES
      LESS THAN (
        '2025-12-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766160000
    VALUES
      LESS THAN (
        '2025-12-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766246400
    VALUES
      LESS THAN (
        '2025-12-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766332800
    VALUES
      LESS THAN (
        '2025-12-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766419200
    VALUES
      LESS THAN (
        '2025-12-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766505600
    VALUES
      LESS THAN (
        '2025-12-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766592000
    VALUES
      LESS THAN (
        '2025-12-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766678400
    VALUES
      LESS THAN (
        '2025-12-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766764800
    VALUES
      LESS THAN (
        '2025-12-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766851200
    VALUES
      LESS THAN (
        '2025-12-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766937600
    VALUES
      LESS THAN (
        '2025-12-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767024000
    VALUES
      LESS THAN (
        '2025-12-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767110400
    VALUES
      LESS THAN (
        '2025-12-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767196800
    VALUES
      LESS THAN (
        '2026-01-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767283200
    VALUES
      LESS THAN (
        '2026-01-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767369600
    VALUES
      LESS THAN (
        '2026-01-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767456000
    VALUES
      LESS THAN (
        '2026-01-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767542400
    VALUES
      LESS THAN (
        '2026-01-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767628800
    VALUES
      LESS THAN (
        '2026-01-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767715200
    VALUES
      LESS THAN (
        '2026-01-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767801600
    VALUES
      LESS THAN (
        '2026-01-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767888000
    VALUES
      LESS THAN (
        '2026-01-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767974400
    VALUES
      LESS THAN (
        '2026-01-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768060800
    VALUES
      LESS THAN (
        '2026-01-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768147200
    VALUES
      LESS THAN (
        '2026-01-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768233600
    VALUES
      LESS THAN (
        '2026-01-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768320000
    VALUES
      LESS THAN (
        '2026-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768406400
    VALUES
      LESS THAN (
        '2026-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768492800
    VALUES
      LESS THAN (
        '2026-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768579200
    VALUES
      LESS THAN (
        '2026-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768665600
    VALUES
      LESS THAN (
        '2026-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768752000
    VALUES
      LESS THAN (
        '2026-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768838400
    VALUES
      LESS THAN (
        '2026-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768924800
    VALUES
      LESS THAN (
        '2026-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769011200
    VALUES
      LESS THAN (
        '2026-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769097600
    VALUES
      LESS THAN (
        '2026-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769184000
    VALUES
      LESS THAN (
        '2026-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769270400
    VALUES
      LESS THAN (
        '2026-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769356800
    VALUES
      LESS THAN (
        '2026-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769443200
    VALUES
      LESS THAN (
        '2026-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769529600
    VALUES
      LESS THAN (
        '2026-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769616000
    VALUES
      LESS THAN (
        '2026-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769702400
    VALUES
      LESS THAN (
        '2026-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769788800
    VALUES
      LESS THAN (
        '2026-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769875200
    VALUES
      LESS THAN (
        '2026-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769961600
    VALUES
      LESS THAN (
        '2026-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770048000
    VALUES
      LESS THAN (
        '2026-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770134400
    VALUES
      LESS THAN (
        '2026-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770220800
    VALUES
      LESS THAN (
        '2026-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770307200
    VALUES
      LESS THAN (
        '2026-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770393600
    VALUES
      LESS THAN (
        '2026-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770480000
    VALUES
      LESS THAN (
        '2026-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770566400
    VALUES
      LESS THAN (
        '2026-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770652800
    VALUES
      LESS THAN (
        '2026-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770739200
    VALUES
      LESS THAN (
        '2026-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770825600
    VALUES
      LESS THAN (
        '2026-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770912000
    VALUES
      LESS THAN (
        '2026-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770998400
    VALUES
      LESS THAN (
        '2026-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771084800
    VALUES
      LESS THAN (
        '2026-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771171200
    VALUES
      LESS THAN (
        '2026-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771257600
    VALUES
      LESS THAN (
        '2026-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771344000
    VALUES
      LESS THAN (
        '2026-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771430400
    VALUES
      LESS THAN (
        '2026-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771516800
    VALUES
      LESS THAN (
        '2026-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771603200
    VALUES
      LESS THAN (
        '2026-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771689600
    VALUES
      LESS THAN (
        '2026-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771776000
    VALUES
      LESS THAN (
        '2026-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771862400
    VALUES
      LESS THAN (
        '2026-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771948800
    VALUES
      LESS THAN (
        '2026-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772035200
    VALUES
      LESS THAN (
        '2026-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772121600
    VALUES
      LESS THAN (
        '2026-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772208000
    VALUES
      LESS THAN (
        '2026-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772294400
    VALUES
      LESS THAN (
        '2026-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772380800
    VALUES
      LESS THAN (
        '2026-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772467200
    VALUES
      LESS THAN (
        '2026-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772553600
    VALUES
      LESS THAN (
        '2026-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772640000
    VALUES
      LESS THAN (
        '2026-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772726400
    VALUES
      LESS THAN (
        '2026-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772812800
    VALUES
      LESS THAN (
        '2026-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772899200
    VALUES
      LESS THAN (
        '2026-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772985600
    VALUES
      LESS THAN (
        '2026-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773072000
    VALUES
      LESS THAN (
        '2026-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773158400
    VALUES
      LESS THAN (
        '2026-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773244800
    VALUES
      LESS THAN (
        '2026-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773331200
    VALUES
      LESS THAN (
        '2026-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773417600
    VALUES
      LESS THAN (
        '2026-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773504000
    VALUES
      LESS THAN (
        '2026-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773590400
    VALUES
      LESS THAN (
        '2026-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773676800
    VALUES
      LESS THAN (
        '2026-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773763200
    VALUES
      LESS THAN (
        '2026-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773849600
    VALUES
      LESS THAN (
        '2026-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773936000
    VALUES
      LESS THAN (
        '2026-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774022400
    VALUES
      LESS THAN (
        '2026-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774108800
    VALUES
      LESS THAN (
        '2026-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774195200
    VALUES
      LESS THAN (
        '2026-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774281600
    VALUES
      LESS THAN (
        '2026-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774368000
    VALUES
      LESS THAN (
        '2026-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774454400
    VALUES
      LESS THAN (
        '2026-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774540800
    VALUES
      LESS THAN (
        '2026-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774627200
    VALUES
      LESS THAN (
        '2026-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774713600
    VALUES
      LESS THAN (
        '2026-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774800000
    VALUES
      LESS THAN (
        '2026-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774886400
    VALUES
      LESS THAN (
        '2026-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774972800
    VALUES
      LESS THAN (
        '2026-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775059200
    VALUES
      LESS THAN (
        '2026-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775145600
    VALUES
      LESS THAN (
        '2026-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775232000
    VALUES
      LESS THAN (
        '2026-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775318400
    VALUES
      LESS THAN (
        '2026-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775404800
    VALUES
      LESS THAN (
        '2026-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775491200
    VALUES
      LESS THAN (
        '2026-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775577600
    VALUES
      LESS THAN (
        '2026-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775664000
    VALUES
      LESS THAN (
        '2026-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775750400
    VALUES
      LESS THAN (
        '2026-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775836800
    VALUES
      LESS THAN (
        '2026-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775923200
    VALUES
      LESS THAN (
        '2026-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776009600
    VALUES
      LESS THAN (
        '2026-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776096000
    VALUES
      LESS THAN (
        '2026-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776182400
    VALUES
      LESS THAN (
        '2026-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776268800
    VALUES
      LESS THAN (
        '2026-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776355200
    VALUES
      LESS THAN (
        '2026-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776441600
    VALUES
      LESS THAN (
        '2026-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776528000
    VALUES
      LESS THAN (
        '2026-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776614400
    VALUES
      LESS THAN (
        '2026-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776700800
    VALUES
      LESS THAN (
        '2026-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776787200
    VALUES
      LESS THAN (
        '2026-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776873600
    VALUES
      LESS THAN (
        '2026-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776960000
    VALUES
      LESS THAN (
        '2026-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777046400
    VALUES
      LESS THAN (
        '2026-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777132800
    VALUES
      LESS THAN (
        '2026-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777219200
    VALUES
      LESS THAN (
        '2026-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777305600
    VALUES
      LESS THAN (
        '2026-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777392000
    VALUES
      LESS THAN (
        '2026-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777478400
    VALUES
      LESS THAN (
        '2026-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777564800
    VALUES
      LESS THAN (
        '2026-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777651200
    VALUES
      LESS THAN (
        '2026-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777737600
    VALUES
      LESS THAN (
        '2026-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777824000
    VALUES
      LESS THAN (
        '2026-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777910400
    VALUES
      LESS THAN (
        '2026-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777996800
    VALUES
      LESS THAN (
        '2026-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778083200
    VALUES
      LESS THAN (
        '2026-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778169600
    VALUES
      LESS THAN (
        '2026-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778256000
    VALUES
      LESS THAN (
        '2026-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778342400
    VALUES
      LESS THAN (
        '2026-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778428800
    VALUES
      LESS THAN (
        '2026-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778515200
    VALUES
      LESS THAN (
        '2026-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778601600
    VALUES
      LESS THAN (
        '2026-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778688000
    VALUES
      LESS THAN (
        '2026-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778774400
    VALUES
      LESS THAN (
        '2026-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778860800
    VALUES
      LESS THAN (
        '2026-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778947200
    VALUES
      LESS THAN (
        '2026-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779033600
    VALUES
      LESS THAN (
        '2026-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779120000
    VALUES
      LESS THAN (
        '2026-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779206400
    VALUES
      LESS THAN (
        '2026-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779292800
    VALUES
      LESS THAN (
        '2026-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779379200
    VALUES
      LESS THAN (
        '2026-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779465600
    VALUES
      LESS THAN (
        '2026-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779552000
    VALUES
      LESS THAN (
        '2026-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779638400
    VALUES
      LESS THAN (
        '2026-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779724800
    VALUES
      LESS THAN (
        '2026-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779811200
    VALUES
      LESS THAN (
        '2026-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779897600
    VALUES
      LESS THAN (
        '2026-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779984000
    VALUES
      LESS THAN (
        '2026-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780070400
    VALUES
      LESS THAN (
        '2026-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780156800
    VALUES
      LESS THAN (
        '2026-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780243200
    VALUES
      LESS THAN (
        '2026-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780329600
    VALUES
      LESS THAN (
        '2026-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780416000
    VALUES
      LESS THAN (
        '2026-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780502400
    VALUES
      LESS THAN (
        '2026-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780588800
    VALUES
      LESS THAN (
        '2026-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780675200
    VALUES
      LESS THAN (
        '2026-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780761600
    VALUES
      LESS THAN (
        '2026-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780848000
    VALUES
      LESS THAN (
        '2026-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780934400
    VALUES
      LESS THAN (
        '2026-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781020800
    VALUES
      LESS THAN (
        '2026-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781107200
    VALUES
      LESS THAN (
        '2026-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781193600
    VALUES
      LESS THAN (
        '2026-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE ads_chnl_rltv_chnl_df IS '关联渠道用户数';

COMMENT ON COLUMN ads_chnl_rltv_chnl_df.data_dt IS '数据日期';

COMMENT ON COLUMN ads_chnl_rltv_chnl_df.rltv_chnl_cnt IS '关联渠道个数';

COMMENT ON COLUMN ads_chnl_rltv_chnl_df.rltv_chnl_nop IS '关联渠道人数';

COMMENT ON COLUMN ads_chnl_rltv_chnl_df.ds IS '分区日期';




SET
  search_path = rec;

CREATE TABLE
  ads_chnl_rgst_to_real_auth_dau_df (
    data_dt timestamp (0) without TIME zone,
    rgst_sec_chnl_nm character varying (128),
    chnl_sub_nm character varying (128),
    rgst_cnt_d bigint,
    rgst_cnt_m bigint,
    rgst_cnt_a bigint,
    real_cnt_d bigint,
    real_cnt_m bigint,
    real_cnt_a bigint,
    auth_cnt_d bigint,
    auth_cnt_m bigint,
    auth_cnt_a bigint,
    rgst_log_cnt_d bigint,
    rgst_log_cnt_m bigint,
    rgst_log_cnt_a bigint,
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '10 years',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(data_dt) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1
    VALUES
      LESS THAN (
        '2025-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752854400
    VALUES
      LESS THAN (
        '2025-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752940800
    VALUES
      LESS THAN (
        '2025-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753027200
    VALUES
      LESS THAN (
        '2025-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753113600
    VALUES
      LESS THAN (
        '2025-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753200000
    VALUES
      LESS THAN (
        '2025-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753286400
    VALUES
      LESS THAN (
        '2025-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753372800
    VALUES
      LESS THAN (
        '2025-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753459200
    VALUES
      LESS THAN (
        '2025-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753545600
    VALUES
      LESS THAN (
        '2025-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753632000
    VALUES
      LESS THAN (
        '2025-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753718400
    VALUES
      LESS THAN (
        '2025-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753804800
    VALUES
      LESS THAN (
        '2025-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753891200
    VALUES
      LESS THAN (
        '2025-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1753977600
    VALUES
      LESS THAN (
        '2025-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754064000
    VALUES
      LESS THAN (
        '2025-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754150400
    VALUES
      LESS THAN (
        '2025-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754236800
    VALUES
      LESS THAN (
        '2025-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754323200
    VALUES
      LESS THAN (
        '2025-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754409600
    VALUES
      LESS THAN (
        '2025-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754496000
    VALUES
      LESS THAN (
        '2025-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754582400
    VALUES
      LESS THAN (
        '2025-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754668800
    VALUES
      LESS THAN (
        '2025-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754755200
    VALUES
      LESS THAN (
        '2025-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754841600
    VALUES
      LESS THAN (
        '2025-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1754928000
    VALUES
      LESS THAN (
        '2025-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755014400
    VALUES
      LESS THAN (
        '2025-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755100800
    VALUES
      LESS THAN (
        '2025-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755187200
    VALUES
      LESS THAN (
        '2025-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755273600
    VALUES
      LESS THAN (
        '2025-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755360000
    VALUES
      LESS THAN (
        '2025-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755446400
    VALUES
      LESS THAN (
        '2025-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755532800
    VALUES
      LESS THAN (
        '2025-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755619200
    VALUES
      LESS THAN (
        '2025-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755705600
    VALUES
      LESS THAN (
        '2025-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755792000
    VALUES
      LESS THAN (
        '2025-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755878400
    VALUES
      LESS THAN (
        '2025-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1755964800
    VALUES
      LESS THAN (
        '2025-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756051200
    VALUES
      LESS THAN (
        '2025-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756137600
    VALUES
      LESS THAN (
        '2025-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756224000
    VALUES
      LESS THAN (
        '2025-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756310400
    VALUES
      LESS THAN (
        '2025-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756396800
    VALUES
      LESS THAN (
        '2025-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756483200
    VALUES
      LESS THAN (
        '2025-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756569600
    VALUES
      LESS THAN (
        '2025-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756656000
    VALUES
      LESS THAN (
        '2025-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756742400
    VALUES
      LESS THAN (
        '2025-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756828800
    VALUES
      LESS THAN (
        '2025-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1756915200
    VALUES
      LESS THAN (
        '2025-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757001600
    VALUES
      LESS THAN (
        '2025-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757088000
    VALUES
      LESS THAN (
        '2025-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757174400
    VALUES
      LESS THAN (
        '2025-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757260800
    VALUES
      LESS THAN (
        '2025-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757347200
    VALUES
      LESS THAN (
        '2025-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757433600
    VALUES
      LESS THAN (
        '2025-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757520000
    VALUES
      LESS THAN (
        '2025-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757606400
    VALUES
      LESS THAN (
        '2025-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757692800
    VALUES
      LESS THAN (
        '2025-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757779200
    VALUES
      LESS THAN (
        '2025-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757865600
    VALUES
      LESS THAN (
        '2025-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1757952000
    VALUES
      LESS THAN (
        '2025-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758038400
    VALUES
      LESS THAN (
        '2025-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758124800
    VALUES
      LESS THAN (
        '2025-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758211200
    VALUES
      LESS THAN (
        '2025-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758297600
    VALUES
      LESS THAN (
        '2025-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758384000
    VALUES
      LESS THAN (
        '2025-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758470400
    VALUES
      LESS THAN (
        '2025-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758556800
    VALUES
      LESS THAN (
        '2025-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758643200
    VALUES
      LESS THAN (
        '2025-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758729600
    VALUES
      LESS THAN (
        '2025-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758816000
    VALUES
      LESS THAN (
        '2025-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758902400
    VALUES
      LESS THAN (
        '2025-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1758988800
    VALUES
      LESS THAN (
        '2025-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759075200
    VALUES
      LESS THAN (
        '2025-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759161600
    VALUES
      LESS THAN (
        '2025-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759248000
    VALUES
      LESS THAN (
        '2025-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759334400
    VALUES
      LESS THAN (
        '2025-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759420800
    VALUES
      LESS THAN (
        '2025-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759507200
    VALUES
      LESS THAN (
        '2025-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759593600
    VALUES
      LESS THAN (
        '2025-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759680000
    VALUES
      LESS THAN (
        '2025-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759766400
    VALUES
      LESS THAN (
        '2025-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759852800
    VALUES
      LESS THAN (
        '2025-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1759939200
    VALUES
      LESS THAN (
        '2025-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760025600
    VALUES
      LESS THAN (
        '2025-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760112000
    VALUES
      LESS THAN (
        '2025-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760198400
    VALUES
      LESS THAN (
        '2025-10-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760284800
    VALUES
      LESS THAN (
        '2025-10-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760371200
    VALUES
      LESS THAN (
        '2025-10-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760457600
    VALUES
      LESS THAN (
        '2025-10-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760544000
    VALUES
      LESS THAN (
        '2025-10-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760630400
    VALUES
      LESS THAN (
        '2025-10-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760716800
    VALUES
      LESS THAN (
        '2025-10-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760803200
    VALUES
      LESS THAN (
        '2025-10-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760889600
    VALUES
      LESS THAN (
        '2025-10-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1760976000
    VALUES
      LESS THAN (
        '2025-10-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761062400
    VALUES
      LESS THAN (
        '2025-10-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761148800
    VALUES
      LESS THAN (
        '2025-10-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761235200
    VALUES
      LESS THAN (
        '2025-10-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761321600
    VALUES
      LESS THAN (
        '2025-10-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761408000
    VALUES
      LESS THAN (
        '2025-10-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761494400
    VALUES
      LESS THAN (
        '2025-10-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761580800
    VALUES
      LESS THAN (
        '2025-10-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761667200
    VALUES
      LESS THAN (
        '2025-10-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761753600
    VALUES
      LESS THAN (
        '2025-10-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761840000
    VALUES
      LESS THAN (
        '2025-10-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1761926400
    VALUES
      LESS THAN (
        '2025-11-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762012800
    VALUES
      LESS THAN (
        '2025-11-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762099200
    VALUES
      LESS THAN (
        '2025-11-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762185600
    VALUES
      LESS THAN (
        '2025-11-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762272000
    VALUES
      LESS THAN (
        '2025-11-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762358400
    VALUES
      LESS THAN (
        '2025-11-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762444800
    VALUES
      LESS THAN (
        '2025-11-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762531200
    VALUES
      LESS THAN (
        '2025-11-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762617600
    VALUES
      LESS THAN (
        '2025-11-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762704000
    VALUES
      LESS THAN (
        '2025-11-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762790400
    VALUES
      LESS THAN (
        '2025-11-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762876800
    VALUES
      LESS THAN (
        '2025-11-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1762963200
    VALUES
      LESS THAN (
        '2025-11-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763049600
    VALUES
      LESS THAN (
        '2025-11-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763136000
    VALUES
      LESS THAN (
        '2025-11-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763222400
    VALUES
      LESS THAN (
        '2025-11-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763308800
    VALUES
      LESS THAN (
        '2025-11-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763395200
    VALUES
      LESS THAN (
        '2025-11-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763481600
    VALUES
      LESS THAN (
        '2025-11-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763568000
    VALUES
      LESS THAN (
        '2025-11-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763654400
    VALUES
      LESS THAN (
        '2025-11-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763740800
    VALUES
      LESS THAN (
        '2025-11-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763827200
    VALUES
      LESS THAN (
        '2025-11-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1763913600
    VALUES
      LESS THAN (
        '2025-11-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764000000
    VALUES
      LESS THAN (
        '2025-11-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764086400
    VALUES
      LESS THAN (
        '2025-11-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764172800
    VALUES
      LESS THAN (
        '2025-11-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764259200
    VALUES
      LESS THAN (
        '2025-11-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764345600
    VALUES
      LESS THAN (
        '2025-11-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764432000
    VALUES
      LESS THAN (
        '2025-11-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764518400
    VALUES
      LESS THAN (
        '2025-12-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764604800
    VALUES
      LESS THAN (
        '2025-12-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764691200
    VALUES
      LESS THAN (
        '2025-12-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764777600
    VALUES
      LESS THAN (
        '2025-12-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764864000
    VALUES
      LESS THAN (
        '2025-12-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1764950400
    VALUES
      LESS THAN (
        '2025-12-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765036800
    VALUES
      LESS THAN (
        '2025-12-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765123200
    VALUES
      LESS THAN (
        '2025-12-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765209600
    VALUES
      LESS THAN (
        '2025-12-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765296000
    VALUES
      LESS THAN (
        '2025-12-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765382400
    VALUES
      LESS THAN (
        '2025-12-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765468800
    VALUES
      LESS THAN (
        '2025-12-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765555200
    VALUES
      LESS THAN (
        '2025-12-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765641600
    VALUES
      LESS THAN (
        '2025-12-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765728000
    VALUES
      LESS THAN (
        '2025-12-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765814400
    VALUES
      LESS THAN (
        '2025-12-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765900800
    VALUES
      LESS THAN (
        '2025-12-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1765987200
    VALUES
      LESS THAN (
        '2025-12-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766073600
    VALUES
      LESS THAN (
        '2025-12-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766160000
    VALUES
      LESS THAN (
        '2025-12-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766246400
    VALUES
      LESS THAN (
        '2025-12-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766332800
    VALUES
      LESS THAN (
        '2025-12-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766419200
    VALUES
      LESS THAN (
        '2025-12-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766505600
    VALUES
      LESS THAN (
        '2025-12-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766592000
    VALUES
      LESS THAN (
        '2025-12-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766678400
    VALUES
      LESS THAN (
        '2025-12-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766764800
    VALUES
      LESS THAN (
        '2025-12-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766851200
    VALUES
      LESS THAN (
        '2025-12-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1766937600
    VALUES
      LESS THAN (
        '2025-12-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767024000
    VALUES
      LESS THAN (
        '2025-12-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767110400
    VALUES
      LESS THAN (
        '2025-12-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767196800
    VALUES
      LESS THAN (
        '2026-01-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767283200
    VALUES
      LESS THAN (
        '2026-01-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767369600
    VALUES
      LESS THAN (
        '2026-01-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767456000
    VALUES
      LESS THAN (
        '2026-01-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767542400
    VALUES
      LESS THAN (
        '2026-01-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767628800
    VALUES
      LESS THAN (
        '2026-01-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767715200
    VALUES
      LESS THAN (
        '2026-01-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767801600
    VALUES
      LESS THAN (
        '2026-01-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767888000
    VALUES
      LESS THAN (
        '2026-01-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1767974400
    VALUES
      LESS THAN (
        '2026-01-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768060800
    VALUES
      LESS THAN (
        '2026-01-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768147200
    VALUES
      LESS THAN (
        '2026-01-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768233600
    VALUES
      LESS THAN (
        '2026-01-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768320000
    VALUES
      LESS THAN (
        '2026-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768406400
    VALUES
      LESS THAN (
        '2026-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768492800
    VALUES
      LESS THAN (
        '2026-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768579200
    VALUES
      LESS THAN (
        '2026-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768665600
    VALUES
      LESS THAN (
        '2026-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768752000
    VALUES
      LESS THAN (
        '2026-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768838400
    VALUES
      LESS THAN (
        '2026-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1768924800
    VALUES
      LESS THAN (
        '2026-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769011200
    VALUES
      LESS THAN (
        '2026-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769097600
    VALUES
      LESS THAN (
        '2026-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769184000
    VALUES
      LESS THAN (
        '2026-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769270400
    VALUES
      LESS THAN (
        '2026-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769356800
    VALUES
      LESS THAN (
        '2026-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769443200
    VALUES
      LESS THAN (
        '2026-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769529600
    VALUES
      LESS THAN (
        '2026-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769616000
    VALUES
      LESS THAN (
        '2026-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769702400
    VALUES
      LESS THAN (
        '2026-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769788800
    VALUES
      LESS THAN (
        '2026-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769875200
    VALUES
      LESS THAN (
        '2026-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1769961600
    VALUES
      LESS THAN (
        '2026-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770048000
    VALUES
      LESS THAN (
        '2026-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770134400
    VALUES
      LESS THAN (
        '2026-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770220800
    VALUES
      LESS THAN (
        '2026-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770307200
    VALUES
      LESS THAN (
        '2026-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770393600
    VALUES
      LESS THAN (
        '2026-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770480000
    VALUES
      LESS THAN (
        '2026-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770566400
    VALUES
      LESS THAN (
        '2026-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770652800
    VALUES
      LESS THAN (
        '2026-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770739200
    VALUES
      LESS THAN (
        '2026-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770825600
    VALUES
      LESS THAN (
        '2026-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770912000
    VALUES
      LESS THAN (
        '2026-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1770998400
    VALUES
      LESS THAN (
        '2026-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771084800
    VALUES
      LESS THAN (
        '2026-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771171200
    VALUES
      LESS THAN (
        '2026-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771257600
    VALUES
      LESS THAN (
        '2026-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771344000
    VALUES
      LESS THAN (
        '2026-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771430400
    VALUES
      LESS THAN (
        '2026-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771516800
    VALUES
      LESS THAN (
        '2026-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771603200
    VALUES
      LESS THAN (
        '2026-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771689600
    VALUES
      LESS THAN (
        '2026-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771776000
    VALUES
      LESS THAN (
        '2026-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771862400
    VALUES
      LESS THAN (
        '2026-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1771948800
    VALUES
      LESS THAN (
        '2026-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772035200
    VALUES
      LESS THAN (
        '2026-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772121600
    VALUES
      LESS THAN (
        '2026-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772208000
    VALUES
      LESS THAN (
        '2026-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772294400
    VALUES
      LESS THAN (
        '2026-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772380800
    VALUES
      LESS THAN (
        '2026-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772467200
    VALUES
      LESS THAN (
        '2026-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772553600
    VALUES
      LESS THAN (
        '2026-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772640000
    VALUES
      LESS THAN (
        '2026-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772726400
    VALUES
      LESS THAN (
        '2026-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772812800
    VALUES
      LESS THAN (
        '2026-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772899200
    VALUES
      LESS THAN (
        '2026-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1772985600
    VALUES
      LESS THAN (
        '2026-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773072000
    VALUES
      LESS THAN (
        '2026-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773158400
    VALUES
      LESS THAN (
        '2026-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773244800
    VALUES
      LESS THAN (
        '2026-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773331200
    VALUES
      LESS THAN (
        '2026-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773417600
    VALUES
      LESS THAN (
        '2026-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773504000
    VALUES
      LESS THAN (
        '2026-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773590400
    VALUES
      LESS THAN (
        '2026-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773676800
    VALUES
      LESS THAN (
        '2026-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773763200
    VALUES
      LESS THAN (
        '2026-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773849600
    VALUES
      LESS THAN (
        '2026-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1773936000
    VALUES
      LESS THAN (
        '2026-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774022400
    VALUES
      LESS THAN (
        '2026-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774108800
    VALUES
      LESS THAN (
        '2026-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774195200
    VALUES
      LESS THAN (
        '2026-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774281600
    VALUES
      LESS THAN (
        '2026-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774368000
    VALUES
      LESS THAN (
        '2026-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774454400
    VALUES
      LESS THAN (
        '2026-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774540800
    VALUES
      LESS THAN (
        '2026-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774627200
    VALUES
      LESS THAN (
        '2026-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774713600
    VALUES
      LESS THAN (
        '2026-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774800000
    VALUES
      LESS THAN (
        '2026-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774886400
    VALUES
      LESS THAN (
        '2026-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1774972800
    VALUES
      LESS THAN (
        '2026-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775059200
    VALUES
      LESS THAN (
        '2026-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775145600
    VALUES
      LESS THAN (
        '2026-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775232000
    VALUES
      LESS THAN (
        '2026-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775318400
    VALUES
      LESS THAN (
        '2026-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775404800
    VALUES
      LESS THAN (
        '2026-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775491200
    VALUES
      LESS THAN (
        '2026-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775577600
    VALUES
      LESS THAN (
        '2026-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775664000
    VALUES
      LESS THAN (
        '2026-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775750400
    VALUES
      LESS THAN (
        '2026-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775836800
    VALUES
      LESS THAN (
        '2026-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1775923200
    VALUES
      LESS THAN (
        '2026-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776009600
    VALUES
      LESS THAN (
        '2026-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776096000
    VALUES
      LESS THAN (
        '2026-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776182400
    VALUES
      LESS THAN (
        '2026-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776268800
    VALUES
      LESS THAN (
        '2026-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776355200
    VALUES
      LESS THAN (
        '2026-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776441600
    VALUES
      LESS THAN (
        '2026-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776528000
    VALUES
      LESS THAN (
        '2026-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776614400
    VALUES
      LESS THAN (
        '2026-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776700800
    VALUES
      LESS THAN (
        '2026-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776787200
    VALUES
      LESS THAN (
        '2026-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776873600
    VALUES
      LESS THAN (
        '2026-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1776960000
    VALUES
      LESS THAN (
        '2026-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777046400
    VALUES
      LESS THAN (
        '2026-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777132800
    VALUES
      LESS THAN (
        '2026-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777219200
    VALUES
      LESS THAN (
        '2026-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777305600
    VALUES
      LESS THAN (
        '2026-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777392000
    VALUES
      LESS THAN (
        '2026-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777478400
    VALUES
      LESS THAN (
        '2026-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777564800
    VALUES
      LESS THAN (
        '2026-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777651200
    VALUES
      LESS THAN (
        '2026-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777737600
    VALUES
      LESS THAN (
        '2026-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777824000
    VALUES
      LESS THAN (
        '2026-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777910400
    VALUES
      LESS THAN (
        '2026-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1777996800
    VALUES
      LESS THAN (
        '2026-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778083200
    VALUES
      LESS THAN (
        '2026-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778169600
    VALUES
      LESS THAN (
        '2026-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778256000
    VALUES
      LESS THAN (
        '2026-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778342400
    VALUES
      LESS THAN (
        '2026-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778428800
    VALUES
      LESS THAN (
        '2026-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778515200
    VALUES
      LESS THAN (
        '2026-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778601600
    VALUES
      LESS THAN (
        '2026-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778688000
    VALUES
      LESS THAN (
        '2026-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778774400
    VALUES
      LESS THAN (
        '2026-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778860800
    VALUES
      LESS THAN (
        '2026-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1778947200
    VALUES
      LESS THAN (
        '2026-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779033600
    VALUES
      LESS THAN (
        '2026-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779120000
    VALUES
      LESS THAN (
        '2026-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779206400
    VALUES
      LESS THAN (
        '2026-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779292800
    VALUES
      LESS THAN (
        '2026-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779379200
    VALUES
      LESS THAN (
        '2026-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779465600
    VALUES
      LESS THAN (
        '2026-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779552000
    VALUES
      LESS THAN (
        '2026-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779638400
    VALUES
      LESS THAN (
        '2026-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779724800
    VALUES
      LESS THAN (
        '2026-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779811200
    VALUES
      LESS THAN (
        '2026-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779897600
    VALUES
      LESS THAN (
        '2026-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1779984000
    VALUES
      LESS THAN (
        '2026-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780070400
    VALUES
      LESS THAN (
        '2026-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780156800
    VALUES
      LESS THAN (
        '2026-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780243200
    VALUES
      LESS THAN (
        '2026-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780329600
    VALUES
      LESS THAN (
        '2026-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780416000
    VALUES
      LESS THAN (
        '2026-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780502400
    VALUES
      LESS THAN (
        '2026-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780588800
    VALUES
      LESS THAN (
        '2026-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780675200
    VALUES
      LESS THAN (
        '2026-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780761600
    VALUES
      LESS THAN (
        '2026-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780848000
    VALUES
      LESS THAN (
        '2026-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1780934400
    VALUES
      LESS THAN (
        '2026-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781020800
    VALUES
      LESS THAN (
        '2026-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781107200
    VALUES
      LESS THAN (
        '2026-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781193600
    VALUES
      LESS THAN (
        '2026-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE ads_chnl_rgst_to_real_auth_dau_df IS '注册到实名/授权/活跃转化率指标_整体与渠道';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.data_dt IS '数据日期';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.rgst_sec_chnl_nm IS '注册二级渠道';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.chnl_sub_nm IS '报送渠道名称';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.rgst_cnt_d IS '注册用户数_日度';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.rgst_cnt_m IS '注册用户数_月度';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.rgst_cnt_a IS '注册用户数_累计';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.real_cnt_d IS '实名用户数_日度';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.real_cnt_m IS '实名用户数_月度';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.real_cnt_a IS '实名用户数_累计';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.auth_cnt_d IS '授权用户数_日度';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.auth_cnt_m IS '授权用户数_月度';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.auth_cnt_a IS '授权用户数_累计';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.rgst_log_cnt_d IS '注册_登录用户数_日度';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.rgst_log_cnt_m IS '注册_登录用户数_月度';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.rgst_log_cnt_a IS '注册_登录用户数_累计';

COMMENT ON COLUMN ads_chnl_rgst_to_real_auth_dau_df.ds IS '日期分区';


SET
  search_path = rec;

CREATE TABLE
  ads_chnl_real_info_df (
    usr_id character varying (128),
    fst_real_tm timestamp without TIME zone,
    cfgc_real_tm timestamp without TIME zone,
    sub_comp_real_tm timestamp without TIME zone,
    ds timestamp (0) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '90 days',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(usr_id) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1781280000
    VALUES
      LESS THAN (
        '2026-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781366400
    VALUES
      LESS THAN (
        '2026-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781452800
    VALUES
      LESS THAN (
        '2026-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781539200
    VALUES
      LESS THAN (
        '2026-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781625600
    VALUES
      LESS THAN (
        '2026-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781712000
    VALUES
      LESS THAN (
        '2026-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781798400
    VALUES
      LESS THAN (
        '2026-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781884800
    VALUES
      LESS THAN (
        '2026-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1781971200
    VALUES
      LESS THAN (
        '2026-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782057600
    VALUES
      LESS THAN (
        '2026-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782144000
    VALUES
      LESS THAN (
        '2026-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782230400
    VALUES
      LESS THAN (
        '2026-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782316800
    VALUES
      LESS THAN (
        '2026-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782403200
    VALUES
      LESS THAN (
        '2026-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782489600
    VALUES
      LESS THAN (
        '2026-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782576000
    VALUES
      LESS THAN (
        '2026-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782662400
    VALUES
      LESS THAN (
        '2026-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782748800
    VALUES
      LESS THAN (
        '2026-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782835200
    VALUES
      LESS THAN (
        '2026-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1782921600
    VALUES
      LESS THAN (
        '2026-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783008000
    VALUES
      LESS THAN (
        '2026-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783094400
    VALUES
      LESS THAN (
        '2026-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783180800
    VALUES
      LESS THAN (
        '2026-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783267200
    VALUES
      LESS THAN (
        '2026-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783353600
    VALUES
      LESS THAN (
        '2026-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783440000
    VALUES
      LESS THAN (
        '2026-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783526400
    VALUES
      LESS THAN (
        '2026-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783612800
    VALUES
      LESS THAN (
        '2026-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783699200
    VALUES
      LESS THAN (
        '2026-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783785600
    VALUES
      LESS THAN (
        '2026-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783872000
    VALUES
      LESS THAN (
        '2026-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1783958400
    VALUES
      LESS THAN (
        '2026-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784044800
    VALUES
      LESS THAN (
        '2026-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784131200
    VALUES
      LESS THAN (
        '2026-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784217600
    VALUES
      LESS THAN (
        '2026-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784304000
    VALUES
      LESS THAN (
        '2026-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784390400
    VALUES
      LESS THAN (
        '2026-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784476800
    VALUES
      LESS THAN (
        '2026-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784563200
    VALUES
      LESS THAN (
        '2026-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784649600
    VALUES
      LESS THAN (
        '2026-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784736000
    VALUES
      LESS THAN (
        '2026-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784822400
    VALUES
      LESS THAN (
        '2026-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784908800
    VALUES
      LESS THAN (
        '2026-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1784995200
    VALUES
      LESS THAN (
        '2026-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785081600
    VALUES
      LESS THAN (
        '2026-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785168000
    VALUES
      LESS THAN (
        '2026-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785254400
    VALUES
      LESS THAN (
        '2026-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785340800
    VALUES
      LESS THAN (
        '2026-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785427200
    VALUES
      LESS THAN (
        '2026-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785513600
    VALUES
      LESS THAN (
        '2026-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785600000
    VALUES
      LESS THAN (
        '2026-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785686400
    VALUES
      LESS THAN (
        '2026-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785772800
    VALUES
      LESS THAN (
        '2026-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785859200
    VALUES
      LESS THAN (
        '2026-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1785945600
    VALUES
      LESS THAN (
        '2026-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786032000
    VALUES
      LESS THAN (
        '2026-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786118400
    VALUES
      LESS THAN (
        '2026-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786204800
    VALUES
      LESS THAN (
        '2026-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786291200
    VALUES
      LESS THAN (
        '2026-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786377600
    VALUES
      LESS THAN (
        '2026-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786464000
    VALUES
      LESS THAN (
        '2026-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786550400
    VALUES
      LESS THAN (
        '2026-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786636800
    VALUES
      LESS THAN (
        '2026-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786723200
    VALUES
      LESS THAN (
        '2026-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786809600
    VALUES
      LESS THAN (
        '2026-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786896000
    VALUES
      LESS THAN (
        '2026-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1786982400
    VALUES
      LESS THAN (
        '2026-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787068800
    VALUES
      LESS THAN (
        '2026-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787155200
    VALUES
      LESS THAN (
        '2026-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787241600
    VALUES
      LESS THAN (
        '2026-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787328000
    VALUES
      LESS THAN (
        '2026-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787414400
    VALUES
      LESS THAN (
        '2026-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787500800
    VALUES
      LESS THAN (
        '2026-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787587200
    VALUES
      LESS THAN (
        '2026-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787673600
    VALUES
      LESS THAN (
        '2026-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787760000
    VALUES
      LESS THAN (
        '2026-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787846400
    VALUES
      LESS THAN (
        '2026-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1787932800
    VALUES
      LESS THAN (
        '2026-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788019200
    VALUES
      LESS THAN (
        '2026-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788105600
    VALUES
      LESS THAN (
        '2026-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788192000
    VALUES
      LESS THAN (
        '2026-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788278400
    VALUES
      LESS THAN (
        '2026-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788364800
    VALUES
      LESS THAN (
        '2026-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788451200
    VALUES
      LESS THAN (
        '2026-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788537600
    VALUES
      LESS THAN (
        '2026-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788624000
    VALUES
      LESS THAN (
        '2026-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788710400
    VALUES
      LESS THAN (
        '2026-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788796800
    VALUES
      LESS THAN (
        '2026-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788883200
    VALUES
      LESS THAN (
        '2026-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1788969600
    VALUES
      LESS THAN (
        '2026-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789056000
    VALUES
      LESS THAN (
        '2026-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789142400
    VALUES
      LESS THAN (
        '2026-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789228800
    VALUES
      LESS THAN (
        '2026-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789315200
    VALUES
      LESS THAN (
        '2026-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789401600
    VALUES
      LESS THAN (
        '2026-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789488000
    VALUES
      LESS THAN (
        '2026-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789574400
    VALUES
      LESS THAN (
        '2026-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789660800
    VALUES
      LESS THAN (
        '2026-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789747200
    VALUES
      LESS THAN (
        '2026-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789833600
    VALUES
      LESS THAN (
        '2026-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1789920000
    VALUES
      LESS THAN (
        '2026-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790006400
    VALUES
      LESS THAN (
        '2026-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790092800
    VALUES
      LESS THAN (
        '2026-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790179200
    VALUES
      LESS THAN (
        '2026-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790265600
    VALUES
      LESS THAN (
        '2026-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790352000
    VALUES
      LESS THAN (
        '2026-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790438400
    VALUES
      LESS THAN (
        '2026-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790524800
    VALUES
      LESS THAN (
        '2026-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790611200
    VALUES
      LESS THAN (
        '2026-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790697600
    VALUES
      LESS THAN (
        '2026-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790784000
    VALUES
      LESS THAN (
        '2026-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790870400
    VALUES
      LESS THAN (
        '2026-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1790956800
    VALUES
      LESS THAN (
        '2026-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791043200
    VALUES
      LESS THAN (
        '2026-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791129600
    VALUES
      LESS THAN (
        '2026-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791216000
    VALUES
      LESS THAN (
        '2026-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791302400
    VALUES
      LESS THAN (
        '2026-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791388800
    VALUES
      LESS THAN (
        '2026-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791475200
    VALUES
      LESS THAN (
        '2026-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791561600
    VALUES
      LESS THAN (
        '2026-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791648000
    VALUES
      LESS THAN (
        '2026-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1791734400
    VALUES
      LESS THAN (
        '2026-10-12 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE ads_chnl_real_info_df IS '实名信息宽表';

COMMENT ON COLUMN ads_chnl_real_info_df.usr_id IS '用户ID';

COMMENT ON COLUMN ads_chnl_real_info_df.fst_real_tm IS '首次实名时间';

COMMENT ON COLUMN ads_chnl_real_info_df.cfgc_real_tm IS '广场实名时间';

COMMENT ON COLUMN ads_chnl_real_info_df.sub_comp_real_tm IS '子公司实名时间';

COMMENT ON COLUMN ads_chnl_real_info_df.ds IS '分区日期';






























