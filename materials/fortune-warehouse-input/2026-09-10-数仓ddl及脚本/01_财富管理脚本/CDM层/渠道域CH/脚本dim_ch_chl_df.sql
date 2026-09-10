-- DWS sql 
-- ******************************************************************** --
-- author: CI-zx-18519129105
-- create time: 2024/10/24 16:29:53 GMT+08:00
-- ******************************************************************** --


CREATE LOCAL TEMPORARY TABLE IF NOT EXISTS  dim_ch_chl_df_tmp 
(    chnl_id               varchar(128)         NULL
    ,chnl_nm               varchar(128)         NULL
    ,chnl_stat             varchar(128)         NULL
    ,chnl_dc               varchar(128)         NULL
    ,thd_chnl_id           varchar(128)         NULL
    ,thd_chnl_nm           varchar(128)         NULL
    ,thd_chnl_stat         varchar(128)         NULL
    ,thd_chnl_dc           varchar(128)         NULL
    ,sec_chnl_id           varchar(128)         NULL
    ,sec_chnl_nm           varchar(128)         NULL
    ,sec_chnl_stat         varchar(128)         NULL
    ,sec_chnl_dc           varchar(128)         NULL
    ,fst_chnl_id           varchar(128)         NULL
    ,fst_chnl_nm           varchar(128)         NULL
    ,fst_chnl_stat         varchar(128)         NULL
    ,fst_chnl_dc           varchar(128)         NULL
    ,chnl_lvl              varchar(128)         NULL
    ,fin_chnl_flg          varchar(128)         NULL
    ,auto_auth_fg          varchar(128)         NULL
    ,wallet_fg             varchar(128)         NULL
    ,chnl_effect_dt        varchar(10)          NULL
    ,effect_tm             timestamp            NULL
    ,is_sec_oth_chnl       varchar(128)         NULL
    ,is_fst_oth_chnl       varchar(128)         NULL
    ,chnl_type             varchar(128)         NULL
    ,chnl_sub_nm           varchar(128)         NULL
)
ON COMMIT DELETE ROWS
DISTRIBUTE BY HASH ( Chnl_Id )  
;


