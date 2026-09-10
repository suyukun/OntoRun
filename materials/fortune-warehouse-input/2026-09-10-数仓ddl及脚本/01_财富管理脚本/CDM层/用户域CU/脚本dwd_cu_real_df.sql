-- DWS sql 
-- ******************************************************************** --
-- author: CI-zx-18519129105
-- create time: 2025/07/15 14:35:42 GMT+08:00
-- ******************************************************************** --
delete from cdm.dwd_cu_real_df where ds = '${data_ds}';
insert into cdm.dwd_cu_real_df 
select t1.usr_id as usr_id
    ,real_dt     
    ,real_tm     
    ,real_way    
    ,real_type   
    ,real_chnl_id
    ,rgst_chnl_id     
    ,rgst_sec_chnl_nm 
    ,rgst_dt
    ,'${data_ds}' as ds
from 
(
    select usr_id
        ,real_dt     
        ,real_tm     
        ,real_way    
        ,real_type   
        ,real_chnl_id
    from cdm.dim_cu_usr_info_df 
    where ds = '${data_ds}'
        and real_fg = 1
)t1 
left join 
(
    select usr_id
        ,rgst_chnl_id
        ,rgst_sec_chnl_nm
        ,rgst_dt
    from 
    (
        select usr_id
            ,rgst_chnl_id
            ,rgst_sec_chnl_nm
            ,if_fin
            ,rgst_dt
            ,row_number() over (partition by usr_id order by if_fin desc) as rn 
        from 
        (
            select usr_id 
                ,rgst_chnl_id     
                ,rgst_sec_chnl_nm
                ,rgst_dt
                ,1 as if_fin
            from cdm.dwd_cu_rgst_fin_di 
            where ds <= '${data_ds}'
                and usr_id is not null
            union all 
            select usr_id 
                ,rgst_chnl_id     
                ,rgst_sec_chnl_nm 
                ,rgst_dt
                ,0 as if_fin
            from cdm.dwd_cu_rgst_nonfin_di 
            where ds <= '${data_ds}'
        )t 
    )t 
    where rn = 1
)t2 on t1.usr_id = t2.usr_id
;