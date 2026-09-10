-- DWS sql 
--删除数据
insert into cdm.dwd_pb_table_dml_motitor_ni 
select
        '${table_schema}'                         as schema                        --schemaname
       ,'${table_nm}'                 as table_name                    --表名称
       ,'delete'                      as dml_type                      --DML操作类型：INSERT、DELETE、UPDATE
       ,count(1)                      as data_cnt                      --影响行数
       ,'删除数据量'                  as dml_exp                       --操作说明
       ,'zg'                          as dml_user                      --操作人
       ,'${ds_tm}'                    as job_batch_date                --作业调度时间
       ,'1'                           as dml_batch_no                  --执行批次号
       ,CURRENT_TIMESTAMP             as  dml_time                     --操作时间
  from  ${table_schema}.${table_nm} 
 where ${ds_col} = '${ds_tm2}'
  ;

delete from  ${table_schema}.${table_nm} 
 where ${ds_col} = '${ds_tm2}'
;

CREATE temp TABLE ${table_nm}_mid as 
select 
      distinct_id                                                           as distinct_id            --用户ID
     ,login_id                                                              as login_id               --登录ID
     ,anonymous_id                                                          as anonymous_id           --匿名ID
     ,app_id                                                                as app_id                 --埋点自身应用id
     ,DATE_FORMAT(FROM_UNIXTIME(time/1000), '%Y-%m-%d %H:%i:%s')            as date_time              --触发时间
     ,event                                                                 as event                  --事件ID
     ,proc_time                                                             as proc_time              --数据入库时间
     ,replace(replace(replace(replace(properties,'\\r',''),'\\n',''),',"$',',"'),'{"$','{"')::jsonb   as properties             --原始properties
     ,flush_time                                                            as create_time            --事件发生时间
     ,track_id                                                              as track_id               --事件追踪ID
     ,trunc(ds_ho)                                                          as ds                     --触发日期，分区字段
     ,concat(kfk_partition,'_',kfk_offset,'_',time)                         as track_record_pk        --埋点记录主键
     ,ds_ho
     ,LEFT(DATE_FORMAT(FROM_UNIXTIME(time/1000), '%Y-%m-%d %H:%i:%s.%f'),23)         as trig_tm_ms       --触发时间毫秒
     ,LEFT(DATE_FORMAT(FROM_UNIXTIME(flush_time/1000), '%Y-%m-%d %H:%i:%s.%f'),23)   as create_time_ms   --事件发生时间毫秒

from ${src_schema}.${src_table}
where ${src_ds_col} = '${ds_tm2}'
  and event <> 'windowSourceExposure'
;

