-- DWS sql 
-- ******************************************************************** --
-- author: CI-zx-18519129105
-- create time: 2025/07/18 10:01:30 GMT+08:00
-- ******************************************************************** --
delete from rec.ads_chnl_auth_qty_df where ds = '${data_ds}';
insert into rec.ads_chnl_auth_qty_df
select '${data_ds}' as data_dt    --数据日期
    ,rgst_sec_chnl_nm    --二级注册渠道名称
    ,rltv_sec_chnl_nm as auth_sec_chnl_nm    --授权渠道名称
    ,count(case when t1.grant_dt  = t3.date_dt then t1.usr_id end)       as auth_today    --当日_授权账户数
    ,count(case when t1.grant_dt >= t3.last_7_dt then t1.usr_id end)     as auth_7d       --近7天_授权账户数
    ,count(case when t1.grant_dt >= t3.last_30_dt then t1.usr_id end)    as auth_30d      --近30天_授权账户数
    ,count(case when t1.grant_dt >= t3.cur_mth_begin then t1.usr_id end) as auth_curmth   --当月_授权账户数
    ,count(case when t1.grant_dt >= t3.year_begin then t1.usr_id end)    as auth_curyear  --当年累计_授权账户数
    ,count(case when t1.grant_dt <= t3.date_dt then t1.usr_id end)       as auth_all      --历史累计_授权账户数
    ,'${data_ds}' as ds
from 
(
    select rltv_sec_chnl_nm
        ,grant_dt
        ,usr_id
    from cdm.dwd_ch_usr_rltv_df 
    where ds = '${data_ds}' 
        and grant_fg = '1'
        and grant_dt between '2022-12-26' and '${data_ds}' 
)t1
join 
(
    select usr_id
        ,rgst_sec_chnl_nm
    from 
    (
        select usr_id
            ,rgst_sec_chnl_nm
            ,if_fin
            ,row_number() over (partition by usr_id order by if_fin desc) as rn 
        from 
        (
            select usr_id 
                ,rgst_sec_chnl_nm
                ,1 as if_fin
            from cdm.dwd_cu_rgst_fin_di 
            where ds <= '${data_ds}' 
                and usr_id is not null
            union all 
            select usr_id 
                ,rgst_sec_chnl_nm 
                ,0 as if_fin
            from cdm.dwd_cu_rgst_nonfin_di 
            where ds <= '${data_ds}' 
        )t 
    )t 
    where rn = 1
)t2 on t1.usr_id = t2.usr_id
cross join 
(
    select * from cdm.dim_pb_date_yf where date_dt = '${data_ds}'
)t3
where t1.grant_dt <= t3.date_dt
group by rgst_sec_chnl_nm
    ,rltv_sec_chnl_nm
;