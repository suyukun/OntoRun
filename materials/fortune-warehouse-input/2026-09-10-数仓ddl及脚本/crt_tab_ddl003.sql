SET
  search_path = ods;

CREATE TABLE
  ods_lm_user_wechat_t_df (
    id character varying (128),
    uid character varying (128),
    union_id character varying (128),
    open_id character varying (128),
    wechat_type character varying (128),
    app_id character varying (128),
    user_id character varying (128),
    reg_status character varying (128),
    create_time timestamp without TIME zone,
    update_time timestamp without TIME zone,
    app_flag character varying (128),
    first_subscribe_time timestamp without TIME zone,
    last_subscribe_time timestamp without TIME zone,
    subscribe_flag bigint,
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
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(uid) TO GROUP v3_logical
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
      ),
      PARTITION p1791734400
    VALUES
      LESS THAN (
        '2026-10-12 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE ods_lm_user_wechat_t_df IS '用户微信绑定表';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.id IS '物理主键,唯一标识';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.uid IS 'uid';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.union_id IS 'unionId';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.open_id IS 'openId';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.wechat_type IS 'type';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.app_id IS 'appId';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.user_id IS 'userId';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.reg_status IS '状态';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.create_time IS '创建时间';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.update_time IS '更新时间';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.app_flag IS '公司';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.first_subscribe_time IS '首次关注时间';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.last_subscribe_time IS '末次关注时间';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.subscribe_flag IS '是否关注';

COMMENT ON COLUMN ods_lm_user_wechat_t_df.ds IS '分区日期';



SET
  search_path = ods;

CREATE TABLE
  madp_collect_all (
    user_id character varying (256),
    login_id character varying (256),
    anony_id character varying (256),
    app_id character varying (256),
    trig_tm timestamp without TIME zone,
    event character varying (2048),
    title character varying (2048),
    function_id character varying (256),
    function_name character varying (2048),
    content_id character varying (216),
    hold_duration numeric (16, 4),
    create_time timestamp without TIME zone,
    event_track_id character varying (256),
    event_duration numeric (16, 4),
    out_channel_id character varying (512),
    product_id character varying (256),
    product_name character varying (2048),
    sdk_version character varying (512),
    source_id character varying (256),
    os character varying (512),
    os_version character varying (512),
    referrer character varying (1024),
    ref_screen_name character varying (2048),
    session_id character varying (256),
    page_id character varying (256),
    ref_page_id character varying (256),
    curr_page_url character varying (8192),
    page_path character varying (2048),
    curr_page_title character varying (2048),
    src_chnl_id character varying (1024),
    area_name character varying (2048),
    visit_source character varying (1024),
    area_sequency character varying (256),
    share_id character varying (256),
    resource_id character varying (256),
    room_id character varying (256),
    book_id character varying (256),
    app_unqi_id character varying (256),
    mission_id character varying (256),
    app_version character varying (512),
    pages_id character varying (256),
    ref_page_source character varying (1024),
    src_scenario character varying (512),
    special_id character varying (256),
    pk_id character varying (256),
    sku_id character varying (256),
    scene_id character varying (256),
    evt_id character varying (256),
    right_id character varying (256),
    short_curr_url character varying (2048),
    short_page_url character varying (2048),
    src_page_id character varying (256),
    ds timestamp (0) without TIME zone,
    navi_start character varying (64),
    redi_start character varying (64),
    redi_end character varying (64),
    fetch_start character varying (64),
    dns_start character varying (64),
    dns_end character varying (64),
    con_start character varying (64),
    con_end character varying (64),
    request_start character varying (64),
    response_start character varying (64),
    response_end character varying (64),
    dom_start character varying (64),
    dom_complete character varying (64),
    load_start character varying (64),
    load_end character varying (64),
    on_page_begin character varying (64),
    on_page_finished character varying (64),
    is_preload_on character varying (64),
    hybrid_h5 character varying (128),
    src_anony_id character varying (256),
    valid_sdk_version_flg character varying (16),
    account_id character varying (128),
    order_id character varying (256),
    goods_id character varying (256),
    special_zone character varying (256),
    sale_num integer,
    parent_order_id character varying (256),
    shop_id character varying (256),
    cate_cd character varying (256),
    after_sale_order_id character varying (256),
    area_text character varying (2048),
    area_name_minus_1 character varying (256),
    area_name_minus_2 character varying (256),
    area_name_minus_3 character varying (256),
    area_name_minus_4 character varying (256),
    resource_bit_id character varying (256),
    share_channel character varying (256),
    object_id character varying (256),
    project_id character varying (128),
    store_id character varying (128),
    meta_event_id character varying (5000),
    chapter_id character varying (128),
    track_record_pk character varying (128),
    source_info_id character varying (128),
    jkid character varying (256),
    proc_time timestamp without TIME zone,
    ds_tm timestamp without TIME zone,
    uuid character varying (256),
    new_sdk character varying (16),
    n_jkid character varying (16),
    trig_tm_ms timestamp (3) without TIME zone,
    create_time_ms timestamp (3) without TIME zone
  )
WITH
  (
    orientation = COLUMN,
    colversion = 3.0,
    enable_hstore_opt = TRUE,
    ttl = '5 years',
    period = '1 day',
    compression = middle,
    enable_delta = FALSE,
    enable_hstore = TRUE,
    enable_turbo_store = TRUE
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(event_track_id) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
    PARTITION p1
    VALUES
      LESS THAN (
        '2023-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1682265600
    VALUES
      LESS THAN (
        '2023-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1682352000
    VALUES
      LESS THAN (
        '2023-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1682438400
    VALUES
      LESS THAN (
        '2023-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1682524800
    VALUES
      LESS THAN (
        '2023-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1682611200
    VALUES
      LESS THAN (
        '2023-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1682697600
    VALUES
      LESS THAN (
        '2023-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1682784000
    VALUES
      LESS THAN (
        '2023-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1682870400
    VALUES
      LESS THAN (
        '2023-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1682956800
    VALUES
      LESS THAN (
        '2023-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1683043200
    VALUES
      LESS THAN (
        '2023-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1683129600
    VALUES
      LESS THAN (
        '2023-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1683216000
    VALUES
      LESS THAN (
        '2023-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1683302400
    VALUES
      LESS THAN (
        '2023-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1683388800
    VALUES
      LESS THAN (
        '2023-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1683475200
    VALUES
      LESS THAN (
        '2023-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1683561600
    VALUES
      LESS THAN (
        '2023-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1683648000
    VALUES
      LESS THAN (
        '2023-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1683734400
    VALUES
      LESS THAN (
        '2023-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1683820800
    VALUES
      LESS THAN (
        '2023-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1683907200
    VALUES
      LESS THAN (
        '2023-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1683993600
    VALUES
      LESS THAN (
        '2023-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1684080000
    VALUES
      LESS THAN (
        '2023-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1684166400
    VALUES
      LESS THAN (
        '2023-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1684252800
    VALUES
      LESS THAN (
        '2023-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1684339200
    VALUES
      LESS THAN (
        '2023-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1684425600
    VALUES
      LESS THAN (
        '2023-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1684512000
    VALUES
      LESS THAN (
        '2023-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1684598400
    VALUES
      LESS THAN (
        '2023-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1684684800
    VALUES
      LESS THAN (
        '2023-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1684771200
    VALUES
      LESS THAN (
        '2023-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1684857600
    VALUES
      LESS THAN (
        '2023-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1684944000
    VALUES
      LESS THAN (
        '2023-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1685030400
    VALUES
      LESS THAN (
        '2023-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1685116800
    VALUES
      LESS THAN (
        '2023-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1685203200
    VALUES
      LESS THAN (
        '2023-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1685289600
    VALUES
      LESS THAN (
        '2023-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1685376000
    VALUES
      LESS THAN (
        '2023-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1685462400
    VALUES
      LESS THAN (
        '2023-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1685548800
    VALUES
      LESS THAN (
        '2023-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1685635200
    VALUES
      LESS THAN (
        '2023-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1685721600
    VALUES
      LESS THAN (
        '2023-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1685808000
    VALUES
      LESS THAN (
        '2023-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1685894400
    VALUES
      LESS THAN (
        '2023-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1685980800
    VALUES
      LESS THAN (
        '2023-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1686067200
    VALUES
      LESS THAN (
        '2023-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1686153600
    VALUES
      LESS THAN (
        '2023-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1686240000
    VALUES
      LESS THAN (
        '2023-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1686326400
    VALUES
      LESS THAN (
        '2023-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1686412800
    VALUES
      LESS THAN (
        '2023-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1686499200
    VALUES
      LESS THAN (
        '2023-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1686585600
    VALUES
      LESS THAN (
        '2023-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1686672000
    VALUES
      LESS THAN (
        '2023-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1686758400
    VALUES
      LESS THAN (
        '2023-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1686844800
    VALUES
      LESS THAN (
        '2023-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1686931200
    VALUES
      LESS THAN (
        '2023-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1687017600
    VALUES
      LESS THAN (
        '2023-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1687104000
    VALUES
      LESS THAN (
        '2023-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1687190400
    VALUES
      LESS THAN (
        '2023-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1687276800
    VALUES
      LESS THAN (
        '2023-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1687363200
    VALUES
      LESS THAN (
        '2023-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1687449600
    VALUES
      LESS THAN (
        '2023-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1687536000
    VALUES
      LESS THAN (
        '2023-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1687622400
    VALUES
      LESS THAN (
        '2023-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1687708800
    VALUES
      LESS THAN (
        '2023-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1687795200
    VALUES
      LESS THAN (
        '2023-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1687881600
    VALUES
      LESS THAN (
        '2023-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1687968000
    VALUES
      LESS THAN (
        '2023-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1688054400
    VALUES
      LESS THAN (
        '2023-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1688140800
    VALUES
      LESS THAN (
        '2023-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1688227200
    VALUES
      LESS THAN (
        '2023-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1688313600
    VALUES
      LESS THAN (
        '2023-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1688400000
    VALUES
      LESS THAN (
        '2023-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1688486400
    VALUES
      LESS THAN (
        '2023-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1688572800
    VALUES
      LESS THAN (
        '2023-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1688659200
    VALUES
      LESS THAN (
        '2023-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1688745600
    VALUES
      LESS THAN (
        '2023-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1688832000
    VALUES
      LESS THAN (
        '2023-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1688918400
    VALUES
      LESS THAN (
        '2023-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1689004800
    VALUES
      LESS THAN (
        '2023-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1689091200
    VALUES
      LESS THAN (
        '2023-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1689177600
    VALUES
      LESS THAN (
        '2023-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1689264000
    VALUES
      LESS THAN (
        '2023-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1689350400
    VALUES
      LESS THAN (
        '2023-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1689436800
    VALUES
      LESS THAN (
        '2023-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1689523200
    VALUES
      LESS THAN (
        '2023-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1689609600
    VALUES
      LESS THAN (
        '2023-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1689696000
    VALUES
      LESS THAN (
        '2023-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1689782400
    VALUES
      LESS THAN (
        '2023-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1689868800
    VALUES
      LESS THAN (
        '2023-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1689955200
    VALUES
      LESS THAN (
        '2023-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1690041600
    VALUES
      LESS THAN (
        '2023-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1690128000
    VALUES
      LESS THAN (
        '2023-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1690214400
    VALUES
      LESS THAN (
        '2023-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1690300800
    VALUES
      LESS THAN (
        '2023-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1690387200
    VALUES
      LESS THAN (
        '2023-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1690473600
    VALUES
      LESS THAN (
        '2023-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1690560000
    VALUES
      LESS THAN (
        '2023-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1690646400
    VALUES
      LESS THAN (
        '2023-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1690732800
    VALUES
      LESS THAN (
        '2023-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1690819200
    VALUES
      LESS THAN (
        '2023-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1690905600
    VALUES
      LESS THAN (
        '2023-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1690992000
    VALUES
      LESS THAN (
        '2023-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1691078400
    VALUES
      LESS THAN (
        '2023-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1691164800
    VALUES
      LESS THAN (
        '2023-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1691251200
    VALUES
      LESS THAN (
        '2023-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1691337600
    VALUES
      LESS THAN (
        '2023-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1691424000
    VALUES
      LESS THAN (
        '2023-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1691510400
    VALUES
      LESS THAN (
        '2023-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1691596800
    VALUES
      LESS THAN (
        '2023-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1691683200
    VALUES
      LESS THAN (
        '2023-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1691769600
    VALUES
      LESS THAN (
        '2023-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1691856000
    VALUES
      LESS THAN (
        '2023-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1691942400
    VALUES
      LESS THAN (
        '2023-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1692028800
    VALUES
      LESS THAN (
        '2023-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1692115200
    VALUES
      LESS THAN (
        '2023-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1692201600
    VALUES
      LESS THAN (
        '2023-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1692288000
    VALUES
      LESS THAN (
        '2023-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1692374400
    VALUES
      LESS THAN (
        '2023-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1692460800
    VALUES
      LESS THAN (
        '2023-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1692547200
    VALUES
      LESS THAN (
        '2023-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1692633600
    VALUES
      LESS THAN (
        '2023-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1692720000
    VALUES
      LESS THAN (
        '2023-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1692806400
    VALUES
      LESS THAN (
        '2023-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1692892800
    VALUES
      LESS THAN (
        '2023-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1692979200
    VALUES
      LESS THAN (
        '2023-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1693065600
    VALUES
      LESS THAN (
        '2023-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1693152000
    VALUES
      LESS THAN (
        '2023-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1693238400
    VALUES
      LESS THAN (
        '2023-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1693324800
    VALUES
      LESS THAN (
        '2023-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1693411200
    VALUES
      LESS THAN (
        '2023-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1693497600
    VALUES
      LESS THAN (
        '2023-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1693584000
    VALUES
      LESS THAN (
        '2023-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1693670400
    VALUES
      LESS THAN (
        '2023-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1693756800
    VALUES
      LESS THAN (
        '2023-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1693843200
    VALUES
      LESS THAN (
        '2023-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1693929600
    VALUES
      LESS THAN (
        '2023-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1694016000
    VALUES
      LESS THAN (
        '2023-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1694102400
    VALUES
      LESS THAN (
        '2023-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1694188800
    VALUES
      LESS THAN (
        '2023-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1694275200
    VALUES
      LESS THAN (
        '2023-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1694361600
    VALUES
      LESS THAN (
        '2023-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1694448000
    VALUES
      LESS THAN (
        '2023-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1694534400
    VALUES
      LESS THAN (
        '2023-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1694620800
    VALUES
      LESS THAN (
        '2023-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1694707200
    VALUES
      LESS THAN (
        '2023-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1694793600
    VALUES
      LESS THAN (
        '2023-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1694880000
    VALUES
      LESS THAN (
        '2023-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1694966400
    VALUES
      LESS THAN (
        '2023-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1695052800
    VALUES
      LESS THAN (
        '2023-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1695139200
    VALUES
      LESS THAN (
        '2023-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1695225600
    VALUES
      LESS THAN (
        '2023-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1695312000
    VALUES
      LESS THAN (
        '2023-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1695398400
    VALUES
      LESS THAN (
        '2023-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1695484800
    VALUES
      LESS THAN (
        '2023-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1695571200
    VALUES
      LESS THAN (
        '2023-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1695657600
    VALUES
      LESS THAN (
        '2023-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1695744000
    VALUES
      LESS THAN (
        '2023-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1695830400
    VALUES
      LESS THAN (
        '2023-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1695916800
    VALUES
      LESS THAN (
        '2023-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1696003200
    VALUES
      LESS THAN (
        '2023-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1696089600
    VALUES
      LESS THAN (
        '2023-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1696176000
    VALUES
      LESS THAN (
        '2023-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1696262400
    VALUES
      LESS THAN (
        '2023-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1696348800
    VALUES
      LESS THAN (
        '2023-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1696435200
    VALUES
      LESS THAN (
        '2023-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1696521600
    VALUES
      LESS THAN (
        '2023-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1696608000
    VALUES
      LESS THAN (
        '2023-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1696694400
    VALUES
      LESS THAN (
        '2023-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1696780800
    VALUES
      LESS THAN (
        '2023-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1696867200
    VALUES
      LESS THAN (
        '2023-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1696953600
    VALUES
      LESS THAN (
        '2023-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1697040000
    VALUES
      LESS THAN (
        '2023-10-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1697126400
    VALUES
      LESS THAN (
        '2023-10-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1697212800
    VALUES
      LESS THAN (
        '2023-10-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1697299200
    VALUES
      LESS THAN (
        '2023-10-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1697385600
    VALUES
      LESS THAN (
        '2023-10-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1697472000
    VALUES
      LESS THAN (
        '2023-10-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1697558400
    VALUES
      LESS THAN (
        '2023-10-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1697644800
    VALUES
      LESS THAN (
        '2023-10-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1697731200
    VALUES
      LESS THAN (
        '2023-10-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1697817600
    VALUES
      LESS THAN (
        '2023-10-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1697904000
    VALUES
      LESS THAN (
        '2023-10-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1697990400
    VALUES
      LESS THAN (
        '2023-10-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1698076800
    VALUES
      LESS THAN (
        '2023-10-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1698163200
    VALUES
      LESS THAN (
        '2023-10-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1698249600
    VALUES
      LESS THAN (
        '2023-10-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1698336000
    VALUES
      LESS THAN (
        '2023-10-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1698422400
    VALUES
      LESS THAN (
        '2023-10-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1698508800
    VALUES
      LESS THAN (
        '2023-10-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1698595200
    VALUES
      LESS THAN (
        '2023-10-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1698681600
    VALUES
      LESS THAN (
        '2023-10-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1698768000
    VALUES
      LESS THAN (
        '2023-11-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1698854400
    VALUES
      LESS THAN (
        '2023-11-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1698940800
    VALUES
      LESS THAN (
        '2023-11-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1699027200
    VALUES
      LESS THAN (
        '2023-11-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1699113600
    VALUES
      LESS THAN (
        '2023-11-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1699200000
    VALUES
      LESS THAN (
        '2023-11-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1699286400
    VALUES
      LESS THAN (
        '2023-11-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1699372800
    VALUES
      LESS THAN (
        '2023-11-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1699459200
    VALUES
      LESS THAN (
        '2023-11-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1699545600
    VALUES
      LESS THAN (
        '2023-11-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1699632000
    VALUES
      LESS THAN (
        '2023-11-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1699718400
    VALUES
      LESS THAN (
        '2023-11-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1699804800
    VALUES
      LESS THAN (
        '2023-11-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1699891200
    VALUES
      LESS THAN (
        '2023-11-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1699977600
    VALUES
      LESS THAN (
        '2023-11-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1700064000
    VALUES
      LESS THAN (
        '2023-11-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1700150400
    VALUES
      LESS THAN (
        '2023-11-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1700236800
    VALUES
      LESS THAN (
        '2023-11-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1700323200
    VALUES
      LESS THAN (
        '2023-11-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1700409600
    VALUES
      LESS THAN (
        '2023-11-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1700496000
    VALUES
      LESS THAN (
        '2023-11-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1700582400
    VALUES
      LESS THAN (
        '2023-11-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1700668800
    VALUES
      LESS THAN (
        '2023-11-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1700755200
    VALUES
      LESS THAN (
        '2023-11-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1700841600
    VALUES
      LESS THAN (
        '2023-11-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1700928000
    VALUES
      LESS THAN (
        '2023-11-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1701014400
    VALUES
      LESS THAN (
        '2023-11-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1701100800
    VALUES
      LESS THAN (
        '2023-11-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1701187200
    VALUES
      LESS THAN (
        '2023-11-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1701273600
    VALUES
      LESS THAN (
        '2023-11-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1701360000
    VALUES
      LESS THAN (
        '2023-12-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1701446400
    VALUES
      LESS THAN (
        '2023-12-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1701532800
    VALUES
      LESS THAN (
        '2023-12-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1701619200
    VALUES
      LESS THAN (
        '2023-12-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1701705600
    VALUES
      LESS THAN (
        '2023-12-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1701792000
    VALUES
      LESS THAN (
        '2023-12-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1701878400
    VALUES
      LESS THAN (
        '2023-12-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1701964800
    VALUES
      LESS THAN (
        '2023-12-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1702051200
    VALUES
      LESS THAN (
        '2023-12-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1702137600
    VALUES
      LESS THAN (
        '2023-12-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1702224000
    VALUES
      LESS THAN (
        '2023-12-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1702310400
    VALUES
      LESS THAN (
        '2023-12-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1702396800
    VALUES
      LESS THAN (
        '2023-12-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1702483200
    VALUES
      LESS THAN (
        '2023-12-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1702569600
    VALUES
      LESS THAN (
        '2023-12-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1702656000
    VALUES
      LESS THAN (
        '2023-12-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1702742400
    VALUES
      LESS THAN (
        '2023-12-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1702828800
    VALUES
      LESS THAN (
        '2023-12-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1702915200
    VALUES
      LESS THAN (
        '2023-12-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1703001600
    VALUES
      LESS THAN (
        '2023-12-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1703088000
    VALUES
      LESS THAN (
        '2023-12-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1703174400
    VALUES
      LESS THAN (
        '2023-12-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1703260800
    VALUES
      LESS THAN (
        '2023-12-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1703347200
    VALUES
      LESS THAN (
        '2023-12-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1703433600
    VALUES
      LESS THAN (
        '2023-12-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1703520000
    VALUES
      LESS THAN (
        '2023-12-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1703606400
    VALUES
      LESS THAN (
        '2023-12-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1703692800
    VALUES
      LESS THAN (
        '2023-12-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1703779200
    VALUES
      LESS THAN (
        '2023-12-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1703865600
    VALUES
      LESS THAN (
        '2023-12-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1703952000
    VALUES
      LESS THAN (
        '2023-12-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1704038400
    VALUES
      LESS THAN (
        '2024-01-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1704124800
    VALUES
      LESS THAN (
        '2024-01-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1704211200
    VALUES
      LESS THAN (
        '2024-01-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1704297600
    VALUES
      LESS THAN (
        '2024-01-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1704384000
    VALUES
      LESS THAN (
        '2024-01-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1704470400
    VALUES
      LESS THAN (
        '2024-01-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1704556800
    VALUES
      LESS THAN (
        '2024-01-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1704643200
    VALUES
      LESS THAN (
        '2024-01-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1704729600
    VALUES
      LESS THAN (
        '2024-01-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1704816000
    VALUES
      LESS THAN (
        '2024-01-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1704902400
    VALUES
      LESS THAN (
        '2024-01-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1704988800
    VALUES
      LESS THAN (
        '2024-01-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1705075200
    VALUES
      LESS THAN (
        '2024-01-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1705161600
    VALUES
      LESS THAN (
        '2024-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1705248000
    VALUES
      LESS THAN (
        '2024-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1705334400
    VALUES
      LESS THAN (
        '2024-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1705420800
    VALUES
      LESS THAN (
        '2024-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1705507200
    VALUES
      LESS THAN (
        '2024-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1705593600
    VALUES
      LESS THAN (
        '2024-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1705680000
    VALUES
      LESS THAN (
        '2024-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1705766400
    VALUES
      LESS THAN (
        '2024-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1705852800
    VALUES
      LESS THAN (
        '2024-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1705939200
    VALUES
      LESS THAN (
        '2024-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1706025600
    VALUES
      LESS THAN (
        '2024-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1706112000
    VALUES
      LESS THAN (
        '2024-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1706198400
    VALUES
      LESS THAN (
        '2024-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1706284800
    VALUES
      LESS THAN (
        '2024-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1706371200
    VALUES
      LESS THAN (
        '2024-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1706457600
    VALUES
      LESS THAN (
        '2024-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1706544000
    VALUES
      LESS THAN (
        '2024-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1706630400
    VALUES
      LESS THAN (
        '2024-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1706716800
    VALUES
      LESS THAN (
        '2024-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1706803200
    VALUES
      LESS THAN (
        '2024-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1706889600
    VALUES
      LESS THAN (
        '2024-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1706976000
    VALUES
      LESS THAN (
        '2024-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1707062400
    VALUES
      LESS THAN (
        '2024-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1707148800
    VALUES
      LESS THAN (
        '2024-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1707235200
    VALUES
      LESS THAN (
        '2024-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1707321600
    VALUES
      LESS THAN (
        '2024-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1707408000
    VALUES
      LESS THAN (
        '2024-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1707494400
    VALUES
      LESS THAN (
        '2024-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1707580800
    VALUES
      LESS THAN (
        '2024-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1707667200
    VALUES
      LESS THAN (
        '2024-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1707753600
    VALUES
      LESS THAN (
        '2024-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1707840000
    VALUES
      LESS THAN (
        '2024-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1707926400
    VALUES
      LESS THAN (
        '2024-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1708012800
    VALUES
      LESS THAN (
        '2024-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1708099200
    VALUES
      LESS THAN (
        '2024-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1708185600
    VALUES
      LESS THAN (
        '2024-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1708272000
    VALUES
      LESS THAN (
        '2024-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1708358400
    VALUES
      LESS THAN (
        '2024-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1708444800
    VALUES
      LESS THAN (
        '2024-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1708531200
    VALUES
      LESS THAN (
        '2024-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1708617600
    VALUES
      LESS THAN (
        '2024-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1708704000
    VALUES
      LESS THAN (
        '2024-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1708790400
    VALUES
      LESS THAN (
        '2024-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1708876800
    VALUES
      LESS THAN (
        '2024-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1708963200
    VALUES
      LESS THAN (
        '2024-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1709049600
    VALUES
      LESS THAN (
        '2024-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1709136000
    VALUES
      LESS THAN (
        '2024-02-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1709222400
    VALUES
      LESS THAN (
        '2024-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1709308800
    VALUES
      LESS THAN (
        '2024-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1709395200
    VALUES
      LESS THAN (
        '2024-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1709481600
    VALUES
      LESS THAN (
        '2024-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1709568000
    VALUES
      LESS THAN (
        '2024-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1709654400
    VALUES
      LESS THAN (
        '2024-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1709740800
    VALUES
      LESS THAN (
        '2024-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1709827200
    VALUES
      LESS THAN (
        '2024-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1709913600
    VALUES
      LESS THAN (
        '2024-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1710000000
    VALUES
      LESS THAN (
        '2024-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1710086400
    VALUES
      LESS THAN (
        '2024-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1710172800
    VALUES
      LESS THAN (
        '2024-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1710259200
    VALUES
      LESS THAN (
        '2024-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1710345600
    VALUES
      LESS THAN (
        '2024-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1710432000
    VALUES
      LESS THAN (
        '2024-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1710518400
    VALUES
      LESS THAN (
        '2024-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1710604800
    VALUES
      LESS THAN (
        '2024-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1710691200
    VALUES
      LESS THAN (
        '2024-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1710777600
    VALUES
      LESS THAN (
        '2024-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1710864000
    VALUES
      LESS THAN (
        '2024-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1710950400
    VALUES
      LESS THAN (
        '2024-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1711036800
    VALUES
      LESS THAN (
        '2024-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1711123200
    VALUES
      LESS THAN (
        '2024-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1711209600
    VALUES
      LESS THAN (
        '2024-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1711296000
    VALUES
      LESS THAN (
        '2024-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1711382400
    VALUES
      LESS THAN (
        '2024-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1711468800
    VALUES
      LESS THAN (
        '2024-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1711555200
    VALUES
      LESS THAN (
        '2024-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1711641600
    VALUES
      LESS THAN (
        '2024-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1711728000
    VALUES
      LESS THAN (
        '2024-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1711814400
    VALUES
      LESS THAN (
        '2024-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1711900800
    VALUES
      LESS THAN (
        '2024-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1711987200
    VALUES
      LESS THAN (
        '2024-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1712073600
    VALUES
      LESS THAN (
        '2024-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1712160000
    VALUES
      LESS THAN (
        '2024-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1712246400
    VALUES
      LESS THAN (
        '2024-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1712332800
    VALUES
      LESS THAN (
        '2024-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1712419200
    VALUES
      LESS THAN (
        '2024-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1712505600
    VALUES
      LESS THAN (
        '2024-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1712592000
    VALUES
      LESS THAN (
        '2024-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1712678400
    VALUES
      LESS THAN (
        '2024-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1712764800
    VALUES
      LESS THAN (
        '2024-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1712851200
    VALUES
      LESS THAN (
        '2024-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1712937600
    VALUES
      LESS THAN (
        '2024-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1713024000
    VALUES
      LESS THAN (
        '2024-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1713110400
    VALUES
      LESS THAN (
        '2024-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1713196800
    VALUES
      LESS THAN (
        '2024-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1713283200
    VALUES
      LESS THAN (
        '2024-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1713369600
    VALUES
      LESS THAN (
        '2024-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1713456000
    VALUES
      LESS THAN (
        '2024-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1713542400
    VALUES
      LESS THAN (
        '2024-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1713628800
    VALUES
      LESS THAN (
        '2024-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1713715200
    VALUES
      LESS THAN (
        '2024-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1713801600
    VALUES
      LESS THAN (
        '2024-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1713888000
    VALUES
      LESS THAN (
        '2024-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1713974400
    VALUES
      LESS THAN (
        '2024-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1714060800
    VALUES
      LESS THAN (
        '2024-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1714147200
    VALUES
      LESS THAN (
        '2024-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1714233600
    VALUES
      LESS THAN (
        '2024-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1714320000
    VALUES
      LESS THAN (
        '2024-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1714406400
    VALUES
      LESS THAN (
        '2024-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1714492800
    VALUES
      LESS THAN (
        '2024-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1714579200
    VALUES
      LESS THAN (
        '2024-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1714665600
    VALUES
      LESS THAN (
        '2024-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1714752000
    VALUES
      LESS THAN (
        '2024-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1714838400
    VALUES
      LESS THAN (
        '2024-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1714924800
    VALUES
      LESS THAN (
        '2024-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1715011200
    VALUES
      LESS THAN (
        '2024-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1715097600
    VALUES
      LESS THAN (
        '2024-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1715184000
    VALUES
      LESS THAN (
        '2024-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1715270400
    VALUES
      LESS THAN (
        '2024-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1715356800
    VALUES
      LESS THAN (
        '2024-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1715443200
    VALUES
      LESS THAN (
        '2024-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1715529600
    VALUES
      LESS THAN (
        '2024-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1715616000
    VALUES
      LESS THAN (
        '2024-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1715702400
    VALUES
      LESS THAN (
        '2024-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1715788800
    VALUES
      LESS THAN (
        '2024-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1715875200
    VALUES
      LESS THAN (
        '2024-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1715961600
    VALUES
      LESS THAN (
        '2024-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1716048000
    VALUES
      LESS THAN (
        '2024-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1716134400
    VALUES
      LESS THAN (
        '2024-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1716220800
    VALUES
      LESS THAN (
        '2024-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1716307200
    VALUES
      LESS THAN (
        '2024-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1716393600
    VALUES
      LESS THAN (
        '2024-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1716480000
    VALUES
      LESS THAN (
        '2024-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1716566400
    VALUES
      LESS THAN (
        '2024-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1716652800
    VALUES
      LESS THAN (
        '2024-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1716739200
    VALUES
      LESS THAN (
        '2024-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1716825600
    VALUES
      LESS THAN (
        '2024-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1716912000
    VALUES
      LESS THAN (
        '2024-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1716998400
    VALUES
      LESS THAN (
        '2024-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1717084800
    VALUES
      LESS THAN (
        '2024-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1717171200
    VALUES
      LESS THAN (
        '2024-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1717257600
    VALUES
      LESS THAN (
        '2024-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1717344000
    VALUES
      LESS THAN (
        '2024-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1717430400
    VALUES
      LESS THAN (
        '2024-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1717516800
    VALUES
      LESS THAN (
        '2024-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1717603200
    VALUES
      LESS THAN (
        '2024-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1717689600
    VALUES
      LESS THAN (
        '2024-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1717776000
    VALUES
      LESS THAN (
        '2024-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1717862400
    VALUES
      LESS THAN (
        '2024-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1717948800
    VALUES
      LESS THAN (
        '2024-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1718035200
    VALUES
      LESS THAN (
        '2024-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1718121600
    VALUES
      LESS THAN (
        '2024-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1718208000
    VALUES
      LESS THAN (
        '2024-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1718294400
    VALUES
      LESS THAN (
        '2024-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1718380800
    VALUES
      LESS THAN (
        '2024-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1718467200
    VALUES
      LESS THAN (
        '2024-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1718553600
    VALUES
      LESS THAN (
        '2024-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1718640000
    VALUES
      LESS THAN (
        '2024-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1718726400
    VALUES
      LESS THAN (
        '2024-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1718812800
    VALUES
      LESS THAN (
        '2024-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1718899200
    VALUES
      LESS THAN (
        '2024-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1718985600
    VALUES
      LESS THAN (
        '2024-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1719072000
    VALUES
      LESS THAN (
        '2024-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1719158400
    VALUES
      LESS THAN (
        '2024-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1719244800
    VALUES
      LESS THAN (
        '2024-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1719331200
    VALUES
      LESS THAN (
        '2024-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1719417600
    VALUES
      LESS THAN (
        '2024-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1719504000
    VALUES
      LESS THAN (
        '2024-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1719590400
    VALUES
      LESS THAN (
        '2024-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1719676800
    VALUES
      LESS THAN (
        '2024-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1719763200
    VALUES
      LESS THAN (
        '2024-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1719849600
    VALUES
      LESS THAN (
        '2024-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1719936000
    VALUES
      LESS THAN (
        '2024-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1720022400
    VALUES
      LESS THAN (
        '2024-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1720108800
    VALUES
      LESS THAN (
        '2024-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1720195200
    VALUES
      LESS THAN (
        '2024-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1720281600
    VALUES
      LESS THAN (
        '2024-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1720368000
    VALUES
      LESS THAN (
        '2024-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1720454400
    VALUES
      LESS THAN (
        '2024-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1720540800
    VALUES
      LESS THAN (
        '2024-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1720627200
    VALUES
      LESS THAN (
        '2024-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1720713600
    VALUES
      LESS THAN (
        '2024-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1720800000
    VALUES
      LESS THAN (
        '2024-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1720886400
    VALUES
      LESS THAN (
        '2024-07-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1720972800
    VALUES
      LESS THAN (
        '2024-07-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1721059200
    VALUES
      LESS THAN (
        '2024-07-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1721145600
    VALUES
      LESS THAN (
        '2024-07-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1721232000
    VALUES
      LESS THAN (
        '2024-07-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1721318400
    VALUES
      LESS THAN (
        '2024-07-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1721404800
    VALUES
      LESS THAN (
        '2024-07-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1721491200
    VALUES
      LESS THAN (
        '2024-07-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1721577600
    VALUES
      LESS THAN (
        '2024-07-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1721664000
    VALUES
      LESS THAN (
        '2024-07-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1721750400
    VALUES
      LESS THAN (
        '2024-07-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1721836800
    VALUES
      LESS THAN (
        '2024-07-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1721923200
    VALUES
      LESS THAN (
        '2024-07-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1722009600
    VALUES
      LESS THAN (
        '2024-07-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1722096000
    VALUES
      LESS THAN (
        '2024-07-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1722182400
    VALUES
      LESS THAN (
        '2024-07-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1722268800
    VALUES
      LESS THAN (
        '2024-07-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1722355200
    VALUES
      LESS THAN (
        '2024-07-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1722441600
    VALUES
      LESS THAN (
        '2024-08-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1722528000
    VALUES
      LESS THAN (
        '2024-08-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1722614400
    VALUES
      LESS THAN (
        '2024-08-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1722700800
    VALUES
      LESS THAN (
        '2024-08-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1722787200
    VALUES
      LESS THAN (
        '2024-08-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1722873600
    VALUES
      LESS THAN (
        '2024-08-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1722960000
    VALUES
      LESS THAN (
        '2024-08-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1723046400
    VALUES
      LESS THAN (
        '2024-08-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1723132800
    VALUES
      LESS THAN (
        '2024-08-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1723219200
    VALUES
      LESS THAN (
        '2024-08-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1723305600
    VALUES
      LESS THAN (
        '2024-08-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1723392000
    VALUES
      LESS THAN (
        '2024-08-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1723478400
    VALUES
      LESS THAN (
        '2024-08-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1723564800
    VALUES
      LESS THAN (
        '2024-08-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1723651200
    VALUES
      LESS THAN (
        '2024-08-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1723737600
    VALUES
      LESS THAN (
        '2024-08-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1723824000
    VALUES
      LESS THAN (
        '2024-08-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1723910400
    VALUES
      LESS THAN (
        '2024-08-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1723996800
    VALUES
      LESS THAN (
        '2024-08-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1724083200
    VALUES
      LESS THAN (
        '2024-08-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1724169600
    VALUES
      LESS THAN (
        '2024-08-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1724256000
    VALUES
      LESS THAN (
        '2024-08-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1724342400
    VALUES
      LESS THAN (
        '2024-08-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1724428800
    VALUES
      LESS THAN (
        '2024-08-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1724515200
    VALUES
      LESS THAN (
        '2024-08-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1724601600
    VALUES
      LESS THAN (
        '2024-08-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1724688000
    VALUES
      LESS THAN (
        '2024-08-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1724774400
    VALUES
      LESS THAN (
        '2024-08-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1724860800
    VALUES
      LESS THAN (
        '2024-08-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1724947200
    VALUES
      LESS THAN (
        '2024-08-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1725033600
    VALUES
      LESS THAN (
        '2024-08-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1725120000
    VALUES
      LESS THAN (
        '2024-09-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1725206400
    VALUES
      LESS THAN (
        '2024-09-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1725292800
    VALUES
      LESS THAN (
        '2024-09-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1725379200
    VALUES
      LESS THAN (
        '2024-09-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1725465600
    VALUES
      LESS THAN (
        '2024-09-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1725552000
    VALUES
      LESS THAN (
        '2024-09-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1725638400
    VALUES
      LESS THAN (
        '2024-09-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1725724800
    VALUES
      LESS THAN (
        '2024-09-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1725811200
    VALUES
      LESS THAN (
        '2024-09-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1725897600
    VALUES
      LESS THAN (
        '2024-09-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1725984000
    VALUES
      LESS THAN (
        '2024-09-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1726070400
    VALUES
      LESS THAN (
        '2024-09-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1726156800
    VALUES
      LESS THAN (
        '2024-09-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1726243200
    VALUES
      LESS THAN (
        '2024-09-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1726329600
    VALUES
      LESS THAN (
        '2024-09-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1726416000
    VALUES
      LESS THAN (
        '2024-09-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1726502400
    VALUES
      LESS THAN (
        '2024-09-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1726588800
    VALUES
      LESS THAN (
        '2024-09-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1726675200
    VALUES
      LESS THAN (
        '2024-09-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1726761600
    VALUES
      LESS THAN (
        '2024-09-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1726848000
    VALUES
      LESS THAN (
        '2024-09-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1726934400
    VALUES
      LESS THAN (
        '2024-09-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1727020800
    VALUES
      LESS THAN (
        '2024-09-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1727107200
    VALUES
      LESS THAN (
        '2024-09-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1727193600
    VALUES
      LESS THAN (
        '2024-09-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1727280000
    VALUES
      LESS THAN (
        '2024-09-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1727366400
    VALUES
      LESS THAN (
        '2024-09-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1727452800
    VALUES
      LESS THAN (
        '2024-09-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1727539200
    VALUES
      LESS THAN (
        '2024-09-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1727625600
    VALUES
      LESS THAN (
        '2024-09-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1727712000
    VALUES
      LESS THAN (
        '2024-10-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1727798400
    VALUES
      LESS THAN (
        '2024-10-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1727884800
    VALUES
      LESS THAN (
        '2024-10-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1727971200
    VALUES
      LESS THAN (
        '2024-10-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1728057600
    VALUES
      LESS THAN (
        '2024-10-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1728144000
    VALUES
      LESS THAN (
        '2024-10-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1728230400
    VALUES
      LESS THAN (
        '2024-10-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1728316800
    VALUES
      LESS THAN (
        '2024-10-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1728403200
    VALUES
      LESS THAN (
        '2024-10-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1728489600
    VALUES
      LESS THAN (
        '2024-10-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1728576000
    VALUES
      LESS THAN (
        '2024-10-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1728662400
    VALUES
      LESS THAN (
        '2024-10-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1728748800
    VALUES
      LESS THAN (
        '2024-10-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1728835200
    VALUES
      LESS THAN (
        '2024-10-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1728921600
    VALUES
      LESS THAN (
        '2024-10-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1729008000
    VALUES
      LESS THAN (
        '2024-10-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1729094400
    VALUES
      LESS THAN (
        '2024-10-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1729180800
    VALUES
      LESS THAN (
        '2024-10-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1729267200
    VALUES
      LESS THAN (
        '2024-10-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1729353600
    VALUES
      LESS THAN (
        '2024-10-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1729440000
    VALUES
      LESS THAN (
        '2024-10-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1729526400
    VALUES
      LESS THAN (
        '2024-10-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1729612800
    VALUES
      LESS THAN (
        '2024-10-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1729699200
    VALUES
      LESS THAN (
        '2024-10-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1729785600
    VALUES
      LESS THAN (
        '2024-10-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1729872000
    VALUES
      LESS THAN (
        '2024-10-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1729958400
    VALUES
      LESS THAN (
        '2024-10-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1730044800
    VALUES
      LESS THAN (
        '2024-10-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1730131200
    VALUES
      LESS THAN (
        '2024-10-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1730217600
    VALUES
      LESS THAN (
        '2024-10-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1730304000
    VALUES
      LESS THAN (
        '2024-10-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1730390400
    VALUES
      LESS THAN (
        '2024-11-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1730476800
    VALUES
      LESS THAN (
        '2024-11-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1730563200
    VALUES
      LESS THAN (
        '2024-11-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1730649600
    VALUES
      LESS THAN (
        '2024-11-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1730736000
    VALUES
      LESS THAN (
        '2024-11-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1730822400
    VALUES
      LESS THAN (
        '2024-11-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1730908800
    VALUES
      LESS THAN (
        '2024-11-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1730995200
    VALUES
      LESS THAN (
        '2024-11-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1731081600
    VALUES
      LESS THAN (
        '2024-11-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1731168000
    VALUES
      LESS THAN (
        '2024-11-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1731254400
    VALUES
      LESS THAN (
        '2024-11-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1731340800
    VALUES
      LESS THAN (
        '2024-11-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1731427200
    VALUES
      LESS THAN (
        '2024-11-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1731513600
    VALUES
      LESS THAN (
        '2024-11-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1731600000
    VALUES
      LESS THAN (
        '2024-11-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1731686400
    VALUES
      LESS THAN (
        '2024-11-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1731772800
    VALUES
      LESS THAN (
        '2024-11-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1731859200
    VALUES
      LESS THAN (
        '2024-11-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1731945600
    VALUES
      LESS THAN (
        '2024-11-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1732032000
    VALUES
      LESS THAN (
        '2024-11-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1732118400
    VALUES
      LESS THAN (
        '2024-11-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1732204800
    VALUES
      LESS THAN (
        '2024-11-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1732291200
    VALUES
      LESS THAN (
        '2024-11-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1732377600
    VALUES
      LESS THAN (
        '2024-11-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1732464000
    VALUES
      LESS THAN (
        '2024-11-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1732550400
    VALUES
      LESS THAN (
        '2024-11-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1732636800
    VALUES
      LESS THAN (
        '2024-11-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1732723200
    VALUES
      LESS THAN (
        '2024-11-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1732809600
    VALUES
      LESS THAN (
        '2024-11-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1732896000
    VALUES
      LESS THAN (
        '2024-11-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1732982400
    VALUES
      LESS THAN (
        '2024-12-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1733068800
    VALUES
      LESS THAN (
        '2024-12-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1733155200
    VALUES
      LESS THAN (
        '2024-12-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1733241600
    VALUES
      LESS THAN (
        '2024-12-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1733328000
    VALUES
      LESS THAN (
        '2024-12-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1733414400
    VALUES
      LESS THAN (
        '2024-12-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1733500800
    VALUES
      LESS THAN (
        '2024-12-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1733587200
    VALUES
      LESS THAN (
        '2024-12-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1733673600
    VALUES
      LESS THAN (
        '2024-12-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1733760000
    VALUES
      LESS THAN (
        '2024-12-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1733846400
    VALUES
      LESS THAN (
        '2024-12-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1733932800
    VALUES
      LESS THAN (
        '2024-12-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1734019200
    VALUES
      LESS THAN (
        '2024-12-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1734105600
    VALUES
      LESS THAN (
        '2024-12-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1734192000
    VALUES
      LESS THAN (
        '2024-12-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1734278400
    VALUES
      LESS THAN (
        '2024-12-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1734364800
    VALUES
      LESS THAN (
        '2024-12-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1734451200
    VALUES
      LESS THAN (
        '2024-12-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1734537600
    VALUES
      LESS THAN (
        '2024-12-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1734624000
    VALUES
      LESS THAN (
        '2024-12-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1734710400
    VALUES
      LESS THAN (
        '2024-12-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1734796800
    VALUES
      LESS THAN (
        '2024-12-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1734883200
    VALUES
      LESS THAN (
        '2024-12-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1734969600
    VALUES
      LESS THAN (
        '2024-12-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1735056000
    VALUES
      LESS THAN (
        '2024-12-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1735142400
    VALUES
      LESS THAN (
        '2024-12-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1735228800
    VALUES
      LESS THAN (
        '2024-12-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1735315200
    VALUES
      LESS THAN (
        '2024-12-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1735401600
    VALUES
      LESS THAN (
        '2024-12-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1735488000
    VALUES
      LESS THAN (
        '2024-12-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1735574400
    VALUES
      LESS THAN (
        '2024-12-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1735660800
    VALUES
      LESS THAN (
        '2025-01-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1735747200
    VALUES
      LESS THAN (
        '2025-01-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1735833600
    VALUES
      LESS THAN (
        '2025-01-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1735920000
    VALUES
      LESS THAN (
        '2025-01-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1736006400
    VALUES
      LESS THAN (
        '2025-01-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1736092800
    VALUES
      LESS THAN (
        '2025-01-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1736179200
    VALUES
      LESS THAN (
        '2025-01-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1736265600
    VALUES
      LESS THAN (
        '2025-01-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1736352000
    VALUES
      LESS THAN (
        '2025-01-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1736438400
    VALUES
      LESS THAN (
        '2025-01-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1736524800
    VALUES
      LESS THAN (
        '2025-01-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1736611200
    VALUES
      LESS THAN (
        '2025-01-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1736697600
    VALUES
      LESS THAN (
        '2025-01-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1736784000
    VALUES
      LESS THAN (
        '2025-01-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1736870400
    VALUES
      LESS THAN (
        '2025-01-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1736956800
    VALUES
      LESS THAN (
        '2025-01-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1737043200
    VALUES
      LESS THAN (
        '2025-01-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1737129600
    VALUES
      LESS THAN (
        '2025-01-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1737216000
    VALUES
      LESS THAN (
        '2025-01-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1737302400
    VALUES
      LESS THAN (
        '2025-01-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1737388800
    VALUES
      LESS THAN (
        '2025-01-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1737475200
    VALUES
      LESS THAN (
        '2025-01-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1737561600
    VALUES
      LESS THAN (
        '2025-01-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1737648000
    VALUES
      LESS THAN (
        '2025-01-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1737734400
    VALUES
      LESS THAN (
        '2025-01-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1737820800
    VALUES
      LESS THAN (
        '2025-01-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1737907200
    VALUES
      LESS THAN (
        '2025-01-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1737993600
    VALUES
      LESS THAN (
        '2025-01-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1738080000
    VALUES
      LESS THAN (
        '2025-01-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1738166400
    VALUES
      LESS THAN (
        '2025-01-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1738252800
    VALUES
      LESS THAN (
        '2025-01-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1738339200
    VALUES
      LESS THAN (
        '2025-02-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1738425600
    VALUES
      LESS THAN (
        '2025-02-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1738512000
    VALUES
      LESS THAN (
        '2025-02-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1738598400
    VALUES
      LESS THAN (
        '2025-02-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1738684800
    VALUES
      LESS THAN (
        '2025-02-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1738771200
    VALUES
      LESS THAN (
        '2025-02-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1738857600
    VALUES
      LESS THAN (
        '2025-02-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1738944000
    VALUES
      LESS THAN (
        '2025-02-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1739030400
    VALUES
      LESS THAN (
        '2025-02-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1739116800
    VALUES
      LESS THAN (
        '2025-02-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1739203200
    VALUES
      LESS THAN (
        '2025-02-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1739289600
    VALUES
      LESS THAN (
        '2025-02-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1739376000
    VALUES
      LESS THAN (
        '2025-02-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1739462400
    VALUES
      LESS THAN (
        '2025-02-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1739548800
    VALUES
      LESS THAN (
        '2025-02-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1739635200
    VALUES
      LESS THAN (
        '2025-02-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1739721600
    VALUES
      LESS THAN (
        '2025-02-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1739808000
    VALUES
      LESS THAN (
        '2025-02-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1739894400
    VALUES
      LESS THAN (
        '2025-02-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1739980800
    VALUES
      LESS THAN (
        '2025-02-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1740067200
    VALUES
      LESS THAN (
        '2025-02-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1740153600
    VALUES
      LESS THAN (
        '2025-02-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1740240000
    VALUES
      LESS THAN (
        '2025-02-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1740326400
    VALUES
      LESS THAN (
        '2025-02-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1740412800
    VALUES
      LESS THAN (
        '2025-02-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1740499200
    VALUES
      LESS THAN (
        '2025-02-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1740585600
    VALUES
      LESS THAN (
        '2025-02-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1740672000
    VALUES
      LESS THAN (
        '2025-02-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1740758400
    VALUES
      LESS THAN (
        '2025-03-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1740844800
    VALUES
      LESS THAN (
        '2025-03-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1740931200
    VALUES
      LESS THAN (
        '2025-03-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1741017600
    VALUES
      LESS THAN (
        '2025-03-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1741104000
    VALUES
      LESS THAN (
        '2025-03-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1741190400
    VALUES
      LESS THAN (
        '2025-03-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1741276800
    VALUES
      LESS THAN (
        '2025-03-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1741363200
    VALUES
      LESS THAN (
        '2025-03-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1741449600
    VALUES
      LESS THAN (
        '2025-03-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1741536000
    VALUES
      LESS THAN (
        '2025-03-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1741622400
    VALUES
      LESS THAN (
        '2025-03-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1741708800
    VALUES
      LESS THAN (
        '2025-03-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1741795200
    VALUES
      LESS THAN (
        '2025-03-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1741881600
    VALUES
      LESS THAN (
        '2025-03-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1741968000
    VALUES
      LESS THAN (
        '2025-03-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1742054400
    VALUES
      LESS THAN (
        '2025-03-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1742140800
    VALUES
      LESS THAN (
        '2025-03-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1742227200
    VALUES
      LESS THAN (
        '2025-03-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1742313600
    VALUES
      LESS THAN (
        '2025-03-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1742400000
    VALUES
      LESS THAN (
        '2025-03-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1742486400
    VALUES
      LESS THAN (
        '2025-03-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1742572800
    VALUES
      LESS THAN (
        '2025-03-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1742659200
    VALUES
      LESS THAN (
        '2025-03-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1742745600
    VALUES
      LESS THAN (
        '2025-03-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1742832000
    VALUES
      LESS THAN (
        '2025-03-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1742918400
    VALUES
      LESS THAN (
        '2025-03-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1743004800
    VALUES
      LESS THAN (
        '2025-03-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1743091200
    VALUES
      LESS THAN (
        '2025-03-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1743177600
    VALUES
      LESS THAN (
        '2025-03-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1743264000
    VALUES
      LESS THAN (
        '2025-03-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1743350400
    VALUES
      LESS THAN (
        '2025-03-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1743436800
    VALUES
      LESS THAN (
        '2025-04-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1743523200
    VALUES
      LESS THAN (
        '2025-04-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1743609600
    VALUES
      LESS THAN (
        '2025-04-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1743696000
    VALUES
      LESS THAN (
        '2025-04-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1743782400
    VALUES
      LESS THAN (
        '2025-04-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1743868800
    VALUES
      LESS THAN (
        '2025-04-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1743955200
    VALUES
      LESS THAN (
        '2025-04-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1744041600
    VALUES
      LESS THAN (
        '2025-04-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1744128000
    VALUES
      LESS THAN (
        '2025-04-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1744214400
    VALUES
      LESS THAN (
        '2025-04-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1744300800
    VALUES
      LESS THAN (
        '2025-04-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1744387200
    VALUES
      LESS THAN (
        '2025-04-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1744473600
    VALUES
      LESS THAN (
        '2025-04-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1744560000
    VALUES
      LESS THAN (
        '2025-04-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1744646400
    VALUES
      LESS THAN (
        '2025-04-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1744732800
    VALUES
      LESS THAN (
        '2025-04-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1744819200
    VALUES
      LESS THAN (
        '2025-04-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1744905600
    VALUES
      LESS THAN (
        '2025-04-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1744992000
    VALUES
      LESS THAN (
        '2025-04-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1745078400
    VALUES
      LESS THAN (
        '2025-04-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1745164800
    VALUES
      LESS THAN (
        '2025-04-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1745251200
    VALUES
      LESS THAN (
        '2025-04-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1745337600
    VALUES
      LESS THAN (
        '2025-04-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1745424000
    VALUES
      LESS THAN (
        '2025-04-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1745510400
    VALUES
      LESS THAN (
        '2025-04-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1745596800
    VALUES
      LESS THAN (
        '2025-04-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1745683200
    VALUES
      LESS THAN (
        '2025-04-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1745769600
    VALUES
      LESS THAN (
        '2025-04-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1745856000
    VALUES
      LESS THAN (
        '2025-04-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1745942400
    VALUES
      LESS THAN (
        '2025-04-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1746028800
    VALUES
      LESS THAN (
        '2025-05-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1746115200
    VALUES
      LESS THAN (
        '2025-05-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1746201600
    VALUES
      LESS THAN (
        '2025-05-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1746288000
    VALUES
      LESS THAN (
        '2025-05-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1746374400
    VALUES
      LESS THAN (
        '2025-05-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1746460800
    VALUES
      LESS THAN (
        '2025-05-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1746547200
    VALUES
      LESS THAN (
        '2025-05-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1746633600
    VALUES
      LESS THAN (
        '2025-05-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1746720000
    VALUES
      LESS THAN (
        '2025-05-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1746806400
    VALUES
      LESS THAN (
        '2025-05-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1746892800
    VALUES
      LESS THAN (
        '2025-05-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1746979200
    VALUES
      LESS THAN (
        '2025-05-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1747065600
    VALUES
      LESS THAN (
        '2025-05-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1747152000
    VALUES
      LESS THAN (
        '2025-05-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1747238400
    VALUES
      LESS THAN (
        '2025-05-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1747324800
    VALUES
      LESS THAN (
        '2025-05-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1747411200
    VALUES
      LESS THAN (
        '2025-05-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1747497600
    VALUES
      LESS THAN (
        '2025-05-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1747584000
    VALUES
      LESS THAN (
        '2025-05-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1747670400
    VALUES
      LESS THAN (
        '2025-05-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1747756800
    VALUES
      LESS THAN (
        '2025-05-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1747843200
    VALUES
      LESS THAN (
        '2025-05-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1747929600
    VALUES
      LESS THAN (
        '2025-05-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1748016000
    VALUES
      LESS THAN (
        '2025-05-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1748102400
    VALUES
      LESS THAN (
        '2025-05-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1748188800
    VALUES
      LESS THAN (
        '2025-05-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1748275200
    VALUES
      LESS THAN (
        '2025-05-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1748361600
    VALUES
      LESS THAN (
        '2025-05-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1748448000
    VALUES
      LESS THAN (
        '2025-05-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1748534400
    VALUES
      LESS THAN (
        '2025-05-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1748620800
    VALUES
      LESS THAN (
        '2025-05-31 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1748707200
    VALUES
      LESS THAN (
        '2025-06-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1748793600
    VALUES
      LESS THAN (
        '2025-06-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1748880000
    VALUES
      LESS THAN (
        '2025-06-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1748966400
    VALUES
      LESS THAN (
        '2025-06-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1749052800
    VALUES
      LESS THAN (
        '2025-06-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1749139200
    VALUES
      LESS THAN (
        '2025-06-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1749225600
    VALUES
      LESS THAN (
        '2025-06-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1749312000
    VALUES
      LESS THAN (
        '2025-06-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1749398400
    VALUES
      LESS THAN (
        '2025-06-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1749484800
    VALUES
      LESS THAN (
        '2025-06-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1749571200
    VALUES
      LESS THAN (
        '2025-06-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1749657600
    VALUES
      LESS THAN (
        '2025-06-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1749744000
    VALUES
      LESS THAN (
        '2025-06-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1749830400
    VALUES
      LESS THAN (
        '2025-06-14 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1749916800
    VALUES
      LESS THAN (
        '2025-06-15 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1750003200
    VALUES
      LESS THAN (
        '2025-06-16 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1750089600
    VALUES
      LESS THAN (
        '2025-06-17 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1750176000
    VALUES
      LESS THAN (
        '2025-06-18 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1750262400
    VALUES
      LESS THAN (
        '2025-06-19 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1750348800
    VALUES
      LESS THAN (
        '2025-06-20 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1750435200
    VALUES
      LESS THAN (
        '2025-06-21 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1750521600
    VALUES
      LESS THAN (
        '2025-06-22 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1750608000
    VALUES
      LESS THAN (
        '2025-06-23 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1750694400
    VALUES
      LESS THAN (
        '2025-06-24 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1750780800
    VALUES
      LESS THAN (
        '2025-06-25 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1750867200
    VALUES
      LESS THAN (
        '2025-06-26 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1750953600
    VALUES
      LESS THAN (
        '2025-06-27 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1751040000
    VALUES
      LESS THAN (
        '2025-06-28 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1751126400
    VALUES
      LESS THAN (
        '2025-06-29 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1751212800
    VALUES
      LESS THAN (
        '2025-06-30 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1751299200
    VALUES
      LESS THAN (
        '2025-07-01 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1751385600
    VALUES
      LESS THAN (
        '2025-07-02 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1751472000
    VALUES
      LESS THAN (
        '2025-07-03 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1751558400
    VALUES
      LESS THAN (
        '2025-07-04 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1751644800
    VALUES
      LESS THAN (
        '2025-07-05 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1751731200
    VALUES
      LESS THAN (
        '2025-07-06 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1751817600
    VALUES
      LESS THAN (
        '2025-07-07 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1751904000
    VALUES
      LESS THAN (
        '2025-07-08 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1751990400
    VALUES
      LESS THAN (
        '2025-07-09 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752076800
    VALUES
      LESS THAN (
        '2025-07-10 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752163200
    VALUES
      LESS THAN (
        '2025-07-11 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752249600
    VALUES
      LESS THAN (
        '2025-07-12 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752336000
    VALUES
      LESS THAN (
        '2025-07-13 00:00:00'::timestamp (0) without TIME zone
      ),
      PARTITION p1752422400
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
      ),
      PARTITION p1791734400
    VALUES
      LESS THAN (
        '2026-10-12 00:00:00'::timestamp (0) without TIME zone
      )
  ) ENABLE ROW MOVEMENT;

COMMENT ON TABLE madp_collect_all IS '广场埋点数据解析';

COMMENT ON COLUMN madp_collect_all.user_id IS '用户ID';

COMMENT ON COLUMN madp_collect_all.login_id IS '登录ID';

COMMENT ON COLUMN madp_collect_all.anony_id IS '匿名ID';

COMMENT ON COLUMN madp_collect_all.app_id IS '埋点自身应用id';

COMMENT ON COLUMN madp_collect_all.trig_tm IS '触发时间';

COMMENT ON COLUMN madp_collect_all.event IS '事件ID';

COMMENT ON COLUMN madp_collect_all.title IS '页面标题';

COMMENT ON COLUMN madp_collect_all.function_id IS '功能ID';

COMMENT ON COLUMN madp_collect_all.function_name IS '功能名';

COMMENT ON COLUMN madp_collect_all.content_id IS '内容id';

COMMENT ON COLUMN madp_collect_all.hold_duration IS '页面停留时长';

COMMENT ON COLUMN madp_collect_all.create_time IS '事件发生时间';

COMMENT ON COLUMN madp_collect_all.event_track_id IS '事件追踪ID';

COMMENT ON COLUMN madp_collect_all.event_duration IS '停留时长';

COMMENT ON COLUMN madp_collect_all.out_channel_id IS '子公司渠道ID/跳转渠道组ID';

COMMENT ON COLUMN madp_collect_all.product_id IS '产品ID';

COMMENT ON COLUMN madp_collect_all.product_name IS '产品名称';

COMMENT ON COLUMN madp_collect_all.sdk_version IS 'sdk版本';

COMMENT ON COLUMN madp_collect_all.source_id IS '绑定活动ID/资源ID/产品ID/活动ID';

COMMENT ON COLUMN madp_collect_all.os IS '操作系统';

COMMENT ON COLUMN madp_collect_all.os_version IS '操作系统版本';

COMMENT ON COLUMN madp_collect_all.referrer IS '向前地址';

COMMENT ON COLUMN madp_collect_all.ref_screen_name IS '上级页面地址';

COMMENT ON COLUMN madp_collect_all.session_id IS '会话id';

COMMENT ON COLUMN madp_collect_all.page_id IS '页面ID';

COMMENT ON COLUMN madp_collect_all.ref_page_id IS '前向页面ID';

COMMENT ON COLUMN madp_collect_all.curr_page_url IS '当前页面URL';

COMMENT ON COLUMN madp_collect_all.page_path IS '页面路径';

COMMENT ON COLUMN madp_collect_all.curr_page_title IS '当前页面标题';

COMMENT ON COLUMN madp_collect_all.src_chnl_id IS '来源渠道ID';

COMMENT ON COLUMN madp_collect_all.area_name IS '功能所属区域名称';

COMMENT ON COLUMN madp_collect_all.visit_source IS '外部渠道投放位置名称';

COMMENT ON COLUMN madp_collect_all.area_sequency IS 'area_sequency';

COMMENT ON COLUMN madp_collect_all.share_id IS '分享事件ID';

COMMENT ON COLUMN madp_collect_all.resource_id IS '资源位id';

COMMENT ON COLUMN madp_collect_all.room_id IS '直播间id';

COMMENT ON COLUMN madp_collect_all.book_id IS '读书id';

COMMENT ON COLUMN madp_collect_all.app_unqi_id IS '应用唯一标识';

COMMENT ON COLUMN madp_collect_all.mission_id IS '活动任务ID';

COMMENT ON COLUMN madp_collect_all.app_version IS '应用版本';

COMMENT ON COLUMN madp_collect_all.pages_id IS '活动页面/活动中间页id';

COMMENT ON COLUMN madp_collect_all.ref_page_source IS '上级页面来源';

COMMENT ON COLUMN madp_collect_all.src_scenario IS '消金上级页面来源';

COMMENT ON COLUMN madp_collect_all.special_id IS '专题ID';

COMMENT ON COLUMN madp_collect_all.pk_id IS '话题pkid';

COMMENT ON COLUMN madp_collect_all.sku_id IS '商品id';

COMMENT ON COLUMN madp_collect_all.scene_id IS '用户场景id';

COMMENT ON COLUMN madp_collect_all.evt_id IS '行为id';

COMMENT ON COLUMN madp_collect_all.right_id IS '权益id';

COMMENT ON COLUMN madp_collect_all.short_curr_url IS '原始url短链';

COMMENT ON COLUMN madp_collect_all.short_page_url IS 'pageid短链';

COMMENT ON COLUMN madp_collect_all.src_page_id IS '原始pageid';

COMMENT ON COLUMN madp_collect_all.ds IS '触发日期,分区字段';

COMMENT ON COLUMN madp_collect_all.navi_start IS '加载开始时间';

COMMENT ON COLUMN madp_collect_all.redi_start IS '重定向开始时间';

COMMENT ON COLUMN madp_collect_all.redi_end IS '重定向结束时间';

COMMENT ON COLUMN madp_collect_all.fetch_start IS '拉取开始时间';

COMMENT ON COLUMN madp_collect_all.dns_start IS 'DNS开始时间';

COMMENT ON COLUMN madp_collect_all.dns_end IS 'DNS结束时间';

COMMENT ON COLUMN madp_collect_all.con_start IS '建连开始时间';

COMMENT ON COLUMN madp_collect_all.con_end IS '建连结束时间';

COMMENT ON COLUMN madp_collect_all.request_start IS '请求开始时间';

COMMENT ON COLUMN madp_collect_all.response_start IS '响应开始时间';

COMMENT ON COLUMN madp_collect_all.response_end IS '响应结束时间';

COMMENT ON COLUMN madp_collect_all.dom_start IS 'DOM开始时间';

COMMENT ON COLUMN madp_collect_all.dom_complete IS 'DOM完成时间';

COMMENT ON COLUMN madp_collect_all.load_start IS 'load开始时间';

COMMENT ON COLUMN madp_collect_all.load_end IS 'load结束时间';

COMMENT ON COLUMN madp_collect_all.on_page_begin IS 'webView容器 加载开始时间';

COMMENT ON COLUMN madp_collect_all.on_page_finished IS 'webView容器 加载完成时间';

COMMENT ON COLUMN madp_collect_all.is_preload_on IS '是否开启了预载0表示未开启预载，1表示开启预载功能';

COMMENT ON COLUMN madp_collect_all.hybrid_h5 IS '数据来源';

COMMENT ON COLUMN madp_collect_all.src_anony_id IS '原始匿名ID';

COMMENT ON COLUMN madp_collect_all.valid_sdk_version_flg IS 'sdk是否有效';

COMMENT ON COLUMN madp_collect_all.account_id IS '财富号ID';

COMMENT ON COLUMN madp_collect_all.order_id IS '子订单ID';

COMMENT ON COLUMN madp_collect_all.goods_id IS '商品id';

COMMENT ON COLUMN madp_collect_all.special_zone IS '专区ID';

COMMENT ON COLUMN madp_collect_all.sale_num IS '商城SKU数量';

COMMENT ON COLUMN madp_collect_all.parent_order_id IS '主订单ID';

COMMENT ON COLUMN madp_collect_all.shop_id IS '店铺ID';

COMMENT ON COLUMN madp_collect_all.cate_cd IS '商城商品分类ID';

COMMENT ON COLUMN madp_collect_all.after_sale_order_id IS '售后订单ID';

COMMENT ON COLUMN madp_collect_all.area_text IS '区域信息';

COMMENT ON COLUMN madp_collect_all.area_name_minus_1 IS '二级内部区域名称';

COMMENT ON COLUMN madp_collect_all.area_name_minus_2 IS '三级内部区域名称';

COMMENT ON COLUMN madp_collect_all.area_name_minus_3 IS '四级内部区域名称';

COMMENT ON COLUMN madp_collect_all.area_name_minus_4 IS '五级内部区域名称';

COMMENT ON COLUMN madp_collect_all.resource_bit_id IS '资源位ID';

COMMENT ON COLUMN madp_collect_all.share_channel IS '分享渠道';

COMMENT ON COLUMN madp_collect_all.object_id IS '活动ID/内容ID/产品ID';

COMMENT ON COLUMN madp_collect_all.project_id IS '项目标识id';

COMMENT ON COLUMN madp_collect_all.store_id IS '商户id';

COMMENT ON COLUMN madp_collect_all.meta_event_id IS '元事件id';

COMMENT ON COLUMN madp_collect_all.chapter_id IS '章节id';

COMMENT ON COLUMN madp_collect_all.track_record_pk IS '埋点记录主键';

COMMENT ON COLUMN madp_collect_all.source_info_id IS '资源信息id';

COMMENT ON COLUMN madp_collect_all.jkid IS '卓信ID';

COMMENT ON COLUMN madp_collect_all.proc_time IS '操作时间';

COMMENT ON COLUMN madp_collect_all.ds_tm IS '分区时间记录';

COMMENT ON COLUMN madp_collect_all.uuid IS '唯一主键';

COMMENT ON COLUMN madp_collect_all.new_sdk IS '新sdk标识';

COMMENT ON COLUMN madp_collect_all.n_jkid IS '卓信ID上报源标识';

COMMENT ON COLUMN madp_collect_all.trig_tm_ms IS '触发时间毫秒';

COMMENT ON COLUMN madp_collect_all.create_time_ms IS '事件发生时间毫秒';


SET
  search_path = ods;

CREATE TABLE
  ods_usms_lm_agreement_version_t_df (
    channel_id character varying (128),
    agreement_version character varying (128),
    last_agreement_version character varying (128),
    take_effect_time timestamp without TIME zone,
    extend1 character varying (128),
    extend2 character varying (128),
    extend3 character varying (128),
    create_time timestamp without TIME zone,
    create_user character varying (128),
    update_time timestamp without TIME zone,
    update_user character varying (128),
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
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(channel_id) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
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

COMMENT ON TABLE ods_usms_lm_agreement_version_t_df IS '渠道协议表';

COMMENT ON COLUMN ods_usms_lm_agreement_version_t_df.channel_id IS '业务渠道id';

COMMENT ON COLUMN ods_usms_lm_agreement_version_t_df.agreement_version IS '协议版本';

COMMENT ON COLUMN ods_usms_lm_agreement_version_t_df.last_agreement_version IS '生效前协议版本';

COMMENT ON COLUMN ods_usms_lm_agreement_version_t_df.take_effect_time IS '生效时间';

COMMENT ON COLUMN ods_usms_lm_agreement_version_t_df.extend1 IS '扩展字段1';

COMMENT ON COLUMN ods_usms_lm_agreement_version_t_df.extend2 IS '扩展字段2';

COMMENT ON COLUMN ods_usms_lm_agreement_version_t_df.extend3 IS '扩展字段3';

COMMENT ON COLUMN ods_usms_lm_agreement_version_t_df.create_time IS '创建时间';

COMMENT ON COLUMN ods_usms_lm_agreement_version_t_df.create_user IS '创建人';

COMMENT ON COLUMN ods_usms_lm_agreement_version_t_df.update_time IS '修改时间';

COMMENT ON COLUMN ods_usms_lm_agreement_version_t_df.update_user IS '修改人';


SET
  search_path = ods;

CREATE TABLE
  ods_usms_lm_channel_base_t_df (
    channel_id character varying (512),
    secret character varying (512),
    name character varying (512),
    group_id character varying (512),
    sensitive_salt character varying (512),
    private_key character varying (512),
    public_key character varying (512),
    third_public_key character varying (512),
    description character varying (512),
    api_version character varying (512),
    resource_ids character varying (512),
    scope character varying (512),
    authorized_grant_types character varying (512),
    auto_approve character varying (128),
    agreement_name character varying (512),
    agreement_url character varying (512),
    auth_redirect_url character varying (512),
    code_expire_time numeric (11, 0),
    token_expire_time numeric (11, 0),
    channel_oauth_type character varying (512),
    req_token_url character varying (512),
    req_token_method character varying (512),
    req_token_headers character varying (512),
    req_token_media_type character varying (512),
    req_token_params character varying (512),
    req_token_resp_mp character varying (512),
    req_userinfo_url character varying (2048),
    req_userinfo_method character varying (512),
    req_userinfo_headers character varying (512),
    req_userinfo_media_type character varying (512),
    req_userinfo_params character varying (512),
    req_userinfo_resp_mp character varying (512),
    send_welcome_sms_flag bigint,
    status bigint,
    support_wallet bigint,
    create_person character varying (128),
    create_time character varying (128),
    update_person character varying (128),
    update_time character varying (128),
    sdk_flag bigint,
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
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY ROUNDROBIN TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
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

COMMENT ON TABLE ods_usms_lm_channel_base_t_df IS '渠道基础信息表';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.channel_id IS '渠道id';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.secret IS '渠道密钥';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.name IS '渠道名称';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.group_id IS '渠道组id';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.sensitive_salt IS '敏感信息加密盐值';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.private_key IS '国密加密私钥';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.public_key IS '国密加密私钥';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.third_public_key IS '成员方公钥';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.description IS '渠道描述(文案)';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.api_version IS 'api版本';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.resource_ids IS '资源id标识-预留';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.scope IS 'auth权限范围';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.authorized_grant_types IS 'auth类型,授权后拼接参数使用';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.auto_approve IS '是否自动授权，0-否，1-是';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.agreement_name IS '三方协议名称';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.agreement_url IS '三方协议地址';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.auth_redirect_url IS '授权重定向地址';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.code_expire_time IS 'code过期时间';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.token_expire_time IS 'token过期时间';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.channel_oauth_type IS '渠道支持的数据交互类型,token&amp;code';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.req_token_url IS '渠道换取token地址';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.req_token_method IS '获取token方法类型，get或post';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.req_token_headers IS '获取token方法头信息';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.req_token_media_type IS '获取token请求类型';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.req_token_params IS 'token请求参数，json格式';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.req_token_resp_mp IS 'token实体mapping';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.req_userinfo_url IS '渠道用户信息获取地址';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.req_userinfo_method IS '获取用户信息方法类型，get或post';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.req_userinfo_headers IS '获取用户信息方法头信息';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.req_userinfo_media_type IS '获取用户信息请求类型';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.req_userinfo_params IS '用户信息请求参数，json格式';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.req_userinfo_resp_mp IS '渠道用户信息实体mapping';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.send_welcome_sms_flag IS '注册完成后发送欢迎短信标志位:1:发送,0:不发送';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.status IS '状态标识:0-不可用，1-可用';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.support_wallet IS '是否支持钱包;0-不支持,1-支持';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.create_person IS '渠道创建人';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.create_time IS '渠道创建时间';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.update_person IS '最后修改人';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.update_time IS '最后修改人';

COMMENT ON COLUMN ods_usms_lm_channel_base_t_df.sdk_flag IS '0:未开通，1:开通';

SET
  search_path = ods;

CREATE TABLE
  ods_usms_lm_channel_group_base_t_df (
    group_id character varying (128),
    group_name character varying (512),
    group_logo_url character varying (2048),
    description character varying (512),
    status bigint,
    create_person character varying (128),
    create_time timestamp without TIME zone,
    update_person character varying (128),
    update_time timestamp without TIME zone,
    group_type bigint,
    extend_1 character varying (128),
    extend_2 character varying (128),
    extend_3 character varying (128),
    extend_4 character varying (128),
    extend_5 character varying (128),
    extend_6 character varying (128),
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
  ) TABLESPACE cu_obs_tbs DISTRIBUTE BY HASH(group_id) TO GROUP v3_logical
PARTITION BY
  RANGE (ds) (
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

COMMENT ON TABLE ods_usms_lm_channel_group_base_t_df IS '渠道分组表';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.group_id IS '渠道分组id';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.group_name IS '渠道分组名称';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.group_logo_url IS '渠道分组logo';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.description IS '渠道分组描述(文案)';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.status IS '状态:删除0,正常1';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.create_person IS '创建人';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.create_time IS '创建时间';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.update_person IS '最后修改人';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.update_time IS '最后修改时间';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.group_type IS '1:产品';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.extend_1 IS '扩展字段1';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.extend_2 IS '扩展字段2';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.extend_3 IS '扩展字段3';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.extend_4 IS '扩展字段4';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.extend_5 IS '扩展字段5';

COMMENT ON COLUMN ods_usms_lm_channel_group_base_t_df.extend_6 IS '扩展字段6';
















