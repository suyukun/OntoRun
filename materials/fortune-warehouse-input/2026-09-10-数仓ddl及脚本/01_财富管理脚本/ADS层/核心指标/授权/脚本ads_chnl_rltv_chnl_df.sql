-- DWS sql 
-- ******************************************************************** --
-- author: CI-zx-18519129105
-- create time: 2025/07/15 20:11:10 GMT+08:00
-- ******************************************************************** --
delete from rec.ads_chnl_rltv_chnl_df where ds = '${data_ds}';
insert into rec.ads_chnl_rltv_chnl_df 
select '${data_ds}' as data_dt
    ,chnl_cnt as rltv_chnl_cnt --关联渠道个数
    ,count(1) as rltv_chnl_nop --关联渠道人数
    ,'${data_ds}' as ds
from 
(
    select usr_id
        ,count(1) as chnl_cnt
    from 
    (
        select usr_id
            ,rltv_sec_chnl_nm
        from cdm.dwd_ch_usr_rltv_df 
        where ds = '${data_ds}'
            and create_dt between '2022-12-26' and '${data_ds}'
            and rltv_sec_chnl_nm in (
                 '中信银行信用卡'   
                ,'中信银行'
                ,'中信建投证券'
                ,'中信证券'
                ,'中信消费金融'
                ,'百信银行'
                ,'中信保诚人寿'
                ,'华夏基金'
                ,'中信建投期货'
                ,'中信期货'
                ,'中信信托'
                ,'信银理财'
                ,'中信优享+公众号'
            )
        group by usr_id
                ,rltv_sec_chnl_nm
    )t 
    group by usr_id
)t
group by chnl_cnt
;