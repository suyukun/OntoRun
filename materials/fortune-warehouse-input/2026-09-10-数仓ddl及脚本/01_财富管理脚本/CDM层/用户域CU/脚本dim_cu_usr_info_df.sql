CREATE LOCAL TEMPORARY TABLE IF NOT EXISTS dim_cu_usr_info_df_01
(    
     usr_id               varchar(128)
    ,rgst_dt              varchar(128)                                                  
    ,rgst_tm              varchar(128)                                                  
    ,usr_stat_fg          varchar(128)                                                        
    ,rgst_chnl_id         varchar(128)                                                       
    ,create_dt            varchar(128)                                                    
    ,rgst_type            varchar(128)                                                    
    ,rgst_act_id          varchar(128)                                                      
    ,usr_sex              varchar(128)                                                              
    ,birthday             date                                                             
    ,rgst_Prot_Ver        varchar(128)                                                              
    ,usr_phone_erpt       varchar(128)                                                         
    ,intl_chnl_id         varchar(128)                                                              
    ,mobile_score         varchar(128)                                                       
    ,allow_login_fg       varchar(128)                                                         
    ,first_enter_stat_cd  varchar(128)                                                              
)
WITH (  
    ORIENTATION = column
    ,colversion = 3.0           --指定列存储的版本
    ,enable_hstore_opt = TRUE   --启用HStore优化
    ,compression = middle 
)
DISTRIBUTE BY HASH (usr_id)   
;


insert into dim_cu_usr_info_df_01
select uid                                                                   as usr_id
    ,date(agreement_sign_time)                                               as rgst_dt
    ,agreement_sign_time                                                     as rgst_tm
    ,case when statu = '0' then '1' when statu = '1' then '0' else statu end as usr_stat_fg  
    ,agreement_sign_channel                                                  as rgst_chnl_id
    ,date(create_time)                                                       as create_dt
    ,register_type                                                           as rgst_type
    ,activity_type                                                           as rgst_act_id
    ,case when sex in (1,2) then sex end                                     as usr_sex              --性别1:男,2:女
    ,case when birthday not in ('0001-01-01') then date(birthday) end        as birthday           
    ,ext_lhj6                                                                as rgst_Prot_Ver           --用户协议版本
    ,phone                                                                   as usr_phone_erpt
    ,initial_channel_id                                                      as intl_chnl_id                             
    ,phone_credit                                                            as mobile_score
    ,allow_login                                                             as allow_login_fg
    ,is_first_in                                                             as first_enter_stat_cd
from ods.ods_usms_lm_user_t_df
where ds = '${data_ds}'   
    and date(agreement_sign_time) >= '2022-12-26'
    and date(agreement_sign_time) <= '${data_ds}'  
    and agreement_sign_channel is not null    
;  


CREATE LOCAL TEMPORARY TABLE IF NOT EXISTS dim_cu_usr_info_df_02
(    
     login_id               varchar(128)
    ,Evt_Trig_Dt            timestamp
)
WITH (  
    ORIENTATION = column
    ,colversion = 3.0           --指定列存储的版本
    ,enable_hstore_opt = TRUE   --启用HStore优化
    ,compression = middle 
)
DISTRIBUTE BY HASH (login_id)   
;


insert into dim_cu_usr_info_df_02
select login_id
    ,Evt_Trig_Dt
from cdm.dwd_lm_pv_df
where ds >= '2022-12-26' 
    and ds <= '${data_ds}'  
    and login_id is not null
    and EVENT = '$pageview'
group by login_id
    ,Evt_Trig_Dt
;


CREATE LOCAL TEMPORARY TABLE IF NOT EXISTS dim_cu_usr_info_df_03
(    
     usr_id               varchar(128)
    ,real_dt              varchar(128)                                     
    ,real_tm              varchar(128)                                     
    ,real_way             varchar(128)                           
    ,real_type            varchar(128)                            
    ,real_chnl_id         varchar(128)                               
    ,real_name_sm3        varchar(128)                                  
    ,birthday             varchar(128)                       
    ,usr_idcardno_erpt    varchar(128)                                     
    ,usr_idcardno_type    varchar(128)                                     
    ,fst_debt_card_fg     varchar(128)                                     
    ,fst_bind_crdt_fg     varchar(128)                                     
)
WITH (  
    ORIENTATION = column
    ,colversion = 3.0           --指定列存储的版本
    ,enable_hstore_opt = TRUE   --启用HStore优化
    ,compression = middle 
)
DISTRIBUTE BY HASH (usr_id)   
;


