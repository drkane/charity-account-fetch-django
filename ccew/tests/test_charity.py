from datetime import date

from django.test import TestCase

from ccew.models import Charity, CharityARPartA, CharityARPartB, CharityTrustee


class CharityTestCase(TestCase):
    def test_charity_str(self):
        charity = Charity.objects.create(
            organisation_number=123,
            registered_charity_number=123,
            linked_charity_number=0,
            charity_name="Test Charity",
        )
        self.assertEqual(str(charity), "Test Charity [123]")
        charity.delete()

        charity = Charity.objects.create(
            organisation_number=123,
            registered_charity_number=123,
            linked_charity_number=1,
            charity_name="Test Charity",
        )
        self.assertEqual(str(charity), "Test Charity [123-1]")

    def test_charity_orgid(self):
        charity = Charity.objects.create(
            organisation_number=123,
            registered_charity_number=123,
            linked_charity_number=0,
            charity_name="Test Charity",
        )
        self.assertEqual(charity.org_id, "GB-CHC-123")

    def test_charity_ccew_url(self):
        charity = Charity.objects.create(
            organisation_number=123,
            registered_charity_number=123,
            linked_charity_number=0,
            charity_name="Test Charity",
        )
        self.assertEqual(
            charity.ccew_url,
            "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/123",
        )

    def test_charity_aoo(self):
        charity = Charity.objects.create(
            organisation_number=123,
            registered_charity_number=123,
            linked_charity_number=0,
            charity_name="Test Charity",
        )

        charity.area_of_operation.create(
            registered_charity_number=charity.registered_charity_number,
            geographic_area_type="Country",
            geographic_area_description="Scotland",
        )
        charity.area_of_operation.create(
            registered_charity_number=charity.registered_charity_number,
            geographic_area_type="Country",
            geographic_area_description="Northern Ireland",
        )
        charity.area_of_operation.create(
            registered_charity_number=charity.registered_charity_number,
            geographic_area_type="Country",
            geographic_area_description="India",
        )
        charity.area_of_operation.create(
            registered_charity_number=charity.registered_charity_number,
            geographic_area_type="Continent",
            geographic_area_description="Antarctica",
        )
        charity.area_of_operation.create(
            registered_charity_number=charity.registered_charity_number,
            geographic_area_type="Region",
            geographic_area_description="Stoke on Trent",
        )

        self.assertEqual(len(charity.aoo["overseas"]), 2)
        self.assertEqual(len(charity.aoo["uk"]), 3)

    def test_charity_address(self):
        charity = Charity.objects.create(
            organisation_number=123,
            registered_charity_number=123,
            linked_charity_number=0,
            charity_name="Test Charity",
            charity_contact_address1="Test Address",
            charity_contact_address2="Test Road",
            charity_contact_address3="Test Town",
            charity_contact_address4="Test County",
            charity_contact_address5="Test Country",
            charity_contact_postcode="TE1 1ST",
        )
        self.assertEqual(len(charity.address()), 6)
        self.assertEqual(
            charity.address(", "),
            "Test Address, Test Road, Test Town, Test County, Test Country, TE1 1ST",
        )
        charity.delete()

        charity = Charity.objects.create(
            organisation_number=123,
            registered_charity_number=123,
            linked_charity_number=0,
            charity_name="Test Charity",
            charity_contact_address1="Test Address",
            charity_contact_address2="Test Road",
            charity_contact_postcode="TE1 1ST",
        )
        self.assertEqual(
            len(charity.address()),
            3,
        )

    def test_charity_financials(self):
        charity = Charity.objects.create(
            organisation_number=123,
            registered_charity_number=123,
            linked_charity_number=0,
            charity_name="Test Charity",
        )
        charity.annual_return_part_a.create(
            registered_charity_number=charity.registered_charity_number,
            fin_period_end_date="2019-12-31",
            fin_period_start_date="2019-01-01",
            latest_fin_period_submitted_ind=True,
        )

        # default gets the latest
        self.assertEqual(
            charity.financials().get("parta").fin_period_end_date,
            date(2019, 12, 31),
        )
        self.assertIsNone(charity.financials().get("partb"))

        # so does "latest_financials"
        self.assertEqual(
            charity.latest_financials.get("parta").fin_period_end_date,
            date(2019, 12, 31),
        )
        self.assertIsNone(charity.latest_financials.get("partb"))

        # a named date should get the one that covers that date
        self.assertEqual(
            charity.financials("2019-06-01").get("parta").fin_period_end_date,
            date(2019, 12, 31),
        )
        self.assertIsNone(charity.financials("2019-06-01").get("partb"))

        # a date outside the range should get None
        self.assertIsNone(charity.financials("2018-06-01").get("parta"))
        self.assertIsNone(charity.financials("2018-06-01").get("partb"))

        charity.annual_return_part_b.create(
            registered_charity_number=charity.registered_charity_number,
            fin_period_end_date="2019-12-31",
            fin_period_start_date="2019-01-01",
            latest_fin_period_submitted_ind=True,
        )

        # default gets the latest
        self.assertEqual(
            charity.financials().get("parta").fin_period_end_date,
            date(2019, 12, 31),
        )
        self.assertEqual(
            charity.financials().get("partb").fin_period_end_date,
            date(2019, 12, 31),
        )

        # so does "latest_financials"
        self.assertEqual(
            charity.latest_financials.get("parta").fin_period_end_date,
            date(2019, 12, 31),
        )
        self.assertEqual(
            charity.latest_financials.get("partb").fin_period_end_date,
            date(2019, 12, 31),
        )

        # a named date should get the one that covers that date
        self.assertEqual(
            charity.financials("2019-06-01").get("parta").fin_period_end_date,
            date(2019, 12, 31),
        )
        self.assertEqual(
            charity.financials("2019-06-01").get("partb").fin_period_end_date,
            date(2019, 12, 31),
        )

        # a date outside the range should get None
        self.assertIsNone(charity.financials("2018-06-01").get("parta"))
        self.assertIsNone(charity.financials("2018-06-01").get("partb"))


