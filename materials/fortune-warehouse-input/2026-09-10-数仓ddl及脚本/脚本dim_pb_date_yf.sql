
--每年在dim_date_holiday更新后，更新此表即可
insert OVERWRITE TABLE DIM_PB_DATE_YF partition(ds='2999-12-31')
select 
     m.date_dt           --日期：YYYY-MM-DD
    ,m.cur_year_mth      --年月：YYYY-MM
    ,m.cur_year          --本年：YYYY
    ,m.cur_quarter       --当前季度：YYYYQx
    ,m.cur_mth           --月份：MM
    ,m.cur_mth_cn        --月份(中文)
    ,m.cur_mth_en        --月份(英文)
    ,m.cur_dt            --本日：DD
    ,m.cur_week          --周几 :例如周日是7 
    ,m.cur_week_cn       --周几(中文) 例：星期五
    ,m.cur_week_en       --周几(英文) 例：Friday
    ,m.workday_ind       --工作日标志：1.是,0否 
    ,m.week_end_ind      --周末标志：1.是,0否
    ,m.holiday_ind       --国务院法定节假日标志：1.是,0否 (每年11月15之后发布法定节假日后，手动更新) 
    ,m.week_of_year      --本年第几周
    ,m.day_of_month      --本月第几天 
    ,m.day_of_year       --本年第几天 
    ,row_number() over (partition by m.cur_quarter     order by m.date_dt asc)   as day_of_quarter    --本季度第几天
    ,row_number() over (partition by m.half_year_begin order by m.date_dt asc)   as day_of_half_year  --本半年第几天
    ,m.last_month_dt     --上月同期:YYYY-MM-DD
    ,m.last_year_dt      --去年同期:YYYY-MM-DD 
    ,m.last_dt           --上一日:YYYY-MM-DD
    ,m.next_dt           --下一日:YYYY-MM-DD
    ,m.cur_mth_begin     --本月初:YYYY-MM-DD 
    ,m.cur_mth_end       --本月末:YYYY-MM-DD 
    ,m.last_mth_begin    --上月初:YYYY-MM-DD 
    ,m.last_mth_end      --上月末:YYYY-MM-DD
    ,m.quar_begin        --季初:YYYY-MM-DD
    ,m.quar_end          --季末:YYYY-MM-DD
    ,m.half_year_begin   --日期所在半年初：YYYY-01-01和YYYY-07-01
    ,m.year_begin        --年初:YYYY-MM-DD
    ,m.year_end          --年末:YYYY-MM-DD
    ,m.last_3_dt         --近3日:YYYY-MM-DD 
    ,m.last_7_dt         --近7日:YYYY-MM-DD 
    ,m.last_15_dt        --近15日:YYYY-MM-DD
	,m.last_30_dt        --近30日:YYYY-MM-DD
    ,m.last_60_dt        --近60日:YYYY-MM-DD
    ,m.last_90_dt        --近90日:YYYY-MM-DD
    ,m.last_180_dt       --近180日:YYYY-MM-DD
	,m.last_360_dt       --近360日:YYYY-MM-DD 
    ,current_timestamp      as etl_time
	,CASE WHEN n.trade_days IS NOT NULL and holiday_ind =0 THEN '1' ELSE 0 END AS sse_ind --上交所交易日标志：1.是,0否
