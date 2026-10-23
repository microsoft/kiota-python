from mypy import api


def test_httpx_request_adapter_is_a_request_adapter_of_httpx_request(tmp_path):
    snippet = tmp_path / "snippet.py"
    snippet.write_text(
        "import httpx\n"
        "from kiota_abstractions.request_adapter import RequestAdapter\n"
        "from kiota_http.httpx_request_adapter import HttpxRequestAdapter\n"
        "\n"
        "def as_httpx_adapter(adapter: HttpxRequestAdapter) -> RequestAdapter[httpx.Request]:\n"
        "    return adapter\n"
    )
    stdout, _, exit_status = api.run(["--follow-imports=silent", str(snippet)])
    assert exit_status == 0, stdout


def test_package_exports():
    import kiota_http
    assert hasattr(kiota_http, "HttpxRequestAdapter")
    assert hasattr(kiota_http, "KiotaClientFactory")
    assert hasattr(kiota_http, "ObservabilityOptions")
    assert hasattr(kiota_http, "__version__")
    assert "HttpxRequestAdapter" in kiota_http.__all__
    assert "KiotaClientFactory" in kiota_http.__all__
    assert "ObservabilityOptions" in kiota_http.__all__
    assert "__version__" in kiota_http.__all__


def test_package_exports_typecheck(tmp_path):
    snippet = tmp_path / "snippet.py"
    snippet.write_text(
        "from kiota_http import (\n"
        "    HttpxRequestAdapter,\n"
        "    KiotaClientFactory,\n"
        "    ObservabilityOptions,\n"
        "    __version__,\n"
        ")\n"
    )
    stdout, _, exit_status = api.run(["--follow-imports=silent", str(snippet)])
    assert exit_status == 0, stdout
