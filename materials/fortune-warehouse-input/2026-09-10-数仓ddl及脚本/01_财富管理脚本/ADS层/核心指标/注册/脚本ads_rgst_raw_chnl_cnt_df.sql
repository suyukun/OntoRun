-- DWS sql 
-- ******************************************************************** --
-- author: CI-zx-18519129105
-- create time: 2025/07/15 18:48:39 GMT+08:00
-- ******************************************************************** --
delete from rec.ads_rgst_raw_chnl_cnt_df where ds = '${data_ds}';
insert into rec.ads_rgst_raw_chnl_cnt_df	
select t2.date_dt as data_dt
    ,t1.rgst_sec_chnl_nm as raw_rgst_sec_chnl_nm       
    ,rgst_enjy_fg
    ,rgst_type
    ,count(case when date(t1.rgst_dt) = t2.date_dt then usr_id end) as new_rgst_cnt_d                              --当日_新增注册用户数                
    ,count(case when date(t1.rgst_dt) between t2.last_7_dt and t2.date_dt then usr_id end) as new_rgst_cnt_7d      --近7日_新增注册用户数                    
    ,count(case when date(t1.rgst_dt) between t2.cur_mth_begin and t2.date_dt then usr_id end) as new_rgst_cnt_m   --当月_新增注册用户数                   
    ,count(case when date(t1.rgst_dt) between t2.year_begin and t2.date_dt then usr_id end) as new_rgst_cnt_y      --当年累计_新增注册用户数              
    ,count(case when date(t1.rgst_dt) <= t2.date_dt then usr_id end) as new_rgst_cnt_a                             --历史累计_新增注册用户数 
    ,'${data_ds}' as ds
from 
(
    select usr_id
        ,rgst_dt
        ,rgst_sec_chnl_nm
        ,rgst_enjy_fg
        ,rgst_type
    from cdm.dim_cu_usr_info_df 
    where ds = '${data_ds}'
)t1
cross join 
(
    select date_dt
        ,last_7_dt
        ,cur_mth_begin
        ,year_begin
    from cdm.dim_pb_date_yf
    where date_dt = '${data_ds}'
)t2 
where date(t1.rgst_dt) <= t2.date_dt  
group by t2.date_dt 
    ,t1.rgst_sec_chnl_nm         --原始注册二级渠道名称	
    ,rgst_enjy_fg
    ,rgst_type
    ,t2.date_dt
;