from 
(
    select 
        a.date_dt                                                                       --日期
        ,date_format(a.date_dt,'yyyy-MM')                       AS cur_year_mth         --年月
        ,year(a.date_dt)                                        AS cur_year             --本年：YYYY
        ,concat(year(a.date_dt),'Q',quarter(a.date_dt))         AS cur_quarter          --当前季度：YYYYQ
        ,date_format(a.date_dt,'MM')                            AS cur_mth              --月份：MM
        ,case when date_format(a.date_dt,'MM')='01' then '一月'
            when date_format(a.date_dt,'MM')='02' then '二月'
            when date_format(a.date_dt,'MM')='03' then '三月'
            when date_format(a.date_dt,'MM')='04' then '四月'
            when date_format(a.date_dt,'MM')='05' then '五月'
            when date_format(a.date_dt,'MM')='06' then '六月'
            when date_format(a.date_dt,'MM')='07' then '七月'
            when date_format(a.date_dt,'MM')='08' then '八月'
            when date_format(a.date_dt,'MM')='09' then '九月'
            when date_format(a.date_dt,'MM')='10' then '十月'
            when date_format(a.date_dt,'MM')='11' then '十一月'
            when date_format(a.date_dt,'MM')='12' then '十二月'
            else  date_format(a.date_dt,'MM') end               AS cur_mth_cn            --月份(中文)
            
        ,case when date_format(a.date_dt,'MM')='01' then 'Jan'
            when date_format(a.date_dt,'MM')='02' then 'Feb'
            when date_format(a.date_dt,'MM')='03' then 'Mar'
            when date_format(a.date_dt,'MM')='04' then 'Apr'
            when date_format(a.date_dt,'MM')='05' then 'May'
            when date_format(a.date_dt,'MM')='06' then 'Jun'
            when date_format(a.date_dt,'MM')='07' then 'Jul'
            when date_format(a.date_dt,'MM')='08' then 'Aug'
            when date_format(a.date_dt,'MM')='09' then 'Sep'
            when date_format(a.date_dt,'MM')='10' then 'Oct'
            when date_format(a.date_dt,'MM')='11' then 'Nov'
            when date_format(a.date_dt,'MM')='12' then 'Dec'
            else  date_format(a.date_dt,'MM') end               AS cur_mth_en              --月份(英文)
        ,date_format(a.date_dt,'dd')                            AS  cur_dt                 --本日：DD
        ,case when dayofweek(a.date_dt)=1 then 7   
            when dayofweek(a.date_dt)=2 then 1
            when dayofweek(a.date_dt)=3 then 2
            when dayofweek(a.date_dt)=4 then 3
            when dayofweek(a.date_dt)=5 then 4
            when dayofweek(a.date_dt)=6 then 5
            when dayofweek(a.date_dt)=7 then 6        
            else dayofweek(a.date_dt) end                       AS  cur_week               --本周周几
        ,case when dayofweek(a.date_dt)=1 then '星期日'    
            when dayofweek(a.date_dt)=2 then '星期一'
            when dayofweek(a.date_dt)=3 then '星期二'
            when dayofweek(a.date_dt)=4 then '星期三'
            when dayofweek(a.date_dt)=5 then '星期四'
            when dayofweek(a.date_dt)=6 then '星期五'
            when dayofweek(a.date_dt)=7 then '星期六'
            else dayofweek(a.date_dt) end                      AS  cur_week_cn            --本周周几(中文)
        ,date_format(a.date_dt,'EEEE')                         AS  cur_week_en            --本周周几(英文) 
        ,if(b.holiday ='补班' or (b.holiday is null and dayofweek(a.date_dt) between 2 and 6),1,0) AS  workday_ind             --工作日标志：1.是,0否 
        ,if(dayofweek(a.date_dt) in(1,7),1,0)                  AS  week_end_ind           --周末标志：1.是,0否 
        ,if( b.holiday is not null and b.holiday !='补班',1,0) AS  holiday_ind            --国务院法定节假日标志：1.是,0否 
        ,weekofyear(a.date_dt)                                 AS  week_of_year           --本年第几周 
        ,date_format(a.date_dt,'d')                            AS  day_of_month           --本月第几天 
        ,date_format(a.date_dt,'D')                            AS  day_of_year            --本年第几天 
        ,add_months(a.date_dt,-1)                              AS  last_month_dt          --上月同期:YYYY-MM-DD 
        ,add_months(a.date_dt,-12)                             AS  last_year_dt           --去年同期:YYYY-MM-DD 
        ,date_sub(a.date_dt,1)                                 AS  last_dt                --上一日:YYYY-MM-DD 
        ,date_add(a.date_dt,1)                                 AS  next_dt                --下一日:YYYY-MM-DD 
        ,trunc(a.date_dt,'MM')                                 AS  cur_mth_begin          --本月初:YYYY-MM-DD 
        ,last_day(a.date_dt)                                   AS  cur_mth_end            --本月末:YYYY-MM-DD 
        ,trunc(add_months(a.date_dt,-1),'MM')                  AS  last_mth_begin         --上月初:YYYY-MM-DD 
        ,last_day(add_months(a.date_dt,-1))                    AS  last_mth_end           --上月末:YYYY-MM-DD 
        ,to_date(concat(year(a.date_dt),'-',lpad(ceil(month(a.date_dt)/3) * 3 -2,2,0),'-01'))             AS  quar_begin         --季初:YYYY-MM-DD 
        ,last_day(to_date(concat(year(a.date_dt),'-',lpad(ceil(month(a.date_dt)/3) * 3,2,0),'-01')))      AS  quar_end               --季末:YYYY-MM-DD 
        ,if(date_format(a.date_dt,'MM') <='06',trunc(a.date_dt,'YY'),add_months(trunc(a.date_dt,'YY'),6)) AS  half_year_begin --日期所在半年初   
        ,trunc(a.date_dt,'YY')                                 AS  year_begin             --年初:YYYY-MM-DD 
        ,last_day(add_months(trunc(a.date_dt,'YY'),11))        AS  year_end               --年末:YYYY-MM-DD 
        ,date_sub(a.date_dt,2)                                 AS  last_3_dt              --近3天日期:YYYY-MM-DD 
        ,date_sub(a.date_dt,6)                                 AS  last_7_dt              --近7天日期:YYYY-MM-DD 
		,date_sub(a.date_dt,14)                                AS  last_15_dt             --近15天日期:YYYY-MM-DD
        ,date_sub(a.date_dt,29)                                AS  last_30_dt             --近30天日期:YYYY-MM-DD
        ,date_sub(a.date_dt,59)                                AS  last_60_dt             --近60天日期:YYYY-MM-DD
        ,date_sub(a.date_dt,89)                                AS  last_90_dt             --近90天日期:YYYY-MM-DD
        ,date_sub(a.date_dt,179)                               AS  last_180_dt            --近180天日期:YYYY-MM-DD
        ,date_sub(a.date_dt,359)                               AS  last_360_dt            --近360天日期:YYYY-MM-DD 
    --from cfgl_iml_data.dim_date_temp1 a 
	from cfgl_iml_data.DIM_PB_DATE_YF a 
    left join cfgl_iml_data.dim_date_holiday b 
    on a.date_dt=b.date_dt
	where a.ds='2999-12-31'
) m
LEFT JOIN
(
    select 
	    trade_days
		,from_unixtime(unix_timestamp(trade_days,'yyyyMMdd'),'yyyy-MM-dd') AS trade_dt
    from cfgl_itl_data.CWMP_WIND_CITIC_ASHARECALENDAR_YF
    WHERE S_INFO_EXCHMARKET = 'SSE' 
	group by 1,2
) n
ON m.date_dt = n.trade_dt
limit 1000000
;