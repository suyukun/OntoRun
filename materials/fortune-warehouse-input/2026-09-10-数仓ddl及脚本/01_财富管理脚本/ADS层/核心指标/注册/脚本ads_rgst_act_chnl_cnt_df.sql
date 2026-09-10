-- DWS sql 
-- ******************************************************************** --
-- author: CI-zx-18519129105
-- create time: 2025/07/15 18:54:30 GMT+08:00
-- ******************************************************************** --
delete from rec.ads_rgst_act_chnl_cnt_df where ds = '${data_ds}';
insert into rec.ads_rgst_act_chnl_cnt_df 
select '${data_ds}' as data_dt
    ,t1.raw_rgst_sec_chnl_nm 
    ,t1.rgst_sec_chnl_nm as act_rgst_sec_chnl_nm       
    ,t3.chnl_sub_nm as act_rgst_chnl_sub_nm    
    ,count(case when date(t1.rgst_dt) = t2.date_dt then usr_id end) as new_rgst_cnt_d                             --当日_新增注册用户数                
    ,count(case when date(t1.rgst_dt) between t2.last_7_dt and t2.date_dt then usr_id end) as new_rgst_cnt_7d      --近7日_新增注册用户数                    
    ,count(case when date(t1.rgst_dt) between t2.cur_mth_begin and t2.date_dt then usr_id end) as new_rgst_cnt_m   --当月_新增注册用户数                   
    ,count(case when date(t1.rgst_dt) between t2.year_begin and t2.date_dt then usr_id end) as new_rgst_cnt_y      --当年累计_新增注册用户数              
    ,count(case when date(t1.rgst_dt) <= t2.date_dt then usr_id end) as new_rgst_cnt_a      --历史累计_新增注册用户数 
    ,'${data_ds}' as ds
from 
(
    select usr_id
        ,rgst_dt
        ,nonfin_rgst_sec_chnl_nm as raw_rgst_sec_chnl_nm
        ,rgst_sec_chnl_nm
    from cdm.dwd_cu_rgst_fin_di 
    where ds <= '${data_ds}'
        and nonfin_rgst_sec_chnl_nm in ('麦当劳','中信书院')
    union all
    select t1.*
    from
    (
        select usr_id
            ,rgst_dt
            ,rgst_sec_chnl_nm as raw_rgst_sec_chnl_nm
            ,rgst_sec_chnl_nm
        from cdm.dwd_cu_rgst_nonfin_di
        where ds <= '${data_ds}'
    )t1 
    left join 
    (
        select usr_id
        from cdm.dwd_cu_rgst_fin_di 
        where ds <= '${data_ds}'
            and nonfin_rgst_sec_chnl_nm in ('麦当劳','中信书院')
    )t2 on t1.usr_id = t2.usr_id
    where t2.usr_id is null
)t1
left join 
(
    select Sec_Chnl_Nm
        ,chnl_sub_nm
    from cdm.dim_ch_chl_df 
    where ds = '${data_ds}'
    group by Sec_Chnl_Nm
        ,chnl_sub_nm
)t3 on t1.rgst_sec_chnl_nm  = t3.Sec_Chnl_Nm 
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
    ,t1.raw_rgst_sec_chnl_nm     
    ,t1.rgst_sec_chnl_nm        
    ,t3.chnl_sub_nm
;