insert into dim_ch_chl_df_tmp 
select 
     T1.channel_id                                                                       as Chnl_Id            --四级渠道ID
    ,T1.name                                                                             as Chnl_Nm            --四级渠道名称
    ,T1.status                                                                           as Chnl_Stat          --四级状态标识
    ,T1.description                                                                      as Chnl_Dc            --四级渠道描述
    ,T2.group_id                                                                         as  Thd_Chnl_Id       --三级渠道ID
    ,T2.group_name                                                                       as  Thd_Chnl_Nm       --三级渠道名称
    ,T2.status                                                                           as  Thd_Chnl_Stat     --三级渠道状态
    ,T2.description                                                                      as  Thd_Chnl_Dc       --三级渠道描述
    ,case when T1.group_id in ('71415A31B80DB390E2230616B51A7A0F','8f0628086566467f839c8b24b12a5d7c','25015275d17544f6960985baed828073','5a838c5cf99b45099462683925b0ec09','A9614BC5ECEAECF8A3E92CFD682972F3') then '71415A31B80DB390E2230616B51A7A0F'  --中信保诚人寿 
            when T1.group_id in ('2391B7E29D34101420BE8DFA761CF13E','b0614390abd14eb59fbfada66b9dc95d','3c14a9e6675a4a5eb12c94101c9af710','B7821F2131772023E4E0261890021C32','a9fe5731d9b04dc3b6216609619274c2','efe49a614c8a43e2ba675429dacaa236')    then '2391B7E29D34101420BE8DFA761CF13E'    --中信银行
            when T1.group_id in ('B6B16FE228BB0C8BCDAD086B949532C4','27C2824306061CAF77E413C7B4DC0555')   then 'B6B16FE228BB0C8BCDAD086B949532C4'    --中信银行信用卡
            when T1.group_id = 'e233a527bd634869bc8293b7d21bd996'   then 'e233a527bd634869bc8293b7d21bd996'    --百信银行
            when T1.group_id in ('7922FC9C4C0C7A0BBD0943F32AFE4B35','9e976fd27b0c4f7a9853cca4b1659757')   then '7922FC9C4C0C7A0BBD0943F32AFE4B35'    --中信证券
            when T1.group_id = '30A0CC386C3A20A2B6654074349338F1'   then '30A0CC386C3A20A2B6654074349338F1'    --华夏基金
            when T1.group_id = '367b6d493f924546a6da01b4f6a29797'   then '367b6d493f924546a6da01b4f6a29797'    --中信期货
            when T1.group_id in ('af38efab659c4be1aab25d38355593cc','3fb6e7b33ab440e0976566397e72481a')   then 'af38efab659c4be1aab25d38355593cc'    --中信建投证券
            when T1.group_id = 'dcdcea4f589b4c1fa0b21ea0ac1260b8'   then 'dcdcea4f589b4c1fa0b21ea0ac1260b8'    --中信信托
            when T1.group_id in ('b223db350b8044a3a463de8f612912d3','07301c99c76a42c9876e671be6a90a1a')   then 'b223db350b8044a3a463de8f612912d3'    --中信消费金融
            when T1.group_id = '277c84b933be4cc1977ba61d7487c038'   then '277c84b933be4cc1977ba61d7487c038'    --麦当劳    
            when T1.group_id = '8ABCAB393E559DD5F60B5C6AA93C589F'   then '8ABCAB393E559DD5F60B5C6AA93C589F'    --财富广场    
            when T1.group_id = '50ed559dec2a486c8917f8ca871b21d9'   then '50ed559dec2a486c8917f8ca871b21d9'    --中信建投期货
            when T1.group_id = 'A8A6825E13E450ABF017D9763FC215E3'   then 'A8A6825E13E450ABF017D9763FC215E3'    --中信书院
            when T1.group_id = '80086a3fb4704fc6b7c806048b5d4f09'   then '80086a3fb4704fc6b7c806048b5d4f09'    --信银理财
        else  T1.group_id    end         as Sec_Chnl_Id                                                         --二级渠道id  
        
    ,case when T1.group_id in ('71415A31B80DB390E2230616B51A7A0F','8f0628086566467f839c8b24b12a5d7c','25015275d17544f6960985baed828073','5a838c5cf99b45099462683925b0ec09','A9614BC5ECEAECF8A3E92CFD682972F3') then '中信保诚人寿'       
            when T1.group_id in ('2391B7E29D34101420BE8DFA761CF13E','b0614390abd14eb59fbfada66b9dc95d','3c14a9e6675a4a5eb12c94101c9af710','B7821F2131772023E4E0261890021C32','a9fe5731d9b04dc3b6216609619274c2','efe49a614c8a43e2ba675429dacaa236')    then '中信银行'    
            when T1.group_id in ('B6B16FE228BB0C8BCDAD086B949532C4','27C2824306061CAF77E413C7B4DC0555')   then '中信银行信用卡'     
            when T1.group_id = 'e233a527bd634869bc8293b7d21bd996'   then '百信银行'     
            when T1.group_id in ('7922FC9C4C0C7A0BBD0943F32AFE4B35','9e976fd27b0c4f7a9853cca4b1659757')   then '中信证券'     
            when T1.group_id = '30A0CC386C3A20A2B6654074349338F1'   then '华夏基金'     
            when T1.group_id = '367b6d493f924546a6da01b4f6a29797'   then '中信期货'     
            when T1.group_id in ('af38efab659c4be1aab25d38355593cc','3fb6e7b33ab440e0976566397e72481a')   then '中信建投证券'    
            when T1.group_id = 'dcdcea4f589b4c1fa0b21ea0ac1260b8'   then '中信信托'   
            when T1.group_id in ('b223db350b8044a3a463de8f612912d3','07301c99c76a42c9876e671be6a90a1a')   then '中信消费金融'     
            when T1.group_id = '277c84b933be4cc1977ba61d7487c038'   then '麦当劳'                
            when T1.group_id = '8ABCAB393E559DD5F60B5C6AA93C589F'   then '中信优享+公众号'                       
        else    T2.group_name     end          as Sec_Chnl_Nm                                                      --二级渠道名称
    ,T2.status                                                                                as Sec_Chnl_Stat  --二级渠道状态（0无效,1有效）
    ,T2.description                                                                           as Sec_Chnl_Dc    --二级渠道描述  
    ,case when T1.group_id in ('2391B7E29D34101420BE8DFA761CF13E','B6B16FE228BB0C8BCDAD086B949532C4','e233a527bd634869bc8293b7d21bd996','80086a3fb4704fc6b7c806048b5d4f09','27C2824306061CAF77E413C7B4DC0555','b0614390abd14eb59fbfada66b9dc95d','3c14a9e6675a4a5eb12c94101c9af710','B7821F2131772023E4E0261890021C32','a9fe5731d9b04dc3b6216609619274c2','efe49a614c8a43e2ba675429dacaa236') then '2391B7E29D34101420BE8DFA761CF13E'                  
            when T1.group_id in ('7922FC9C4C0C7A0BBD0943F32AFE4B35','30A0CC386C3A20A2B6654074349338F1','367b6d493f924546a6da01b4f6a29797','9e976fd27b0c4f7a9853cca4b1659757') then '7922FC9C4C0C7A0BBD0943F32AFE4B35'          
            when T1.group_id in ('71415A31B80DB390E2230616B51A7A0F','8f0628086566467f839c8b24b12a5d7c','25015275d17544f6960985baed828073','5a838c5cf99b45099462683925b0ec09','A9614BC5ECEAECF8A3E92CFD682972F3') then '71415A31B80DB390E2230616B51A7A0F'            
            when T1.group_id in ('50ed559dec2a486c8917f8ca871b21d9','af38efab659c4be1aab25d38355593cc','3fb6e7b33ab440e0976566397e72481a') then 'af38efab659c4be1aab25d38355593cc'     --  中信建投证券(含子公司)             
            when T1.group_id = 'dcdcea4f589b4c1fa0b21ea0ac1260b8'   then 'dcdcea4f589b4c1fa0b21ea0ac1260b8' 
            when T1.group_id in ('b223db350b8044a3a463de8f612912d3','07301c99c76a42c9876e671be6a90a1a')   then 'b223db350b8044a3a463de8f612912d3' 
            when T1.group_id = '277c84b933be4cc1977ba61d7487c038'   then '277c84b933be4cc1977ba61d7487c038' 
            when T1.group_id = '8ABCAB393E559DD5F60B5C6AA93C589F'   then '8ABCAB393E559DD5F60B5C6AA93C589F'          
        else  T1.group_id    end  as Fst_Chnl_Id                                               --一级渠道id
    ,case when T1.group_id in ('2391B7E29D34101420BE8DFA761CF13E','B6B16FE228BB0C8BCDAD086B949532C4','e233a527bd634869bc8293b7d21bd996','80086a3fb4704fc6b7c806048b5d4f09','27C2824306061CAF77E413C7B4DC0555','b0614390abd14eb59fbfada66b9dc95d','3c14a9e6675a4a5eb12c94101c9af710','B7821F2131772023E4E0261890021C32','a9fe5731d9b04dc3b6216609619274c2','efe49a614c8a43e2ba675429dacaa236') then '中信银行(含子公司)'                 
            when T1.group_id in ('7922FC9C4C0C7A0BBD0943F32AFE4B35','30A0CC386C3A20A2B6654074349338F1','367b6d493f924546a6da01b4f6a29797','9e976fd27b0c4f7a9853cca4b1659757') then '中信证券(含子公司)'              
            when T1.group_id in ('71415A31B80DB390E2230616B51A7A0F','8f0628086566467f839c8b24b12a5d7c','25015275d17544f6960985baed828073','5a838c5cf99b45099462683925b0ec09','A9614BC5ECEAECF8A3E92CFD682972F3') then '中信保诚人寿'      
            when T1.group_id in ('50ed559dec2a486c8917f8ca871b21d9','af38efab659c4be1aab25d38355593cc','3fb6e7b33ab440e0976566397e72481a') then '中信建投证券(含子公司)'     --  中信建投证券(含子公司)    
            when T1.group_id = 'dcdcea4f589b4c1fa0b21ea0ac1260b8'   then '中信信托'    
            when T1.group_id in ('b223db350b8044a3a463de8f612912d3','07301c99c76a42c9876e671be6a90a1a')   then '中信消费金融'    
            when T1.group_id = '277c84b933be4cc1977ba61d7487c038'   then '麦当劳'  
            when T1.group_id = '8ABCAB393E559DD5F60B5C6AA93C589F'   then '中信优享+公众号'               
    else   T2.group_name  end  as Fst_Chnl_Nm                                            --一级渠道名称          
    ,case when T1.group_id in ('2391B7E29D34101420BE8DFA761CF13E','B6B16FE228BB0C8BCDAD086B949532C4','e233a527bd634869bc8293b7d21bd996','80086a3fb4704fc6b7c806048b5d4f09') then '1'         else  T2.status      end  as Fst_Chnl_Stat                                                --一级渠道状态（0无效,1有效）
    ,case when T1.group_id in ('2391B7E29D34101420BE8DFA761CF13E','B6B16FE228BB0C8BCDAD086B949532C4','e233a527bd634869bc8293b7d21bd996','80086a3fb4704fc6b7c806048b5d4f09','27C2824306061CAF77E413C7B4DC0555','b0614390abd14eb59fbfada66b9dc95d','3c14a9e6675a4a5eb12c94101c9af710','B7821F2131772023E4E0261890021C32','a9fe5731d9b04dc3b6216609619274c2','efe49a614c8a43e2ba675429dacaa236')  then       '中信银行(含子公司)'                   
            when T1.group_id in ('7922FC9C4C0C7A0BBD0943F32AFE4B35','30A0CC386C3A20A2B6654074349338F1','367b6d493f924546a6da01b4f6a29797','9e976fd27b0c4f7a9853cca4b1659757') then '中信证券(含子公司)'             
            when T1.group_id in ('71415A31B80DB390E2230616B51A7A0F','8f0628086566467f839c8b24b12a5d7c','25015275d17544f6960985baed828073','5a838c5cf99b45099462683925b0ec09','A9614BC5ECEAECF8A3E92CFD682972F3') then '中信保诚人寿'  
            when T1.group_id in ('50ed559dec2a486c8917f8ca871b21d9','af38efab659c4be1aab25d38355593cc','3fb6e7b33ab440e0976566397e72481a') then '中信建投证券(含子公司)'     --  中信建投证券(含子公司)                     
            when T1.group_id = 'dcdcea4f589b4c1fa0b21ea0ac1260b8'   then '中信信托'     
            when T1.group_id in ('b223db350b8044a3a463de8f612912d3','07301c99c76a42c9876e671be6a90a1a')   then '中信消费金融'    
            when T1.group_id = '277c84b933be4cc1977ba61d7487c038'   then '麦当劳'          
            when T1.group_id = '8ABCAB393E559DD5F60B5C6AA93C589F'   then '中信优享+公众号'                    
        else  T2.description end  as  Fst_Chnl_Dc                                             --一级渠道描述
    ,'4'                                                                                                                     as Chnl_Lvl       --渠道级别
    ,case when T1.group_id in ('277c84b933be4cc1977ba61d7487c038','4938561d819a455aae9a0070552cbd64','A8A6825E13E450ABF017D9763FC215E3') then '0' else '1' end  as Fin_Chnl_Flg   --金融渠道标识  麦当劳/权益代理/中信书院
    ,T1.auto_approve                                                                                                         as Auto_Auth_Fg   --自动授权标识
    ,T1.support_wallet                                                                                                       as Wallet_Fg      --支持钱包标识
    ,date(T3.take_effect_time)                                                                                               as Chnl_Effect_Dt --生效日期
    ,T3.take_effect_time                                                                                                     as Effect_Tm      --生效时
    ,case when T1.group_id in ('71415A31B80DB390E2230616B51A7A0F','8f0628086566467f839c8b24b12a5d7c'  --中信保诚人寿  信诚20周年
                                ,'2391B7E29D34101420BE8DFA761CF13E'                                     --中信银行
                                ,'B6B16FE228BB0C8BCDAD086B949532C4'                                     --中信银行信用卡
                                ,'e233a527bd634869bc8293b7d21bd996'                                     --百信银行
                                ,'7922FC9C4C0C7A0BBD0943F32AFE4B35'                                     --中信证券
                                ,'30A0CC386C3A20A2B6654074349338F1'                                     --华夏基金
                                ,'367b6d493f924546a6da01b4f6a29797'                                     --中信期货
                                ,'af38efab659c4be1aab25d38355593cc'                                     --中信建投证券
                                ,'dcdcea4f589b4c1fa0b21ea0ac1260b8'                                     --中信信托
                                ,'b223db350b8044a3a463de8f612912d3'                                     --中信消费金融
                                ,'277c84b933be4cc1977ba61d7487c038'                                     --麦当劳    
                                ,'8ABCAB393E559DD5F60B5C6AA93C589F'                                     --中信优享+公众号
                                ,'50ed559dec2a486c8917f8ca871b21d9'                                     --中信建投期货
                                ,'A8A6825E13E450ABF017D9763FC215E3'                                     --中信书院
                                ,'80086a3fb4704fc6b7c806048b5d4f09'                                     --信银理财
                                )  then  0   else  1   end           as  Sec_Chnl_Flg     --是否二级其他渠道                     
        ,case when T1.group_id in ('2391B7E29D34101420BE8DFA761CF13E','B6B16FE228BB0C8BCDAD086B949532C4'
                                ,'e233a527bd634869bc8293b7d21bd996','7922FC9C4C0C7A0BBD0943F32AFE4B35'
                                ,'30A0CC386C3A20A2B6654074349338F1','367b6d493f924546a6da01b4f6a29797'           
                                ,'71415A31B80DB390E2230616B51A7A0F','8f0628086566467f839c8b24b12a5d7c'
                                ,'af38efab659c4be1aab25d38355593cc','dcdcea4f589b4c1fa0b21ea0ac1260b8'
                                ,'b223db350b8044a3a463de8f612912d3','277c84b933be4cc1977ba61d7487c038' 
                                ,'8ABCAB393E559DD5F60B5C6AA93C589F','50ed559dec2a486c8917f8ca871b21d9'
                                ,'A8A6825E13E450ABF017D9763FC215E3','80086a3fb4704fc6b7c806048b5d4f09' 
                                )  then  0   else   1 end           as  Is_Fst_Oth_Chnl  --是否一级其他渠道
    ,case when T1.group_id in ('71415A31B80DB390E2230616B51A7A0F','8f0628086566467f839c8b24b12a5d7c','25015275d17544f6960985baed828073','5a838c5cf99b45099462683925b0ec09','A9614BC5ECEAECF8A3E92CFD682972F3') then '子公司渠道' -- 中信保诚人寿      
            when T1.group_id in ('2391B7E29D34101420BE8DFA761CF13E','b0614390abd14eb59fbfada66b9dc95d','3c14a9e6675a4a5eb12c94101c9af710','B7821F2131772023E4E0261890021C32','a9fe5731d9b04dc3b6216609619274c2','efe49a614c8a43e2ba675429dacaa236')   then '子公司渠道'                                     -- 中信银行
            when T1.group_id in ('B6B16FE228BB0C8BCDAD086B949532C4','27C2824306061CAF77E413C7B4DC0555')   then '子公司渠道'                                     -- 中信银行信用卡
            when T1.group_id = 'e233a527bd634869bc8293b7d21bd996'   then '子公司渠道'                                     -- 百信银行
            when T1.group_id in ('7922FC9C4C0C7A0BBD0943F32AFE4B35','9e976fd27b0c4f7a9853cca4b1659757')   then '子公司渠道'                                     -- 中信证券
            when T1.group_id = '80086a3fb4704fc6b7c806048b5d4f09'   then '子公司渠道'                                     -- 信银理财
            when T1.group_id = '30A0CC386C3A20A2B6654074349338F1'   then '子公司渠道'                                     -- 华夏基金
            when T1.group_id = '367b6d493f924546a6da01b4f6a29797'   then '子公司渠道'                                     -- 中信期货
            when T1.group_id in ('af38efab659c4be1aab25d38355593cc','3fb6e7b33ab440e0976566397e72481a')   then '子公司渠道'                                     -- 中信建投证券
            when T1.group_id = '50ed559dec2a486c8917f8ca871b21d9'   then '子公司渠道'                                     -- 中信建投期货
            when T1.group_id = 'dcdcea4f589b4c1fa0b21ea0ac1260b8'   then '子公司渠道'                                     -- 中信信托
            when T1.group_id in ('b223db350b8044a3a463de8f612912d3','07301c99c76a42c9876e671be6a90a1a')   then '子公司渠道'                                     -- 中信消费金融   
            when T1.group_id = '277c84b933be4cc1977ba61d7487c038'   then '麦当劳'                                         -- 麦当劳       
            when T1.group_id = 'A8A6825E13E450ABF017D9763FC215E3'   then '中信书院'                                       -- 中信书院
            when T1.group_id = '4938561d819a455aae9a0070552cbd64'   then '权益代理'                                       -- 权益代理                     
        else '财富广场自营渠道'   end             as chnl_type                       --渠道类型
    ,case when T1.group_id in ('71415A31B80DB390E2230616B51A7A0F','8f0628086566467f839c8b24b12a5d7c','25015275d17544f6960985baed828073','5a838c5cf99b45099462683925b0ec09','A9614BC5ECEAECF8A3E92CFD682972F3') then '中信保诚人寿'       
            when T1.group_id in ('2391B7E29D34101420BE8DFA761CF13E','b0614390abd14eb59fbfada66b9dc95d','3c14a9e6675a4a5eb12c94101c9af710','B7821F2131772023E4E0261890021C32','a9fe5731d9b04dc3b6216609619274c2','efe49a614c8a43e2ba675429dacaa236')   then '中信银行'
            when T1.group_id in ('B6B16FE228BB0C8BCDAD086B949532C4','27C2824306061CAF77E413C7B4DC0555')   then '中信银行信用卡'
            when T1.group_id = 'e233a527bd634869bc8293b7d21bd996'   then '百信银行'
            when T1.group_id in ('7922FC9C4C0C7A0BBD0943F32AFE4B35','9e976fd27b0c4f7a9853cca4b1659757')   then '中信证券'
            when T1.group_id = '80086a3fb4704fc6b7c806048b5d4f09'   then '信银理财'
            when T1.group_id = '30A0CC386C3A20A2B6654074349338F1'   then '华夏基金'
            when T1.group_id = '367b6d493f924546a6da01b4f6a29797'   then '中信期货'
            when T1.group_id in ('af38efab659c4be1aab25d38355593cc','3fb6e7b33ab440e0976566397e72481a')   then '中信建投证券'
            when T1.group_id = '50ed559dec2a486c8917f8ca871b21d9'   then '中信建投期货'
            when T1.group_id = 'dcdcea4f589b4c1fa0b21ea0ac1260b8'   then '中信信托'   
            when T1.group_id in ('b223db350b8044a3a463de8f612912d3','07301c99c76a42c9876e671be6a90a1a')   then '中信消费金融'  
            when T1.group_id = '277c84b933be4cc1977ba61d7487c038'   then '麦当劳'                                         -- 麦当劳
            when T1.group_id = 'A8A6825E13E450ABF017D9763FC215E3'   then '中信书院'                                       -- 中信书院
            when T1.group_id = '4938561d819a455aae9a0070552cbd64'   then '权益代理'                                       -- 权益代理
        else '财富广场自营渠道'   end            as chnl_sub_nm                     --报送渠道名