class CharityPartATestCase(TestCase):
    def setUp(self):
        self.charity = Charity.objects.create(
            organisation_number=123,
            registered_charity_number=123,
            linked_charity_number=0,
            charity_name="Test Charity",
        )

    def test_count_salary_band_over_60000_all(self):
        parta = CharityARPartA.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            count_salary_band_60001_70000=1,
            count_salary_band_70001_80000=1,
            count_salary_band_80001_90000=1,
            count_salary_band_90001_100000=1,
            count_salary_band_100001_110000=1,
            count_salary_band_110001_120000=1,
            count_salary_band_120001_130000=1,
            count_salary_band_130001_140000=1,
            count_salary_band_140001_150000=1,
            count_salary_band_150001_200000=1,
            count_salary_band_200001_250000=1,
            count_salary_band_250001_300000=1,
            count_salary_band_300001_350000=1,
            count_salary_band_350001_400000=1,
            count_salary_band_400001_450000=1,
            count_salary_band_450001_500000=1,
            count_salary_band_over_500000=1,
        )

        self.assertEqual(parta.count_salary_band_over_60000, 17)
        self.assertEqual(len(parta.list_salary_band_over_60000), 17)

    def test_count_salary_band_over_60000_some(self):
        parta = CharityARPartA.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            count_salary_band_60001_70000=10,
            count_salary_band_130001_140000=5,
            count_salary_band_over_500000=15,
        )

        self.assertEqual(parta.count_salary_band_over_60000, 30)
        self.assertEqual(len(parta.list_salary_band_over_60000), 3)