--临时表解析字段
create temp table ${table_nm}_analytic as 
(
    select 
         distinct_id                                                           as user_id                --用户ID
        ,login_id                                                              as login_id               --登录ID
        ,anonymous_id                                                          as anony_id               --匿名ID
        ,app_id                                                                as app_id                 --埋点自身应用id
        ,date_time                                                             as trig_tm                --触发时间
        ,event                                                                 as event                  --事件ID
        ,jsonb_extract_path_text(properties, 'title')                          as title                  --页面标题
        ,jsonb_extract_path_text(properties, 'function_id')                    as function_id            --功能ID
        ,jsonb_extract_path_text(properties, 'function_name')                  as function_name          --功能名
		,jsonb_extract_path_text(properties, 'content_id')                     as content_id             --内容id		   
        ,jsonb_extract_path_text(properties, 'hold_duration')                  as hold_duration          --页面停留时长
        ,DATE_FORMAT(FROM_UNIXTIME(create_time/1000), '%Y-%m-%d %H:%i:%s')     as create_time            --事件发生时间
        ,track_id                                                              as event_track_id         --事件追踪ID
        ,jsonb_extract_path_text(properties, 'event_duration')                 as event_duration         --停留时长
        ,jsonb_extract_path_text(properties, 'out_channel_id')                 as out_channel_id         --子公司渠道ID/跳转渠道组ID
        ,jsonb_extract_path_text(properties, 'product_id')                     as product_id             --产品ID
        ,jsonb_extract_path_text(properties, 'product_name')                   as product_name           --产品名称
        ,jsonb_extract_path_text(properties, 'sdk_version')                    as sdk_version            --sdk版本
        ,jsonb_extract_path_text(properties, 'source_id')                      as source_id              --绑定活动ID/资源ID/产品ID/活动ID       
        ,case when jsonb_extract_path_text(properties, 'sdk_version')='1.2.5' then 'iPhone' else jsonb_extract_path_text(properties, 'os') end as os --操作系统
        ,jsonb_extract_path_text(properties, 'os_version')                     as os_version             --操作系统版本			  
		,jsonb_extract_path_text(properties, 'referrer')                       as referrer               --前向地址	  
        ,jsonb_extract_path_text(properties, 'ref_screen_name')                as ref_screen_name        --上级页面地址
        ,jsonb_extract_path_text(properties, 'session_id')                     as session_id             --会话id
        ,jsonb_extract_path_text(properties, 'page_id')                        as page_id                --页面ID
        ,jsonb_extract_path_text(properties, 'ref_page_id')                    as ref_page_id            --前向页面ID
        ,REGEXP_REPLACE(jsonb_extract_path_text(properties, 'url'),'\n+', '')   as curr_page_url          --当前页面URL
        ,jsonb_extract_path_text(properties, 'url_path')                       as page_path              --页面路径
        ,jsonb_extract_path_text(properties, 'title')                          as curr_page_title        --当前页面标题
        ,jsonb_extract_path_text(properties, 'in_channel_id')                  as src_chnl_id            --来源渠道ID
        ,jsonb_extract_path_text(properties, 'area_name')                      as area_name              --功能所属区域名称
        ,jsonb_extract_path_text(properties, 'visit_source')                   as visit_source           --外部渠道投放位置名称
        ,jsonb_extract_path_text(properties, 'area_sequency')                  as area_sequency          --area_sequency
        ,jsonb_extract_path_text(properties, 'share_id')                       as share_id               --分享事件ID
        ,jsonb_extract_path_text(properties, 'resource_id')                    as resource_id            --资源位id
        ,jsonb_extract_path_text(properties, 'room_id')                        as room_id                --直播间id
        ,jsonb_extract_path_text(properties, 'book_id')                        as book_id                --读书id
        ,jsonb_extract_path_text(properties, 'app_id')                         as app_unqi_id            --应用唯一标识
        ,jsonb_extract_path_text(properties, 'mission_id')                     as mission_id             --活动任务ID
        ,jsonb_extract_path_text(properties, 'app_version')                    as app_version            --应用版本
        ,jsonb_extract_path_text(properties, 'pages_id')                       as pages_id               --活动页面/活动中间页id
        ,jsonb_extract_path_text(properties, 'ref_page_source')                as ref_page_source        --上级页面来源
        ,jsonb_extract_path_text(properties, 'src_scenario')                   as src_scenario           --消金上级页面来源
        ,jsonb_extract_path_text(properties, 'special_id')                     as special_id             --专题ID
        ,jsonb_extract_path_text(properties, 'pk_id')                          as pk_id                  --话题pkid
        ,jsonb_extract_path_text(properties, 'sku_id')                         as sku_id                 --商品id
        ,jsonb_extract_path_text(properties, 'scene_id')                       as scene_id               --用户场景id
        ,jsonb_extract_path_text(properties, 'evt_id')                         as evt_id                 --行为id
        ,jsonb_extract_path_text(properties, 'right_id')                       as right_id               --权益id 
	    ,CASE WHEN REGEXP_REPLACE(jsonb_extract_path_text(properties, 'url'),'\n+', '') LIKE 'http%' 
              THEN SUBSTR(SPLIT(REPLACE(REGEXP_REPLACE(jsonb_extract_path_text(properties, 'url'),'\n+', ''), 'https://', ''), '?')[1],INSTR(SPLIT(REPLACE(REGEXP_REPLACE(jsonb_extract_path_text(properties, 'url'),'\n+', ''), 'https://', ''), '?')[1], '/'))
              ELSE REGEXP_REPLACE(jsonb_extract_path_text(properties, 'url'),'\n+', '') 
              END AS short_curr_url  --原始url短链
        ,ds                                                                    as ds                     --触发日期，分区字段
        ,jsonb_extract_path_text(properties, 'navi_start')                 AS  navi_start               --加载开始时间.加载开始时间
        ,jsonb_extract_path_text(properties, 'redi_start')                 AS  redi_start               --重定向开始时间.重定向开始时间
        ,jsonb_extract_path_text(properties, 'redi_end')                   AS  redi_end                 --重定向结束时间.重定向结束时间
        ,jsonb_extract_path_text(properties, 'fetch_start')                AS  fetch_start              --拉取开始时间.拉取开始时间
        ,jsonb_extract_path_text(properties, 'dns_start')                  AS  dns_start                --DNS开始时间.DNS开始时间
        ,jsonb_extract_path_text(properties, 'dns_end')                    AS  dns_end                  --DNS结束时间.DNS结束时间
        ,jsonb_extract_path_text(properties, 'con_start')                  AS  con_start                --建连开始时间.建连开始时间
        ,jsonb_extract_path_text(properties, 'con_end')                    AS  con_end                  --建连结束时间.建连结束时间
        ,jsonb_extract_path_text(properties, 'request_start')              AS  request_start            --请求开始时间.请求开始时间
        ,jsonb_extract_path_text(properties, 'response_start')             AS  response_start           --响应开始时间.响应开始时间
        ,jsonb_extract_path_text(properties, 'response_end')               AS  response_end             --响应结束时间.响应结束时间
        ,jsonb_extract_path_text(properties, 'dom_start')                  AS  dom_start                --DOM开始时间.DOM开始时间
        ,jsonb_extract_path_text(properties, 'dom_complete')               AS  dom_complete             --DOM完成时间.DOM完成时间
        ,jsonb_extract_path_text(properties, 'load_start')                 AS  load_start               --load开始时间.load开始时间
        ,jsonb_extract_path_text(properties, 'load_end')                   AS  load_end                 --load结束时间.load结束时间
        ,jsonb_extract_path_text(properties, 'on_page_begin')              AS  on_page_begin            --webView容器 加载开始时间.webView容器 加载开始时间
        ,jsonb_extract_path_text(properties, 'on_page_finished')           AS  on_page_finished         --webView容器 加载完成时间.webView容器 加载完成时间
        ,jsonb_extract_path_text(properties, 'is_preload_on')              AS  is_preload_on            --是否开启了预载0表示未开启预载，1表示开启预载功能
        ,jsonb_extract_path_text(properties, '_hybrid_h5')                 AS  hybrid_h5                --数据来源.数据来源
        ,jsonb_extract_path_text(properties, 'account_id')                 as  account_id               --财富号ID
        ,jsonb_extract_path_text(properties, 'order_id')                   as  order_id                 --子订单ID         20250711新增
        ,jsonb_extract_path_text(properties, 'goods_id')                   as  goods_id                 --商品id           20250711新增
        ,jsonb_extract_path_text(properties, 'special_zone')               as  special_zone             --专区ID           20250711新增
        ,trim(jsonb_extract_path_text(properties, 'sale_num'))             as  sale_num                 --商城SKU数量      20250711新增
        ,jsonb_extract_path_text(properties, 'parent_order_id')            as  parent_order_id          --主订单ID         20250711新增
        ,jsonb_extract_path_text(properties, 'shop_id')                    as  shop_id                  --店铺ID           20250711新增
        ,jsonb_extract_path_text(properties, 'cate_cd')                    as  cate_cd                  --商城商品分类ID   20250711新增
        ,jsonb_extract_path_text(properties, 'after_sale_order_id')        as  after_sale_order_id      --售后订单ID       20250711新增
        ,jsonb_extract_path_text(properties, 'area_text')                  as  area_text                --区域信息          20250711zg新增
        ,jsonb_extract_path_text(properties, 'area_name_minus_1')          as  area_name_minus_1        --二级内部区域名称  20250711zg新增
        ,jsonb_extract_path_text(properties, 'area_name_minus_2')          as  area_name_minus_2        --三级内部区域名称  20250711zg新增
        ,jsonb_extract_path_text(properties, 'area_name_minus_3')          as  area_name_minus_3        --四级内部区域名称  20250711zg新增
        ,jsonb_extract_path_text(properties, 'area_name_minus_4')          as  area_name_minus_4        --五级内部区域名称  20250711zg新增
        ,jsonb_extract_path_text(properties, 'resource_bit_id')            as  resource_bit_id          --资源位ID
        ,jsonb_extract_path_text(properties, 'share_channel')              as  share_channel            --分享渠道
        ,jsonb_extract_path_text(properties, 'object_id')                  as  object_id                --活动ID/内容ID/产品ID
        ,jsonb_extract_path_text(properties, 'project_id')                 as  project_id               --项目标识ID
        ,jsonb_extract_path_text(properties, 'store_id')                   as  store_id                 --商户id
        ,jsonb_extract_path_text(properties, 'meta_event_id')              as  meta_event_id            --元事件id
        ,jsonb_extract_path_text(properties, 'chapter_id')                 as  chapter_id               --章节id
        ,track_record_pk                                                   as  track_record_pk          --埋点记录主键
        ,jsonb_extract_path_text(properties, 'source_info_id')             as source_info_id            --资源信息id  --add 20251216
        ,jsonb_extract_path_text(properties, 'jkid')                       as jkid                      --卓信ID
        ,proc_time                                                         as  proc_time                --数据入库时间
        ,ds_ho                                                             as  ds_tm                    --分区日期时间
        ,jsonb_extract_path_text(properties, 'uuid')                       as uuid                      --唯一主键 
        ,jsonb_extract_path_text(properties, 'new_sdk')                    as new_sdk                   --新sdk标识
        ,jsonb_extract_path_text(properties, 'n_jkid')                     as n_jkid                    --卓信ID上报源标识
        ,trig_tm_ms                                                        as trig_tm_ms                --触发时间毫秒
        ,create_time_ms                                                    as create_time_ms            --事件发生时间毫秒
        
    from ${table_nm}_mid
);

