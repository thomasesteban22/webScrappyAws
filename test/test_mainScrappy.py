import pytest
from unittest.mock import patch, MagicMock
from descargahtml_mitula.mainScrappy import download_pages


@pytest.fixture
def mock_event():
    """
    Fixture para simular el event.
    """
    return {}


@pytest.fixture
def mock_context():
    """
    Fixture para simular el contexto Lambda.
    """
    return {}


@patch("descargahtml_mitula.mainScrappy.requests.Session")
@patch("descargahtml_mitula.mainScrappy.boto3.client")
def test_download_ok(mock_boto3_client, mock_requests_session,
                     mock_event, mock_context):
    """
    Caso 1: Todas las páginas devuelven 200 => 10 .html subidos + 1 ready.txt.
    """
    mock_session_instance = MagicMock()
    mock_requests_session.return_value = mock_session_instance

    # Simulamos que todas las páginas dan 200
    mock_response = MagicMock(status_code=200, text="<html>OK</html>")
    mock_session_instance.get.return_value = mock_response

    # Mock S3
    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3

    # Llamamos a la función real
    result = download_pages(mock_event, mock_context)

    assert result["status"] == "success"
    # Se hicieron 10 GET requests
    assert mock_session_instance.get.call_count == 10
    # Se suben 10 .html + 1 ready.txt = 11
    assert mock_s3.put_object.call_count == 11


@patch("descargahtml_mitula.mainScrappy.requests.Session")
@patch("descargahtml_mitula.mainScrappy.boto3.client")
def test_download_404(mock_boto3_client, mock_requests_session,
                      mock_event, mock_context):
    """
    Caso 2: Todas las páginas devuelven 404 => 0 .html subidos + 1 ready.txt.
    """
    mock_session_instance = MagicMock()
    mock_requests_session.return_value = mock_session_instance

    # Simulamos que todas las páginas dan 404
    mock_response = MagicMock(status_code=404, text="Not Found")
    mock_session_instance.get.return_value = mock_response

    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3

    result = download_pages(mock_event, mock_context)

    assert result["status"] == "success"
    # 10 GET requests
    assert mock_session_instance.get.call_count == 10
    # No se suben .html, pero sí se sube 1 ready.txt
    assert mock_s3.put_object.call_count == 1


@patch("descargahtml_mitula.mainScrappy.requests.Session")
@patch("descargahtml_mitula.mainScrappy.boto3.client")
def test_download_partial(mock_boto3_client, mock_requests_session,
                          mock_event, mock_context):
    """
    Caso 3: 5 páginas 200, 5 páginas 500 => 5 .html subidos + 1 ready.txt.
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
    # 5 .html + 1 ready.txt = 6
    assert mock_s3.put_object.call_count == 6
