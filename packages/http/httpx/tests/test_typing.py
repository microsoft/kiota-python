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