--全部埋点数据加工
create temp table ${table_nm}_total as 
select 
     m.user_id                --用户ID
    ,m.login_id               --登录ID
    ,case when m.valid_sdk_version_flg = '1' then m.anony_id
          when trim(m.src_chnl_id) in
                              ('7922FC9C4C0C7A0BBD0943F32AFE4B35'    --中信证券
                              ,'ec1dfbd11e7c4d38a22a5a0957b8fe26'    --中信证券
                              ,'de7bbd8e30c34f06b4811e1fcc0ee267'    --中信证券
                              ,'c67469c8837e4443bcd763d6d13b18b2'    --中信证券
                              ,'dcdcea4f589b4c1fa0b21ea0ac1260b8'    --中信信托
                              ,'a493ffb94fc0442a93bc3338e5fe7feb'    --中信信托
                              ,'348ef047b96b4bd080e06733370e6dfa'    --中信信托
                              ,'b223db350b8044a3a463de8f612912d3'    --中信消费金融
                              ,'a79b1da4835b415991a3b12a9c421ab1'    --中信消费金融
                              ,'425d022d32434f8d9f0172ea0b780d85'    --中信消费金融
                              ,'30A0CC386C3A20A2B6654074349338F1'    --华夏基金
                              ,'d1cb893ac6694831b8c1d1e551a73cd5'    --华夏基金
                              ,'34804aec0cff41509be2be9dc6b97da8'    --华夏基金
                              ,'B6B16FE228BB0C8BCDAD086B949532C4'    --中信银行信用卡
                              ,'53e9a873e9864cc28c558636c4bc2e80'    --中信银行信用卡
                              ,'79bc1138c9704f549eff3568d5b12479'    --中信银行信用卡
                              ,'33f49cee2f7b4b92b2c0a353f658ceb7'    --中信银行信用卡
                              ,'71fe34d150a44ae59d4ca599334ac696'    --中信银行信用卡
                              ,'5bfa94f19b924765b589087d2b6ea188'    --中信银行信用卡
                              ,'6d80020af6734c19bf99a8b8e32ab2bd'    --中信银行信用卡
                              ,'face2a836627410492c851d91bd82285'    --中信银行信用卡
                              ,'7bc8bdfa479d4e9cb4b6a0ed9ca8be3e'    --中信银行信用卡
                              ,'4d9c9e800d25425ea1ac2962538c9aeb'    --中信银行信用卡
                              ,'11D201B46A9B3AD76A217BC0D087BB56'    --中信银行信用卡
                              ,'780F3E276BCB665EF64A66D907D07DFF'    --中信银行信用卡
                              ,'27d99219455549db8d042d004a684e51'    --中信银行信用卡
                              ,'e233a527bd634869bc8293b7d21bd996'    --百信银行
                              ,'fa15b252f34f44a1984813210e1bd70c'    --百信银行
                              ,'589ef0a141ae45c08c46a1da9642704d'    --百信银行
                              ,'346528dc6b4a4ff394910c8ed4e560d6'    --百信银行
                              ,'9aca08e939074ec3a572dea8b6e9dc01'    --百信银行
                              ,'a9fe5731d9b04dc3b6216609619274c2'    --中信银行
                              ,'efe49a614c8a43e2ba675429dacaa236'    --中信银行
                              ,'B7821F2131772023E4E0261890021C32'    --中信银行
                              ,'2391B7E29D34101420BE8DFA761CF13E'    --中信银行
                              ,'a7059726d1dd45f6ab304285aa218b64'    --中信银行
                              ,'0250711fd72c4528bc7baa8f15e50b99'    --中信银行
                              ,'a55adb527faf4931bb54a7a2ca894bdc'    --中信银行
                              ,'4e324f98a6264ae3a54feb966514a176'    --中信银行
                              ,'7f81f0dd8edb478885b7cc3b47dacb04'    --中信银行
                              ,'471ecae2c4db437cb1b706389038003e'    --中信银行
                              ,'4b2c877d32b24c49b4a8aa34ff28d86a'    --中信银行
                              ,'44f9b2e962a247929d267895250e970a'    --中信银行
                              ,'53dc7150710b4a378fad04da3d3a5bbd'    --中信银行
                              ,'4574d26531704f71a1c47d1b75df3086'    --中信银行
                              ,'3975177504e64880adce4611f6784af2'    --中信银行
                              ,'fff0becb132540a48a17cdd972bce48a'    --中信银行
                              ,'ffcd19ebf3444221ad0b783277e804ef'    --中信银行
                              ,'77ca40b545224e458a11b9372968a31e'    --中信银行
                              ,'9de6dc36ca794affb8e54fa3836bf473'    --中信银行
                              ,'68a1c940d7a14d04b0ac7631fdf70637'    --中信银行
                              ,'2d050caa66454de9a5de16b79ca81d68'    --中信银行
                              ,'4cb4ef97bb5843ac820976cfe50d0a05'    --中信银行
                              ) then 'sdk_error_20250516' 
              else m.anony_id end                                                                                        AS  anony_id--匿名id，判断sdk有效取原始anony_id，sdk版本无效且满足渠道范围，取默认值'sdk_error_20250516'
    ,m.app_id                 --埋点自身应用id
    ,m.trig_tm                --触发时间
    ,m.event                  --事件ID
    ,m.title                  --页面标题
    ,m.function_id            --功能ID
    ,REGEXP_REPLACE(m.function_name,'[\r\n]+', '', 'g')  as function_name          --功能名
	,m.content_id             --内容id
    ,m.hold_duration          --页面停留时长
    ,m.create_time            --事件发生时间
    ,m.event_track_id         --事件追踪ID
    ,m.event_duration         --停留时长
    ,trim(m.out_channel_id)  as out_channel_id        --子公司渠道ID/跳转渠道组ID
    ,m.product_id             --产品ID
    ,m.product_name           --产品名称
    ,m.sdk_version            --sdk版本
	,nvl(h.act_id_new,m.source_id) as source_id   --绑定活动ID/资源ID/产品ID/活动ID    --20250312变更
    --,m.source_id              --绑定活动ID/资源ID/产品ID/活动ID  
    ,m.os                     --操作系统
    ,m.os_version             --操作系统版本
	,m.referrer               --前向地址
    ,m.ref_screen_name        --上级页面地址
    ,m.session_id             --会话id
    ,case when trim(m.page_id) is not null then m.page_id        --20250312变更
	      when trim(n.page_id) is not null then n.page_id
          when trim(m.curr_page_url) like '%/mkt-actives-page/index.html#/GoldenAutumn%'          then  'CF070018'
          when trim(m.curr_page_url) like '%/cfgc/index.html#/Login%'                             then  'CF040004'
          when trim(m.curr_page_url) like '%/mall/index.html#/Orderlist%'                         then  'CF050003'
          when trim(m.curr_page_url) like '%/manor/index.html%'                                   then  'CF080000'
          when trim(m.curr_page_url) like '%/cfgc/index.html#/onescreen%'                         then  'CF000001'
          when trim(m.curr_page_url) like '%/mkt-mobile/index.html#/pages/customActivity/zxjk/wealthFestival/DecIndex%'   then  'CF070047'
          when trim(m.curr_page_url) like '%/zxjk/liveRoom%'                                      then  'WB010001'
          when trim(m.curr_page_url) like '%/zxjk/liveBack%'                                      then  'WB010002'
          when trim(m.curr_page_url) like '%/zxjk/home%'                                          then  'WB010003'
          when trim(m.curr_page_url) like '%/jkcgjr/liveRoom%'                                    then  'WB010004'
          when trim(m.curr_page_url) like '%/jkcgjr/liveBack%'                                    then  'WB010005'
          when trim(m.curr_page_url) like '%/jkcgjr/home%'                                        then  'WB010006'
          when trim(m.curr_page_url) like '%share/cuid/%'                                         then  'QT000060'
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/HotRecommend/%'              then  'CF011003'
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/aggressiveInvestment/%'      then  'CF011004'
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/addedValue/%'                then  'CF011005'
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/flexibleAccess/%'            then  'CF011006'
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/insuranceGuarantee/%'        then  'CF011007'
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/spendMoney/%'                then  'CF011008'
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/keepvalue/%'                 then  'CF011017'
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/InvestMoney/%'               then  'CF011019'
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/SecurityMoney/%'             then  'CF011022'
          when trim(m.curr_page_url) like '%/Beta.LeadsH5/finance/finIndex.html%'                 then  'WB020001'
          when trim(m.curr_page_url) like '%/Beta.LeadsH5/topic/hot24Detail.html%'                then  'WB020002'
          when trim(m.curr_page_url) like '%/Beta.LeadsH5/topic/hot24List.html%'                  then  'WB020003'
          when trim(m.curr_page_url) like '%/Beta.LeadsH5/finance/closeComments.html%'            then  'WB020004'
          when trim(m.curr_page_url) like '%/Beta.LeadsH5/finance/newsReport.html%'               then  'WB020005'
          when trim(m.curr_page_url) like '%/Beta.LeadsH5/finance/videoDetail.html%'              then  'WB020006'
          when trim(m.curr_page_url) like '%/Beta.LeadsH5/finance/indexNumber.html%'              then  'WB020007'
          when trim(m.curr_page_url) like '%/Beta.WxFriendsH5/customer%'                          then  'WB020008'
          when trim(m.curr_page_url) like '%/Beta.WxFriendsH5/recommand%'                         then  'WB020009'
          when trim(m.curr_page_url) like '%/Beta.WxFriendsH5/setting%'                           then  'WB020010'
          when trim(m.curr_page_url) like '%/Beta.WxFriendsH5/allFriend%'                         then  'WB020011'
          when trim(m.curr_page_url) like '%/Beta.WxFriendsH5/pop%'                               then  'WB020012'
          when trim(m.curr_page_url) like '%/findDetail%'                                         then  'CF020002'
          when trim(m.curr_page_url) like '%/informationDetail%'                                  then  'CF020032'
          when trim(m.curr_page_url) like '%/mall/%'                                              then  'CF050001'
          when trim(m.curr_page_url) like '%/lm-activity/cross-selling-web/index.html%'           then  'CF060008'
          when trim(m.curr_page_url) like '%/overseasFinance_ZXBC%'                               then  'CF011041'
          when trim(m.curr_page_url) like '%/overseasFinance%'                                    then  'CF011040'
          when trim(m.curr_page_url) like '%indSecurityPassword%'                                 then  'CF040018'
          else null end as page_id                    --新版page_id   
    ,m.ref_page_id            --前向页面ID
    ,substr(m.curr_page_url,1,2000)  as  curr_page_url       -- 当前页面URL
    ,m.page_path              --页面路径
    ,m.curr_page_title        --当前页面标题
    ,substr(m.src_chnl_id,1,32)      as src_chnl_id          -- 来源渠道ID
    ,m.area_name              --功能所属区域名称
    ,substr(REGEXP_REPLACE(m.visit_source,'[\r\n]+', '', 'g'),1,200) as visit_source           --外部渠道投放位置名称
    ,m.area_sequency          --area_sequency
    ,m.share_id               --分享事件ID
    ,COALESCE(j.new_resource_id,m.resource_id,m.resource_bit_id)              as resource_id           --资源位id
    ,m.room_id                --直播间id
    ,m.book_id                --读书id
    ,m.app_unqi_id            --应用唯一标识
    ,m.mission_id             --活动任务ID
    ,m.app_version            --应用版本
    ,m.pages_id               --活动页面/活动中间页id
    ,m.ref_page_source        --上级页面来源
    ,m.src_scenario           --消金上级页面来源
    ,m.special_id             --专题ID
    ,m.pk_id                  --话题pkid
    ,substr(m.sku_id,1,250)  as sku_id                 --商品id
    ,m.scene_id               --用户场景id
    ,m.evt_id                 --行为id
    ,m.right_id               --权益id    
    ,m.short_curr_url         --原始url短链
    ,case when trim(m.page_id) is not null  then if(trim(i.page_id) is not null, i.page_short_url ,null)     --20250312逻辑调整
	      when trim(n.page_id) is not null  then m.short_curr_url        
          when trim(m.curr_page_url) like '%/mkt-actives-page/index.html#/GoldenAutumn%'          then  '/mkt-actives-page/index.html#/GoldenAutumn'  
          when trim(m.curr_page_url) like '%/cfgc/index.html#/Login%'                             then  '/cfgc/index.html#/Login'                     
          when trim(m.curr_page_url) like '%/mall/index.html#/Orderlist%'                         then  '/mall/index.html#/Orderlist'                 
          when trim(m.curr_page_url) like '%/manor/index.html%'                                   then  '/manor/index.html'                         
          when trim(m.curr_page_url) like '%/cfgc/index.html#/onescreen%'                         then  '/cfgc/index.html#/onescreen'                 
          when trim(m.curr_page_url) like '%/mkt-mobile/index.html#/pages/customActivity/zxjk/wealthFestival/DecIndex%'   then  '/mkt-mobile/index.html#/pages/customActivity/zxjk/wealthFestival/DecIndex'
          when trim(m.curr_page_url) like '%/zxjk/liveRoom%'                                      then  '/zxjk/liveRoom'  
          when trim(m.curr_page_url) like '%/zxjk/liveBack%'                                      then  '/zxjk/liveBack'  
          when trim(m.curr_page_url) like '%/jkcgjr/liveBack%'                                    then  '/jkcgjr/liveBack'
          when trim(m.curr_page_url) like '%/jkcgjr/liveRoom%'                                    then  '/jkcgjr/liveRoom'
          when trim(m.curr_page_url) like '%/zxjk/home%'                                          then  '/zxjk/home'      
          when trim(m.curr_page_url) like '%/jkcgjr/home%'                                        then  '/jkcgjr/home'    
          when trim(m.curr_page_url) like '%/share/cuid/%'                                        then  '/share/cuid/'    
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/HotRecommend/%'              then  '/cfgc/index.html#/wealth/HotRecommend/'          
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/aggressiveInvestment/%'      then  '/cfgc/index.html#/wealth/aggressiveInvestment/'  
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/addedValue/%'                then  '/cfgc/index.html#/wealth/addedValue/'            
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/flexibleAccess/%'            then  '/cfgc/index.html#/wealth/flexibleAccess/'        
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/insuranceGuarantee/%'        then  '/cfgc/index.html#/wealth/insuranceGuarantee/'    
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/spendMoney/%'                then  '/cfgc/index.html#/wealth/spendMoney/'            
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/keepvalue/%'                 then  '/cfgc/index.html#/wealth/keepvalue/'             
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/InvestMoney/%'               then  '/cfgc/index.html#/wealth/InvestMoney/'           
          when trim(m.curr_page_url) like '%/cfgc/index.html#/wealth/SecurityMoney/%'             then  '/cfgc/index.html#/wealth/SecurityMoney/'         
          when trim(m.curr_page_url) like '%/Beta.LeadsH5/finance/finIndex.html%'                 then  '/Beta.LeadsH5/finance/finIndex.html'      
          when trim(m.curr_page_url) like '%/Beta.LeadsH5/topic/hot24Detail.html%'                then  '/Beta.LeadsH5/topic/hot24Detail.html'     
          when trim(m.curr_page_url) like '%/Beta.LeadsH5/topic/hot24List.html%'                  then  '/Beta.LeadsH5/topic/hot24List.html'       
          when trim(m.curr_page_url) like '%/Beta.LeadsH5/finance/closeComments.html%'            then  '/Beta.LeadsH5/finance/closeComments.html' 
          when trim(m.curr_page_url) like '%/Beta.LeadsH5/finance/newsReport.html%'               then  '/Beta.LeadsH5/finance/newsReport.html'    
          when trim(m.curr_page_url) like '%/Beta.LeadsH5/finance/videoDetail.html%'              then  '/Beta.LeadsH5/finance/videoDetail.html'   
          when trim(m.curr_page_url) like '%/Beta.LeadsH5/finance/indexNumber.html%'              then  '/Beta.LeadsH5/finance/indexNumber.html'   
          when trim(m.curr_page_url) like '%/Beta.WxFriendsH5/customer%'                          then  '/Beta.WxFriendsH5/customer'               
          when trim(m.curr_page_url) like '%/Beta.WxFriendsH5/recommand%'                         then  '/Beta.WxFriendsH5/recommand'              
          when trim(m.curr_page_url) like '%/Beta.WxFriendsH5/setting%'                           then  '/Beta.WxFriendsH5/setting'                
          when trim(m.curr_page_url) like '%/Beta.WxFriendsH5/allFriend%'                         then  '/Beta.WxFriendsH5/allFriend'              
          when trim(m.curr_page_url) like '%/Beta.WxFriendsH5/pop%'                               then  '/Beta.WxFriendsH5/pop'                    
          when trim(m.curr_page_url) like '%/findDetail%'                                         then '/cfgc/index.html#/find/findDetail'
          when trim(m.curr_page_url) like '%/informationDetail%'                                  then '/cfgc/index.html#/find/informationDetail'
          when trim(m.curr_page_url) like '%/mall/%'                                              then '/mall/index.html#/index'
          when trim(m.curr_page_url) like '%/lm-activity/cross-selling-web/index.html%'           then '/lm-activity/cross-selling-web/index.html#/home'
          when trim(m.curr_page_url) like '%/overseasFinance_ZXBC%'                               then '/cfgc/index.html#/wealth/overseasFinance_zxbc'
          when trim(m.curr_page_url) like '%/overseasFinance%'                                    then '/cfgc/index.html#/wealth/overseasFinance'
          when trim(m.curr_page_url) like '%indSecurityPassword%'                                 then '/cfgc/index.html#/findSecurityPassword'
          else null end      as short_page_url         --pageid短链
    ,m.page_id               as src_page_id            --原始pageid
    ,ds                                                                    as ds     
    ,m.navi_start                 AS  navi_start               --加载开始时间.加载开始时间
    ,m.redi_start                 AS  redi_start               --重定向开始时间.重定向开始时间
    ,m.redi_end                   AS  redi_end                 --重定向结束时间.重定向结束时间
    ,m.fetch_start                AS  fetch_start              --拉取开始时间.拉取开始时间
    ,m.dns_start                  AS  dns_start                --DNS开始时间.DNS开始时间
    ,m.dns_end                    AS  dns_end                  --DNS结束时间.DNS结束时间
    ,m.con_start                  AS  con_start                --建连开始时间.建连开始时间
    ,m.con_end                    AS  con_end                  --建连结束时间.建连结束时间
    ,m.request_start              AS  request_start            --请求开始时间.请求开始时间
    ,m.response_start             AS  response_start           --响应开始时间.响应开始时间
    ,m.response_end               AS  response_end             --响应结束时间.响应结束时间
    ,m.dom_start                  AS  dom_start                --DOM开始时间.DOM开始时间
    ,m.dom_complete               AS  dom_complete             --DOM完成时间.DOM完成时间
    ,m.load_start                 AS  load_start               --load开始时间.load开始时间
    ,m.load_end                   AS  load_end                 --load结束时间.load结束时间
    ,m.on_page_begin              AS  on_page_begin            --webView容器 加载开始时间.webView容器 加载开始时间
    ,m.on_page_finished           AS  on_page_finished         --webView容器 加载完成时间.webView容器 加载完成时间
    ,m.is_preload_on              AS  is_preload_on            --是否开启了预载0表示未开启预载，1表示开启预载功能
    ,m.hybrid_h5                  AS  hybrid_h5                --数据来源.数据来源
    ,m.anony_id                   AS  src_anony_id             --原始匿名ID.anony_id
    ,m.valid_sdk_version_flg      as  valid_sdk_version_flg    --sdk是否有效
    ,m.account_id                 as  account_id               --财富号ID
    ,m.order_id                  --子订单ID         20250711新增
    ,m.goods_id                  --商品id           20250711新增
    ,m.special_zone              --专区ID           20250711新增
    ,m.sale_num                  --商城SKU数量      20250711新增
    ,m.parent_order_id           --主订单ID         20250711新增
    ,m.shop_id                   --店铺ID           20250711新增
    ,m.cate_cd                   --商城商品分类ID   20250711新增
    ,m.after_sale_order_id       --售后订单ID       20250711新增
    ,m.area_text                  --区域信息          20250711zg新增
    ,m.area_name_minus_1          --二级内部区域名称  20250711zg新增
    ,m.area_name_minus_2          --三级内部区域名称  20250711zg新增
    ,m.area_name_minus_3          --四级内部区域名称  20250711zg新增
    ,m.area_name_minus_4          --五级内部区域名称  20250711zg新增
    ,m.resource_bit_id            --资源位ID
    ,m.share_channel              --分享渠道
    ,m.object_id                  --活动ID/内容ID/产品ID
    ,m.project_id                 --项目标识ID
    ,m.store_id                   as  store_id                --商户id
    ,m.meta_event_id              as  meta_event_id           --元事件id
    ,m.chapter_id                 as  chapter_id              --章节id
    ,m.track_record_pk            as  track_record_pk         --埋点记录主键
    ,m.source_info_id             as  source_info_id          --资源信息id
    ,m.jkid                       as  jkid                    --卓信ID
    ,m.proc_time                  --操作时间
    ,m.ds_tm                      --分区时间
    ,m.uuid                       as uuid                      --唯一主键 
    ,m.new_sdk                    as new_sdk                   --新sdk标识
    ,m.n_jkid                     as n_jkid                    --卓信ID上报源标识
    ,m.trig_tm_ms                 as trig_tm_ms                --触发时间毫秒
    ,m.create_time_ms             as create_time_ms            --事件发生时间毫秒


