--pass
ALTER TABLE edware.map_sect_group_sect ADD CONSTRAINT dim_section_group_fk FOREIGN KEY (dim_section_group_key) references edware.dim_section_group (dim_section_group_key);
--pass
ALTER TABLE edware.map_sect_group_sect ADD CONSTRAINT dim_section_fk FOREIGN KEY (dim_section_key) references edware.dim_section (dim_section_key);
--pass
ALTER TABLE edware.map_staff_group_sect ADD CONSTRAINT dim_staff_group_fk FOREIGN KEY (dim_staff_group_key) references edware.dim_staff_group (dim_staff_group_key);
--pass
ALTER TABLE edware.map_assmt_subj_subj ADD CONSTRAINT dim_assmt_subject_fk FOREIGN KEY (dim_assmt_subject_key) references edware.dim_assmt_subject (dim_assmt_subject_key);
--pass
ALTER TABLE edware.map_assmt_subj_subj ADD CONSTRAINT dim_subject_fk FOREIGN KEY (dim_subject_key) references edware.dim_subject (dim_subject_key);
--pass
ALTER TABLE edware.map_inst_group_inst ADD CONSTRAINT dim_inst_group_fk FOREIGN KEY (dim_inst_group_key) references edware.dim_inst_group (dim_inst_group_key);
--pass
ALTER TABLE edware.map_inst_group_inst ADD CONSTRAINT dim_institution_fk FOREIGN KEY (dim_institution_key) references edware.dim_institution (dim_institution_key);
--pass
ALTER TABLE edware.map_staff_group_staff ADD CONSTRAINT dim_staff_group_fk FOREIGN KEY (dim_staff_group_key) references edware.dim_staff_group (dim_staff_group_key);
--passALTER TABLE edware.map_staff_group_staff ADD CONSTRAINT dim_staff_fk FOREIGN KEY (dim_staff_key) references edware.dim_staff (dim_staff_key);

--fail
ALTER TABLE edware.fact_enroll ADD CONSTRAINT dim_student_fk FOREIGN KEY (dim_student_key) references edware.dim_student (dim_student_key);
--ALTER TABLE edware.fact_enroll ADD CONSTRAINT dim_student_fk FOREIGN KEY (dim_student_key) references edware.dim_student (dim_student_key);
--UPDATE: FOREIGN KEY constraint 'fact_enroll.dim_student_fk' violated

--fail
ALTER TABLE edware.fact_enroll ADD CONSTRAINT dim_grade_fk FOREIGN KEY (dim_grade_key) references edware.dim_grade (dim_grade_key);
sql>ALTER TABLE edware.fact_enroll ADD CONSTRAINT dim_grade_fk FOREIGN KEY (dim_grade_key) references edware.dim_grade (dim_grade_key);
UPDATE: FOREIGN KEY constraint 'fact_enroll.dim_grade_fk' violated

ALTER TABLE edware.fact_enroll ADD CONSTRAINT dim_section_fk FOREIGN KEY (dim_section_key) references edware.dim_section (dim_section_key);

ALTER TABLE edware.fact_enroll ADD CONSTRAINT dim_teacher_staff_fk FOREIGN KEY (dim_teacher_staff_key) references edware.dim_staff (dim_staff_key);

ALTER TABLE edware.fact_enroll ADD CONSTRAINT dim_enroll_attr_fk FOREIGN KEY (dim_enroll_attr_key) references edware.dim_enroll_attr (dim_enroll_attr_key);

ALTER TABLE edware.fact_enroll ADD CONSTRAINT dim_inst_admit_time_fk FOREIGN KEY (dim_inst_admit_time_key) references edware.dim_time (dim_time_key);

ALTER TABLE edware.fact_enroll ADD CONSTRAINT dim_inst_disc_time_fk FOREIGN KEY (dim_inst_disc_time_key) references edware.dim_time (dim_time_key);

ALTER TABLE edware.fact_enroll ADD CONSTRAINT dim_sect_admit_time_fk FOREIGN KEY (dim_sect_admit_time_key) references edware.dim_time (dim_time_key);

ALTER TABLE edware.fact_enroll ADD CONSTRAINT dim_sect_disc_time_fk FOREIGN KEY (dim_sect_disc_time_key) references edware.dim_time (dim_time_key);

ALTER TABLE edware.fact_assmt_outcome ADD CONSTRAINT dim_student_fk FOREIGN KEY (dim_student_key) references edware.dim_student (dim_student_key);

ALTER TABLE edware.fact_assmt_outcome ADD CONSTRAINT dim_assmt_staff_fk FOREIGN KEY (dim_assmt_staff_key) references edware.dim_staff (dim_staff_key);

ALTER TABLE edware.fact_assmt_outcome ADD CONSTRAINT dim_assmt_outcome_type_fk FOREIGN KEY (dim_assmt_outcome_type_key) references edware.dim_assmt_outcome_type (dim_assmt_outcome_type_key);

ALTER TABLE edware.fact_assmt_outcome ADD CONSTRAINT dim_assmt_period_fk FOREIGN KEY (dim_assmt_period_key) references edware.dim_period (dim_period_key);

ALTER TABLE edware.fact_assmt_outcome ADD CONSTRAINT dim_assmt_grade_fk FOREIGN KEY (dim_assmt_grade_key) references edware.dim_grade (dim_grade_key);

ALTER TABLE edware.fact_assmt_outcome ADD CONSTRAINT dim_assmt_time_fk FOREIGN KEY (dim_assmt_time_key) references edware.dim_time (dim_time_key);

ALTER TABLE edware.fact_assmt_outcome ADD CONSTRAINT dim_assmt_sync_time_fk FOREIGN KEY (dim_assmt_sync_time_key) references edware.dim_time (dim_time_key);

ALTER TABLE edware.fact_assmt_outcome ADD CONSTRAINT dim_perf_level_fk FOREIGN KEY (dim_perf_level_key) references edware.dim_perf_level (dim_perf_level_key);

ALTER TABLE edware.fact_assmt_outcome ADD CONSTRAINT dim_assmt_institution_fk FOREIGN KEY (dim_assmt_institution_key) references edware.dim_institution (dim_institution_key);

\q