insert into dim_cu_usr_info_df_03
select id as usr_id
    ,date(auth_time)         as real_dt                   --实名认证日期
    ,auth_time               as real_tm              
    ,auth_way                as real_way
    ,auth_type               as real_type
    ,channel_id              as real_chnl_id
    ,real_name               as real_name_sm3  
    ,birthday                as birthday
    ,identity_card_no        as usr_idcardno_erpt           
    ,card_no_type            as usr_idcardno_type      
    ,first_citic_credit_card as fst_debt_card_fg          
    ,first_citic_bankcard    as fst_bind_crdt_fg                             
from ods.ods_usms_lml_account_t_df
where ds = '${data_ds}'   
    and identity_authentication = '1'  --实名标识
    and (date(auth_time) <= '${data_ds}' or auth_time is null)
;


CREATE LOCAL TEMPORARY TABLE IF NOT EXISTS dim_cu_usr_info_df_04
(    
     usr_id                  varchar(128)                
    ,rgst_dt                 varchar(128)                
    ,rgst_tm                 varchar(128)                
    ,usr_stat_fg             varchar(128)                
    ,rgst_enjy_fg            varchar(128)                  
    ,rgst_type               varchar(128)                       
    ,rgst_fin_chnl_ind       varchar(128)                       
    ,rgst_fst_chnl_id        varchar(128)                       
    ,rgst_fst_chnl_nm        varchar(128)                       
    ,rgst_sec_chnl_id        varchar(128)                       
    ,rgst_sec_chnl_nm        varchar(128)                       
    ,rgst_thd_chnl_id        varchar(128)                       
    ,rgst_thd_chnl_nm        varchar(128)                       
    ,rgst_chnl_id            varchar(128)                       
    ,rgst_chnl_nm            varchar(128)                       
    ,rgst_act_id             varchar(128)                       
    ,rgst_Prot_Ver           varchar(128)                       
    ,usr_sex                 varchar(128)                       
    ,usr_phone_erpt          varchar(128)                       
    ,intl_chnl_id            varchar(128)                       
    ,mobile_score            varchar(128)                       
    ,allow_login_fg          varchar(128)                       
    ,first_enter_stat_cd     varchar(128)  
    ,birthday                varchar(128)                                                                         
)
WITH (  
    ORIENTATION = column
    ,colversion = 3.0           --指定列存储的版本
    ,enable_hstore_opt = TRUE   --启用HStore优化
    ,compression = middle 
)
DISTRIBUTE BY HASH (usr_id)   
;


insert into dim_cu_usr_info_df_04
select 
     t1.usr_id                                                     as usr_id                    --用户ID
    ,t1.rgst_dt                                                    as rgst_dt                   --注册日期
    ,t1.rgst_tm                                                    as rgst_tm                   --注册时间
    ,t1.usr_stat_fg                                                as usr_stat_fg               --用户状态：1有效,0注销
    ,case when t1.create_dt < '2022-12-26' then '1' else '0'  end  as rgst_enjy_fg              --是否优享升级客户：1是0否
    ,case 
              when t1.create_dt >= '2022-12-26' and t1.rgst_type = 'syncChannel' then '0' 
              when t1.create_dt >= '2022-12-26' then '1' 
              when t1.create_dt < '2022-12-26' and t3.login_id is null then '0' 
              when t1.create_dt < '2022-12-26' and t3.login_id is not null then '1' 
    else '2' end                                                   as rgst_type                 --注册类型：0（子公司）同步注册1登录注册
    ,t2.Fin_Chnl_Flg                                               as rgst_fin_chnl_ind        --注册金融渠道标识
    ,t2.Fst_Chnl_Id                                                as rgst_fst_chnl_id          --注册一级渠道ID
    ,t2.Fst_Chnl_Nm                                                as rgst_fst_chnl_nm          --注册一级渠道名称
    ,t2.Sec_Chnl_Id                                                as rgst_sec_chnl_id          --注册二级渠道ID
    ,t2.Sec_Chnl_Nm                                                as rgst_sec_chnl_nm          --注册二级渠道名称
    ,t2.Thd_Chnl_Id                                                as rgst_thd_chnl_id          --注册三级渠道ID
    ,t2.Thd_Chnl_Nm                                                as rgst_thd_chnl_nm          --注册三级渠道名称
    ,t1.rgst_chnl_id                                               as rgst_chnl_id              --注册渠道ID 
    ,t2.Chnl_Nm                                                    as rgst_chnl_nm              --注册渠道名称
    ,t1.rgst_act_id                                                as rgst_act_id               --注册活动ID
    ,t1.rgst_Prot_Ver                                              as rgst_Prot_Ver             --注册协议版本
    ,t1.usr_sex                                                    as usr_sex                   --用户性别:1:男,2:女
    ,t1.usr_phone_erpt                                             as usr_phone_erpt            --用户手机号加密（aes）
    ,t1.intl_chnl_id                                               as intl_chnl_id              --用户初始渠道id
    ,t1.mobile_score                                               as mobile_score              --手机号信誉评分
    ,t1.allow_login_fg                                             as allow_login_fg            --允许登录标志
    ,t1.first_enter_stat_cd                                        as first_enter_stat_cd       --首次进入系统状态代码
    ,birthday