from (select * from ods.ods_usms_lm_channel_base_t_df where ds = '${data_ds}')T1
left join (select * from ods.ods_usms_lm_channel_group_base_t_df where ds = '${data_ds}')T2 on T1.group_id = T2.group_id
left join (select * from ods.ods_usms_lm_agreement_version_t_df where ds = '${data_ds}')T3 on T1.channel_id = T3.channel_id
;

--将三级渠道补充
DELETE FROM cdm.dim_ch_chl_df WHERE ds='${data_ds}';
insert into cdm.dim_ch_chl_df 
select  chnl_id         
    ,chnl_nm         
    ,chnl_stat       
    ,chnl_dc         
    ,thd_chnl_id     
    ,thd_chnl_nm     
    ,thd_chnl_stat   
    ,thd_chnl_dc     
    ,sec_chnl_id     
    ,sec_chnl_nm     
    ,sec_chnl_stat   
    ,sec_chnl_dc     
    ,fst_chnl_id     
    ,fst_chnl_nm     
    ,fst_chnl_stat   
    ,fst_chnl_dc     
    ,chnl_lvl        
    ,fin_chnl_flg    
    ,auto_auth_fg    
    ,wallet_fg       
    ,chnl_effect_dt  
    ,effect_tm       
    ,is_sec_oth_chnl 
    ,is_fst_oth_chnl 
    ,chnl_type       
    ,chnl_sub_nm     
    ,'${data_ds}' as ds              
