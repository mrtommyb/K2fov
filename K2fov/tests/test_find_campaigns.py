"""Tests the K2findCampaigns module."""
import tempfile

from .. import K2findCampaigns


def test_find_campaigns_basics():
    campaigns = K2findCampaigns.findCampaigns(269.5, -28.5)
    assert(campaigns == [9])
    campaigns = K2findCampaigns.findCampaigns(0, 0)
    assert(campaigns == [])


def test_K2findCampaigns_csv():
    """Test the csv version."""
    csv = '269.5, -28.5, 0\n0, 0, 0\n'
    with tempfile.NamedTemporaryFile() as temp:
        try:
            # Python 3
            temp.write(bytes(csv, 'utf-8'))
        except TypeError:
            # Legacy Python
            temp.write(csv)
        temp.flush()
        K2findCampaigns.K2findCampaigns_csv_main(args=[temp.name])