from 
(
    select t.* 
           ,case when os in ('iPhone','Android') and trim(nvl(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),''))='' then '0'
                 when os = 'iPhone' and substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',1)>1 then '1'
                 when os = 'iPhone' and substring_index(substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',2),'.',-1)>2 then '1'
                 when os = 'iPhone' and substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',2)='1.2' and substring_index(substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',3),'.',-1)>=5 then '1'
                 when os = 'Android' and substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',1)>1 then '1'
                 when os = 'Android' and substring_index(substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',2),'.',-1)>3 then '1'
                 when os = 'Android' and substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',2)='1.3' and substring_index(substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',3),'.',-1)>=7 then '1'
                 when os is null and substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',2)='1.4' and substring_index(substring_index(regexp_replace(regexp_replace(sdk_version, '-', '.'), '_', '.'),'.',3),'.',-1)>=0 then '1'
                 when os not in ('Android','iPhone')  then '1'
           else '0' end as valid_sdk_version_flg          -- sdk是否有效

    from ${table_nm}_analytic t
    where app_id in ('04ae4423559f4283'      --金控广场
                             ,'73371995d4bb4285'     --中信人
                             ,'7105c44ca6cc49b8'     --鸭鸭庄园
                             ,'6921eadcca4f4b7c'     --积分商城
                             ,'3c973fdfa26e4957'     --中车人
                             ,'a447cc0fc515405a'     --一汽人
                             ,'453ba19267684efb'     --中信优享m+
                             ,'aaf268e726af4176'     --营销mgm
                             ,'49bcef756fc64ec1'     --第二届财顾大赛
                             ,'3902b26a9e234898'     --直播
                             ,'9eb7d38ec46b4686'     --beta
                             ,'5ffe2f8dc0ff40c9'     --百信银行-资讯对接
                             ,'f17111f9f2f54ebc'     --中信消费金融
                             ,'9C0Rg2mblEXx5Hvg'     --科技商城--2025-10-16新增
                             ,'RNQXoUIiOTjQxC6'      --中信建投&中信银行代发企业认证融合项目--20260204新增
                            )
    and (page_id <> 'WB999999' or page_id is null)
    and ((app_id <> 'f17111f9f2f54ebc' and  (page_id <> 'WB030001' or page_id is null))
          or (app_id = 'f17111f9f2f54ebc' and page_id = 'WB030001'))
) m
left join cdm.dim_pb_page_func_info n
       on m.short_curr_url = n.page_short_url
