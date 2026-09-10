-- DWS sql 
-- ******************************************************************** --
-- author: CI-zx-18610914036
-- create time: 2024/11/14 16:20:25 GMT+08:00
-- ******************************************************************** --
DELETE FROM cdm.dwd_ch_usr_rltv_df WHERE ds='${data_ds}';
insert into cdm.dwd_ch_usr_rltv_df
SELECT
     t1.usr_id                                                      as usr_id                          --用户ID
    ,t1.channel_id                                                  as rltv_chnl_id                    --渠道ID
    ,date(t1.create_time)                                           as create_dt                       --关联创建日期
    ,t1.create_time                                                 as create_tm                       --关联创建时间
    ,t1.update_time                                                 as update_tm                       --关联修改时间
    ,t2.fst_chnl_id                                                 as rltv_fst_chnl_id                --关联一级渠道id
    ,t2.fst_chnl_nm                                                 as rltv_fst_chnl_nm                --关联一级渠道名称
    ,t2.sec_chnl_id                                                 as rltv_sec_chnl_id                --关联二级渠道id
    ,t2.sec_chnl_nm                                                 as rltv_sec_chnl_nm                --关联二级渠道名称 
    ,t2.Thd_Chnl_Id                                                 as rltv_thd_chnl_id                --关联三级渠道ID
    ,t2.Thd_Chnl_Nm                                                 as rltv_thd_chnl_nm                --关联三级渠道名称
    ,t2.Chnl_Nm                                                     as rltv_chnl_nm                    --关联渠道名称
    ,t2.is_sec_oth_chnl                                             as rltv_is_sec_oth_chnl            --关联是否二级其他渠道
    ,t2.is_fst_oth_chnl                                             as rltv_is_fst_oth_chnl            --关联是否一级其他渠道
    ,date(t1.grant_time)                                            as grant_dt                        --授权日期
    ,t1.grant_time                                                  as grant_tm                        --授权时间
    ,t1.auth_result                                                 as grant_result                    --授权结果：1授权3无账户4拒绝授权0未授权
    ,case when t1.auth_result = '1' then '1' else '0' end           as grant_fg                        --是否授权：1是0否
    ,t1.usr_status                                                  as rltv_usr_status                 --用户关联状态: 0正常1已解绑2已删除34历史数据
    ,t2.Fin_Chnl_Flg                                                as rltv_fin_chnl_ind	           --关联金融渠道标识
	,'${data_ds}' as ds
FROM 
(
    SELECT 
         uid as usr_id                                                   
        ,channel_id                                              
        ,grant_time                                              
        ,create_time                                             
        ,update_time                                             
        ,grant_status as auth_result 
        ,status       as usr_status 
		,ds
    FROM ods.ods_usms_lm_channel_user_t_df 	
    where ds = '${data_ds}'
)t1
left join 
( 
    select * 
    from cdm.dim_ch_chl_df 
    where ds = '${data_ds}'
)t2 on t1.channel_id = t2.Chnl_Id
join 
(
    select uid  as usr_id
    from ods.ods_usms_lm_user_t_df
    where ds = '${data_ds}' 
        and date(agreement_sign_time) >= '2022-12-26'
        and date(agreement_sign_time) <= '${data_ds}'
        and agreement_sign_channel is not null 
    group by uid                                        
)t3 on t1.usr_id = t3.usr_id
;