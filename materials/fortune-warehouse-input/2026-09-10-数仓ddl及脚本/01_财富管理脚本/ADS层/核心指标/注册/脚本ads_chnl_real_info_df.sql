-- DWS sql 
-- ******************************************************************** --
-- author: CI-zx-18519129105
-- create time: 2025/11/04 15:51:12 GMT+08:00
-- ******************************************************************** --
delete from rec.ads_chnl_real_info_df where ds = '${data_ds}';
insert into rec.ads_chnl_real_info_df
select usr_id
    ,min(real_time) as fst_real_tm
    ,min(case when real_info_from = 0 then real_time end) as cfgc_real_tm
    ,min(case when real_info_from = 1 then real_time end) as sub_comp_real_tm
    ,'${data_ds}'  as ds
from 
(
    select t2.uid as usr_id 
        ,update_time as real_time
        ,1 as real_info_from
    from 
    (
        select user_id
            ,channel_id
            ,min(update_time) as update_time
        from ods.ods_usms_sub_company_real_name_sync_record_df
        where ds = '${data_ds}'
        group by user_id
            ,channel_id
    )t1 
    join 
    (
        SELECT uid
            ,user_id
            ,channel_id
        FROM ods.ods_usms_lm_channel_user_t_df
        WHERE ds = '${data_ds}'
        group by uid
            ,user_id
            ,channel_id
    )t2 on t1.user_id = t2.user_id and t1.channel_id = t2.channel_id
    union all 
    select usr_id
        ,real_tm as real_time
        ,0 as real_info_from
    from cdm.dwd_cu_real_df
    where ds = '${data_ds}'
)t 
group by usr_id
;