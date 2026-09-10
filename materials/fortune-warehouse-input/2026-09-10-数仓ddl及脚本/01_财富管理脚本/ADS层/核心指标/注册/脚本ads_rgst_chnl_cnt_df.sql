-- DWS sql 
-- ******************************************************************** --
-- author: CI-zx-18519129105
-- create time: 2025/07/15 18:36:47 GMT+08:00
-- ******************************************************************** --
delete from rec.ads_rgst_chnl_cnt_df where ds = '${data_ds}'; 
insert into rec.ads_rgst_chnl_cnt_df 
select t2.date_dt as data_dt
    ,t3.fst_lvl_chnl_id
    ,t3.fst_lvl_chnl_nm  
    ,t3.sec_chnl_id
    ,t3.sec_chnl_nm 
    ,t3.thd_cls_chnl_id
    ,t3.thd_cls_chnl_nm
    ,sum(case when t1.rgst_dt = t2.date_dt then rgst_num else 0 end) as New_Rgst_Cnt_D                              --当日_新增注册用户数                
    ,sum(case when t1.rgst_dt between t2.last_7_dt and t2.date_dt then rgst_num else 0 end) as New_Rgst_Cnt_7D      --近7日_新增注册用户数                    
    ,sum(case when t1.rgst_dt between t2.cur_mth_begin and t2.date_dt then rgst_num else 0 end) as New_Rgst_Cnt_M   --当月_新增注册用户数                   
    ,sum(case when t1.rgst_dt between t2.year_begin and t2.date_dt then rgst_num else 0 end) as New_Rgst_Cnt_Y      --当年累计_新增注册用户数              
    ,sum(case when t1.rgst_dt <= t2.date_dt then rgst_num else 0 end) as New_Rgst_Cnt_A                             --历史累计_新增注册用户数 
    ,t3.fin_chnl_flg --金融渠道标识
    ,t3.chnl_type    --渠道类型
    ,t3.chnl_sub_nm  --报送渠道名称
    ,'${data_ds}' as ds
from 
(
    select *
    from cdm.dwd_cu_rgst_fin_di
    where ds <= '${data_ds}'
)t1
cross join (select * from cdm.dim_pb_date_yf where date_dt = '${data_ds}')t2 
left join 
(
    select Chnl_Id
        ,Fst_Chnl_Id as fst_lvl_chnl_id
        ,Fst_Chnl_Nm as fst_lvl_chnl_nm  
        ,sec_chnl_id
        ,sec_chnl_nm 
        ,Chnl_Id as thd_cls_chnl_id
        ,Chnl_Nm as thd_cls_chnl_nm
        ,fin_chnl_flg
        ,chnl_type   
        ,chnl_sub_nm 
    from cdm.dim_ch_chl_df 
    where ds = '${data_ds}'  
)t3 on t1.rgst_chnl_id  = t3.Chnl_Id 
group by t2.date_dt 
    ,t3.fst_lvl_chnl_id
    ,t3.fst_lvl_chnl_nm  
    ,t3.sec_chnl_id
    ,t3.sec_chnl_nm 
    ,t3.thd_cls_chnl_id
    ,t3.thd_cls_chnl_nm
    ,t3.fin_chnl_flg --金融渠道标识
    ,t3.chnl_type    --渠道类型
    ,t3.chnl_sub_nm  --报送渠道名称
;