left join cdm.dim_or_act_mapping_nf h 
       on m.source_id = h.act_id_old
left join cdm.dim_pb_page_func_info i
       on m.page_id = i.page_id
left join cdm.dim_pb_resource_mapping_nf j        --新旧资源位映射
       on m.resource_id = j.old_resource_id
;

--插入数据不含科技商城数据
insert into ${table_schema}.${table_nm} 
select 
     user_id                   --用户ID
    ,login_id                  --登录ID
    ,anony_id                  --匿名id，判断sdk有效取原始anony_id，sdk版本无效且满足渠道范围，取默认值'sdk_error_20250516'
    ,app_id                    --埋点自身应用id
    ,trig_tm                   --触发时间
    ,event                     --事件ID
    ,title                     --页面标题
    ,function_id               --功能ID
    ,function_name             --功能名
	,content_id                --内容id
    ,hold_duration             --页面停留时长
    ,create_time               --事件发生时间
    ,event_track_id            --事件追踪ID
    ,event_duration            --停留时长
    ,out_channel_id            --子公司渠道ID/跳转渠道组ID
    ,product_id                --产品ID
    ,product_name              --产品名称
    ,sdk_version               --sdk版本
	,source_id                 --绑定活动ID/资源ID/产品ID/活动ID    --20250312变更
    ,os                        --操作系统
    ,os_version                --操作系统版本
	,referrer                  --前向地址
    ,ref_screen_name           --上级页面地址
    ,session_id                --会话id
    ,page_id                   --新版page_id   
    ,ref_page_id               --前向页面ID
    ,curr_page_url             -- 当前页面URL
    ,page_path                 --页面路径
    ,curr_page_title           --当前页面标题
    ,src_chnl_id               -- 来源渠道ID
    ,area_name                 --功能所属区域名称
    ,visit_source              --外部渠道投放位置名称
    ,area_sequency             --area_sequency
    ,share_id                  --分享事件ID
    ,resource_id               --资源位id
    ,room_id                   --直播间id
    ,book_id                   --读书id
    ,app_unqi_id               --应用唯一标识
    ,mission_id                --活动任务ID
    ,app_version               --应用版本
    ,pages_id                  --活动页面/活动中间页id
    ,ref_page_source           --上级页面来源
    ,src_scenario              --消金上级页面来源
    ,special_id                --专题ID
    ,pk_id                     --话题pkid
    ,sku_id                    --商品id
    ,scene_id                  --用户场景id
    ,evt_id                    --行为id
    ,right_id                  --权益id    
    ,short_curr_url            --原始url短链
    ,short_page_url            --pageid短链
    ,src_page_id               --原始pageid
    ,ds                             
    ,navi_start                --加载开始时间.加载开始时间
    ,redi_start                --重定向开始时间.重定向开始时间
    ,redi_end                  --重定向结束时间.重定向结束时间
    ,fetch_start               --拉取开始时间.拉取开始时间
    ,dns_start                 --DNS开始时间.DNS开始时间
    ,dns_end                   --DNS结束时间.DNS结束时间
    ,con_start                 --建连开始时间.建连开始时间
    ,con_end                   --建连结束时间.建连结束时间
    ,request_start             --请求开始时间.请求开始时间
    ,response_start            --响应开始时间.响应开始时间
    ,response_end              --响应结束时间.响应结束时间
    ,dom_start                 --DOM开始时间.DOM开始时间
    ,dom_complete              --DOM完成时间.DOM完成时间
    ,load_start                --load开始时间.load开始时间
    ,load_end                  --load结束时间.load结束时间
    ,on_page_begin             --webView容器 加载开始时间.webView容器 加载开始时间
    ,on_page_finished          --webView容器 加载完成时间.webView容器 加载完成时间
    ,is_preload_on             --是否开启了预载0表示未开启预载，1表示开启预载功能
    ,hybrid_h5                 --数据来源.数据来源
    ,src_anony_id                  --原始匿名ID.anony_id
    ,valid_sdk_version_flg     --sdk是否有效
    ,account_id                --财富号ID
    ,order_id                  --子订单ID         20250711新增
    ,goods_id                  --商品id           20250711新增
    ,special_zone              --专区ID           20250711新增
    ,sale_num                  --商城SKU数量      20250711新增
    ,parent_order_id           --主订单ID         20250711新增
    ,shop_id                   --店铺ID           20250711新增
    ,cate_cd                   --商城商品分类ID   20250711新增
    ,after_sale_order_id       --售后订单ID       20250711新增
    ,area_text                 --区域信息          20250711zg新增
    ,area_name_minus_1         --二级内部区域名称  20250711zg新增
    ,area_name_minus_2         --三级内部区域名称  20250711zg新增
    ,area_name_minus_3         --四级内部区域名称  20250711zg新增
    ,area_name_minus_4         --五级内部区域名称  20250711zg新增
    ,resource_bit_id           --资源位ID
    ,share_channel             --分享渠道
    ,object_id                 --活动ID/内容ID/产品ID
    ,project_id                --项目标识ID
    ,store_id                  --商户id
    ,meta_event_id             --元事件id
    ,chapter_id                --章节id
    ,track_record_pk           --埋点记录主键
    ,source_info_id            --资源信息id
    ,jkid                      --卓信ID
    ,proc_time                 --操作时间
    ,ds_tm                     --分区时间
    ,uuid                      --唯一主键 
    ,new_sdk                   --新sdk标识
    ,n_jkid                    --卓信ID上报源标识
    ,trig_tm_ms                 as trig_tm_ms                --触发时间毫秒
    ,create_time_ms             as create_time_ms            --事件发生时间毫秒
    
 from ${table_nm}_total
