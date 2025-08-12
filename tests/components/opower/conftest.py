"""Fixtures for the Opower integration tests."""

from collections.abc import Generator
from datetime import date
from unittest.mock import AsyncMock, Mock, patch

from opower import Account, Forecast, MeterType, ReadResolution, UnitOfMeasure
from opower.utilities.nationalgridma import NationalGridMA
from opower.utilities.pge import PGE
import pytest

from homeassistant.components.opower.const import (
    CONF_CUSTOMER_URN,
    CONF_JWT_TOKEN,
    CONF_REGISTER_ID,
    CONF_SA_UUID,
    CONF_SP_UUID,
    DOMAIN,
)
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


@pytest.fixture
def mock_config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Return the default mocked config entry."""
    config_entry = MockConfigEntry(
        title="Pacific Gas & Electric (test-username)",
        domain=DOMAIN,
        data={
            "utility": "Pacific Gas and Electric Company (PG&E)",
            "username": "test-username",
            "password": "test-password",
        },
    )
    config_entry.add_to_hass(hass)
    return config_entry


@pytest.fixture
def mock_opower_api() -> Generator[AsyncMock]:
    """Mock Opower API."""
    with patch(
        "homeassistant.components.opower.coordinator.Opower", autospec=True
    ) as mock_api:
        api = mock_api.return_value
        api.utility = PGE

        api.async_get_accounts.return_value = [
            Account(
                customer=Mock(),
                uuid="111111-uuid",
                utility_account_id="111111",
                id="111111",
                meter_type=MeterType.ELEC,
                read_resolution=ReadResolution.HOUR,
            ),
            Account(
                customer=Mock(),
                uuid="222222-uuid",
                utility_account_id="222222",
                id="222222",
                meter_type=MeterType.GAS,
                read_resolution=ReadResolution.DAY,
            ),
        ]
        api.async_get_forecast.return_value = [
            Forecast(
                account=Account(
                    customer=Mock(),
                    uuid="111111-uuid",
                    utility_account_id="111111",
                    id="111111",
                    meter_type=MeterType.ELEC,
                    read_resolution=ReadResolution.HOUR,
                ),
                usage_to_date=100,
                cost_to_date=20.0,
                forecasted_usage=200,
                forecasted_cost=40.0,
                typical_usage=180,
                typical_cost=36.0,
                unit_of_measure=UnitOfMeasure.KWH,
                start_date=date(2023, 1, 1),
                end_date=date(2023, 1, 31),
                current_date=date(2023, 1, 15),
            ),
            Forecast(
                account=Account(
                    customer=Mock(),
                    uuid="222222-uuid",
                    utility_account_id="222222",
                    id="222222",
                    meter_type=MeterType.GAS,
                    read_resolution=ReadResolution.DAY,
                ),
                usage_to_date=50,
                cost_to_date=15.0,
                forecasted_usage=100,
                forecasted_cost=30.0,
                typical_usage=90,
                typical_cost=27.0,
                unit_of_measure=UnitOfMeasure.CCF,
                start_date=date(2023, 1, 1),
                end_date=date(2023, 1, 31),
                current_date=date(2023, 1, 15),
            ),
        ]
        api.async_get_cost_reads.return_value = []
        yield api


@pytest.fixture
def mock_config_entry_ng_ma(hass: HomeAssistant) -> MockConfigEntry:
    """Return the National Grid MA config entry with real-time data."""
    config_entry = MockConfigEntry(
        title="National Grid (MA) (test-username)",
        domain=DOMAIN,
        data={
            "utility": "National Grid (MA)",
            "username": "test-username",
            "password": "test-password",
            CONF_JWT_TOKEN: "test-jwt-token",
            CONF_CUSTOMER_URN: "test-customer-urn",
            CONF_SA_UUID: "test-sa-uuid",
            CONF_SP_UUID: "test-sp-uuid",
            CONF_REGISTER_ID: "test-register-id",
        },
    )
    config_entry.add_to_hass(hass)
    return config_entry


@pytest.fixture
def mock_opower_api_ng_ma() -> Generator[AsyncMock]:
    """Mock Opower API for National Grid MA with real-time data."""
    with patch(
        "homeassistant.components.opower.coordinator.Opower", autospec=True
    ) as mock_api:
        api = mock_api.return_value
        api.utility = NationalGridMA

        api.async_get_accounts.return_value = [
            Account(
                customer=Mock(),
                uuid="ng-ma-111111-uuid",
                utility_account_id="ng-ma-111111",
                id="ng-ma-111111",
                meter_type=MeterType.ELEC,
                read_resolution=ReadResolution.HOUR,
            ),
        ]
        api.async_get_forecast.return_value = [
            Forecast(
                account=Account(
                    customer=Mock(),
                    uuid="ng-ma-111111-uuid",
                    utility_account_id="ng-ma-111111",
                    id="ng-ma-111111",
                    meter_type=MeterType.ELEC,
                    read_resolution=ReadResolution.HOUR,
                ),
                usage_to_date=150,
                cost_to_date=25.0,
                forecasted_usage=300,
                forecasted_cost=50.0,
                typical_usage=280,
                typical_cost=45.0,
                unit_of_measure=UnitOfMeasure.KWH,
                start_date=date(2023, 1, 1),
                end_date=date(2023, 1, 31),
                current_date=date(2023, 1, 15),
            ),
        ]
        api.async_get_cost_reads.return_value = []

        # Mock the session for GraphQL requests
        mock_session = AsyncMock()
        api._session = mock_session

        # Mock GraphQL response
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "data": {
                "billingAccountByAuthContext": {
                    "serviceAgreementsConnection": {
                        "edges": [
                            {
                                "node": {
                                    "servicePointsConnection": {
                                        "edges": [
                                            {
                                                "node": {
                                                    "intervalReads": [
                                                        {
                                                            "unit": "KWH",
                                                            "registerId": (
                                                                "test-register-id"
                                                            ),
                                                            "reads": [
                                                                {
                                                                    "timeInterval": (
                                                                        "2023-01-15T12:00:00Z/"
                                                                        "2023-01-15T12:15:00Z"
                                                                    ),
                                                                    "measuredAmount": {
                                                                        "value": 1.5
                                                                    }
                                                                },
                                                                {
                                                                    "timeInterval": (
                                                                        "2023-01-15T12:15:00Z/"
                                                                        "2023-01-15T12:30:00Z"
                                                                    ),
                                                                    "measuredAmount": {
                                                                        "value": 1.8
                                                                    }
                                                                },
                                                                {
                                                                    "timeInterval": (
                                                                        "2023-01-15T12:30:00Z/"
                                                                        "2023-01-15T12:45:00Z"
                                                                    ),
                                                                    "measuredAmount": {
                                                                        "value": 2.1
                                                                    }
                                                                }
                                                            ]
                                                        }
                                                    ],
                                                    "uuid": "test-sp-uuid"
                                                }
                                            }
                                        ]
                                    },
                                    "urn": "test-customer-urn",
                                    "uuid": "test-sa-uuid"
                                }
                            }
                        ]
                    },
                    "urn": "test-customer-urn"
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response

        yield api
