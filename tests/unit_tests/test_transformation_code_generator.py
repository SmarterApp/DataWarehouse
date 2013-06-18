'''
Created on June 17th, 2013

@author: lichen
'''

import rule_maker.rules.transformation_code_generator as tg
import rule_maker.rules.code_generator_sql_template as sql_tpl
from rule_maker.rules.rule_keys import PCLEAN, INLIST, LOOKUP, OUTLIST, COMPARE_LENGTH, UPPER, REMNL, TRIM


import unittest


class TestTransformationCodeGenerator(unittest.TestCase):
    def setUp(self):
        self.code_version = sql_tpl.POSTGRES

    def test_generate_transformations_not_supported_version(self):
        rule_names = ['clean']
        code_version = 'not_supported_version'
        self.assertRaises(ValueError, tg.generate_transformations, rule_names, code_version=code_version)

    def test_generate_transformations_not_supported_rule(self):
        rule_names = ['not_supported_rule']
        actual_result = tg.generate_transformations(rule_names)
        expected_result = []
        self.assertEqual(actual_result, expected_result)

    def test_generate_transformations(self):
        rule_conf = {'clean': {PCLEAN: [REMNL, TRIM]},
                     'cleanUpper': {PCLEAN: [UPPER, REMNL, TRIM]}
                     }
        rule_names = list(rule_conf.keys())
        actual_result = tg.generate_transformations(rule_names, rule_conf)
        self.assertEqual(len(actual_result), len(rule_conf))
        for i in range(len(actual_result)):
            code_triple = actual_result[i]
            self.assertEqual(code_triple[0], rule_names[i])
            self.assertEqual(code_triple[1], tg.FUNC_PREFIX + rule_names[i])
            self.assertTrue(len(code_triple[2]) > 0)

    def test_generate_single_transformation_code_pclean(self):
        rule_name = 'test_rule1'
        rule_def = {PCLEAN: [UPPER, REMNL, TRIM]}
        actual_result = tg.generate_single_transformation_code(self.code_version, rule_name, rule_def)
        expected_result = (rule_name, tg.FUNC_PREFIX + rule_name, EXPECTED_CODE_FOR_PCLEAN.format(col_name=rule_name))
        actual_result_update = update_actual_result(actual_result)
        self.assertEqual(actual_result_update, expected_result)

    def test_generate_single_transformation_code_inlist_comparelength(self):
        rule_name = 'test_rule2'
        rule_def = {INLIST: ['abc', 'def'],
                    COMPARE_LENGTH: 2}
        actual_result = tg.generate_single_transformation_code(self.code_version, rule_name, rule_def)
        expected_result = (rule_name, tg.FUNC_PREFIX + rule_name, EXPECTED_CODE_FOR_INLIST_COMPARE_LENGTH.format(col_name=rule_name))
        actual_result_update = update_actual_result(actual_result)
        self.assertEqual(actual_result_update, expected_result)

    def test_generate_single_transformation_code_inlist_outlist_comparelength(self):
        rule_name = 'test_rule3'
        rule_def = {INLIST: ['abc', 'def'],
                    OUTLIST: ['first', 'second'],
                    COMPARE_LENGTH: 2}
        actual_result = tg.generate_single_transformation_code(self.code_version, rule_name, rule_def)
        expected_result = (rule_name, tg.FUNC_PREFIX + rule_name, EXPECTED_CODE_FOR_INLIST_OUTLIST_COMPARE_LENGTH.format(col_name=rule_name))
        actual_result_update = update_actual_result(actual_result)
        self.assertEqual(actual_result_update, expected_result)

    def test_generate_single_transformation_code_lookup(self):
        rule_name = 'test_rule4'
        rule_def = {LOOKUP: {'ONE': ['one', '1'], 'TWO': ['two', '2']}}
        actual_result = tg.generate_single_transformation_code(self.code_version, rule_name, rule_def)
        expected_result = (rule_name, tg.FUNC_PREFIX + rule_name, EXPECTED_CODE_FOR_LOOKUP.format(col_name=rule_name))
        actual_result_update = update_actual_result(actual_result)
        self.assertEqual(actual_result_update, expected_result)


def update_actual_result(actual_result):
    start_index = actual_result[2].index('CREATE OR REPLACE')
    actual_sql = actual_result[2][start_index:].replace('\t', '    ')
    return (actual_result[0], actual_result[1], actual_sql)


