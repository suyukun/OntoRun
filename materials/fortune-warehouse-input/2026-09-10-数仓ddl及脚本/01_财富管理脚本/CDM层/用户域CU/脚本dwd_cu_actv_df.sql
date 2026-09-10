-- DWS sql 
-- ******************************************************************** --
-- author: CI-zx-18519129105
-- create time: 2025/07/14 15:38:25 GMT+08:00
-- ******************************************************************** --
DELETE FROM cdm.dwd_cu_actv_df WHERE ds = '${data_ds}';

CREATE LOCAL TEMPORARY TABLE IF NOT EXISTS dwd_cu_actv_df_mid_01
(    
     usr_id             varchar(128)
    ,rgst_tm            timestamp
    ,rgst_dt            date   
    ,rgst_chnl_id       varchar(128)
    ,rgst_enjy_fg       int
    ,rgst_sec_chnl_nm   varchar(128)                                  
)
WITH (  
    ORIENTATION = column
    ,colversion = 3.0           --指定列存储的版本
    ,enable_hstore_opt = TRUE   --启用HStore优化
    ,compression = middle 
)
DISTRIBUTE BY HASH (usr_id)   
;


insert into dwd_cu_actv_df_mid_01
select usr_id
    ,cast(rgst_tm as timestamp) as rgst_tm 
    ,date(rgst_dt) as rgst_dt  
    ,rgst_chnl_id
    ,cast(rgst_enjy_fg as int) as rgst_enjy_fg
    ,rgst_sec_chnl_nm    
from cdm.dim_cu_usr_info_df
where ds = '${data_ds}'
    and rgst_sec_chnl_nm in ('麦当劳','中信书院')
;



CREATE LOCAL TEMPORARY TABLE IF NOT EXISTS dwd_cu_actv_df_mid_02
(    
     usr_id             varchar(128)
    ,actv_date          date
    ,actv_time          timestamp 
    ,actv_Chnl_Id       varchar(128)                     
    ,actv_Chnl_Nm       varchar(128)                       
    ,actv_Sec_Chnl_Id   varchar(128)                         
    ,actv_Sec_Chnl_Nm   varchar(128)                         
    ,actv_chnl_sub_nm   varchar(128)                                                           
)
WITH (  
    ORIENTATION = column
    ,colversion = 3.0           --指定列存储的版本
    ,enable_hstore_opt = TRUE   --启用HStore优化
    ,compression = middle 
)
DISTRIBUTE BY HASH (usr_id)   
;



insert into dwd_cu_actv_df_mid_02
select t1.usr_id as usr_id
    ,date(t1.create_time) as actv_date
    ,t1.create_time as actv_time
    ,t1.channel_id  as actv_Chnl_Id
    ,t2.Chnl_Nm     as actv_Chnl_Nm  
    ,t2.Sec_Chnl_Id as actv_Sec_Chnl_Id
    ,t2.Sec_Chnl_Nm as actv_Sec_Chnl_Nm
    ,t2.chnl_sub_nm as actv_chnl_sub_nm
from 
(
    select uid as usr_id
        ,channel_id
        ,create_time
    from ods.ods_usms_lm_channel_user_t_df
    where ds = '${data_ds}'
        and date(create_time) >= '2022-12-26'
        and date(create_time) <= '${data_ds}'
)t1 
join 
(
    select Chnl_Id
        ,Sec_Chnl_Id
        ,Sec_Chnl_Nm
        ,Chnl_Nm   
        ,chnl_sub_nm 
    from cdm.dim_ch_chl_df 
    where ds = '${data_ds}'
        and Sec_Chnl_Nm in 
        (
             '中信保诚人寿'
            ,'中信优享+公众号'
            ,'中信消费金融'
            ,'中信建投证券'
            ,'中信银行信用卡'
            ,'中信银行'
            ,'百信银行'
            ,'华夏基金'
            ,'中信建投期货'
            ,'中信证券'
            ,'中信信托'
            ,'信银理财'
            ,'中信期货'
        )
)t2 on t1.channel_id  = t2.Chnl_Id
;