class CharityPartBTestCase(TestCase):
    def setUp(self):
        self.charity = Charity.objects.create(
            organisation_number=123,
            registered_charity_number=123,
            linked_charity_number=0,
            charity_name="Test Charity",
        )

    def test_income_donations(self):
        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_donations_and_legacies=100,
            income_legacies=10,
            income_endowments=20,
        )
        self.assertEqual(partb.income_donations, 70)

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_donations_and_legacies=100,
        )
        self.assertEqual(partb.income_donations, 100)

    def test_expenditure_other_raising_funds(self):
        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            expenditure_raising_funds=100,
            expenditure_investment_management=20,
        )
        self.assertEqual(partb.expenditure_other_raising_funds, 80)

    def test_expenditure_other_charitable_activities(self):
        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            expenditure_charitable_expenditure=100,
            expenditure_grants_institution=20,
        )
        self.assertEqual(partb.expenditure_other_charitable_activities, 80)

    def test_assets_current(self):
        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            assets_other_assets=20,
        )
        self.assertEqual(partb.assets_current, 20)

    def test_assets_other_current(self):
        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            assets_other_assets=100,
            assets_cash=20,
            assets_current_investment=30,
        )
        self.assertEqual(partb.assets_other_current, 50)

    def test_assets_net_current(self):
        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            assets_other_assets=100,
            creditors_one_year_total_current=80,
        )
        self.assertEqual(partb.assets_net_current, 20)

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            assets_other_assets=80,
            creditors_one_year_total_current=100,
        )
        self.assertEqual(partb.assets_net_current, -20)

    def test_assets_less_current_liabilities(self):
        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            assets_total_fixed=100,
            assets_other_assets=80,
            creditors_one_year_total_current=20,
        )
        self.assertEqual(partb.assets_less_current_liabilities, 160)

    def test_assets_total_excluding_pension(self):
        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            assets_total_assets_and_liabilities=100,
            defined_benefit_pension_scheme=80,
        )
        self.assertEqual(partb.assets_total_excluding_pension, 20)

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            assets_total_assets_and_liabilities=80,
            defined_benefit_pension_scheme=100,
        )
        self.assertEqual(partb.assets_total_excluding_pension, -20)

    def test_scale(self):
        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=80,
            funds_total=20_000_000,
        )
        self.assertEqual(partb.scale, 1_000_000)

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=50_000,
            funds_total=100,
        )
        self.assertEqual(partb.scale, 1_000)

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=200,
            funds_total=100,
        )
        self.assertEqual(partb.scale, 1)

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
        )
        self.assertEqual(partb.scale, 1)

    def test_scale_value(self):
        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=80,
            funds_total=20_000_000,
        )
        self.assertEqual(partb.scale_value(20_000_000), 20)

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=50_000,
            funds_total=100,
        )
        self.assertEqual(partb.scale_value(20_000_000), 20_000)

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=200,
            funds_total=100,
        )
        self.assertEqual(partb.scale_value(20_000_000), 20_000_000)

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
        )
        self.assertEqual(partb.scale_value(20_000_000), 20_000_000)

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=80,
            funds_total=20_000_000,
            expenditure_grants_institution=20_000_000,
        )
        self.assertEqual(partb.scale_value("expenditure_grants_institution"), 20)

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=50_000,
            funds_total=100,
            expenditure_grants_institution=20_000_000,
        )
        self.assertEqual(partb.scale_value("expenditure_grants_institution"), 20_000)

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=200,
            funds_total=100,
            expenditure_grants_institution=20_000_000,
        )
        self.assertEqual(
            partb.scale_value("expenditure_grants_institution"), 20_000_000
        )

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            expenditure_grants_institution=20_000_000,
        )
        self.assertEqual(
            partb.scale_value("expenditure_grants_institution"), 20_000_000
        )

    def test_scale_value_format(self):
        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=80,
            funds_total=20_000_000,
        )
        self.assertEqual(partb.scale_value_format(20_000_000), "£20.0m")

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=50_000,
            funds_total=100,
        )
        self.assertEqual(partb.scale_value_format(20_000_000), "£20,000.0k")

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=200,
            funds_total=100,
        )
        self.assertEqual(partb.scale_value_format(20_000_000), "£20,000,000")

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
        )
        self.assertEqual(partb.scale_value_format(20_000_000), "£20,000,000")

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=80,
            funds_total=20_000_000,
            expenditure_grants_institution=20_000_000,
        )
        self.assertEqual(
            partb.scale_value_format("expenditure_grants_institution"), "£20.0m"
        )

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=50_000,
            funds_total=100,
            expenditure_grants_institution=20_000_000,
        )
        self.assertEqual(
            partb.scale_value_format("expenditure_grants_institution"), "£20,000.0k"
        )

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=200,
            funds_total=100,
            expenditure_grants_institution=20_000_000,
        )
        self.assertEqual(
            partb.scale_value_format("expenditure_grants_institution"), "£20,000,000"
        )

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            expenditure_grants_institution=20_000_000,
        )
        self.assertEqual(
            partb.scale_value_format("expenditure_grants_institution"), "£20,000,000"
        )

        partb = CharityARPartB.objects.create(
            charity=self.charity,
            registered_charity_number=self.charity.registered_charity_number,
            income_total_income_and_endowments=100,
            expenditure_total=200,
            funds_total=100,
            expenditure_grants_institution=20_000_000,
        )
        self.assertEqual(
            partb.scale_value_format(
                "expenditure_grants_institution", with_currency=False
            ),
            "20,000,000",
        )


class CharityTrusteeTestCase(TestCase):
    def test_other_trusteeships(self):
        charity_a = Charity.objects.create(
            organisation_number=123,
            registered_charity_number=123,
            linked_charity_number=0,
            charity_name="Test Charity A",
        )
        charity_b = Charity.objects.create(
            organisation_number=124,
            registered_charity_number=124,
            linked_charity_number=0,
            charity_name="Test Charity B",
        )

        trustee_a = CharityTrustee.objects.create(
            charity=charity_a,
            registered_charity_number=charity_a.registered_charity_number,
            linked_charity_number=charity_a.linked_charity_number,
            trustee_id=1,
        )
        trustee_b = CharityTrustee.objects.create(
            charity=charity_b,
            registered_charity_number=charity_b.registered_charity_number,
            linked_charity_number=charity_b.linked_charity_number,
            trustee_id=1,
        )

        self.assertEqual(list(trustee_a.other_trusteeships), [trustee_b])
        self.assertEqual(list(trustee_b.other_trusteeships), [trustee_a])

    def test_other_trusteeships_single(self):
        charity_a = Charity.objects.create(
            organisation_number=123,
            registered_charity_number=123,
            linked_charity_number=0,
            charity_name="Test Charity A",
        )
        charity_b = Charity.objects.create(
            organisation_number=124,
            registered_charity_number=124,
            linked_charity_number=0,
            charity_name="Test Charity B",
        )

        trustee_a = CharityTrustee.objects.create(
            charity=charity_a,
            registered_charity_number=charity_a.registered_charity_number,
            linked_charity_number=charity_a.linked_charity_number,
            trustee_id=1,
        )
        self.assertEqual(trustee_a.other_trusteeships.count(), 0)
