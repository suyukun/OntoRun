-- DWS sql 
-- author: CI-zx-18519129105
DELETE FROM cdm.dwd_lm_pv_df WHERE ds = '${data_ds}' ;
insert into cdm.dwd_lm_pv_df 
select evt_id as evt_id                                                                                                                                                                  --1.事件编号
    ,login_id as login_id                                                                                                                                                                  --2.登录id
    ,source_id as acty_id                                                                                                                                                                  --3.活动id
    ,product_id as prod_id                                                                                                                                                                 --4.产品id
    ,anony_id as anony_id                                                                                                                                                                  --6.匿名id
    ,src_chnl_id as src_chnl_id                                                                                                                                                            --7.来源渠道id
    ,os as opr_sys                                                                                                                                                                         --8.操作系统
    ,app_id as app_id                                                                                                                                                                      --9.app_id
    ,visit_source as visit_source                                                                                                                                                          --10.外部渠道投放位置名称（预设维度表、全埋点需求表里有）
    ,curr_page_url as pg_addr_cmplt                                                                                                                                                        --11.完整地址
    ,split(REGEXP_REPLACE(curr_page_url,'https?://',''),'?')[1]   as pg_addr                                                                                                               --12.页面地址（预设维度表）
    ,case when curr_page_url like 'http%' then split(regexp_replace(split(REGEXP_REPLACE(curr_page_url,'https?://',''),'?')[1],'^(.*?)/','@@'),'@@')[2] else curr_page_url end as pg_pth    --13.目录地址
    ,create_time as evt_happ_tm                                                                                                                                                            --15.事件发生时间
    ,trig_tm as evt_trig_tm                                                                                                                                                                --16.事件触发时间
    ,date(trig_tm) as evt_trig_dt                                                                                                                                                          --17.事件触发日期
    ,event as event                                                                                                                                                                        --18.事件名
    ,case when char_length(login_id)=0 or login_id is null then '1' else '0' end as is_visit                                                                                                                   --20.是否游客（0:否，1:是）
    ,event_track_id as evt_pursue_id                                                                                                                                                       --22.事件追踪id
    ,ref_screen_name as up_pg                                                                                                                                                              --33.上级页面
    ,sdk_version as sdk_ver                                                                                                                                                                --34.金控sdk版本号
    ,1 as pv                                                                                                                                                                             --35.浏览
    ,if(length(trim(login_id))>0,trim(login_id),trim(anony_id)) as uid_anony_id                                                                                                            --36.用户uuid
    ,content_id as content_id    --修改                                                                                                                                                          --37.内容id
    ,curr_page_title as curr_page_title                                                                                                                                                    --38.当前页面标题
     ,case when os in ('iPhone','Android') and trim(nvl(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'')) is null then '0'
           when os = 'iPhone' and substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',1)>1 then '1'
           when os = 'iPhone' and substring_index(substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',2),'.',-1)>2 then '1'
           when os = 'iPhone' and substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',2)='1.2' and substring_index(substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',3),'.',-1)>=5 then '1'
           when os = 'Android' and substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',1)>1 then '1'
           when os = 'Android' and substring_index(substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',2),'.',-1)>3 then '1'
           when os = 'Android' and substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',2)='1.3' and substring_index(substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',3),'.',-1)>=7 then '1'
	         when os is null and substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',2)='1.4' and substring_index(substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',3),'.',-1)>=0 then '1'
           when os not in ('Android','iPhone')  then '1'
	         else '0' end as Valid_Sdk_Version_Flg
    ,share_id         --20240119 新增 分享事件id
    ,mission_id       --20240119 新增 活动任务id
    ,product_name as prod_nm -- 产品名称 --20240318 新增
    ,area_name as area_nm --功能所属区域名称
    ,pages_id           --20241009新增：活动页面/活动中间页id
    ,room_id            --20241009新增：直播间id
    ,book_id            --20241009新增：读书id
    ,ref_page_source    --20241009新增：上级页面来源
    ,src_scenario       --20241009新增：消金上级页面来源
    ,special_id         --20241009新增：专题id
    ,pk_id              --20241009新增：话题pkid
    ,sku_id             --20241009新增：商品id
    ,right_id           --20241009新增：权益id
    ,page_id            --20241009新增：页面id
    ,short_curr_url     --20241009新增：原有url短链
    ,short_page_url     --20241009新增：页面url短链
    ,src_page_id        --20241009新增：原有页面id    
    ,ds
    ,ref_page_id        --20241031新增：前向页面页面id  
    ,account_id         --财富号ID 
    ,project_id         --项目标识ID--20251016新增，用于识别科技商城埋点数据
    ,store_id                   as store_id                     --商户id
    ,meta_event_id              as  meta_event_id               --元事件id
    ,chapter_id                 as  chapter_id                  --章节id
    ,track_record_pk            as  track_record_pk             --埋点记录主键
    ,goods_id                   as goods_id                     -- 商品id
    ,jkid                       as jkid                         --卓信ID
    ,uuid                       as uuid                         --唯一主键
    ,new_sdk                    as new_sdk                      --新sdk标识
    ,n_jkid                     as n_jkid                       --卓信ID上报源标识
    ,trig_tm_ms                 as evt_trig_tm_ms               --触发时间毫秒
    ,create_time_ms             as evt_happ_tm_ms               --事件发生时间毫秒
    
from ods.madp_collect_all
where ds = '${data_ds}' 
    and event in ('$pageview','visitPage')  
    and date(trig_tm) not in ('2023-04-16','2023-04-17','2023-04-18','2023-08-08')
;