from dim_cu_usr_info_df_01 t1
left join (select * from cdm.dim_ch_chl_df where ds = '${data_ds}')t2 on t1.rgst_chnl_id  = t2.Chnl_Id
left join dim_cu_usr_info_df_02 t3 on t1.usr_id = t3.login_id and t1.rgst_dt = t3.Evt_Trig_Dt
;



DELETE FROM cdm.dim_cu_usr_info_df WHERE ds='${data_ds}';
insert into cdm.dim_cu_usr_info_df 
select 
     t1.usr_id                                                     as usr_id                    --用户ID
    ,rgst_dt                   --注册日期
    ,rgst_tm                   --注册时间
    ,usr_stat_fg               --用户状态：1有效,0注销
    ,rgst_enjy_fg              --是否优享升级客户：1是0否
    ,rgst_type                 --注册类型：0（子公司）同步注册1登录注册
    ,rgst_fin_chnl_ind        --注册金融渠道标识
    ,rgst_fst_chnl_id          --注册一级渠道ID
    ,rgst_fst_chnl_nm          --注册一级渠道名称
    ,rgst_sec_chnl_id          --注册二级渠道ID
    ,rgst_sec_chnl_nm          --注册二级渠道名称
    ,rgst_thd_chnl_id          --注册三级渠道ID
    ,rgst_thd_chnl_nm          --注册三级渠道名称
    ,rgst_chnl_id              --注册渠道ID 
    ,rgst_chnl_nm              --注册渠道名称
    ,rgst_act_id               --注册活动ID
    ,rgst_Prot_Ver             --注册协议版本
    ,case when t4.Usr_Id is not null then '1' else '0' end         as real_fg                   --是否实名：1是0否
    ,real_dt                   --实名认证日期
    ,real_tm                   --实名认证时间
    ,real_way                  --实名认证方式：0子公司同步,1银行卡四要素
    ,real_type                 --实名认证类型：0子公司同步,1财富广场
    ,real_chnl_id              --实名渠道ID
    ,real_name_sm3             --用户姓名加密（sm3）
    ,usr_sex                   --用户性别:1:男,2:女
    ,COALESCE(t1.birthday,t4.birthday)                             as usr_birthday              --用户生日
    ,usr_phone_erpt            --用户手机号加密（aes）
    ,usr_idcardno_erpt         --身份证号加密（aes）
    ,usr_idcardno_type         --证件类型：01-居民身份证;02-军官证;03-护照;04-回乡证(港澳);05-台胞证;06-警官证;07-士兵证;99-其它证件
    ,fst_debt_card_fg          --首次绑定借记卡
    ,fst_bind_crdt_fg          --首次绑定信用卡
    ,intl_chnl_id              --用户初始渠道id
    ,mobile_score              --手机号信誉评分
    ,allow_login_fg            --允许登录标志
    ,first_enter_stat_cd       --首次进入系统状态代码
    ,'${data_ds}' as ds
from dim_cu_usr_info_df_04 t1
left join dim_cu_usr_info_df_03 t4 on t1.usr_id = t4.usr_id
;
