from django.db import models

from .charity import Charity


class CharityARPartB(models.Model):
    date_of_extract = models.DateField(
        null=True,
        blank=True,
        help_text="The date that the extract was taken from the main dataset.",
    )
    charity = models.ForeignKey(
        Charity,
        db_column="organisation_number",
        to_field="organisation_number",
        on_delete=models.CASCADE,
        help_text="The organisation number for the charity. This is the index value for the charity.",
        related_name="annual_return_part_b",
    )
    registered_charity_number = models.IntegerField(
        db_index=True,
        help_text="The registration number of the registered organisation allocated by the Commission. Note that a main charity and all its linked charities will share the same registered_charity_number.",
    )
    latest_fin_period_submitted_ind = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates whether the financial data on this line relates to the latest financial data submitted by the charity. (True or False)",
    )
    fin_period_order_number = models.IntegerField(
        null=True,
        blank=True,
        help_text="A field to aid ordering of the financial data for each charity. (1=Most recent data in the table, 5=Least recent data in the table)",
    )
    ar_cycle_reference = models.CharField(
        max_length=255,
        help_text="The annual return cycle to which the submission details relate.",
    )
    fin_period_start_date = models.DateField(
        null=True,
        blank=True,
        help_text="The start date of the financial period which is detailed for the charity.",
    )
    fin_period_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="The end date of the financial period which is detailed for the charity.",
    )
    ar_due_date = models.DateField(
        null=True,
        blank=True,
        help_text="The due date of the annual return which is detailed for the charity.",
    )
    ar_received_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date the annual return was received for the financial period which is detailed for the charity.",
    )
    income_donations_and_legacies = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Income from donations and legacies as entered on the Annual Return form for the financial period detailed.",
    )
    income_charitable_activities = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Income received as fees or grants specifically for goods and services supplied by the charity to meet the needs of its beneficiaries for the financial period detailed.",
    )
    income_other_trading_activities = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Income from other trading activity as entered on the Annual Return form for the financial period detailed.",
    )
    income_investments = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Income from investments including dividends, interest and rents but excluding changes (realised and unrealised gains) in the capital value of the investment portfolio for the financial period detailed.",
    )
    income_other = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Other income. This category includes gains on the disposal of own use assets (i.e. fixed assets not held as investments), but otherwise is only used exceptionally for very unusual transactions that cannot be accounted for in the categories above for the financial period detailed.",
    )
    income_total_income_and_endowments = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Total income including endowments for the financial period detailed.",
    )
    income_legacies = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Income from legacies as entered on the Annual Return form for the financial period detailed.",
    )
    income_endowments = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Income from endowments as entered on the Annual Return form for the financial period detailed.",
    )
    expenditure_raising_funds = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Costs associated with providing goods and services to the public, where the main motive is to raise funds for the charity rather than providing goods or services to meet the needs of its beneficiaries for the financial period detailed. (eg charity shops, fundraising dinners etc.).",
    )
    expenditure_charitable_expenditure = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Costs incurred by the charity in supplying goods or services to meet the needs of its beneficiaries. Grants made to meet the needs of the charity’s beneficiaries for the financial period detailed.",
    )
    expenditure_other = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Other expenditure for the financial period detailed. This category is only used very exceptionally for items that don’t fit within one of the categories above.",
    )
    expenditure_total = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Total expenditure for the financial period detailed on the Part B of the annual return.",
    )
    expenditure_investment_management = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Expenditure managing investments for the financial period detailed.",
    )
    expenditure_grants_institution = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Any grants that the charity has awarded to other institutions to further their charitable work.",
    )
    expenditure_governance = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Costs associated with running the charity itself for the financial period. (e.g. costs of trustee meetings, internal and external audit costs and legal advice relating to governance matters).",
    )
    expenditure_support_costs = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Support costs should be allocated across activities and are those costs which, while necessary to deliver an activity, do not themselves produce the activity.  They include the central office functions of the charity and are often apportioned to activities.  The amount shown here is the total amount of support costs (for charitable, fundraising and governance activities) included in resources expended.",
    )
    expenditure_depreciation = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Depreciation charge for the year can be found in the fixed asset analysis notes to the accounts.  This is the amount of depreciation on tangible fixed assets (including impairment charges, if any), which will be shown as the charge for the year in the tangible fixed asset note to the accounts.",
    )
    gain_loss_investment = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="The gain or loss associated with the charity’s investments",
    )
    gain_loss_pension_fund = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="The gain or loss associated with the charity’s pension fund",
    )
    gain_loss_revaluation_fixed_investment = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="The gain or loss associated with any revaluation of fixed assets",
    )
    gain_loss_other = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="The gain or loss associated with any other assets",
    )
    reserves = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="The level of reserves is those unrestricted funds which are freely available for the charity to spend and can be found in the Financial Review in the Trustees Annual Report and will exclude endowments.",
    )
    assets_total_fixed = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Total fixed assets. Fixed assets are those held for continuing use and include tangible fixed assets such as land, buildings, equipment and vehicles, and any investments held on a long-term basis to generate income or gains.",
    )
    assets_own_use = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Total own use assets. This is a calculated field. assets_own_use = assets_total_fixed – assets_long_term_investment",
    )
    assets_long_term_investment = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Fixed Asset Investment are held for the long term to generate income or gains and may include quoted and unquoted shares, bonds, gilts, common investment funds, investment property and term deposits held as part of an investment portfolio.",
    )
    defined_benefit_pension_scheme = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="This is surplus or deficit in any defined benefit pension scheme operated and represents a potential long-term asset or liability.",
    )
    assets_other_assets = models.BigIntegerField(
        null=True, blank=True, help_text="The value of any other assets"
    )
    assets_total_liabilities = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="The value of the total liabilities for the charity. This is a calculated field. assets_total_liabilities = creditors_one_year_total_current + creditors_falling_due_after_one_year",
    )
    assets_current_investment = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Total Current Assets are a separate class of Total Current Asset and they are held with intention of disposing of them within 12 months.",
    )
    assets_total_assets_and_liabilities = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Total Net assets or liabilities can be found on the Balance Sheet. This is the total of all assets shown less all liabilities. This should be the same as the Total funds of the charity.",
    )
    creditors_one_year_total_current = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Creditors due within one year are the amounts owed to creditors and include loans and overdrafts, trade creditors, accruals and deferred income and they are payable within one year.",
    )
    creditors_falling_due_after_one_year = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="These are the amounts owed to creditors payable after more than one year, with provisions for liabilities and charges.",
    )
    assets_cash = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Cash at bank and in hand are a separate class of Total Current Assets.  This amount includes deposits with banks and other financial institutions, which are repayable on demand, but excludes bank overdrafts.",
    )
    funds_endowment = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Endowment funds include the amount of all permanent and expendable endowment funds.",
    )
    funds_unrestricted = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Unrestricted funds include the amount of all funds held for the general purposes of the charity.  This will include unrestricted income funds, designated funds, revaluation reserves and any pension reserve.",
    )
    funds_restricted = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Restricted funds include the amount of all funds held that must be spent on the purposes of the charity.",
    )
    funds_total = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Total funds can be found on the Balance Sheet and should be the same as Total net assets/(liabilities).",
    )
    count_employees = models.IntegerField(
        null=True,
        blank=True,
        help_text="The number of people that the charity employs",
    )
    charity_only_accounts = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if the accounts represent only the charity accounts",
    )
    consolidated_accounts = models.BooleanField(
        null=True,
        blank=True,
        help_text="Consolidated accounts bring together the resources of the charity and the subsidiaries under its control in one statement. These subsidiaries may be non-charitable and to exist for purposes that benefit the parent charity e.g. fund-raising. If set to 1 the accounts are consolidated.",
    )

    @property
    def income_donations(self):
        return (self.income_donations_and_legacies or 0) - (
            (self.income_legacies or 0) + (self.income_endowments or 0)
        )

    @property
    def expenditure_other_raising_funds(self):
        return (self.expenditure_raising_funds or 0) - (
            self.expenditure_investment_management or 0
        )

    @property
    def expenditure_other_charitable_activities(self):
        return (self.expenditure_charitable_expenditure or 0) - (
            self.expenditure_grants_institution or 0
        )

    @property
    def assets_current(self):
        return self.assets_other_assets

    @property
    def assets_other_current(self):
        return (self.assets_other_assets or 0) - (
            (self.assets_cash or 0) + (self.assets_current_investment or 0)
        )

    @property
    def assets_net_current(self):
        return (self.assets_current or 0) - (self.creditors_one_year_total_current or 0)

    @property
    def assets_less_current_liabilities(self):
        return (self.assets_total_fixed or 0) + (self.assets_net_current or 0)

    @property
    def assets_total_excluding_pension(self):
        return (self.assets_total_assets_and_liabilities or 0) - (
            self.defined_benefit_pension_scheme or 0
        )

    @property
    def scale(self):
        max_value = max(
            abs((self.income_total_income_and_endowments or 0)),
            abs((self.expenditure_total or 0)),
            abs((self.funds_total or 0)),
        )
        if max_value > 10_000_000:
            return 1_000_000
        if max_value > 10_000:
            return 1_000
        return 1

    def scale_value(self, attr):
        if isinstance(attr, (float, int)):
            value = attr
        else:
            value = getattr(self, attr) or 0
        return value / self.scale

    def scale_value_format(self, attr, with_currency=True, if_zero="-"):
        prefix = "£" if with_currency else ""
        suffix = ""
        if self.scale == 1_000_000:
            suffix = "m"
        elif self.scale == 1_000:
            suffix = "k"
        format_str = "{:,.1f}" if self.scale > 1 else "{:,.0f}"
        value = self.scale_value(attr)
        if value == 0 and if_zero:
            return if_zero
        return prefix + format_str.format(value) + suffix

    class Meta:
        verbose_name = "Annual Return - Part B"
        verbose_name_plural = "Annual Return - Part B"
