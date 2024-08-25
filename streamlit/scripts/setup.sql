-- ==========================================
-- This script runs when the app is installed 
-- ==========================================


-- Create Application Role and Schema
create application role if not exists app_instance_role;
create or alter versioned schema app_instance_schema;
grant usage on schema app_instance_schema to application role app_instance_role;
    
create table if not exists app_instance_schema.risk_score_base_table(
    PARENT_SOURCE_ID VARCHAR(16777216),
    DIAGNOSES VARCHAR(16777216),
    SUBSCRIBER_ID VARCHAR(16777216),
    BASE_DEMOGRAPHIC_SEX VARCHAR(16777216),
    AGE NUMBER(38,0),
    MEDICAID BOOLEAN,
    ENROLLMENT_DURATION NUMBER(38,0),
    ELIG VARCHAR(16777216),
    OREC VARCHAR(16777216)
    );

create table if not exists app_instance_schema.platform_base_table (
	PARENT_SOURCE_ID VARCHAR(16777216),
	DIAGNOSES VARCHAR(16777216),
	SUBSCRIBER_ID VARCHAR(16777216),
	BASE_DEMOGRAPHIC_SEX VARCHAR(16777216),
	AGE NUMBER(38,0),
	MEDICAID BOOLEAN,
	ENROLLMENT_DURATION NUMBER(38,0),
	ELIG VARCHAR(16777216),
	OREC VARCHAR(16777216),
	RISK_SCORE_JSON VARIANT,
	RISKSCORE FLOAT
);

grant select , insert , update , delete  on table app_instance_schema.risk_score_base_table to application role app_instance_role;
grant select , insert , update , delete  on table app_instance_schema.platform_base_table to application role app_instance_role;

-- Create Streamlit app
create or replace streamlit app_instance_schema.streamlit from '/libraries' main_file='streamlit.py';


-- Grant usage and permissions on objects
grant usage on schema app_instance_schema to application role app_instance_role with grant option;
grant SELECT on view app_instance_schema.risk_score_base_table to application role app_instance_role;
grant SELECT on table app_instance_schema.risk_score_base_table to application role app_instance_role;
grant usage on streamlit app_instance_schema.streamlit to application role app_instance_role;

grant SELECT on view app_instance_schema.platform_base_table to application role app_instance_role;
grant SELECT on table app_instance_schema.platform_base_table to application role app_instance_role;








