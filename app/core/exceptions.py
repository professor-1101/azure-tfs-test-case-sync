"""Custom exceptions for the Azure DevOps Test Plan Import API."""

class AzureDevOpsException(Exception):
    """Base exception for Azure DevOps related errors."""
    pass


class GherkinParseException(Exception):
    """Exception for Gherkin parsing errors."""
    pass


class TestPlanNotFoundException(Exception):
    """Exception when test plan is not found."""
    pass


class TestSuiteCreationException(Exception):
    """Exception when test suite creation fails."""
    pass


class TestCaseCreationException(Exception):
    """Exception when test case creation fails."""
    pass 