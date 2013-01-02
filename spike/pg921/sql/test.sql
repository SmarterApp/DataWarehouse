select
    di.account_sid as account_code
  , di.account_name as account_name
  , di.account_sid as account_abbrev
     , /*case when min(di.state_sid)
       over(partition by di.account_sid)
       <> max(di.state_sid)
       over(partition by di.account_sid)
       then 'Multiple States' else di.state_name end */
       'state' as state_name
     , /*case when min(di.state_sid)
       over(partition by di.account_sid)
       <> max(di.state_sid)
       over(partition by di.account_sid)
       then 'Multi States' else di.state_code end */
       'ST' as state_abbrev
     , /*case when min(di.state_sid)
       over(partition by di.account_sid)
       <> max(di.state_sid)
       over(partition by di.account_sid)
       then '-1' else di.state_sid end */
       'CD' as state_code
     , di.district_sid          as school_group_inst_code
     , di.district_name          as school_group_inst_name
     , di.district_name        as school_group_inst_abbrev
     , di.school_sid        as school_loc_code
     , di.school_name             as school_name
     , di.school_name           as school_abbrev
     , dg.grade_level_sid          as grade_code
     , dg.grade_level_order           as grade_order  
     , dg.grade_level_name  as grade_name
     , cast(null as char)                      as subject_code
     , cast(null as char)                      as subject_name
     , cast(null as char)                      as subject_abbrev
     , cast(null as char)                      as course_code
     , cast(null as char)                      as course_name
     , cast(null as char)                      as course_abbrev
     , cast(null as char)                 as staff_sid
     , cast(null as char)                 as staff_last_name
     , cast(null as char)                 as staff_first_name
     , cast(null as char)                      as section_sid
     , cast(null as char)                      as section_name
     , cast(null as char)                      as section_abbrev
     , cast(null as char)                      as attribute_category_code
     , cast(null as char)                      as attribute_category_name
     , cast(null as char)                     as attribute_value_code
     , cast(null as char)                     as attribute_value_label
     , cast(null as char)                     as student_first_name
     , cast(null as char)                      as student_last_name
     , cast(null as char)                      as student_sid
     , cast(null as char)                      as student_code
     , cast(null as char)                      as school_loc_code_curr
     , fao.assmt_code           as assmt_code 
     , fao.assmt_name as assmt_name
     , fao.assmt_name as assmt_abbrev
     , fao.assmt_version_code    as assmt_family_code
     , fao.daot_hier_level_code           as group_code
     , fao.daot_hier_level_name           as group_name
     , fao.daot_hier_level_name         as group_abbrev         
     , fao.daot_hier_level_rank         as subgroup_rank
     , case 
         when daot_hier_level = 1 then daot_hier_level_1_code 
         when daot_hier_level = 2 then daot_hier_level_2_code 
         when daot_hier_level = 3 then daot_hier_level_3_code 
         when daot_hier_level = 4 then daot_hier_level_4_code 
         when daot_hier_level = 5 then daot_hier_level_5_code 
       end
         as subgroup_code 
     , case 
         when daot_hier_level = 1 then daot_hier_level_1_abbrev 
         when daot_hier_level = 2 then daot_hier_level_2_abbrev 
         when daot_hier_level = 3 then daot_hier_level_3_abbrev 
         when daot_hier_level = 4 then daot_hier_level_4_abbrev 
         when daot_hier_level = 5 then daot_hier_level_5_abbrev 
       end
         as subgroup_name  
     , case 
         when daot_hier_level = 1 then daot_hier_level_1_abbrev 
         when daot_hier_level = 2 then daot_hier_level_2_abbrev 
         when daot_hier_level = 3 then daot_hier_level_3_abbrev 
         when daot_hier_level = 4 then daot_hier_level_4_abbrev 
         when daot_hier_level = 5 then daot_hier_level_5_abbrev 
       end
         as subgroup_abbrev 
     , fao.performance_level_flag
     , dp.academic_year_code     as academic_year_code
     , dp.academic_year_name     as academic_year_name
     , dp.academic_year_abbrev   as academic_year_abbrev
     , dp.period_code || '_' || dp.academic_year_code   as period_sid -- really this is period_sid
     , dp.period_order           as period_order
     , dp.academic_year_abbrev || ' ' || dp.period_abbrev as period_name  
     , dp.period_abbrev as period_abbrev
     , dpl.level_order           
     , 'level_name' as level_name       
     , 'level_code' as level_code
     , count(*) -- over (partition by dstu.eternal_student_sid, di.school_sid )
       as std_total_rows
     , cast(null as char)                         as assmt_grade_code
     , cast(null as integer)                      as assmt_grade_order
     , cast(null as char)                         as assmt_grade_name
    from    
    (
        select dim_student_key
             , eternal_student_sid   
             , year_sid
             , dim_assmt_period_key
             , dim_assmt_grade_key
             , assmt_code
             , assmt_name
             , case when assmt_code = '706' then 'TRC All Versions'
                    when assmt_code = '706s' then 'TRC All Versions'
                    else assmt_version_code end
                as assmt_version_code
             , daot_hier_level
             , daot_hier_level_code
             , daot_hier_level_name          
             , daot_hier_level_rank
             , daot.daot_hier_level_1_code 
             , daot.daot_hier_level_1_name
             , daot.daot_hier_level_1_abbrev     
             , daot.daot_hier_level_2_code 
             , daot.daot_hier_level_2_name
             , daot.daot_hier_level_2_abbrev
             , daot.daot_hier_level_3_code 
             , daot.daot_hier_level_3_name
             , daot.daot_hier_level_3_abbrev
             , daot.daot_hier_level_4_code 
             , daot.daot_hier_level_4_name
             , daot.daot_hier_level_4_abbrev
             , daot.daot_hier_level_5_code 
             , daot.daot_hier_level_5_name
             , daot.daot_hier_level_5_abbrev
             , dim_perf_level_key
             , performance_level_flag
          from edware.fact_assmt_outcome fao
          join edware.dim_assmt_outcome_type daot
               on fao.dim_assmt_outcome_type_key  = daot.dim_assmt_outcome_type_key
              and daot.daot_hier_level_code    in ('2')
              and daot.assmt_code         in ('7')
              and case
                    when daot.assmt_code = '706' then true
                    when daot.assmt_code = '706s' then true
                    else (daot.assmt_version_code in ('1'))
                  end
              and  case 
                     when daot.daot_hier_level = 1 then daot.daot_hier_level_1_code 
                     when daot.daot_hier_level = 2 then daot.daot_hier_level_2_code 
                     when daot.daot_hier_level = 3 then daot.daot_hier_level_3_code 
                     when daot.daot_hier_level = 4 then daot.daot_hier_level_4_code 
                     when daot.daot_hier_level = 5 then daot.daot_hier_level_5_code 
                   end in ('INSTREC')
         where fao.assmt_instance_rank=1 -- avoid duplicate assmt results in the same period
           and fao.year_sid in ('8')
       and daot.daot_measure_type_code = 'BM_AM'
       -- limit 10;
) as fao
        join edware.fact_enroll fe on  fao.dim_student_key = fe.dim_student_key  and fe.is_reporting_classe 
        join edware.dim_institution di on fe.dim_institution_key = di.dim_institution_key and not di.demo_flag and ( di.school_sid in ('79394925', '79394423', '79395100', '79395771', '79394101', '79394310', '79395205', '79394622', '15770391', '79395476', '79394066', '79394220', '79395057', '137672224', '79393989', '79394822', '79394491', '79394656', '79396033', '79394353', '79394891', '79395979', '15770388', '15770384', '79394856')) in ('15753404') and di.account_sid = '15753406'
        join edware.dim_period dp on fao.dim_assmt_period_key = dp.dim_period_key and dp.period_code || '_' || dp.academic_year_code in ('32_8')
        join edware.dim_perf_level dpl on fao.dim_perf_level_key = dpl.dim_perf_level_key and dpl.level_order in ('1', '2', '3')                                                             
        join edware.dim_grade dg on fe.dim_grade_key = dg.dim_grade_key and dg.grade_level_sid in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14')
        join edware.dim_student dstu on fe.dim_student_key = dstu.dim_student_key and not dstu.demo_flag
group by 
  account_code
, account_name
, account_abbrev
, state_name
, state_abbrev
, state_code
, school_group_inst_code
, school_group_inst_name
, school_group_inst_abbrev
, school_loc_code
, school_name
, school_abbrev
, grade_code
, grade_order
, grade_name
, subject_code
, subject_name
, subject_abbrev
, course_code
, course_name
, course_abbrev
, section_sid
, section_name
, section_abbrev
, staff_sid
, staff_first_name
, staff_last_name
, attribute_category_code
, attribute_category_name
, attribute_value_code
, attribute_value_label
, student_last_name
, student_first_name
, student_sid
, student_code
, school_loc_code_curr
, assmt_code
, assmt_name
, assmt_abbrev
, assmt_family_code
, group_code
, group_name
, group_abbrev
, subgroup_code
, subgroup_name
, subgroup_abbrev
, subgroup_rank
, academic_year_code
, academic_year_name
, academic_year_abbrev
, period_sid
, period_order
, period_name
, period_abbrev
, level_order
, level_name
, level_code
, assmt_grade_code
, assmt_grade_order
, assmt_grade_name
, performance_level_flag
limit 10;
