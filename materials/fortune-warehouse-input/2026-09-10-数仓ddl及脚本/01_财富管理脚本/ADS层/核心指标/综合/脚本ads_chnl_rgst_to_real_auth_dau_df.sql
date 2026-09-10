-- DWS sql 
-- ******************************************************************** --
-- author: CI-zx-18519129105
-- create time: 2025/07/17 17:39:17 GMT+08:00
-- ******************************************************************** --
delete from rec.ads_chnl_rgst_to_real_auth_dau_df where ds = '${data_ds}';

CREATE LOCAL TEMPORARY TABLE IF NOT EXISTS ads_chnl_rgst_to_real_auth_dau_df_mid_01
(     
     data_dt            date      
    ,usr_id             varchar(128) 
    ,rgst_dt            date
    ,rgst_sec_chnl_nm   varchar(128)  
    ,evt_trig_dt        date                        
    ,cur_mth_begin      varchar(128)                                                                      
)
WITH (  
    ORIENTATION = column
    ,colversion = 3.0           --指定列存储的版本
    ,enable_hstore_opt = TRUE   --启用HStore优化
    ,compression = middle 
)
DISTRIBUTE BY HASH (usr_id)   
;


insert into ads_chnl_rgst_to_real_auth_dau_df_mid_01
select t3.date_dt as data_dt
    ,t1.usr_id
    ,t1.rgst_dt
    ,t1.rgst_sec_chnl_nm
    ,t2.evt_trig_dt
    ,t3.cur_mth_begin
from 
(
    select usr_id
        ,rgst_dt
        ,rgst_sec_chnl_nm
    from cdm.dwd_cu_rgst_fin_di 
    where ds <= '${data_ds}'
    group by usr_id
        ,rgst_dt
        ,rgst_sec_chnl_nm
)t1 
join 
(
    select evt_trig_dt
        ,login_id
    from cdm.dwd_lm_pv_df
    where ds >= '2022-12-26' 
        and ds <= '${data_ds}'
        and event = '$pageview'
    group by evt_trig_dt
        ,login_id
)t2 on t1.usr_id = t2.login_id
cross join (select * from cdm.dim_pb_date_yf where date_dt = '${data_ds}')t3 
where t1.rgst_dt <= t3.date_dt
    and t1.rgst_dt <= t2.evt_trig_dt
;

insert into rec.ads_chnl_rgst_to_real_auth_dau_df 
select t1.data_dt
    ,t1.rgst_sec_chnl_nm
    ,t1.chnl_sub_nm
    ,t1.rgst_cnt_d
    ,t1.rgst_cnt_m
    ,t1.rgst_cnt_a
    ,t2.real_cnt_d
    ,t2.real_cnt_m
    ,t2.real_cnt_a
    ,t3.auth_cnt_d
    ,t3.auth_cnt_m
    ,t3.auth_cnt_a
    ,t4.rgst_log_cnt_d 
    ,t4.rgst_log_cnt_m 
    ,t4.rgst_log_cnt_a 
    ,'${data_ds}' as ds
