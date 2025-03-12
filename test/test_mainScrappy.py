# webScrappyAws/test/test_mainScrappy.py

import pytest
from unittest.mock import patch, MagicMock
from descargahtml_mitula.mainScrappy import download_pages

@pytest.fixture
def mock_event():
    return {}

@pytest.fixture
def mock_context():
    return {}

@patch("descargahtml_mitula.mainScrappy.requests.Session")
@patch("descargahtml_mitula.mainScrappy.boto3.client")
def test_download_ok(mock_boto3_client, mock_requests_session, mock_event, mock_context):
    """
    Caso 1: Simulamos que todas las páginas devuelven status_code=200,
    y se suben 10 archivos .html a S3.
    """
    # Mockear requests
    mock_session_instance = MagicMock()
    mock_requests_session.return_value = mock_session_instance

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html>Fake HTML</html>"
    mock_session_instance.get.return_value = mock_response

    # Mockear S3
    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3

    result = download_pages(mock_event, mock_context)

    assert result["status"] == "success"
    assert mock_session_instance.get.call_count == 10  # 10 páginas
    assert mock_s3.put_object.call_count == 10         # 10 subidas

@patch("descargahtml_mitula.mainScrappy.requests.Session")
@patch("descargahtml_mitula.mainScrappy.boto3.client")
def test_download_404(mock_boto3_client, mock_requests_session, mock_event, mock_context):
    """
    Caso 2: Simulamos que todas devuelven 404, no sube nada a S3.
    """
    mock_session_instance = MagicMock()
    mock_requests_session.return_value = mock_session_instance

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_session_instance.get.return_value = mock_response

    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3

    result = download_pages(mock_event, mock_context)
    assert result["status"] == "success"

    assert mock_session_instance.get.call_count == 10
    assert mock_s3.put_object.call_count == 0

@patch("descargahtml_mitula.mainScrappy.requests.Session")
@patch("descargahtml_mitula.mainScrappy.boto3.client")
def test_download_partial(mock_boto3_client, mock_requests_session, mock_event, mock_context):
    """
    Caso 3: 5 páginas 200, 5 páginas 500 => sube 5 a S3.
    """
    mock_session_instance = MagicMock()
    mock_requests_session.return_value = mock_session_instance

    responses = []
    for i in range(10):
        r = MagicMock()
        if i < 5:
            r.status_code = 200
            r.text = f"<html>Fake HTML {i}</html>"
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