from dim_ch_chl_df_tmp
;


insert into cdm.dim_ch_chl_df 
select distinct
     T1.Thd_Chnl_Id       --三级渠道ID
    ,T1.Thd_Chnl_Nm       --三级渠道名称
    ,T1.Thd_Chnl_Stat     --三级渠道状态
    ,T1.Thd_Chnl_Dc       --三级渠道描述
    ,T1.Thd_Chnl_Id       --三级渠道ID
    ,T1.Thd_Chnl_Nm       --三级渠道名称
    ,T1.Thd_Chnl_Stat     --三级渠道状态
    ,T1.Thd_Chnl_Dc       --三级渠道描述
    ,T1.Sec_Chnl_Id        --二级渠道id
    ,T1.Sec_Chnl_Nm        --二级渠道名称
    ,T1.Sec_Chnl_Stat      --二级渠道状态（0无效,1有效）
    ,T1.Sec_Chnl_Dc        --二级渠道描述
    ,T1.Fst_Chnl_Id        --一级渠道id
    ,T1.Fst_Chnl_Nm        --一级渠道名称
    ,T1.Fst_Chnl_Stat      --一级渠道状态（0无效,1有效）
    ,T1.Fst_Chnl_Dc        --一级渠道描述
    ,'3' as    Chnl_Lvl --渠道级别
    ,T1.Fin_Chnl_Flg       --金融渠道标识
    ,''               --自动授权标识
    ,''               --支持钱包标识
    ,''               --生效日期
    ,''               --生效时间
    ,T1.Is_Sec_Oth_Chnl    --是否二级其他渠道
    ,T1.Is_Fst_Oth_Chnl    --是否一级其他渠道
    ,T1.chnl_type as chnl_type                       --渠道类型
    ,T1.chnl_sub_nm as chnl_sub_nm                   --报送渠道名称
    ,'${data_ds}' as ds
from dim_ch_chl_df_tmp t1
  where T1.Chnl_Lvl = '4'
  and not exists (
                    select 1
                    from cdm.dim_ch_chl_df T2
                    where ds = '${data_ds}'  
                    and T2.Chnl_Id = T1.Thd_Chnl_Id
                 )
;