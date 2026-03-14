class ScrapeError(Exception):
    """Base scraper exception."""


class SiteBlockedError(ScrapeError):
    """The site returned a blocked / forbidden / challenge page."""


class TransientNavigationError(ScrapeError):
    """The page did not become ready, but it may succeed on a later retry."""


class PageStructureChangedError(ScrapeError):
    """The page loaded, but the expected structure/data could not be parsed."""
