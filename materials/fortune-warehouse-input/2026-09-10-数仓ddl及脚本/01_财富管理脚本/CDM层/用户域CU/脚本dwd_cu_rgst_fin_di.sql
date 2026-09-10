-- DWS sql 
-- ******************************************************************** --
-- author: CI-zx-18519129105
-- create time: 2025/07/15 09:38:21 GMT+08:00
-- ******************************************************************** --
delete from cdm.dwd_cu_rgst_fin_di where ds = '${data_ds}';
insert into cdm.dwd_cu_rgst_fin_di 
select t1.usr_id
    ,'${data_ds}' as rgst_dt
    ,rgst_dt as rgst_dt_src
    ,rgst_tm as rgst_tm_src
    ,rgst_enjy_fg
    ,rgst_type 
    ,rgst_chnl_id    
    ,rgst_sec_chnl_nm
    ,rgst_act_id 
    ,0 as if_act 
    ,1 as rgst_num
    ,null as nonfin_rgst_dt         
    ,null as nonfin_rgst_chnl_id    
    ,null as nonfin_rgst_sec_chnl_nm
    ,'${data_ds}' as ds
from 
(
    select usr_id
        ,date(rgst_dt) as rgst_dt
        ,cast(rgst_tm as timestamp) as rgst_tm
        ,rgst_enjy_fg
        ,rgst_type 
        ,rgst_chnl_id    
        ,rgst_sec_chnl_nm
        ,rgst_act_id 
    from cdm.dim_cu_usr_info_df
    where ds = '${data_ds}'
        and rgst_sec_chnl_nm not in ('麦当劳','中信书院')
)t1 
left join 
(
    select usr_id 
    from cdm.dwd_cu_rgst_fin_di 
    where ds < '${data_ds}'
        and if_act = 0
)t2 on t1.usr_id = t2.usr_id 
where t2.usr_id is null
union all 
select t1.usr_id
    ,'${data_ds}' as rgst_dt
    ,actv_dt as rgst_dt_src           
    ,actv_tm as rgst_tm_src
    ,rgst_enjy_fg
    ,rgst_type
    ,actv_chnl_id as rgst_chnl_id
    ,actv_sec_chnl_nm as rgst_sec_chnl_nm
    ,rgst_act_id
    ,1 as if_act
    ,1 as rgst_num
    ,rgst_dt as nonfin_rgst_dt
    ,rgst_chnl_id as nonfin_rgst_chnl_id     
    ,rgst_sec_chnl_nm as nonfin_rgst_sec_chnl_nm 
    ,'${data_ds}' as ds
from 
(
    select t1.usr_id          
        ,actv_dt              
        ,actv_tm 
        ,actv_chnl_id 
        ,actv_sec_chnl_nm 
    from 
    (
        select usr_id          
            ,actv_dt              
            ,actv_tm 
            ,actv_chnl_id 
            ,actv_sec_chnl_nm 
        from 
        (
            select *,row_number() over (partition by usr_id order by actv_dt asc,actv_tag asc) as rn   --如果关联渠道和关注公众号有usr_id重复的，取最早的一条
            from cdm.dwd_cu_actv_df
            where ds = '${data_ds}'
                and actv_dt <= '${data_ds}'
                and ((((actv_dt <= '2024-06-30' and actv_sec_chnl_nm <> '中信优享+公众号') or actv_dt >= '2024-07-01') and actv_tag = '1')  -- 关联渠道：去掉6月的公众号关联渠道，从0701开始算
                or (actv_tag = '2' and actv_dt >= '2024-07-09'))   --企微+公众号小程序关注：从0709上线开始算
        )t 
        where rn = 1
    )t1 
    left join 
    (
        select usr_id 
        from cdm.dwd_cu_rgst_fin_di 
        where ds < '${data_ds}'
            and if_act = 1
    )t3 on t1.usr_id = t3.usr_id 
    where t3.usr_id is null
)t1 
left join 
(
    select usr_id
        ,rgst_enjy_fg
        ,rgst_type
        ,rgst_act_id
        ,rgst_chnl_id     
        ,rgst_sec_chnl_nm 
        ,rgst_dt
    from cdm.dim_cu_usr_info_df
    where ds = '${data_ds}'
        and rgst_sec_chnl_nm in ('麦当劳','中信书院')
)t2 on t1.usr_id = t2.usr_id
;




