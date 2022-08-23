from faker.generator import Generator
from faker.providers import BaseProvider
from faker.providers.address import Provider as AddressProvider


class CharityProvider(BaseProvider):
    def __init__(self, generator: Generator) -> None:
        """Declare the other faker providers."""
        super().__init__(generator)
        self.address = AddressProvider(generator)

    charity_suffixes = (
        "Trust",
        "Society",
        "Foundation",
        "Trustees",
        "Cares",
        "Institute",
        "Association",
        "Charity",
        "Group",
        "CIO",
        "Charitable Incorporated Organisation",
    )

    charity_causes = (
        "Animal Welfare",
        "Arts and Culture",
        "Children",
        "Community",
        "Crime and Justice",
        "Disability",
        "Disaster Relief",
        "Education",
        "Environment",
        "Health",
        "Human Rights",
        "International Development",
        "Justice",
        "Mental Health",
        "Poverty",
        "Religion",
        "Social Services",
    )

    def charity_type(self):
        return "Demonstration Charity"

    def company_number(self):
        return self.numerify("XX00####")

    def charity_name(self):
        return "{} {} {}".format(
            self.address.city(),
            self.random_element(self.charity_causes),
            self.random_element(self.charity_suffixes),
        )