# expected result
EXPECTED_CODE_FOR_PCLEAN = """CREATE OR REPLACE FUNCTION sp_{col_name}
(
    p_{col_name} IN VARCHAR
)
RETURNS VARCHAR AS
$$
DECLARE
    v_{col_name} VARCHAR(255);
    t_{col_name} VARCHAR(255);
    v_result VARCHAR(255);

BEGIN
v_{col_name} := TRIM(REPLACE(UPPER(p_{col_name}), CHR(13), ''));
t_{col_name} := v_{col_name};

    v_result := t_{col_name};

    RETURN v_result;

EXCEPTION
    WHEN OTHERS THEN
        RETURN v_{col_name};
END;
$$ LANGUAGE plpgsql;
"""

EXPECTED_CODE_FOR_INLIST_COMPARE_LENGTH = """CREATE OR REPLACE FUNCTION sp_{col_name}
(
    p_{col_name} IN VARCHAR
)
RETURNS VARCHAR AS
$$
DECLARE
    v_{col_name} VARCHAR(255);
    t_{col_name} VARCHAR(255);
    v_result VARCHAR(255);
vals_{col_name} text[] = ARRAY['abc','def'];
BEGIN
v_{col_name} := p_{col_name};
t_{col_name} := v_{col_name};
v_result := 'NOT FOUND';

    FOR cntr IN array_lower(vals_{col_name}, 1)..array_upper(vals_{col_name}, 1)
    LOOP
            IF SUBSTRING(t_{col_name}, 1, 2) = SUBSTRING(vals_{col_name}[cntr], 1, 2) THEN
            v_result := vals_{col_name}[cntr];
            EXIT;
        END IF;
    END LOOP;


    IF v_result = 'NOT FOUND' THEN
        v_result := v_{col_name};
    END IF;

    RETURN v_result;

EXCEPTION
    WHEN OTHERS THEN
        RETURN v_{col_name};
END;
$$ LANGUAGE plpgsql;
"""

EXPECTED_CODE_FOR_INLIST_OUTLIST_COMPARE_LENGTH = """CREATE OR REPLACE FUNCTION sp_{col_name}
(
    p_{col_name} IN VARCHAR
)
RETURNS VARCHAR AS
$$
DECLARE
    v_{col_name} VARCHAR(255);
    t_{col_name} VARCHAR(255);
    v_result VARCHAR(255);
keys_{col_name} text[] = ARRAY['abc','def'];
vals_{col_name} text[] = ARRAY['first','second'];
BEGIN
v_{col_name} := p_{col_name};
t_{col_name} := v_{col_name};
v_result := 'NOT FOUND';

    FOR cntr IN array_lower(keys_{col_name}, 1)..array_upper(keys_{col_name}, 1)
    LOOP
            IF SUBSTRING(t_{col_name}, 1, 2) = SUBSTRING(keys_{col_name}[cntr], 1, 2) THEN
            v_result := vals_{col_name}[cntr];
            EXIT;
        END IF;
    END LOOP;


    IF v_result = 'NOT FOUND' THEN
        v_result := v_{col_name};
    END IF;

    RETURN v_result;

EXCEPTION
    WHEN OTHERS THEN
        RETURN v_{col_name};
END;
$$ LANGUAGE plpgsql;
"""

EXPECTED_CODE_FOR_LOOKUP = """CREATE OR REPLACE FUNCTION sp_{col_name}
(
    p_{col_name} IN VARCHAR
)
RETURNS VARCHAR AS
$$
DECLARE
    v_{col_name} VARCHAR(255);
    t_{col_name} VARCHAR(255);
    v_result VARCHAR(255);

BEGIN
v_{col_name} := p_{col_name};
t_{col_name} := v_{col_name};

    IF    SUBSTRING(t_{col_name}, 1, 3) = 'one'
    OR    SUBSTRING(t_{col_name}, 1, 1) = '1' THEN
        v_result := 'ONE';
    ELSIF SUBSTRING(t_{col_name}, 1, 3) = 'two'
    OR    SUBSTRING(t_{col_name}, 1, 1) = '2' THEN
        v_result := 'TWO';

    ELSE
        v_result := v_{col_name};
    END IF;
    RETURN v_result;

EXCEPTION
    WHEN OTHERS THEN
        RETURN v_{col_name};
END;
$$ LANGUAGE plpgsql;
"""

if __name__ == "__main__":
    unittest.main()
