-- DWS sql 
-- ******************************************************************** --
-- author: CI-zx-18519129105
-- create time: 2025/07/15 19:22:16 GMT+08:00
-- ******************************************************************** --
delete from rec.ads_chnl_real_user_df where ds = '${data_ds}';
insert into rec.ads_chnl_real_user_df
select date_dt as data_dt     
    ,real_type        
    ,fst_chnl_id      
    ,fst_chnl_nm      
    ,sec_chnl_id      
    ,sec_chnl_nm       
    ,chnl_id
    ,chnl_nm
    ,chnl_sub_nm     
    ,real_today       
    ,real_last7d      
    ,real_last30d     
    ,real_curmth      
    ,real_curyear     
    ,real_all         
    ,real_rgst_curyear
    ,'${data_ds}' as ds  
from 
(
    SELECT t2.date_dt  --1.数据日期
        ,real_type     --2.实名类型
        ,fst_chnl_id   --一级渠道ID
        ,fst_chnl_nm   --一级渠道名称
        ,sec_chnl_id   --二级渠道ID
        ,sec_chnl_nm   --二级渠道名称
        ,chnl_id
        ,chnl_nm
        ,chnl_sub_nm  --报送渠道名称
        ,count(distinct case when t1.real_dt = t2.date_dt then t1.usr_id end) as real_today    --9.当日_实名
        ,count(distinct case when t1.real_dt >= t2.last_7_dt then t1.usr_id end) as real_last7d    --10.近7日_实名
        ,count(distinct case when t1.real_dt >= t2.last_30_dt then t1.usr_id end) as real_last30d    --11.近30日_实名
        ,count(distinct case when t1.real_dt >= t2.cur_mth_begin then t1.usr_id end) as real_curmth    --12.当月_实名
        ,count(distinct case when t1.real_dt >= t2.quar_begin then t1.usr_id end) as real_curquar    --13.当季_实名
        ,count(distinct case when t1.real_dt >= t2.half_year_begin then t1.usr_id end) as real_halfyear    --14.本半年_实名
        ,count(distinct case when t1.real_dt >= t2.year_begin then t1.usr_id end) as real_curyear    --15.当年累计_实名
        ,count(distinct t1.usr_id) as real_all    --16.历史累计_实名
        ,count(case when t1.real_dt >= t2.year_begin and t1.rgst_dt >= t2.year_begin then t1.usr_id end) as real_rgst_curyear    --1720241204新增.当年注册&当年实名
    FROM 
    (
        select usr_id
            ,real_dt
            ,real_type 
            ,rgst_chnl_id
            ,rgst_dt
        from cdm.dwd_cu_real_df
        where ds = '${data_ds}' 
    )t1 
    cross JOIN (select * from cdm.dim_pb_date_yf where date_dt = '${data_ds}')t2 
    left join 
    (
        select chnl_id
            ,chnl_nm
            ,chnl_sub_nm  
            ,fst_chnl_id
            ,fst_chnl_nm
            ,sec_chnl_id
            ,sec_chnl_nm
        from cdm.dim_ch_chl_df 
        where ds = '${data_ds}'
    )t3 on t1.rgst_chnl_id  = t3.Chnl_Id
    GROUP BY t2.date_dt 
        ,real_type     
        ,fst_chnl_id   
        ,fst_chnl_nm   
        ,sec_chnl_id   
        ,sec_chnl_nm 
        ,chnl_id
        ,chnl_nm  
        ,chnl_sub_nm  
)t 
;