where project_id <> '9C0Rg2mblEXx5Hvg' 
   or project_id IS NULL
;


delete from  ${table_schema}.${tmms_table_nm} 
 where ${ds_col} = '${ds_tm2}'
;
--插入科技商城数据
insert into ${table_schema}.${tmms_table_nm} 
select 
     user_id                   --用户ID
    ,login_id                  --登录ID
    ,anony_id                  --匿名id，判断sdk有效取原始anony_id，sdk版本无效且满足渠道范围，取默认值'sdk_error_20250516'
    ,app_id                    --埋点自身应用id
    ,trig_tm                   --触发时间
    ,event                     --事件ID
    ,title                     --页面标题
    ,function_id               --功能ID
    ,function_name             --功能名
	,content_id                --内容id
    ,hold_duration             --页面停留时长
    ,create_time               --事件发生时间
    ,event_track_id            --事件追踪ID
    ,event_duration            --停留时长
    ,out_channel_id            --子公司渠道ID/跳转渠道组ID
    ,product_id                --产品ID
    ,product_name              --产品名称
    ,sdk_version               --sdk版本
	,source_id                 --绑定活动ID/资源ID/产品ID/活动ID    --20250312变更
    ,os                        --操作系统
    ,os_version                --操作系统版本
	,referrer                  --前向地址
    ,ref_screen_name           --上级页面地址
    ,session_id                --会话id
    ,page_id                   --新版page_id   
    ,ref_page_id               --前向页面ID
    ,curr_page_url             -- 当前页面URL
    ,page_path                 --页面路径
    ,curr_page_title           --当前页面标题
    ,src_chnl_id               -- 来源渠道ID
    ,area_name                 --功能所属区域名称
    ,visit_source              --外部渠道投放位置名称
    ,area_sequency             --area_sequency
    ,share_id                  --分享事件ID
    ,resource_id               --资源位id
    ,room_id                   --直播间id
    ,book_id                   --读书id
    ,app_unqi_id               --应用唯一标识
    ,mission_id                --活动任务ID
    ,app_version               --应用版本
    ,pages_id                  --活动页面/活动中间页id
    ,ref_page_source           --上级页面来源
    ,src_scenario              --消金上级页面来源
    ,special_id                --专题ID
    ,pk_id                     --话题pkid
    ,sku_id                    --商品id
    ,scene_id                  --用户场景id
    ,evt_id                    --行为id
    ,right_id                  --权益id    
    ,short_curr_url            --原始url短链
    ,short_page_url            --pageid短链
    ,src_page_id               --原始pageid
    ,ds                             
    ,navi_start                --加载开始时间.加载开始时间
    ,redi_start                --重定向开始时间.重定向开始时间
    ,redi_end                  --重定向结束时间.重定向结束时间
    ,fetch_start               --拉取开始时间.拉取开始时间
    ,dns_start                 --DNS开始时间.DNS开始时间
    ,dns_end                   --DNS结束时间.DNS结束时间
    ,con_start                 --建连开始时间.建连开始时间
    ,con_end                   --建连结束时间.建连结束时间
    ,request_start             --请求开始时间.请求开始时间
    ,response_start            --响应开始时间.响应开始时间
    ,response_end              --响应结束时间.响应结束时间
    ,dom_start                 --DOM开始时间.DOM开始时间
    ,dom_complete              --DOM完成时间.DOM完成时间
    ,load_start                --load开始时间.load开始时间
    ,load_end                  --load结束时间.load结束时间
    ,on_page_begin             --webView容器 加载开始时间.webView容器 加载开始时间
    ,on_page_finished          --webView容器 加载完成时间.webView容器 加载完成时间
    ,is_preload_on             --是否开启了预载0表示未开启预载，1表示开启预载功能
    ,hybrid_h5                 --数据来源.数据来源
    ,src_anony_id                  --原始匿名ID.anony_id
    ,valid_sdk_version_flg     --sdk是否有效
    ,account_id                --财富号ID
    ,order_id                  --子订单ID         20250711新增
    ,goods_id                  --商品id           20250711新增
    ,special_zone              --专区ID           20250711新增
    ,sale_num                  --商城SKU数量      20250711新增
    ,parent_order_id           --主订单ID         20250711新增
    ,shop_id                   --店铺ID           20250711新增
    ,cate_cd                   --商城商品分类ID   20250711新增
    ,after_sale_order_id       --售后订单ID       20250711新增
    ,area_text                 --区域信息          20250711zg新增
    ,area_name_minus_1         --二级内部区域名称  20250711zg新增
    ,area_name_minus_2         --三级内部区域名称  20250711zg新增
    ,area_name_minus_3         --四级内部区域名称  20250711zg新增
    ,area_name_minus_4         --五级内部区域名称  20250711zg新增
    ,resource_bit_id           --资源位ID
    ,share_channel             --分享渠道
    ,object_id                 --活动ID/内容ID/产品ID
    ,project_id                --项目标识ID
    ,store_id                  --商户id
    ,meta_event_id             --元事件id
    ,chapter_id                --章节id
    ,track_record_pk           --埋点记录主键
    ,source_info_id            --资源信息id
    ,jkid                      --卓信ID
    ,proc_time                 --操作时间
    ,ds_tm                     --分区时间
    ,uuid                      --唯一主键 
    ,new_sdk                   --新sdk标识
    ,n_jkid                    --卓信ID上报源标识
    ,trig_tm_ms                 as trig_tm_ms                --触发时间毫秒
    ,create_time_ms             as create_time_ms            --事件发生时间毫秒
    
 from ${table_nm}_total
where project_id = '9C0Rg2mblEXx5Hvg' 
;


insert into cdm.dwd_pb_table_dml_motitor_ni 
select
        '${table_schema}'             as schema                        --schemaname
       ,'${table_nm}'                 as table_name                    --表名称
       ,'insert'                      as dml_type                      --DML操作类型：INSERT、DELETE、UPDATE
       ,count(1)                      as data_cnt                      --影响行数
       ,'${table_nm}表数据插入'       as dml_exp                       --操作说明
       ,'zg'                          as dml_user                      --操作人
       ,'${ds_tm}'                    as job_batch_date                --作业调度时间
       ,'1'                           as dml_batch_no                  --执行批次号
       ,CURRENT_TIMESTAMP             as  dml_time                     --操作时间
  from  ${table_schema}.${table_nm} 
   where ${ds_col} = '${ds_tm2}'
  ;