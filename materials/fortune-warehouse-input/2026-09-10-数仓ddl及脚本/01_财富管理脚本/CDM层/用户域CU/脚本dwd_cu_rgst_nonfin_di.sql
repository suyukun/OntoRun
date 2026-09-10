-- DWS sql 
-- ******************************************************************** --
-- author: CI-zx-18519129105
-- create time: 2025/07/15 10:42:16 GMT+08:00
-- ******************************************************************** --
/**
--历史
delete from cdm.dwd_cu_rgst_nonfin_di where ds <= '2025-07-20';
insert into cdm.dwd_cu_rgst_nonfin_di 
select usr_id
    ,date(rgst_dt) as rgst_dt
    ,date(rgst_dt) as rgst_dt_src
    ,cast(rgst_tm as timestamp) as rgst_tm_src
    ,rgst_enjy_fg
    ,rgst_type 
    ,rgst_chnl_id    
    ,rgst_sec_chnl_nm
    ,rgst_act_id 
    ,1 as rgst_num
    ,rgst_dt as ds
from cdm.dim_cu_usr_info_df
where ds = '2025-07-20'
    and rgst_sec_chnl_nm in ('麦当劳','中信书院')
;
**/



--增量
delete from cdm.dwd_cu_rgst_nonfin_di where ds = '${data_ds}';
insert into cdm.dwd_cu_rgst_nonfin_di
select t1.usr_id
    ,'${data_ds}' as rgst_dt
    ,date(rgst_dt) as rgst_dt_src
    ,cast(rgst_tm as timestamp) as rgst_tm_src
    ,rgst_enjy_fg
    ,rgst_type 
    ,rgst_chnl_id    
    ,rgst_sec_chnl_nm
    ,rgst_act_id
    ,1 as rgst_num 
    ,'${data_ds}' as ds
from 
(
    select usr_id
        ,rgst_dt
        ,rgst_tm
        ,rgst_enjy_fg
        ,rgst_type 
        ,rgst_chnl_id    
        ,rgst_sec_chnl_nm
        ,rgst_act_id 
    from cdm.dim_cu_usr_info_df
    where ds = '${data_ds}'
        and rgst_sec_chnl_nm in ('麦当劳','中信书院')
)t1 
left join 
(
    select usr_id 
    from cdm.dwd_cu_rgst_nonfin_di 
    where ds < '${data_ds}'
)t2 on t1.usr_id = t2.usr_id 
where t2.usr_id is null
;