insert into cdm.dwd_cu_actv_df 
select usr_id                                                   as usr_id                    --用户ID
    ,date(actv_time)                                            as actv_dt                   --激活日期 
    ,cast(actv_time as TIMESTAMP)                               as actv_tm                   --激活时间 
    ,actv_Chnl_Id                                               as actv_chnl_id              --激活渠道ID
    ,actv_Chnl_Nm                                               as actv_chnl_nm              --激活渠道名称
    ,actv_Sec_Chnl_Id                                           as actv_sec_chnl_id          --激活二级渠道ID
    ,actv_Sec_Chnl_Nm                                           as actv_sec_chnl_nm          --激活二级渠道名称
    ,actv_chnl_sub_nm                                           as actv_chnl_sub_nm          --激活报送渠道
    ,'1'                                                        as actv_tag                  --激活类型(1-关联渠道2-企微3-公众号)
    ,actv_date_src 
    ,rgst_dt
    ,rgst_sec_chnl_nm              
    ,rgst_enjy_fg 
    ,'${data_ds}' as ds
from 
(
    select usr_id
        ,actv_Chnl_Id
        ,actv_Chnl_Nm  
        ,actv_Sec_Chnl_Id
        ,actv_Sec_Chnl_Nm
        ,actv_chnl_sub_nm
        ,rgst_dt 
        ,rgst_sec_chnl_nm 
        ,rgst_enjy_fg
        ,case 
        when actv_date <= '2024-06-30' and substr(cast(actv_time as varchar),9,2) = '31' then concat('2024-06-30',substr(cast(actv_time as varchar),11,11))
        when actv_date <= '2024-06-30' and cast(substr(cast(actv_time as varchar),9,2) as int) <= 30 then concat('2024-06-',substr(cast(actv_time as varchar),9,2),substr(cast(actv_time as varchar),11,11)) 
        else cast(actv_time as varchar) end as actv_time
        ,actv_date as actv_date_src
    from 
    (
        select t1.usr_id as usr_id
            ,t1.rgst_tm
            ,t1.rgst_dt
            ,t1.rgst_enjy_fg
            ,t1.rgst_sec_chnl_nm 
            ,t3.actv_time
            ,t3.actv_date
            ,t3.actv_Chnl_Id
            ,t3.actv_Chnl_Nm  
            ,t3.actv_Sec_Chnl_Id
            ,t3.actv_Sec_Chnl_Nm
            ,t3.actv_chnl_sub_nm
            ,row_number() over (partition by t1.usr_id,t1.rgst_dt,t1.rgst_sec_chnl_nm order by t3.actv_date,t3.actv_Sec_Chnl_Id,t3.actv_Chnl_Id asc) as rn
        from dwd_cu_actv_df_mid_01 t1
        join dwd_cu_actv_df_mid_02 t3 on t1.usr_id = t3.usr_id and t3.actv_date >= t1.rgst_dt  
    )t 
    where rn = 1
)t 
union all 
select usr_id                                                   as usr_id                    --用户ID
    ,actv_date                                                  as actv_dt                   --激活时间 
    ,cast(actv_date as timestamp)                               as actv_tm                   --激活日期
    ,'e5abe0293b434e4c86ee406a371509a5'                         as actv_chnl_id              --激活渠道ID
    ,'财富广场-公众号'                                           as actv_chnl_nm              --激活渠道名称
    ,'8ABCAB393E559DD5F60B5C6AA93C589F'                         as actv_sec_chnl_id          --激活二级渠道ID
    ,'中信优享+公众号'                                           as actv_sec_chnl_nm          --激活二级渠道名称
    ,'财富广场自营渠道'                                          as actv_chnl_sub_nm          --激活报送渠道   
    ,'2'                                                        as actv_tag                  --激活类型(1-关联渠道2-企微3-公众号)
    ,actv_date as actv_date_src
    ,rgst_dt               
    ,rgst_sec_chnl_nm   
    ,'0' as rgst_enjy_fg  --同步注册     
    ,'${data_ds}' as ds    
from 
(
    select usr_id
        ,rgst_dt
        ,rgst_sec_chnl_nm
        ,actv_date
    from
    (
        select t1.usr_id
            ,t1.rgst_dt
            ,t1.rgst_sec_chnl_nm
            ,min(actv_date) as actv_date
        from dwd_cu_actv_df_mid_01 t1 
        join 
        (
            select user_id as usr_id
                ,date(create_time) as actv_date
            from ods.ods_lm_user_wechat_t_df
            where ds = '${data_ds}'
                and user_id is not null
        )t2 on t1.usr_id = t2.usr_id
        where t2.actv_date >= t1.rgst_dt
        group by t1.usr_id
            ,t1.rgst_dt
            ,t1.rgst_sec_chnl_nm
    )t 
    where actv_date >= '2024-07-09' and actv_date <= '${data_ds}' --从20240709开始加入到注册里，历史不追
)t 
;