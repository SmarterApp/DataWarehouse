'''
Created on Feb 19, 2013

@author: nparoha
'''
# # DO NOT DELETE THE COMMENTED CODE ##
# # Few of the tests are disabled to reduce the runtime for FTs on Jenkins. These tests will be enabled when the role based access functionality is implemented. ##
from selenium.webdriver.support.ui import WebDriverWait

from edware_testing_automation.frontend_tests.los_helper import LosHelper


class LoginPage(LosHelper):
    '''
    Tests login functionality for OpenAM
    '''

    def __init__(self, *args, **kwargs):
        LosHelper.__init__(self, *args, **kwargs)

    def setUp(self):
        '''
        PRE: setUp - Create a new instance of the driver and open the browser
        '''
        self.driver = self.get_driver()

    def test_los_login_redirect_state_education_administrator(self):
        ##Open a LOS page and validate login redirect as a State Education Admin (jmollica)
        self.open_requested_page_redirects_login_page("list_of_students")
        self.enter_login_credentials("jmollica", "jmollica1234")
        self.check_redirected_requested_page("list_of_students")

    def test_los_login_redirect_state_admin_pii(self):
        ##TC: Open a LOS page and validate login redirect as a State Admin with PII permissions(arice : Austin Rice)
        self.open_requested_page_redirects_login_page("list_of_students")
        self.enter_login_credentials("arice", "arice1234")
        self.check_redirected_requested_page("list_of_students")

    def test_list_of_grades_login_redirect_school_ed_admin_PII(self):
        ##TC: Open a CPOP-School View page and validate login redirect as a School Education Admin (cdavis) to view the list of grades
        self.driver.get(
                self.get_url() + "/assets/html/comparingPopulations.html?stateCode=NC&schoolGuid=936&districtGuid=229")
        self.enter_login_credentials("cdavis", "cdavis1234")
        self.check_redirected_requested_page("school_view")

    #    def test_individual_student_report_login_redirect_student(self):
    #        '''
    #        TC: Open an ISR page and validate login redirect as a student (msollars)
    #        '''
    #        self.driver.get(self.get_url() + "/assets/html/indivStudentReport.html?studentGuid=96b30045-d9e4-459d-85df-b99b0a778ffe&stateCode=NC")
    #        self.enter_login_credentials("msollars", "msollars1234")
    #        self.check_redirected_requested_page("individual_student_report")
    #
    def test_list_of_schools_login_redirect(self):
        ##TC: Open a CPOP-District View page and validate login redirect as a State Admin with PII (cseabaugh) to view the list of schools
        self.open_requested_page_redirects_login_page("district_view")
        self.enter_login_credentials("cseabaugh", "cseabaugh1234")
        self.check_redirected_requested_page("district_view")

    def test_los_login_redirect_teacher(self):
        ##TC: Open a LOS page and validate login redirect as a teacher (hgoree)
        self.open_requested_page_redirects_login_page("list_of_students")
        self.enter_login_credentials("hgoree", "hgoree1234")
        self.check_redirected_requested_page("list_of_students")

    def test_forgot_password(self):
        ##TC: Validate the 'Forgot password' feature and redirect to the login page from the forgot password page
        self.open_requested_page_redirects_login_page("individual_student_report")
        self.driver.find_element_by_class_name("controls").find_element_by_link_text("Forgot Password?").click()
        WebDriverWait(self.driver, 15).until(lambda driver: driver.find_element_by_id("content"))
        forgot_password_page_msg = self.driver.find_element_by_id("content").text
        expected_msg = "If you have forgotten your username or password, please send an email to the System Administrator, and be sure to include your username in the body of the email. You should receive a response within 2 business days."
        self.assertIn(expected_msg, forgot_password_page_msg), "Forgot password page displaying incorrect text"
        self.driver.find_element_by_link_text("Return to login page").click()
        try:
            WebDriverWait(self.driver, 20).until(lambda driver: driver.find_element_by_id("IDToken1"))
        except:
            self.assertTrue(False, "Error in re directing to the login page")

    def test_invalid_credentials(self):
        ##TC: Enter invalid username and password and validate the invalid credentials functionality
        self.open_requested_page_redirects_login_page("state_view_sds")
        login_page = self.driver.find_element_by_class_name("box-content")
        login_page.find_element_by_id("IDToken1").send_keys("invalid")
        login_page.find_element_by_id("IDToken2").send_keys("1234")
        login_page.find_element_by_name("Login.Submit").click()
        incorrect_login_msg = self.driver.find_element_by_class_name("clear-float").text
        expected_msg = "Invalid username/password combination. Please re-enter your credentials."
        self.assertIn(expected_msg,
                      incorrect_login_msg), "Invalid user/password redirect page displaying incorrect text"

    def test_invalid_password(self):
        ##TC: Enter valid username and invalid password and validate the invalid credentials functionality
        self.open_requested_page_redirects_login_page("state_view_sds")
        login_page = self.driver.find_element_by_class_name("box-content")
        login_page.find_element_by_id("IDToken1").send_keys("cdavis")
        login_page.find_element_by_id("IDToken2").send_keys("000000")
        login_page.find_element_by_name("Login.Submit").click()
        incorrect_login_msg = self.driver.find_element_by_class_name("clear-float").text
        expected_msg = "Invalid username/password combination. Please re-enter your credentials."
        self.assertIn(expected_msg,
                      incorrect_login_msg), "Invalid user/password redirect page displaying incorrect text"

    def test_logout(self):
        ##TC: Validate logout functionality.
        self.open_requested_page_redirects_login_page("state_view_sds")
        self.enter_login_credentials("eseinfeld", "eseinfeld1234")
        self.check_redirected_requested_page("state_view_sds")
        header_bar = self.driver.find_element_by_id("header")
        header_bar.find_element_by_id('user-settings').click()
        self.driver.implicitly_wait(1)
        logout = header_bar.find_element_by_id("log_out_button")
        logout.click()
        try:
            alert = self.driver.switch_to_alert()
            alert.accept()
            WebDriverWait(self.driver, 20).until(lambda driver: driver.find_element_by_id("IDToken1"))
        except:
            WebDriverWait(self.driver, 20).until(lambda driver: driver.find_element_by_id("IDToken1"))
            print("No security alert found.")

            #    ''' Data Loader/Extractor/Corrector Login '''
            #    def test_los_login_redirect_data_loaders(self):
            #        self.open_requested_page_redirects_login_page("list_of_students")
            #        self.enter_login_credentials("lmui", "lmui1234")
            #        self.check_redirected_requested_page("list_of_students")
            #
            #    def test_los_login_redirect_state_data_extractor(self):
            #        self.open_requested_page_redirects_login_page("list_of_students")
            #        self.enter_login_credentials("kbester", "kbester1234")
            #        self.check_redirected_requested_page("list_of_students")
            #
            #    def test_los_login_redirect_data_correctors(self):
            #        self.open_requested_page_redirects_login_page("list_of_students")
            #        self.enter_login_credentials("hgoree", "hgoree1234")
            #        self.check_redirected_requested_page("list_of_students")
            #
            #    ''' Admissions Officer Login '''
            #    def test_los_login_redirect_higher_education_admissions_officer(self):
            #        self.open_requested_page_redirects_login_page("list_of_students")
            #        self.enter_login_credentials("ecroker", "ecroker1234")
            #        self.check_redirected_requested_page("list_of_students")
            #
            #    ''' Psychometricians Login '''
            #    def test_los_login_redirect_psychometrician(self):
            #        self.open_requested_page_redirects_login_page("list_of_students")
            #        self.enter_login_credentials("cseabaugh", "cseabaugh1234")
            #        self.check_redirected_requested_page("list_of_students")
            #
            #    def test_los_login_redirect_consortium_education_administrator(self):
            #        self.open_requested_page_redirects_login_page("list_of_students")
            #        self.enter_login_credentials("eseinfeld", "eseinfeld1234")
            #        self.check_redirected_requested_page("list_of_students")
            #
            #    def test_individual_student_report_login_redirect_system_administrator(self):
            #        self.open_requested_page_redirects_login_page("list_of_students")
            #        self.enter_login_credentials("cdavis", "cdavis1234")
            #        self.check_redirected_requested_page("list_of_students")
            #
            #    def test_los_login_redirect_deployment_administrator(self):
            #        self.open_requested_page_redirects_login_page("list_of_students")
            #        self.enter_login_credentials("jhine", "jhine1234")
            #        self.check_redirected_requested_page("list_of_students")

    def tearDown(self):
        self.driver.quit()
