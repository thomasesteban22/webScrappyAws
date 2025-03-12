import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_event():
    return {}


@pytest.fixture
def mock_context():
    return {}


@patch("descargahtml_mitula.mainScrappy.requests.Session")
@patch("descargahtml_mitula.mainScrappy.boto3.client")
def test_download_ok(mock_boto3_client, mock_requests_session,
                     mock_event, mock_context):
    """
    Caso 1: Todas las páginas devuelven 200, se suben 10 .html a S3.
    """
    mock_session_instance = MagicMock()
    mock_requests_session.return_value = mock_session_instance

    mock_response = MagicMock(status_code=200, text="<html>OK</html>")
    mock_session_instance.get.return_value = mock_response

    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3

    result = download_pages(mock_event, mock_context)

    assert result["status"] == "success"
    assert mock_session_instance.get.call_count == 10
    assert mock_s3.put_object.call_count == 10


@patch("descargahtml_mitula.mainScrappy.requests.Session")
@patch("descargahtml_mitula.mainScrappy.boto3.client")
def test_download_404(mock_boto3_client, mock_requests_session,
                      mock_event, mock_context):
    """
    Caso 2: Todas devuelven 404, no se sube nada a S3.
    """
    mock_session_instance = MagicMock()
    mock_requests_session.return_value = mock_session_instance

    mock_response = MagicMock(status_code=404, text="Not Found")
    mock_session_instance.get.return_value = mock_response

    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3

    result = download_pages(mock_event, mock_context)

    assert result["status"] == "success"
    assert mock_session_instance.get.call_count == 10
    assert mock_s3.put_object.call_count == 0


@patch("descargahtml_mitula.mainScrappy.requests.Session")
@patch("descargahtml_mitula.mainScrappy.boto3.client")
def test_download_partial(mock_boto3_client, mock_requests_session,
                          mock_event, mock_context):
    """
    Caso 3: Algunas páginas 200, otras 500 => sube solo las 200.
    """
    mock_session_instance = MagicMock()
    mock_requests_session.return_value = mock_session_instance

    responses = []
    for i in range(10):
        r = MagicMock()
        if i < 5:
            r.status_code = 200
            r.text = f"<html>Fake page {i}</html>"
        else:
            r.status_code = 500
            r.text = "Server Error"
        responses.append(r)

    mock_session_instance.get.side_effect = responses

    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3

    result = download_pages(mock_event, mock_context)

    assert result["status"] == "success"
    assert mock_session_instance.get.call_count == 10
    assert mock_s3.put_object.call_count == 5