from 
(
    select data_dt
        ,'整体' as chnl_sub_nm
        ,'整体' as rgst_sec_chnl_nm
        ,sum(new_rgst_cnt_d) as rgst_cnt_d
        ,sum(new_rgst_cnt_m) as rgst_cnt_m
        ,sum(new_rgst_cnt_a) as rgst_cnt_a
    from rec.ads_rgst_chnl_cnt_df 
    where ds = '${data_ds}'
        and sec_chnl_nm not in ('麦当劳','中信书院')
    group by data_dt
    union all 
    select data_dt
        ,chnl_sub_nm
        ,sec_chnl_nm as rgst_sec_chnl_nm
        ,sum(new_rgst_cnt_d) as rgst_cnt_d
        ,sum(new_rgst_cnt_m) as rgst_cnt_m
        ,sum(new_rgst_cnt_a) as rgst_cnt_a
    from rec.ads_rgst_chnl_cnt_df 
    where ds = '${data_ds}'
        and sec_chnl_nm not in ('麦当劳','中信书院')
    group by data_dt
        ,chnl_sub_nm
        ,sec_chnl_nm    
)t1 
left join 
(
    select data_dt
        ,'整体' as chnl_sub_nm
        ,'整体' as rgst_sec_chnl_nm
        ,sum(real_today)  as real_cnt_d
        ,sum(real_curmth) as real_cnt_m
        ,sum(real_all)    as real_cnt_a
    from rec.ads_chnl_real_user_df
    where ds = '${data_ds}'
    group by data_dt
    union all 
    select data_dt
        ,chnl_sub_nm
        ,sec_chnl_nm as rgst_sec_chnl_nm
        ,sum(real_today)  as real_cnt_d
        ,sum(real_curmth) as real_cnt_m
        ,sum(real_all)    as real_cnt_a
    from rec.ads_chnl_real_user_df
    where ds = '${data_ds}'
    group by data_dt
        ,chnl_sub_nm
        ,sec_chnl_nm
)t2 on t1.data_dt = t2.data_dt and t1.rgst_sec_chnl_nm = t2.rgst_sec_chnl_nm and t1.chnl_sub_nm = t2.chnl_sub_nm
left join 
(
    select data_dt
        ,'整体' as chnl_sub_nm
        ,'整体' as rgst_sec_chnl_nm
        ,sum(auth_user_cnt)     as auth_cnt_d
        ,sum(auth_user_mon_cnt) as auth_cnt_m
        ,sum(auth_user_all_cnt) as auth_cnt_a
    from rec.ads_chnl_auth_qty_df
    where ds = '${data_ds}'
    group by data_dt
    union all
    select t1.data_dt
        ,t2.chnl_sub_nm 
        ,t1.rgst_sec_chnl_nm as rgst_sec_chnl_nm 
        ,sum(auth_cnt_d) as auth_cnt_d
        ,sum(auth_cnt_m) as auth_cnt_m
        ,sum(auth_cnt_a) as auth_cnt_a
    from 
    (
        select data_dt
            ,rgst_sec_chnl_nm
            ,sum(auth_user_cnt)     as auth_cnt_d
            ,sum(auth_user_mon_cnt) as auth_cnt_m
            ,sum(auth_user_all_cnt) as auth_cnt_a
        from rec.ads_chnl_auth_qty_df
        where ds = '${data_ds}'
        group by data_dt
            ,rgst_sec_chnl_nm
    )t1 
    left join 
    (
        select sec_chnl_nm
            ,chnl_sub_nm
        from cdm.dim_ch_chl_df 
        where ds = '${data_ds}' 
        group by sec_chnl_nm
            ,chnl_sub_nm
    )t2 on t1.rgst_sec_chnl_nm  = t2.sec_chnl_nm 
    group by t1.data_dt
        ,t1.rgst_sec_chnl_nm 
        ,t2.chnl_sub_nm 
)t3 on t1.data_dt = t3.data_dt and t1.rgst_sec_chnl_nm = t3.rgst_sec_chnl_nm and t1.chnl_sub_nm = t3.chnl_sub_nm
left join 
(
    select data_dt 
        ,'整体' as chnl_sub_nm
        ,'整体' as rgst_sec_chnl_nm 
        ,count(distinct case when rgst_dt = data_dt then usr_id end)        as rgst_log_cnt_d
        ,count(distinct case when rgst_dt >= cur_mth_begin then usr_id end) as rgst_log_cnt_m
        ,count(distinct usr_id)                                             as rgst_log_cnt_a
    from ads_chnl_rgst_to_real_auth_dau_df_mid_01
    where rgst_sec_chnl_nm not in ('麦当劳','中信书院')
    group by data_dt 
    union all
    select data_dt 
        ,t2.chnl_sub_nm
        ,t1.rgst_sec_chnl_nm 
        ,count(distinct case when rgst_dt = data_dt then usr_id end)        as rgst_log_cnt_d
        ,count(distinct case when rgst_dt >= cur_mth_begin then usr_id end) as rgst_log_cnt_m
        ,count(distinct usr_id)                                             as rgst_log_cnt_a
    from ads_chnl_rgst_to_real_auth_dau_df_mid_01 t1
    left join 
    (
        select sec_chnl_nm
            ,chnl_sub_nm
        from cdm.dim_ch_chl_df 
        where ds = '${data_ds}' 
        group by sec_chnl_nm
            ,chnl_sub_nm
    )t2 on t1.rgst_sec_chnl_nm  = t2.Sec_Chnl_Nm 
    group by data_dt 
        ,t2.chnl_sub_nm
        ,t1.rgst_sec_chnl_nm
)t4 on t1.data_dt = t4.data_dt and t1.rgst_sec_chnl_nm = t4.rgst_sec_chnl_nm and t1.chnl_sub_nm = t4.chnl_sub_nm
;